import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/card';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '../ui/tabs';
import { Alert, AlertDescription } from '../ui/alert';

const StandingsTable = ({ standings, title }) => (
  <Card>
    <CardHeader>
      <CardTitle>{title}</CardTitle>
    </CardHeader>
    <CardContent>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b">
              <th className="text-left p-2">Pos</th>
              <th className="text-left p-2">Player</th>
              <th className="text-center p-2">P</th>
              <th className="text-center p-2">W</th>
              <th className="text-center p-2">D</th>
              <th className="text-center p-2">L</th>
              <th className="text-center p-2">GF</th>
              <th className="text-center p-2">GA</th>
              <th className="text-center p-2">GD</th>
              <th className="text-center p-2">Pts</th>
            </tr>
          </thead>
          <tbody>
            {standings.map((player, index) => (
              <tr key={player.player_id} className="border-b hover:bg-gray-50">
                <td className="p-2">{index + 1}</td>
                <td className="p-2">{player.player_name}</td>
                <td className="text-center p-2">{player.matches_played}</td>
                <td className="text-center p-2">{player.wins}</td>
                <td className="text-center p-2">{player.draws}</td>
                <td className="text-center p-2">{player.losses}</td>
                <td className="text-center p-2">{player.goals_scored}</td>
                <td className="text-center p-2">{player.goals_against}</td>
                <td className="text-center p-2">{player.goal_difference}</td>
                <td className="text-center p-2 font-bold">{player.points}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </CardContent>
  </Card>
);

export const Standings = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [standings, setStandings] = useState(null);

  useEffect(() => {
    const fetchStandings = async () => {
      try {
        const response = await fetch('http://localhost:8000/standings');
        if (!response.ok) {
          throw new Error('Failed to fetch standings');
        }
        const data = await response.json();
        const { tournament, round1, round2 } = data;

        // Combine Round 1 and Round 2 data into Tournament Standings
        const allPlayers = new Map();
        for (const player of round1) {
          allPlayers.set(player.player_id, {
            player_id: player.player_id,
            player_name: player.player_name,
            matches_played: player.matches_played,
            points: player.points,
            wins: player.wins,
            draws: player.draws,
            losses: player.losses,
            goals_scored: player.goals_scored,
            goals_against: player.goals_against,
            goal_difference: player.goal_difference
          });
        }
        for (const player of round2) {
          let existingPlayer = allPlayers.get(player.player_id);
          if (existingPlayer) {
            existingPlayer.matches_played += player.matches_played;
            existingPlayer.points += player.points;
            existingPlayer.wins += player.wins;
            existingPlayer.draws += player.draws;
            existingPlayer.losses += player.losses;
            existingPlayer.goals_scored += player.goals_scored;
            existingPlayer.goals_against += player.goals_against;
            existingPlayer.goal_difference += player.goal_difference;
          } else {
            allPlayers.set(player.player_id, {
              player_id: player.player_id,
              player_name: player.player_name,
              matches_played: player.matches_played,
              points: player.points,
              wins: player.wins,
              draws: player.draws,
              losses: player.losses,
              goals_scored: player.goals_scored,
              goals_against: player.goals_against,
              goal_difference: player.goal_difference
            });
          }
        }
        const tournamentStandings = Array.from(allPlayers.values());
        tournamentStandings.sort((a, b) => b.points - a.points || b.goal_difference - a.goal_difference);
        setStandings({ tournament: tournamentStandings, round1, round2 });
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchStandings();
  }, []);

  if (loading) {
    return <div className="text-center p-4">Loading standings...</div>;
  }

  if (error) {
    return <Alert variant="destructive"><AlertDescription>{error}</AlertDescription></Alert>;
  }

  if (!standings) {
    return <Alert><AlertDescription>No standings data available</AlertDescription></Alert>;
  }

  return (
    <div className="space-y-6">
      <Tabs defaultValue="tournament" className="w-full">
        <TabsList className="grid w-full grid-cols-3 mb-8">
          <TabsTrigger value="tournament">Tournament</TabsTrigger>
          <TabsTrigger value="round1">Round 1 (1v1)</TabsTrigger>
          <TabsTrigger value="round2">Round 2 (2v2)</TabsTrigger>
        </TabsList>

        <TabsContent value="tournament">
          <StandingsTable standings={standings.tournament} title="Tournament Standings" />
        </TabsContent>

        <TabsContent value="round1">
          <StandingsTable standings={standings.round1} title="Round 1 Standings (1v1)" />
        </TabsContent>

        <TabsContent value="round2">
          <StandingsTable standings={standings.round2} title="Round 2 Standings (2v2)" />
        </TabsContent>
      </Tabs>
    </div>
  );
};