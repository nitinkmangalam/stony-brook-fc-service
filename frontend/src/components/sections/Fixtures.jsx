import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/card';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '../ui/tabs';
import { Alert, AlertDescription } from '../ui/alert';
import moment from 'moment';

const FixturesTable = ({ matches, title }) => (
  <Card>
    <CardHeader>
      <CardTitle>{title}</CardTitle>
    </CardHeader>
    <CardContent>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b">
              <th className="text-left p-2">Date</th>
              <th className="text-left p-2">Round</th>
              <th className="text-left p-2">Team 1</th>
              <th className="text-left p-2">Team 2</th>
            </tr>
          </thead>
          <tbody>
            {matches.map((match, index) => (
              <tr key={index} className="border-b hover:bg-gray-50">
                <td className="p-3">{moment(match.match_date).format('MMM D, YYYY h:mm A')}</td>
                <td className="p-2">{match.round}</td>
                <td className="p-2">{match.team1_player1_name} {match.team1_player2_name ? `& ${match.team1_player2_name}` : ''}</td>
                <td className="p-2">{match.team2_player1_name} {match.team2_player2_name ? `& ${match.team2_player2_name}` : ''}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </CardContent>
  </Card>
);

const ResultsTable = ({ matches, title }) => (
  <Card>
    <CardHeader>
      <CardTitle>{title}</CardTitle>
    </CardHeader>
    <CardContent>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b">
              <th className="text-left p-2">Date</th>
              <th className="text-left p-2">Round</th>
              <th className="text-left p-2">Team 1</th>
              <th className="text-left p-2">Team 2</th>
              <th className="text-center p-2">Score</th>
            </tr>
          </thead>
          <tbody>
            {matches.map((match, index) => (
              <tr key={index} className="border-b hover:bg-gray-50">
                <td className="p-3">{moment(match.match_date).format('MMM D, YYYY h:mm A')}</td>
                <td className="p-3">{match.round}</td>
                <td className="p-3">{match.team1_player1_name} {match.team1_player2_name ? `& ${match.team1_player2_name}` : ''}</td>
                <td className="p-3">{match.team2_player1_name} {match.team2_player2_name ? `& ${match.team2_player2_name}` : ''}</td>
                <td className="p-3 text-center">{match.team1_goals} - {match.team2_goals}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </CardContent>
  </Card>
);

export const Fixtures = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [upcomingMatches, setUpcomingMatches] = useState(null);
  const [pastResults, setPastResults] = useState(null);

  useEffect(() => {
    const fetchFixturesAndResults = async () => {
      try {
        const response = await fetch('http://localhost:8000/matches');
        if (!response.ok) {
          throw new Error('Failed to fetch matches');
        }
        const data = await response.json();
        const upcoming = data.filter(match => match.status === 'SCHEDULED')
          .sort((a, b) => new Date(a.match_date) - new Date(b.match_date));
        const past = data.filter(match => match.status === 'COMPLETED')
          .sort((a, b) => new Date(b.match_date) - new Date(a.match_date));
        setUpcomingMatches(upcoming);
        setPastResults(past);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchFixturesAndResults();
  }, []);

  if (loading) {
    return <div className="text-center p-4">Loading fixtures and results...</div>;
  }

  if (error) {
    return <Alert variant="destructive"><AlertDescription>{error}</AlertDescription></Alert>;
  }

  if (!upcomingMatches || !pastResults) {
    return <Alert><AlertDescription>No fixtures or results data available</AlertDescription></Alert>;
  }

  return (
    <div className="space-y-6">
      <Tabs defaultValue="upcoming" className="w-full">
        <TabsList className="grid w-full grid-cols-2 mb-8">
          <TabsTrigger value="upcoming">Upcoming Matches</TabsTrigger>
          <TabsTrigger value="results">Results</TabsTrigger>
        </TabsList>

        <TabsContent value="upcoming">
          <FixturesTable matches={upcomingMatches} title="Upcoming Matches" />
        </TabsContent>

        <TabsContent value="results">
          <ResultsTable matches={pastResults} title="Results" />
        </TabsContent>
      </Tabs>
    </div>
  );
};