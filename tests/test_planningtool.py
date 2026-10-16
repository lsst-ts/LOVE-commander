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

from unittest.mock import patch

from .test_utils import assert_all_objects_in_list_have_keys


class MockZephyrInterface:
    """Mock Zephyr interface for testing."""

    async def get_test_cycles(self, cycle_keys):
        return [
            {
                "id": "12345678",
                "key": "CYCLE-1",
                "name": "Test cycle #1",
            },
            {
                "id": "12345679",
                "key": "CYCLE-2",
                "name": "Test cycle #2",
            },
            {
                "id": "12345670",
                "key": "CYCLE-3",
                "name": "Test cycle #3",
            },
        ]

    async def get_test_cycle(self, cycle_key):
        return {
            "id": "12345678",
            "key": cycle_key,
            "name": f"Test cycle {cycle_key}",
            "description": "Test cycle description",
            "project": "BLOCK",
            "status": "Done",
            "folder": "/Folder",
            "owner": "User",
            "customFields": {
                "Night Support": "Tiago Ribeiro",
                "Night Planner": "Bruno Quint",
                "Night Summary": "Test cycle summary",
                "TMA walk around done": True,
                "TMA walk around - performed by": "User",
                "TMA walk around - comments": "Test cycle comments",
                "TMA ready for use?": True,
                "End of Night - TMA El Position": "El Position",
                "End of Night - TMA Az Position": "Az Position",
                "End of Night - OSS Power Status": "Power Status",
                "End of Night - Power Supply Status": "Power Supply Status",
            },
        }

    async def get_test_cases(self, cycle_key):
        return [
            {
                "id": "12345678",
                "key": "CASE-1",
                "name": "Test case #1",
                "environment": "Test environment",
                "status": "Done",
                "executed_by": "User",
            },
            {
                "id": "12345679",
                "key": "CASE-2",
                "name": "Test case #2",
                "environment": "Test environment",
                "status": "Done",
                "executed_by": "User",
            },
            {
                "id": "12345670",
                "key": "CASE-3",
                "name": "Test case #3",
                "environment": "Test environment",
                "status": "Done",
                "executed_by": "User",
            },
        ]

    async def get_last_test_execution(self, cycle_key, case_key):
        return {
            "test_case": "BLOCK-T17",
            "version": "1.0",
            "title": "AuxTel Daytime Checkouts",
            "status": "PASSED",
            "environment": "2. Late Afternoon",
            "release_version": "None",
            "executed_by": "Bruno Quint",
            "executed_time": 15,
            "iteration": "None",
            "assignee": "Bruno Quint",
            "estimated_time": 1200,
            "objective": "Complete AuxTel Daytime Checkouts",
            "precondition": "AuxTel is in a good state",
            "comment": "All tests passed successfully",
            "steps": [
                {
                    "title": "Enable LATISS",
                    "status": "NOT EXECUTED",
                    "test_data": "None",
                    "expected_result": (
                        "Script completes without error. "
                        "All ATSpectrograph components are enabled."
                    ),
                    "sal_script": "auxtel/enable_latiss.py",
                    "script_configuration": "",
                    "is_external": True,
                    "actual_result": "None",
                },
                {
                    "title": "Run LATISS checkouts",
                    "status": "NOT EXECUTED",
                    "test_data": "None",
                    "expected_result": "Script completes without error.",
                    "sal_script": "auxtel/daytime_checkout/latiss_checkout.py",
                    "script_configuration": "",
                    "is_external": False,
                    "actual_result": "None",
                },
                {
                    "title": "Enable ATCS.",
                    "status": "NOT EXECUTED",
                    "test_data": "None",
                    "expected_result": (
                        "Script completes without error. "
                        "All AuxTel components are in enabled mode."
                    ),
                    "sal_script": "auxtel/enable_atcs.py",
                    "script_configuration": "",
                    "is_external": False,
                    "actual_result": "None",
                },
                {
                    "title": "ATPneumatics Checkout",
                    "status": "NOT EXECUTED",
                    "test_data": "None",
                    "expected_result": "Script completes without error.",
                    "sal_script": "auxtel/daytime_checkout/atpneumatics_checkout.py",
                    "script_configuration": "",
                    "is_external": False,
                    "actual_result": "None",
                },
            ],
        }


async def test_query_zephyr_test_cycles(http_client):
    """Test the get test cycle response."""
    # Arrange
    # Start patching `ZephyrInterface`.
    mock_zephyr_patcher = patch("love.commander.planningtool.ZephyrInterface")
    mock_zephyr_client = mock_zephyr_patcher.start()
    mock_zephyr_client.return_value = MockZephyrInterface()

    request_data = {
        "zephyr_api_token": "test",
        "jira_api_token": "test",
        "jira_username": "test",
    }

    # Act
    response = await http_client.post("/planningtool/test-cycles/", json=request_data)

    # Assert
    assert response.status == 200
    response_data = await response.json()

    assert len(response_data) == 3
    assert_all_objects_in_list_have_keys(["id", "key", "name"], response_data)

    # Stop patches
    mock_zephyr_patcher.stop()


