import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/card';

export const Players = ({ players }) => {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Player Statistics</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b">
                <th className="text-left p-2">Player</th>
                <th className="text-center p-2">Played</th>
                <th className="text-center p-2">Won</th>
                <th className="text-center p-2">Drawn</th>
                <th className="text-center p-2">Lost</th>
                <th className="text-center p-2">GF</th>
                <th className="text-center p-2">GA</th>
                <th className="text-center p-2">GD</th>
              </tr>
            </thead>
            <tbody>
              {players.map(player => (
                <tr key={player.player_id} className="border-b hover:bg-gray-50">
                  <td className="p-2">{player.player_name}</td>
                  <td className="text-center p-2">{player.matches_played}</td>
                  <td className="text-center p-2">{player.wins}</td>
                  <td className="text-center p-2">{player.draws}</td>
                  <td className="text-center p-2">{player.losses}</td>
                  <td className="text-center p-2">{player.goals_scored}</td>
                  <td className="text-center p-2">{player.goals_against}</td>
                  <td className="text-center p-2">{player.goal_difference}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
};