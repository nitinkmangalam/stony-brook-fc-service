from datetime import datetime, timedelta
from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from models import MatchType, ScoreUpdate
from routers.match_router import get_match_service, router

app = FastAPI()
app.include_router(router)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_match_service():
    return AsyncMock()


@pytest.fixture
def sample_match():
    return {
        "id": 1,
        "round": "Round 1",
        "match_type": MatchType.ONE_V_ONE,
        "team1_player1_id": 1,
        "team2_player1_id": 2,
        "match_date": datetime.now() + timedelta(days=1),
        "scheduled_date": datetime.now() + timedelta(days=1),
        "team1_goals": None,
        "team2_goals": None,
        "status": "SCHEDULED",
        "result": None,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }


@pytest.mark.asyncio
class TestMatchRouter:
    async def test_get_matches(self, client, mock_match_service, sample_match):
        app.dependency_overrides[get_match_service] = lambda: mock_match_service
        mock_match_service.get_matches.return_value = [sample_match]

        response = client.get("/matches")

        assert response.status_code == 200
        assert len(response.json()) == 1
        mock_match_service.get_matches.assert_called_once()

    async def test_create_match(self, client, mock_match_service, sample_match):
        app.dependency_overrides[get_match_service] = lambda: mock_match_service
        mock_match_service.create_match.return_value = sample_match

        match_data = {
            "round": "Round 1",
            "match_type": "1v1",
            "team1_player1_id": 1,
            "team2_player1_id": 2,
            "match_date": (datetime.now() + timedelta(days=1)).isoformat(),
        }

        response = client.post("/matches", json=match_data)

        assert response.status_code == 200
        assert response.json()["id"] == 1
        mock_match_service.create_match.assert_called_once()

    async def test_get_match_by_id(self, client, mock_match_service, sample_match):
        app.dependency_overrides[get_match_service] = lambda: mock_match_service
        mock_match_service.get_match_by_id.return_value = sample_match

        response = client.get("/matches/1")

        assert response.status_code == 200
        assert response.json()["id"] == 1
        mock_match_service.get_match_by_id.assert_called_once_with(1)

    async def test_update_match(self, client, mock_match_service, sample_match):
        app.dependency_overrides[get_match_service] = lambda: mock_match_service
        mock_match_service.update_match.return_value = sample_match

        match_data = {
            "round": "Round 1",
            "match_type": "1v1",
            "team1_player1_id": 1,
            "team2_player1_id": 2,
            "match_date": (datetime.now() + timedelta(days=1)).isoformat(),
        }

        response = client.put("/matches/1", json=match_data)

        assert response.status_code == 200
        assert response.json()["id"] == 1
        mock_match_service.update_match.assert_called_once()

    async def test_update_match_score(self, client, mock_match_service, sample_match):
        app.dependency_overrides[get_match_service] = lambda: mock_match_service
        mock_match_service.update_match_score.return_value = sample_match

        score_data = ScoreUpdate(team1_goals=2, team2_goals=1)

        response = client.put("/matches/1/score", json=score_data.dict())

        assert response.status_code == 200
        mock_match_service.update_match_score.assert_called_once()

    async def test_delete_match(self, client, mock_match_service, sample_match):
        app.dependency_overrides[get_match_service] = lambda: mock_match_service
        mock_match_service.delete_match.return_value = sample_match

        response = client.delete("/matches/1")

        assert response.status_code == 200
        assert response.json()["id"] == 1
        mock_match_service.delete_match.assert_called_once_with(1)
