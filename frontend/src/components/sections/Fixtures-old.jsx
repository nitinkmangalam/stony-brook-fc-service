import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/card';

export const Fixtures = ({ matches }) => {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Match History</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {matches.map(match => (
            <div key={match.id} className="border rounded-lg p-4">
              <div className="text-sm text-gray-500 mb-2">
                {new Date(match.match_date).toLocaleDateString()} - {match.round} ({match.match_type})
              </div>
              <div className="flex justify-between items-center">
                <div className="text-right flex-1">
                  <div>{match.team1_player1_name}</div>
                  {match.team1_player2_name && (
                    <div className="text-sm text-gray-500">{match.team1_player2_name}</div>
                  )}
                </div>
                <div className="mx-4 text-xl font-bold">
                  {match.team1_goals} - {match.team2_goals}
                </div>
                <div className="text-left flex-1">
                  <div>{match.team2_player1_name}</div>
                  {match.team2_player2_name && (
                    <div className="text-sm text-gray-500">{match.team2_player2_name}</div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};