import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/card';
import { Alert, AlertDescription } from '../ui/alert';

export const Overview = ({ topScorer, latestMatch }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <Card>
        <CardHeader>
          <CardTitle>Tournament Progress</CardTitle>
        </CardHeader>
        <CardContent>
          <Alert>
            <AlertDescription>
              Currently in League Phase - Round 1
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Top Scorer</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{topScorer.name}</div>
          <div className="text-gray-600">{topScorer.goals} goals</div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Latest Result</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex justify-between items-center">
            <span>{latestMatch.team1}</span>
            <span className="text-xl font-bold">
              {latestMatch.score1} - {latestMatch.score2}
            </span>
            <span>{latestMatch.team2}</span>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};