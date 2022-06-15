"""Define LOVE CSC subapplication, which provides the endpoints to request info to the LOVE CSC from SAL."""
import json
from aiohttp import web
from lsst.ts import utils
from lsst.ts import salobj


def create_app(*args, **kwargs):
    """Create the LFA application

    Returns
    -------
    object
        The application instance
    """
    lfa_app = web.Application()

    mock_s3 = True
    s3_bucket_name = salobj.AsyncS3Bucket.make_bucket_name(
        s3instance="Tucson"
    )  # TODO: dynamic instance
    s3_bucket = salobj.AsyncS3Bucket(
        name=s3_bucket_name, domock=mock_s3, create=mock_s3
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
                    "ack": "<Description about the success state of the request>"
                }
        """
        data = await request.json()

        try:
            assert "file" in data
        except AssertionError:
            return web.json_response(
                {
                    "ack": "Request must have JSON data with the following keys:"
                    + f" file. Received {json.dumps(data)}"
                },
                status=400,
            )

        file = data["file"]
        file_type = file.split(".")[-1]
        key = s3_bucket.make_key(
            salname="LOVE",
            salindexname=0,
            generator="OLE",
            date=utils.astropy_time_from_tai_unix(utils.current_tai()),
            suffix=file_type,
        )

        try:
            await s3_bucket.upload(fileobj=file, key=key)
            print("File uploaded correctly!")
            new_url = f"{s3_bucket.service_resource.meta.client.meta.endpoint_url}/{s3_bucket.name}/{key}"
            print(new_url)
        except Exception as e:
            print("File could not be uploaded")
            print(e)

        return web.json_response(
            {
                "ack": "Added new file to S3 bucket",
                "url": new_url,
            },
            status=200,
        )

    lfa_app.router.add_post("/upload_file", upload_file)

    async def on_cleanup(lfa_app):
        pass

    lfa_app.on_cleanu.pappend(on_cleanup)

    return lfa_app
