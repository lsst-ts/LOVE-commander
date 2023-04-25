"""Define LOVE CSC subapplication, which provides the endpoints
to request info to the LOVE CSC from SAL."""
import os
import logging
from tempfile import TemporaryFile
from aiohttp import web
from lsst.ts import utils
from lsst.ts import salobj


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

    def unavailable_s3_bucket():
        """Return a response for the case when the S3 bucket is not available.

        Returns
        -------
        Response
            The response for the HTTP request with the following structure:

            .. code-block:: json

                {
                    "ack": "<Description about the \
                    success state of the request>"
                }
        """
        return web.json_response(
            {"ack": "Could not stablish connection with S3 Bucket "},
            status=400,
        )

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

    def unavailable_love_controller():
        """Return a response for the case when the LOVE CSC is not available.

        Returns
        -------
        Response
            The response for the HTTP request with the following structure:

            .. code-block:: json

                {
                    "ack": "<Description about the \
                    success state of the request>"
                }
        """
        return web.json_response(
            {"ack": "LOVE CSC could not stablish connection"}, status=400
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
        if not s3_bucket:
            connect_to_s3_bucket()
        if not s3_bucket:
            return unavailable_s3_bucket()

        if not LOVE_controller:
            connect_to_love_controller()
        if not LOVE_controller:
            return unavailable_love_controller()
        await LOVE_controller.start_task

        reader = await request.multipart()
        field = await reader.next()

        try:
            assert field.name == "uploaded_file"
        except AssertionError:
            return web.json_response(
                {"ack": "Request must have a file uploaded"},
                status=400,
            )

        filename = field.filename
        file_type = filename.split(".")[-1]
        key = s3_bucket.make_key(
            salname="LOVE",
            salindexname=0,
            generator="OLE",
            date=utils.astropy_time_from_tai_unix(utils.current_tai()),
            suffix="." + file_type,
        )

        try:
            with TemporaryFile() as f:
                file_data = await field.read()
                f.write(file_data)
                f.seek(0)
                await s3_bucket.upload(fileobj=f, key=key)
            new_url = f"{s3_bucket.service_resource.meta.client.meta.endpoint_url}/{s3_bucket.name}/{key}"
        except Exception as e:
            return web.json_response(
                {"ack": f"File could not be uploaded: {e}"},
                status=400,
            )

        await LOVE_controller.evt_largeFileObjectAvailable.set_write(
            url=new_url,
            generator=f"{LOVE_controller.salinfo.name}:{LOVE_controller.salinfo.index}",
        )

        return web.json_response(
            {
                "ack": "Added new file to S3 bucket",
                "url": new_url,
            },
            status=200,
        )

    async def on_cleanup(lfa_app):
        pass

    connect_to_love_controller()
    lfa_app.router.add_post("/upload-file", upload_file)
    lfa_app.on_cleanup.append(on_cleanup)

    return lfa_app