async def test_query_zephyr_test_cycle(http_client):
    """Test the get test cycle response."""
    # Arrange
    # Start patching `ZephyrInterface`.
    mock_zephyr_patcher = patch("love.commander.planningtool.ZephyrInterface")
    mock_zephyr_client = mock_zephyr_patcher.start()
    mock_zephyr_client.return_value = MockZephyrInterface()

    request_data = {
        "zephyr_api_token": "test",
        "jira_api_token": "test",
        "jira_username": "test",
        "test_cycle_key": "CYCLE-1",
    }

    # Act
    response = await http_client.post("/planningtool/test-cycle/", json=request_data)

    # Assert
    assert response.status == 200
    response_data = await response.json()

    assert response_data["id"] == "12345678"
    assert response_data["key"] == "CYCLE-1"
    assert response_data["name"] == "Test cycle CYCLE-1"
    assert response_data["description"] == "Test cycle description"
    assert response_data["project"] == "BLOCK"
    assert response_data["status"] == "Done"
    assert response_data["folder"] == "/Folder"
    assert response_data["owner"] == "User"
    assert response_data["customFields"]["Night Support"] == "Tiago Ribeiro"
    assert response_data["customFields"]["Night Planner"] == "Bruno Quint"
    assert response_data["customFields"]["Night Summary"] == "Test cycle summary"
    assert response_data["customFields"]["TMA walk around done"] is True
    assert response_data["customFields"]["TMA walk around - performed by"] == "User"
    assert (
        response_data["customFields"]["TMA walk around - comments"]
        == "Test cycle comments"
    )
    assert response_data["customFields"]["TMA ready for use?"] is True
    assert (
        response_data["customFields"]["End of Night - TMA El Position"] == "El Position"
    )
    assert (
        response_data["customFields"]["End of Night - TMA Az Position"] == "Az Position"
    )
    assert (
        response_data["customFields"]["End of Night - OSS Power Status"]
        == "Power Status"
    )
    assert (
        response_data["customFields"]["End of Night - Power Supply Status"]
        == "Power Supply Status"
    )

    # Stop patches
    mock_zephyr_patcher.stop()


async def test_query_zephyr_test_cases(http_client):
    """Test the get test case response."""
    # Arrange
    # Start patching `ZephyrInterface`.
    mock_zephyr_patcher = patch("love.commander.planningtool.ZephyrInterface")
    mock_zephyr_client = mock_zephyr_patcher.start()
    mock_zephyr_client.return_value = MockZephyrInterface()

    request_data = {
        "zephyr_api_token": "test",
        "jira_api_token": "test",
        "jira_username": "test",
        "test_cycle_key": "CYCLE-1",
    }

    # Act
    response = await http_client.post("/planningtool/test-cases/", json=request_data)

    # Assert
    assert response.status == 200
    response_data = await response.json()

    assert len(response_data) == 3
    assert_all_objects_in_list_have_keys(
        ["id", "key", "name", "environment", "status", "executed_by"],
        response_data,
    )

    # Stop patches
    mock_zephyr_patcher.stop()


async def test_query_zephyr_last_test_execution(http_client):
    """Test the get last test execution response."""
    # Arrange
    # Start patching `ZephyrInterface`.
    mock_zephyr_patcher = patch("love.commander.planningtool.ZephyrInterface")
    mock_zephyr_client = mock_zephyr_patcher.start()
    mock_zephyr_client.return_value = MockZephyrInterface()

    request_data = {
        "zephyr_api_token": "test",
        "jira_api_token": "test",
        "jira_username": "test",
        "test_cycle_key": "CYCLE-1",
        "test_case_key": "CASE-1",
    }

    # Act
    response = await http_client.post(
        "/planningtool/test-last-execution/", json=request_data
    )

    # Assert
    assert response.status == 200
    response_data = await response.json()

    assert response_data["test_case"] == "BLOCK-T17"
    assert response_data["version"] == "1.0"
    assert response_data["title"] == "AuxTel Daytime Checkouts"
    assert response_data["status"] == "PASSED"
    assert response_data["environment"] == "2. Late Afternoon"
    assert response_data["release_version"] == "None"
    assert response_data["executed_by"] == "Bruno Quint"
    assert response_data["executed_time"] == 15
    assert response_data["iteration"] == "None"
    assert response_data["assignee"] == "Bruno Quint"
    assert response_data["estimated_time"] == 1200
    assert response_data["objective"] == "Complete AuxTel Daytime Checkouts"
    assert response_data["precondition"] == "AuxTel is in a good state"
    assert response_data["comment"] == "All tests passed successfully"

    assert len(response_data["steps"]) == 4
    assert_all_objects_in_list_have_keys(
        [
            "title",
            "status",
            "test_data",
            "expected_result",
            "sal_script",
            "script_configuration",
            "is_external",
            "actual_result",
        ],
        response_data["steps"],
    )

    # Stop patches
    mock_zephyr_patcher.stop()
