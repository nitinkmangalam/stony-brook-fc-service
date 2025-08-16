from datetime import datetime
from unittest.mock import Mock, patch

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from app.models import Player, PlayerCreate
from app.routers.player_router import router

# Setup test app
app = FastAPI()
app.include_router(router)
client = TestClient(app)

# Mock data
mock_player_data = {
    "player_id": 1,
    "player_name": "Test Player",
    "created_at": datetime.now(),
    "updated_at": datetime.now(),
}

mock_player = Player(**mock_player_data)


# Fixture for mocking PlayerService
@pytest.fixture
def mock_player_service():
    with patch("routers.player_router.PlayerService") as mock:
        service_instance = Mock()
        mock.return_value = service_instance
        yield service_instance


# Test GET /players
def test_get_players_success(mock_player_service):
    # Arrange
    mock_player_service.get_all_players.return_value = [mock_player]

    # Act
    response = client.get("/players")

    # Assert
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["player_name"] == mock_player_data["player_name"]
    mock_player_service.get_all_players.assert_called_once()


def test_get_players_empty(mock_player_service):
    # Arrange
    mock_player_service.get_all_players.return_value = []

    # Act
    response = client.get("/players")

    # Assert
    assert response.status_code == 200
    assert response.json() == []
    mock_player_service.get_all_players.assert_called_once()


# Test POST /players
def test_create_player_success(mock_player_service):
    # Arrange
    mock_player_service.create_player.return_value = mock_player
    player_data = {"player_name": "Test Player"}

    # Act
    response = client.post("/players", json=player_data)

    # Assert
    assert response.status_code == 200
    assert response.json()["player_name"] == player_data["player_name"]
    mock_player_service.create_player.assert_called_once()
    created_player = mock_player_service.create_player.call_args[0][0]
    assert isinstance(created_player, PlayerCreate)
    assert created_player.player_name == player_data["player_name"]


def test_create_player_invalid_data(mock_player_service):
    # Arrange
    player_data = {"invalid_field": "Test Player"}  # Missing required player_name

    # Act
    response = client.post("/players", json=player_data)

    # Assert
    assert response.status_code == 422  # Validation error
    mock_player_service.create_player.assert_not_called()


# Test GET /players/{player_id}
def test_get_player_by_id_success(mock_player_service):
    # Arrange
    mock_player_service.get_player_by_id.return_value = mock_player

    # Act
    response = client.get("/players/1")

    # Assert
    assert response.status_code == 200
    assert response.json()["player_name"] == mock_player_data["player_name"]
    mock_player_service.get_player_by_id.assert_called_once_with(1)


def test_get_player_by_id_not_found(mock_player_service):
    # Arrange
    mock_player_service.get_player_by_id.side_effect = HTTPException(status_code=404, detail="Player not found")

    # Act
    response = client.get("/players/999")

    # Assert
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
    mock_player_service.get_player_by_id.assert_called_once_with(999)


# Test DELETE /players/{player_id}
def test_delete_player_success(mock_player_service):
    # Arrange
    mock_player_service.delete_player.return_value = mock_player

    # Act
    response = client.delete("/players/1")

    # Assert
    assert response.status_code == 200
    assert response.json()["player_name"] == mock_player_data["player_name"]
    mock_player_service.delete_player.assert_called_once_with(1)


def test_delete_player_not_found(mock_player_service):
    # Arrange
    mock_player_service.delete_player.side_effect = HTTPException(status_code=404, detail="Player not found")

    # Act
    response = client.delete("/players/999")

    # Assert
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
    mock_player_service.delete_player.assert_called_once_with(999)


def test_delete_player_with_matches(mock_player_service):
    # Arrange
    error_message = "Cannot delete player with ID 1 as they have 5 matches associated"
    mock_player_service.delete_player.side_effect = HTTPException(status_code=400, detail=error_message)

    # Act
    response = client.delete("/players/1")

    # Assert
    assert response.status_code == 400
    assert error_message in response.json()["detail"]
    mock_player_service.delete_player.assert_called_once_with(1)


# Test error handling
def test_internal_server_error(mock_player_service):
    # Arrange
    mock_player_service.get_all_players.side_effect = HTTPException(status_code=500, detail="Database error")

    # Act
    response = client.get("/players")

    # Assert
    assert response.status_code == 500
    assert response.json()["detail"] == "Database error"
    mock_player_service.get_all_players.assert_called_once()
