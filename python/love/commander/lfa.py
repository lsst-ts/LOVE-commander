# This file is part of LOVE-commander.
#
# Copyright (c) 2023 Inria Chile.
#
# Developed by Inria Chile.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or at
# your option any later version.
#
# This program is distributed in the hope that it will be useful,but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
# for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.

import logging
import os

from aiohttp import web
from love.commander.utils import (
    check_file_exists_in_s3_bucket,
    unavailable_love_controller,
    unavailable_s3_bucket,
    upload_file_to_s3_bucket,
)
from lsst.ts import salobj

s3_bucket = None
LOVE_controller = None


def create_app(*args, **kwargs):
    """Create the LFA application.

    Define the LFA subapplication, which provides the endpoints to
    connect to the LFA S3 bucket.

    Returns
    -------
    `aiohttp.web.Application`
        The application instance.
    """
    lfa_app = web.Application()

    def connect_to_s3_bucket():
        """Connect to the S3 bucket to be used for the OLE requests.

        Notes
        -----
        The S3 bucket is defined by the environment variable S3_INSTANCE.
        If the environment variable MOCK_S3 is set to True, the connection
        will be mocked.

        s3_bucket is a global variable that will be used to store the
        connection to the S3 bucket. If the connection could not be
        established, s3_bucket will be set to None.
        """
        global s3_bucket
        S3_INSTANCE = os.environ.get("S3_INSTANCE")
        mock_s3 = True if os.environ.get("MOCK_S3", False) else False

        try:
            s3_bucket_name = salobj.AsyncS3Bucket.make_bucket_name(
                s3instance=S3_INSTANCE
            )
            s3_bucket = salobj.AsyncS3Bucket(
                name=s3_bucket_name, domock=mock_s3, create=mock_s3
            )
        except Exception as e:
            logging.warning(e)
            s3_bucket = None

    async def connect_to_love_controller():
        """Connect to the LOVE CSC.

        Notes
        -----
        LOVE_controller is a global variable that will be used to store the
        connection to the LOVE CSC using `salobj.Controller`.
        If the connection could not be established, LOVE_controller will
        be set to None.
        """
        global LOVE_controller
        try:
            LOVE_controller = salobj.Controller(
                "LOVE", index=None, do_callbacks=False, write_only=True
            )
            await LOVE_controller.start_task
        except Exception as e:
            logging.warning(e)
            LOVE_controller = None

    async def close_love_controller():
        """Close the connection to the LOVE CSC.

        Notes
        -----
        This function will close the connection to the LOVE CSC and set
        LOVE_controller to None.
        """
        global LOVE_controller
        if LOVE_controller:
            await LOVE_controller.close()
            LOVE_controller = None

    async def check_file_exists(request):
        """Check if a file exists in the S3 bucket.

        Parameters
        ----------
        request : `Request`
            The original HTTP request

        Returns
        -------
        Response
            The response for the HTTP request with the following structure:

            .. code-block:: json

                {
                    "exists": "<True if the file exists, False otherwise>"
                }
        """
        global s3_bucket
        if not s3_bucket:
            return unavailable_s3_bucket()

        json_req = await request.json()
        file_key = json_req["file_key"]
        return await check_file_exists_in_s3_bucket(s3_bucket, file_key)

    async def upload_love_thumbnail(request):
        """Handle file upload for LOVE thumbnail requests.

        Parameters
        ----------
        request : `Request`
            The original HTTP request.

        Returns
        -------
        Response
            The response for the HTTP request with the following structure:

            .. code-block:: json

                {
                    "ack": "<Description about the \
                    success state of the request>",
                    "url": "<URL to the uploaded file>"
                }
        """

        global s3_bucket, LOVE_controller
        if not s3_bucket:
            return unavailable_s3_bucket()
        if not LOVE_controller:
            return unavailable_love_controller()

        reader = await request.multipart()
        field = await reader.next()

        return await upload_file_to_s3_bucket(
            field, s3_bucket, LOVE_controller, "THUMBNAIL"
        )

    async def upload_love_config_file(request):
        """Handle file upload for LOVE config requests.

        Parameters
        ----------
        request : `Request`
            The original HTTP request.

        Returns
        -------
        Response
            The response for the HTTP request with the following structure:

            .. code-block:: json

                {
                    "ack": "<Description about the \
                    success state of the request>",
                    "url": "<URL to the uploaded file>"
                }
        """

        global s3_bucket, LOVE_controller
        if not s3_bucket:
            return unavailable_s3_bucket()
        if not LOVE_controller:
            return unavailable_love_controller()

        reader = await request.multipart()
        field = await reader.next()

        return await upload_file_to_s3_bucket(
            field, s3_bucket, LOVE_controller, "CONFIG"
        )

    async def upload_file(request):
        """Handle file upload for OLE requests.

        Parameters
        ----------
        request : `Request`
            The original HTTP request.

        Returns
        -------
        Response
            The response for the HTTP request with the following structure:

            .. code-block:: json

                {
                    "ack": "<Description about the \
                    success state of the request>",
                    "url": "<URL to the uploaded file>"
                }
        """

        global s3_bucket, LOVE_controller
        if not s3_bucket:
            return unavailable_s3_bucket()
        if not LOVE_controller:
            return unavailable_love_controller()

        try:
            reader = await request.multipart()
        except AssertionError:
            return web.json_response(
                {"ack": "Request content type must be multipart"}, status=400
            )

        field = await reader.next()
        return await upload_file_to_s3_bucket(field, s3_bucket, LOVE_controller, "OLE")

    async def on_startup(lfa_app):
        logging.info("Running LOVE controller")
        await connect_to_love_controller()
        logging.info("Running S3 bucket connection")
        connect_to_s3_bucket()

    async def on_cleanup(lfa_app):
        logging.info("Closing LOVE controller")
        await close_love_controller()

    lfa_app.router.add_post("/file-exists", check_file_exists)
    lfa_app.router.add_post("/upload-file", upload_file)
    lfa_app.router.add_post("/upload-love-config-file", upload_love_config_file)
    lfa_app.router.add_post("/upload-love-thumbnail", upload_love_thumbnail)

    lfa_app.on_startup.append(on_startup)
    lfa_app.on_cleanup.append(on_cleanup)

    return lfa_app
