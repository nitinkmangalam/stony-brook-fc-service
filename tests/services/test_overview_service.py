from datetime import datetime
from unittest.mock import Mock

import pytest
from fastapi import HTTPException
from services.overview_service import OverviewService


@pytest.fixture
def overview_service():
    service = OverviewService()
    service.repository = Mock()
    return service


@pytest.fixture
def sample_overview_data():
    return {
        "progress": {
            "matches_played": 10,
            "total_expected_matches": 29,
            "completion_percentage": 34.5,
            "current_phase": "League Phase",
        },
        "stats": {"total_matches": 10, "total_goals": 25, "avg_goals_per_match": 2.5},
        "top_scorer": {"player_name": "John Doe", "goals_scored": 5, "matches_played": 10, "goals_per_game": 0.5},
        "latest_match": {
            "team1_display_name": "Team A",
            "team2_display_name": "Team B",
            "team1_goals": 3,
            "team2_goals": 2,
            "match_type": "1v1",
        },
    }


class TestOverviewService:
    def test_get_overview_stats_success(self, overview_service, sample_overview_data):
        # Mock individual repository methods
        overview_service.repository.get_tournament_progress.return_value = sample_overview_data["progress"]
        overview_service.repository.get_basic_tournament_stats.return_value = sample_overview_data["stats"]
        overview_service.repository.get_top_scorer.return_value = sample_overview_data["top_scorer"]
        overview_service.repository.get_latest_match.return_value = sample_overview_data["latest_match"]
        overview_service.repository.get_highest_scoring_match.return_value = None
        overview_service.repository.get_current_streak.return_value = None
        overview_service.repository.get_best_defense.return_value = None
        overview_service.repository.get_clean_sheets.return_value = None

        result = overview_service.get_overview_stats()

        assert result["progress"]["matchesPlayed"] == 10
        assert result["stats"]["totalMatches"] == 10
        assert len(overview_service.repository.get_tournament_progress.call_args_list) == 1

    def test_get_overview_stats_repository_error(self, overview_service):
        overview_service.repository.get_tournament_progress.side_effect = Exception("Database error")

        with pytest.raises(HTTPException) as exc:
            overview_service.get_overview_stats()

        assert exc.value.status_code == 500
        assert "Error fetching overview stats" in str(exc.value.detail)

    def test_get_overview_stats_no_data(self, overview_service):
        # Mock all repository methods to return None
        overview_service.repository.get_tournament_progress.return_value = None
        overview_service.repository.get_basic_tournament_stats.return_value = None
        overview_service.repository.get_top_scorer.return_value = None
        overview_service.repository.get_latest_match.return_value = None
        overview_service.repository.get_highest_scoring_match.return_value = None
        overview_service.repository.get_current_streak.return_value = None
        overview_service.repository.get_best_defense.return_value = None
        overview_service.repository.get_clean_sheets.return_value = None

        result = overview_service.get_overview_stats()

        assert result["progress"]["matchesPlayed"] == 0
        assert result["stats"]["totalMatches"] == 0
        assert result["topScorer"] is None

    def test_get_tournament_progress_partial(self, overview_service):
        overview_service.repository.get_tournament_progress.return_value = {
            "matches_played": 15,
            "total_expected_matches": 29,
            "completion_percentage": 51.7,
            "current_phase": "League Phase",
        }

        overview_service.repository.get_basic_tournament_stats.return_value = None
        overview_service.repository.get_top_scorer.return_value = None
        overview_service.repository.get_latest_match.return_value = None
        overview_service.repository.get_highest_scoring_match.return_value = None
        overview_service.repository.get_current_streak.return_value = None
        overview_service.repository.get_best_defense.return_value = None
        overview_service.repository.get_clean_sheets.return_value = None

        result = overview_service.get_overview_stats()

        assert result["progress"]["matchesPlayed"] == 15
        assert result["progress"]["currentPhase"] == "League Phase"

    def test_get_top_scorer_zero_goals(self, overview_service):
        overview_service.repository.get_tournament_progress.return_value = None
        overview_service.repository.get_basic_tournament_stats.return_value = None
        overview_service.repository.get_top_scorer.return_value = {
            "player_name": "New Player",
            "goals_scored": 0,
            "matches_played": 5,
            "goals_per_game": 0,
        }
        overview_service.repository.get_latest_match.return_value = None
        overview_service.repository.get_highest_scoring_match.return_value = None
        overview_service.repository.get_current_streak.return_value = None
        overview_service.repository.get_best_defense.return_value = None
        overview_service.repository.get_clean_sheets.return_value = None

        result = overview_service.get_overview_stats()

        assert result["topScorer"]["name"] == "New Player"
        assert result["topScorer"]["goals"] == 0

    def test_get_latest_match_different_types(self, overview_service):
        overview_service.repository.get_tournament_progress.return_value = None
        overview_service.repository.get_basic_tournament_stats.return_value = None
        overview_service.repository.get_top_scorer.return_value = None
        overview_service.repository.get_latest_match.return_value = {
            "team1_display_name": "Solo Player 1",
            "team2_display_name": "Solo Player 2",
            "team1_goals": 3,
            "team2_goals": 2,
            "match_type": "1v1",
            "match_date": datetime.now(),
        }
        overview_service.repository.get_highest_scoring_match.return_value = None
        overview_service.repository.get_current_streak.return_value = None
        overview_service.repository.get_best_defense.return_value = None
        overview_service.repository.get_clean_sheets.return_value = None

        result = overview_service.get_overview_stats()

        assert result["latestMatch"]["team1"] == "Solo Player 1"
        assert result["latestMatch"]["matchType"] == "1v1"
