from unittest.mock import Mock

import pytest
from fastapi import HTTPException
from models import PlayerCreate
from services.player_service import PlayerService


@pytest.fixture
def player_service():
    service = PlayerService()
    service.repository = Mock()
    return service


@pytest.fixture
def sample_player():
    return {
        "player_id": 1,
        "player_name": "John Doe",
        "matches_played": 0,
        "wins": 0,
        "draws": 0,
        "losses": 0,
        "goals_scored": 0,
        "goals_against": 0,
        "goal_difference": 0,
        "clean_sheets": 0,
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00",
    }


class TestPlayerService:
    def test_get_all_players_success(self, player_service, sample_player):
        player_service.repository.get_all_players.return_value = [sample_player]

        result = player_service.get_all_players()

        assert len(result) == 1
        assert result[0].player_name == "John Doe"
        player_service.repository.get_all_players.assert_called_once()

    def test_get_all_players_error(self, player_service):
        player_service.repository.get_all_players.side_effect = Exception("Database error")

        with pytest.raises(HTTPException) as exc:
            player_service.get_all_players()
        assert exc.value.status_code == 500
        assert "Error fetching players" in str(exc.value.detail)

    def test_create_player_success(self, player_service, sample_player):
        player_create = PlayerCreate(player_name="John Doe")
        player_service.repository.create_player.return_value = sample_player

        result = player_service.create_player(player_create)

        assert result.player_name == "John Doe"
        assert result.player_id == 1
        player_service.repository.create_player.assert_called_once_with(player_create)

    def test_create_player_error(self, player_service):
        player_create = PlayerCreate(player_name="John Doe")
        player_service.repository.create_player.side_effect = Exception("Database error")

        with pytest.raises(HTTPException) as exc:
            player_service.create_player(player_create)
        assert exc.value.status_code == 400
        assert "Error creating player" in str(exc.value.detail)

    def test_get_player_by_id_success(self, player_service, sample_player):
        player_service.repository.get_player_by_id.return_value = sample_player

        result = player_service.get_player_by_id(1)

        assert result.player_id == 1
        assert result.player_name == "John Doe"
        player_service.repository.get_player_by_id.assert_called_once_with(1)

    def test_get_player_by_id_not_found(self, player_service):
        player_service.repository.get_player_by_id.return_value = None

        with pytest.raises(HTTPException) as exc:
            player_service.get_player_by_id(1)
        assert exc.value.status_code == 404
        assert "Player with ID 1 not found" in str(exc.value.detail)

    def test_delete_player_success(self, player_service, sample_player):
        player_service.repository.delete_player.return_value = sample_player

        result = player_service.delete_player(1)

        assert result.player_id == 1
        player_service.repository.delete_player.assert_called_once_with(1)

    def test_delete_player_not_found(self, player_service):
        player_service.repository.delete_player.side_effect = ValueError("Player with ID 1 not found")

        with pytest.raises(HTTPException) as exc:
            player_service.delete_player(1)
        assert exc.value.status_code == 400
        assert "Player with ID 1 not found" in str(exc.value.detail)

    def test_delete_player_error(self, player_service):
        player_service.repository.delete_player.side_effect = Exception("Database error")

        with pytest.raises(HTTPException) as exc:
            player_service.delete_player(1)
        assert exc.value.status_code == 500
        assert "Error deleting player" in str(exc.value.detail)
