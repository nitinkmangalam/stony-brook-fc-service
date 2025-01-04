from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock

import pytest
from models import MatchCreate, MatchType
from services.match_service import MatchService


@pytest.fixture
def match_service():
    service = MatchService()
    service.repository = Mock()
    return service


@pytest.fixture
def sample_1v1_match():
    return MatchCreate(
        round="Round 1",
        match_type=MatchType.ONE_V_ONE,
        team1_player1_id=1,
        team2_player1_id=2,
        match_date=datetime.now() + timedelta(days=1),
        team1_player2_id=None,
        team2_player2_id=None,
        team1_goals=None,
        team2_goals=None,
        status=None,
        scheduled_date=None,
    )


@pytest.fixture
def sample_2v2_match():
    return MatchCreate(
        round="Round 2",
        match_type="2v2",
        team1_player1_id=1,
        team1_player2_id=2,
        team2_player1_id=3,
        team2_player2_id=4,
        match_date=datetime.now() + timedelta(days=1),
        team1_goals=None,
        team2_goals=None,
        status=None,
        scheduled_date=None,
    )


@pytest.mark.asyncio
class TestMatchService:
    async def test_create_1v1_match_success(self, match_service, sample_1v1_match):
        match_service.repository = AsyncMock()
        mock_response = {
            "id": 1,
            "round": sample_1v1_match.round,
            "match_type": sample_1v1_match.match_type,
            "team1_player1_id": sample_1v1_match.team1_player1_id,
            "team2_player1_id": sample_1v1_match.team2_player1_id,
            "match_date": sample_1v1_match.match_date,
        }
        match_service.repository.create_match.return_value = mock_response

        result = await match_service.create_match(sample_1v1_match)

        assert result["id"] == 1
        assert result["match_type"] == "1v1"
        match_service.repository.create_match.assert_called_once()

    async def test_create_1v1_match_with_second_players_fails(self, match_service, sample_1v1_match):
        match_service.repository = AsyncMock()
        sample_1v1_match.team1_player2_id = 3

        with pytest.raises(ValueError, match="1v1 matches should not have secondary players"):
            await match_service.create_match(sample_1v1_match)

    async def test_create_2v2_match_success(self, match_service, sample_2v2_match):
        match_service.repository = AsyncMock()
        mock_response = {
            "id": 1,
            "round": sample_2v2_match.round,
            "match_type": sample_2v2_match.match_type,
            "team1_player1_id": sample_2v2_match.team1_player1_id,
            "team1_player2_id": sample_2v2_match.team1_player2_id,
            "team2_player1_id": sample_2v2_match.team2_player1_id,
            "team2_player2_id": sample_2v2_match.team2_player2_id,
            "match_date": sample_2v2_match.match_date,
        }
        match_service.repository.create_match.return_value = mock_response

        result = await match_service.create_match(sample_2v2_match)

        assert result["id"] == 1
        assert result["match_type"] == "2v2"
        match_service.repository.create_match.assert_called_once()

    async def test_create_2v2_match_missing_players_fails(self, match_service, sample_2v2_match):
        match_service.repository = AsyncMock()
        sample_2v2_match.team1_player2_id = None

        with pytest.raises(ValueError, match="2v2 matches require all player positions"):
            await match_service.create_match(sample_2v2_match)

    async def test_create_2v2_match_duplicate_players_fails(self, match_service, sample_2v2_match):
        match_service.repository = AsyncMock()
        sample_2v2_match.team1_player2_id = sample_2v2_match.team1_player1_id

        with pytest.raises(ValueError, match="Cannot use the same player"):
            await match_service.create_match(sample_2v2_match)

    async def test_create_match_past_date_fails(self, match_service, sample_1v1_match):
        match_service.repository = AsyncMock()
        sample_1v1_match.match_date = datetime.now() - timedelta(days=1)

        with pytest.raises(ValueError, match="Scheduled matches cannot be in the past"):
            await match_service.create_match(sample_1v1_match)

    async def test_update_match_score_success(self, match_service):
        match_service.repository = AsyncMock()
        match_id = 1
        score = Mock(team1_goals=2, team2_goals=1)
        match_service.repository.get_match_by_id.return_value = {"id": match_id}
        match_service.repository.update_match_score.return_value = {
            "id": match_id,
            "team1_goals": 2,
            "team2_goals": 1,
            "result": "Team1",
        }

        result = await match_service.update_match_score(match_id, score)

        assert result["result"] == "Team1"
        assert result["team1_goals"] == 2
        match_service.repository.update_match_score.assert_called_once()

    async def test_update_match_score_not_found(self, match_service):
        match_service.repository = AsyncMock()
        match_service.repository.get_match_by_id.return_value = None

        with pytest.raises(ValueError, match="Match not found"):
            await match_service.update_match_score(1, Mock())
