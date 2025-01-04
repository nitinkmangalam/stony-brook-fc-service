from unittest.mock import patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from routers.standing_router import router as standing_router
from services.standing_service import StandingService

# Create the application and include the router
app = FastAPI()
app.include_router(standing_router)

# Create the test client
client = TestClient(app)


@pytest.fixture
def mock_standings_data():
    return {
        "tournament": [
            {
                "player_id": 1,
                "player_name": "John Doe",
                "matches_played": 5,
                "points": 15,
                "wins": 2,
                "draws": 1,
                "losses": 2,
                "goals_scored": 8,
                "goals_against": 6,
                "goal_difference": 2,
            }
        ],
        "round1": [
            {
                "player_id": 1,
                "player_name": "John Doe",
                "matches_played": 3,
                "points": 9,
                "wins": 1,
                "draws": 1,
                "losses": 1,
                "goals_scored": 5,
                "goals_against": 4,
                "goal_difference": 1,
            }
        ],
        "round2": [
            {
                "player_id": 1,
                "player_name": "John Doe",
                "matches_played": 2,
                "points": 6,
                "wins": 1,
                "draws": 0,
                "losses": 1,
                "goals_scored": 3,
                "goals_against": 2,
                "goal_difference": 1,
            }
        ],
    }


@pytest.mark.asyncio
async def test_get_standings_success(mock_standings_data):
    with patch.object(StandingService, "get_standings", return_value=mock_standings_data) as mock_service:
        response = client.get("/standings")

        assert response.status_code == 200
        assert response.json() == mock_standings_data
        mock_service.assert_called_once()


@pytest.mark.asyncio
async def test_get_standings_service_error():
    with patch.object(StandingService, "get_standings", side_effect=Exception("Database error")) as mock_service:
        response = client.get("/standings")

        assert response.status_code == 500
        assert response.json() == {"detail": "Database error"}
        mock_service.assert_called_once()
