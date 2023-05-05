from aiohttp import web
from lsst.ts import utils
from tempfile import TemporaryFile


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

async def check_file_exists_in_s3_bucket(s3_bucket, file_key):
    """Check if a file exists in the S3 bucket.

    Parameters
    ----------
    s3_bucket: S3Bucket
        The S3 bucket to check if the file exists
    file_key: str
        The key of the file to check if it exists

    Returns
    -------
    Response
        The response for the HTTP request with the following structure:

        .. code-block:: json

            {
                "exists": "<True if the file exists, False otherwise>"
            }
    """
    exists = await s3_bucket.exists(file_key)
    return web.json_response({"exists": exists})

async def upload_file_to_s3_bucket(field, s3_bucket, LOVE_controller, generator):
    """Handle file upload for LOVE config requests.

    Parameters
    ----------
    field: MultipartReader
        The file uploaded on the HTTP request
    s3_bucket: S3Bucket
        The S3 bucket to upload the file
    LOVE_controller: salobj.Controller
        The LOVE CSC controller
    generator: str
        The generator of the file, used for custom LOVE purposes

    Returns
    -------
    Response
        The response for the HTTP request with the following structure:

        .. code-block:: json

            {
                "ack": "<Description about the \
                success state of the request>",
                "url": "<URL to the uploaded file, if successful>"
            }
    """

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
        generator=generator,
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
