import json

from lsst.ts import salobj


async def test_successful_command(client, *args, **kwargs):
    # Arrange
    remote = salobj.Remote(domain=salobj.Domain(), name="LOVE")

    await remote.start_task

    observing_log_msg = {
        "user": "an user",
        "message": "a message",
    }

    # Act
    remote.evt_observingLog.flush()
    response = await client.post(
        "/lovecsc/observinglog", data=json.dumps(observing_log_msg)
    )

    # Assert
    assert response.status == 200
    response = await response.json()
    assert response["ack"] == "Added new observing log to SAL"

    result = await remote.evt_observingLog.next(flush=False)
    assert result.user == "an user"
    assert result.message == "a message"

    # Clean up
    await remote.close()


async def test_wrong_data(client, *args, **kwargs):
    # Arrange
    data = {"wrong": "data"}

    # Act
    response = await client.post("/lovecsc/observinglog", json=data)

    # Assert
    assert response.status == 400
    response = await response.json()
    assert (
        response["ack"]
        == "Request must have JSON data with the following keys: user, message."
        + f" Received {json.dumps(data)}"
    )
