"""Define LOVE CSC subapplication, which provides the endpoints
to request info to the LOVE CSC from SAL."""
import os
from tempfile import TemporaryFile
from aiohttp import web
from lsst.ts import utils
from lsst.ts import salobj


s3_bucket = None


def create_app(*args, **kwargs):
    """Create the LFA application

    Returns
    -------
    object
        The application instance
    """
    lfa_app = web.Application()

    def connect_to_s3_bucket():
        global s3_bucket

        # Define the S3 instance to be used
        S3_INSTANCE = os.environ.get("S3_INSTANCE")

        mock_s3 = True  # Remove on production

        try:
            s3_bucket_name = salobj.AsyncS3Bucket.make_bucket_name(
                s3instance=S3_INSTANCE
            )

            s3_bucket = salobj.AsyncS3Bucket(
                name=s3_bucket_name, domock=mock_s3, create=mock_s3
            )
        except Exception:
            s3_bucket = None

    def unavailable_s3_bucket():
        return web.json_response(
            {"ack": "Could not stablish connection with S3 Bucket "},
            status=400,
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
                    success state of the request>"
                }
        """

        global s3_bucket
        if not s3_bucket:
            connect_to_s3_bucket()
        if not s3_bucket:
            return unavailable_s3_bucket()

        if s3_bucket is None:
            return web.json_response(
                {"ack": "Connection to the S3 bucket could not be stablished"},
                status=400,
            )

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
            size = 0
            with TemporaryFile() as f:
                while True:
                    chunk = await field.read_chunk()
                    if not chunk:
                        break
                    size += len(chunk)
                    f.write(chunk)
                await s3_bucket.upload(fileobj=f, key=key)
            new_url = f"{s3_bucket.service_resource.meta.client.meta.endpoint_url}/{s3_bucket.name}/{key}"
        except Exception as e:
            print(e, flush=True)
            return web.json_response(
                {"ack": "File could not be uploaded"},
                status=400,
            )

        return web.json_response(
            {
                "ack": "Added new file to S3 bucket",
                "url": new_url,
            },
            status=200,
        )

    lfa_app.router.add_post("/upload-file", upload_file)

    async def on_cleanup(lfa_app):
        pass

    lfa_app.on_cleanup.append(on_cleanup)

    return lfa_app
