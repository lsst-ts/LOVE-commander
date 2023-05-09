"""Define LOVE CSC subapplication, which provides the endpoints
to request info to the LOVE CSC from SAL."""
import os
import logging
from aiohttp import web
from lsst.ts import salobj
from love.commander.utils import (
    unavailable_love_controller,
    unavailable_s3_bucket,
    check_file_exists_in_s3_bucket,
    upload_file_to_s3_bucket,
)


s3_bucket = None
LOVE_controller = None


def create_app(*args, **kwargs):
    """Create the LFA application

    Returns
    -------
    object
        The application instance
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

    def connect_to_love_controller():
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
            LOVE_controller = salobj.Controller("LOVE", index=None, do_callbacks=False)
        except Exception as e:
            logging.warning(e)
            LOVE_controller = None

    def make_connections():
        """Make connections to the LOVE CSC and the S3 bucket.

        Returns
        -------
        bool
            True if both connections are established, False otherwise.
        """
        global s3_bucket, LOVE_controller
        if not s3_bucket:
            connect_to_s3_bucket()
        if not LOVE_controller:
            connect_to_love_controller()

    async def check_file_exists(request):
        """Check if a file exists in the S3 bucket.

        Parameters
        ----------
        request : Request
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
        make_connections()
        if not s3_bucket:
            return unavailable_s3_bucket()

        json_req = await request.json()
        file_key = json_req["file_key"]
        return await check_file_exists_in_s3_bucket(s3_bucket, file_key)

    async def upload_love_thumbnail(request):
        """Handle file upload for LOVE thumbnail requests.

        Parameters
        ----------
        request : Request
            The original HTTP request

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
        make_connections()
        if not s3_bucket:
            return unavailable_s3_bucket()
        if not LOVE_controller:
            return unavailable_love_controller()

        # Wait for the LOVE controller to be ready
        await LOVE_controller.start_task

        reader = await request.multipart()
        field = await reader.next()

        return await upload_file_to_s3_bucket(
            field, s3_bucket, LOVE_controller, "THUMBNAIL"
        )

    async def upload_love_config_file(request):
        """Handle file upload for LOVE config requests.

        Parameters
        ----------
        request : Request
            The original HTTP request

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
        make_connections()
        if not s3_bucket:
            return unavailable_s3_bucket()
        if not LOVE_controller:
            return unavailable_love_controller()

        # Wait for the LOVE controller to be ready
        await LOVE_controller.start_task

        reader = await request.multipart()
        field = await reader.next()

        return await upload_file_to_s3_bucket(
            field, s3_bucket, LOVE_controller, "CONFIG"
        )

    async def upload_file(request):
        """Handle file upload for OLE requests.

        Parameters
        ----------
        request : Request
            The original HTTP request

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
        make_connections()
        if not s3_bucket:
            return unavailable_s3_bucket()
        if not LOVE_controller:
            return unavailable_love_controller()

        # Wait for the LOVE controller to be ready
        await LOVE_controller.start_task

        reader = await request.multipart()
        field = await reader.next()

        return await upload_file_to_s3_bucket(field, s3_bucket, LOVE_controller, "OLE")

    async def on_cleanup(lfa_app):
        pass

    make_connections()
    lfa_app.router.add_post("/file-exists", check_file_exists)
    lfa_app.router.add_post("/upload-file", upload_file)
    lfa_app.router.add_post("/upload-love-config-file", upload_love_config_file)
    lfa_app.router.add_post("/upload-love-thumbnail", upload_love_thumbnail)
    lfa_app.on_cleanup.append(on_cleanup)

    return lfa_app
