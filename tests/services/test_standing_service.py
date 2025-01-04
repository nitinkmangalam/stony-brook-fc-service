from unittest.mock import patch

import pytest
from services.standing_service import StandingService


@pytest.fixture
def standing_service():
    return StandingService()


@pytest.fixture
def mock_repository_data():
    round1_data = [
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
    ]

    round2_data = [
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
    ]

    return round1_data, round2_data


@pytest.mark.asyncio
async def test_get_standings(standing_service, mock_repository_data):
    round1_data, round2_data = mock_repository_data

    with patch.object(
        standing_service.repository, "get_round1_standings", return_value=round1_data
    ) as mock_round1, patch.object(
        standing_service.repository, "get_round2_standings", return_value=round2_data
    ) as mock_round2:
        result = await standing_service.get_standings()

        assert "tournament" in result
        assert "round1" in result
        assert "round2" in result
        assert result["round1"] == round1_data
        assert result["round2"] == round2_data

        tournament_player = result["tournament"][0]
        assert tournament_player["matches_played"] == 5
        assert tournament_player["points"] == 15
        assert tournament_player["goals_scored"] == 8
        assert tournament_player["goals_against"] == 6
        assert tournament_player["goal_difference"] == 2

        mock_round1.assert_called_once()
        mock_round2.assert_called_once()


@pytest.mark.asyncio
async def test_get_standings_repository_error(standing_service):
    with patch.object(standing_service.repository, "get_round1_standings", side_effect=Exception("Database error")):
        with pytest.raises(Exception) as exc_info:
            await standing_service.get_standings()
        assert str(exc_info.value) == "Database error"


def test_calculate_tournament_standings(standing_service, mock_repository_data):
    round1_data, round2_data = mock_repository_data

    result = standing_service._calculate_tournament_standings(round1_data, round2_data)

    assert len(result) == 1
    player = result[0]
    assert player["matches_played"] == 5
    assert player["points"] == 15
    assert player["wins"] == 2
    assert player["draws"] == 1
    assert player["losses"] == 2
    assert player["goals_scored"] == 8
    assert player["goals_against"] == 6
    assert player["goal_difference"] == 2
