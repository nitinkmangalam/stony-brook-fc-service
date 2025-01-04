from unittest.mock import Mock, patch

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from routers.overview_router import router

# Setup test app
app = FastAPI()
app.include_router(router)
client = TestClient(app)

# Mock data
mock_overview_data = {
    "progress": {"matchesPlayed": 10, "totalMatches": 29, "currentPhase": "League Phase"},
    "stats": {"totalMatches": 10, "totalGoals": 25, "averageGoals": 2.5},
    "topScorer": {"name": "John Doe", "goals": 5},
}


# Fixture for mocking OverviewService
@pytest.fixture
def mock_overview_service():
    with patch("routers.overview_router.OverviewService") as mock:
        service_instance = Mock()
        mock.return_value = service_instance
        yield service_instance


# Test GET /overview
def test_get_overview_stats_success(mock_overview_service):
    # Arrange
    mock_overview_service.get_overview_stats.return_value = mock_overview_data

    # Act
    response = client.get("/overview")

    # Assert
    assert response.status_code == 200
    assert response.json()["progress"]["matchesPlayed"] == 10
    assert response.json()["stats"]["totalMatches"] == 10
    mock_overview_service.get_overview_stats.assert_called_once()


def test_get_overview_stats_empty(mock_overview_service):
    # Arrange
    mock_empty_data = {
        "progress": {"matchesPlayed": 0, "totalMatches": 29},
        "stats": {"totalMatches": 0, "totalGoals": 0, "averageGoals": 0},
        "topScorer": None,
    }
    mock_overview_service.get_overview_stats.return_value = mock_empty_data

    # Act
    response = client.get("/overview")

    # Assert
    assert response.status_code == 200
    assert response.json()["progress"]["matchesPlayed"] == 0
    mock_overview_service.get_overview_stats.assert_called_once()


def test_internal_server_error(mock_overview_service):
    # Arrange
    mock_overview_service.get_overview_stats.side_effect = HTTPException(status_code=500, detail="Database error")

    # Act
    response = client.get("/overview")

    # Assert
    assert response.status_code == 500
    assert response.json()["detail"] == "Database error"
    mock_overview_service.get_overview_stats.assert_called_once()
