from typing import Dict, List

from repositories.standing_repository import StandingRepository


class StandingService:
    def __init__(self):
        self.repository = StandingRepository()

    async def get_standings(self) -> Dict:
        round1_standings = await self.repository.get_round1_standings()
        round2_standings = await self.repository.get_round2_standings()

        tournament_standings = self._calculate_tournament_standings(round1_standings, round2_standings)

        return {"tournament": tournament_standings, "round1": round1_standings, "round2": round2_standings}

    def _calculate_tournament_standings(self, round1_standings: List[Dict], round2_standings: List[Dict]) -> List[Dict]:
        tournament_standings = []

        for player in round1_standings:
            round2_player = next((p for p in round2_standings if p["player_id"] == player["player_id"]), None)

            if round2_player:
                tournament_standings.append(
                    {
                        "player_id": player["player_id"],
                        "player_name": player["player_name"],
                        "matches_played": player["matches_played"] + round2_player["matches_played"],
                        "points": player["points"] + round2_player["points"],
                        "wins": player["wins"] + round2_player["wins"],
                        "draws": player["draws"] + round2_player["draws"],
                        "losses": player["losses"] + round2_player["losses"],
                        "goals_scored": player["goals_scored"] + round2_player["goals_scored"],
                        "goals_against": player["goals_against"] + round2_player["goals_against"],
                        "goal_difference": (
                            (player["goals_scored"] + round2_player["goals_scored"])
                            - (player["goals_against"] + round2_player["goals_against"])
                        ),
                    }
                )
            else:
                tournament_standings.append(player)

        tournament_standings.sort(key=lambda x: (-x["points"], -x["goal_difference"]))
        return tournament_standings
