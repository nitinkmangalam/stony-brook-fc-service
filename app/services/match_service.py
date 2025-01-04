from datetime import datetime

from models import MatchCreate, ScoreUpdate
from repositories.match_repository import MatchRepository


class MatchService:
    def __init__(self):
        self.repository = MatchRepository()

    async def get_matches(self):
        return await self.repository.get_matches()

    async def create_match(self, match: MatchCreate):
        # Validate 2v2 match requirements
        if match.match_type == "2v2":
            if not all(
                [match.team1_player1_id, match.team1_player2_id, match.team2_player1_id, match.team2_player2_id]
            ):
                raise ValueError("2v2 matches require all player positions to be filled")

            # Check for duplicate players
            players = [match.team1_player1_id, match.team1_player2_id, match.team2_player1_id, match.team2_player2_id]
            if len(set(players)) != 4:
                raise ValueError("Cannot use the same player multiple times in a match")

        # For 1v1 matches, ensure second player slots are null
        if match.match_type == "1v1":
            if match.team1_player2_id is not None or match.team2_player2_id is not None:
                raise ValueError("1v1 matches should not have secondary players")
            match.team1_player2_id = None
            match.team2_player2_id = None

        # Set scheduled_date to match_date if not provided
        scheduled_date = match.scheduled_date or match.match_date

        # Determine status and result
        status = "COMPLETED" if match.team1_goals is not None and match.team2_goals is not None else "SCHEDULED"
        result = None
        if status == "COMPLETED":
            if match.team1_goals > match.team2_goals:
                result = "Team1"
            elif match.team2_goals > match.team1_goals:
                result = "Team2"
            else:
                result = "Draw"

        # Validate match date
        if match.match_date < datetime.now() and status == "SCHEDULED":
            raise ValueError("Scheduled matches cannot be in the past")

        return await self.repository.create_match(match, scheduled_date, status, result)

    async def update_match(self, match_id: int, match: MatchCreate):
        # First check if match exists
        existing_match = await self.repository.get_match_by_id(match_id)
        if not existing_match:
            raise ValueError("Match not found")

        # Determine status and result based on goals
        if match.team1_goals is not None and match.team2_goals is not None:
            status = "COMPLETED"
            if match.team1_goals > match.team2_goals:
                result = "Team1"
            elif match.team2_goals > match.team1_goals:
                result = "Team2"
            else:
                result = "Draw"
        else:
            status = "SCHEDULED"
            result = None
            match.team1_goals = None
            match.team2_goals = None

        return await self.repository.update_match(match_id, match, status, result)

    async def update_match_score(self, match_id: int, score: ScoreUpdate):
        # Verify match exists
        existing_match = await self.repository.get_match_by_id(match_id)
        if not existing_match:
            raise ValueError("Match not found")

        # Calculate result based on scores
        if score.team1_goals > score.team2_goals:
            result = "Team1"
        elif score.team2_goals > score.team1_goals:
            result = "Team2"
        else:
            result = "Draw"

        return await self.repository.update_match_score(match_id, score.team1_goals, score.team2_goals, result)

    async def delete_match(self, match_id: int):
        # Verify match exists
        existing_match = await self.repository.get_match_by_id(match_id)
        if not existing_match:
            raise ValueError("Match not found")

        return await self.repository.delete_match(match_id)
