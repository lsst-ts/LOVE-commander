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

import random
from unittest.mock import patch

from astropy.time import Time
from love.commander.app import create_app
from love.commander.reports import CHRONOGRAF_DASHBOARDS_PATHS, SITE_DOMAINS


class MockEFDClient:
    pass


class MockBumpTestTimes:
    async def find_times(self, actuator_id, start, end):
        return (
            [
                (Time("2024-01-01T00:00:00"), Time("2024-01-01T01:00:00")),
                (Time("2024-01-02T00:00:00"), Time("2024-01-02T01:00:00")),
                (Time("2024-01-03T00:00:00"), Time("2024-01-03T01:00:00")),
            ],
            [
                (Time("2024-01-01T00:00:00"), Time("2024-01-01T01:00:00")),
                (Time("2024-01-02T00:00:00"), Time("2024-01-02T01:00:00")),
                (Time("2024-01-03T00:00:00"), Time("2024-01-03T01:00:00")),
            ],
        )


async def test_query_m1m3_bump_tests(aiohttp_client):
    """Test the get timeseries response."""
    # Arrange
    ac = await anext(aiohttp_client)
    client = await ac(create_app())

    # Start patching `EfdClient`.
    mock_efd_patcher = patch("lsst_efd_client.EfdClient")
    mock_efd_client = mock_efd_patcher.start()
    mock_efd_client.return_value = MockEFDClient()

    # Start patching `BumpTestTimes`.
    mock_bump_test_times_patcher = patch("love.commander.reports.BumpTestTimes")
    mock_bump_test_times = mock_bump_test_times_patcher.start()
    mock_bump_test_times.return_value = MockBumpTestTimes()

    selected_efd_instance = random.choice(["summit_efd", "usdf_efd"])
    request_data = {
        "efd_instance": selected_efd_instance,
        "start_date": "2024-01-01T00:00:00",
        "end_date": "2024-01-31T00:00:00",
        "actuator_id": 437,
    }
    response = await client.post("/reports/m1m3-bump-tests/", json=request_data)
    assert response.status == 200

    response_data = await response.json()

    assert "primary" in response_data
    assert "secondary" in response_data

    assert len(response_data["primary"]) == 3
    assert len(response_data["secondary"]) == 3

    assert response_data["primary"][0]["start"] == "2024-01-01T00:00:00.000"
    assert response_data["primary"][0]["end"] == "2024-01-01T01:00:00.000"

    assert "url" in response_data["primary"][0]
    assert response_data["primary"][0]["url"].startswith(
        "https://"
        + SITE_DOMAINS[selected_efd_instance]
        + CHRONOGRAF_DASHBOARDS_PATHS["m1m3_bump_tests"][selected_efd_instance]
    )

    # Stop patches
    mock_efd_patcher.stop()
    mock_bump_test_times_patcher.stop()
