from typing import Dict, Optional

from fastapi import HTTPException
from repositories.overview_repository import OverviewRepository


class OverviewService:
    def __init__(self):
        self.repository = OverviewRepository()

    def get_overview_stats(self) -> Dict:
        try:
            progress = self._get_tournament_progress()
            basic_stats = self._get_basic_tournament_stats()
            top_scorer = self._get_top_scorer()
            latest_match = self._get_latest_match()
            highest_scoring = self._get_highest_scoring_match()
            current_streak = self._get_current_streak()
            best_defense = self._get_best_defense()
            clean_sheets = self._get_clean_sheets()

            return {
                "progress": progress,
                "stats": basic_stats,
                "topScorer": top_scorer,
                "latestMatch": latest_match,
                "highestScoring": highest_scoring,
                "currentStreak": current_streak,
                "bestDefense": best_defense,
                "cleanSheets": clean_sheets,
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching overview stats: {str(e)}")

    def _get_tournament_progress(self) -> Dict:
        progress = self.repository.get_tournament_progress()
        return (
            {
                "percentage": progress.get("completion_percentage", 0),
                "matchesPlayed": progress.get("matches_played", 0),
                "totalMatches": progress.get("total_expected_matches", 29),
                "currentPhase": progress.get("current_phase", "League Phase"),
                "phasePercentage": progress.get("phase_completion_percentage", 0),
                "phaseTotalMatches": progress.get("phase_total_matches", 25),
            }
            if progress
            else {
                "percentage": 0,
                "matchesPlayed": 0,
                "totalMatches": 29,
                "currentPhase": "League Phase",
                "phasePercentage": 0,
                "phaseTotalMatches": 25,
            }
        )

    def _get_basic_tournament_stats(self) -> Dict:
        basic_stats = self.repository.get_basic_tournament_stats()
        return (
            {
                "totalMatches": basic_stats.get("total_matches", 0),
                "totalGoals": basic_stats.get("total_goals", 0),
                "averageGoals": float(basic_stats.get("avg_goals_per_match", 0)),
            }
            if basic_stats
            else {"totalMatches": 0, "totalGoals": 0, "averageGoals": 0}
        )

    def _get_top_scorer(self) -> Optional[Dict]:
        top_scorer = self.repository.get_top_scorer()
        return (
            {
                "name": top_scorer.get("player_name"),
                "goals": top_scorer.get("goals_scored"),
                "matches": top_scorer.get("matches_played"),
                "average": float(top_scorer.get("goals_per_game")),
                "details": top_scorer.get("match_details", []),
            }
            if top_scorer
            else None
        )

    def _get_latest_match(self) -> Optional[Dict]:
        latest_match = self.repository.get_latest_match()
        return (
            {
                "team1": latest_match.get("team1_display_name"),
                "team2": latest_match.get("team2_display_name"),
                "score1": latest_match.get("team1_goals", 0),
                "score2": latest_match.get("team2_goals", 0),
                "date": latest_match.get("match_date").strftime("%Y-%m-%d %H:%M")
                if latest_match and latest_match.get("match_date")
                else None,
                "matchType": latest_match.get("match_type"),
                "isComplete": latest_match
                and latest_match.get("team1_goals") is not None
                and latest_match.get("team2_goals") is not None,
            }
            if latest_match
            else None
        )

    def _get_highest_scoring_match(self) -> Optional[Dict]:
        highest_scoring = self.repository.get_highest_scoring_match()
        if not highest_scoring or highest_scoring.get("team1_goals") is None:
            return None

        return {
            "team1": (
                f"{highest_scoring.get('team1_player1_name')} & {highest_scoring.get('team1_player2_name')}"
                if highest_scoring.get("team1_player2_name")
                else highest_scoring.get("team1_player1_name")
            ),
            "team2": (
                f"{highest_scoring.get('team2_player1_name')} & {highest_scoring.get('team2_player2_name')}"
                if highest_scoring.get("team2_player2_name")
                else highest_scoring.get("team2_player1_name")
            ),
            "score1": highest_scoring.get("team1_goals", 0),
            "score2": highest_scoring.get("team2_goals", 0),
            "totalGoals": highest_scoring.get("total_goals", 0),
            "date": highest_scoring.get("match_date").strftime("%Y-%m-%d")
            if highest_scoring and highest_scoring.get("match_date")
            else None,
            "matchType": highest_scoring.get("match_type"),
        }

    def _get_current_streak(self) -> Optional[Dict]:
        streak = self.repository.get_current_streak()
        return (
            {
                "player": streak.get("player_name"),
                "wins": streak.get("streak", 0),
                "matchType": "1v1/2v2",
                "lastMatch": streak.get("last_match_date").strftime("%Y-%m-%d")
                if streak and streak.get("last_match_date")
                else None,
            }
            if streak
            else None
        )

    def _get_best_defense(self) -> Optional[Dict]:
        best_defense = self.repository.get_best_defense()
        return (
            {
                "player": best_defense.get("player_name"),
                "goalsAgainst": best_defense.get("goals_against"),
                "average": float(best_defense.get("average")),
                "matches": best_defense.get("matches_played"),
                "details": best_defense.get("match_details", []),
            }
            if best_defense
            else None
        )

    def _get_clean_sheets(self) -> Optional[Dict]:
        clean_sheets_data = self.repository.get_clean_sheets()
        return (
            {
                "player": clean_sheets_data.get("player_name"),
                "count": clean_sheets_data.get("count", 0),
                "percentage": round(clean_sheets_data.get("percentage", 0), 1),
                "matches": [
                    {
                        "date": match["match_date"],
                        "opponent": match.get("opponent"),
                        "matchType": match.get("match_type"),
                    }
                    for match in clean_sheets_data.get("matches_detail", [])
                ],
            }
            if clean_sheets_data
            else None
        )
