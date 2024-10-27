import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/card';
import TournamentProgressCard from '../ui/tournament_progress';
import { Alert, AlertDescription } from '../ui/alert';
import { Trophy, Goal, Activity, Star, TrendingUp, Shield, Lock } from 'lucide-react';

export const Overview = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [overviewData, setOverviewData] = useState(null);

  useEffect(() => {
    const fetchOverviewData = async () => {
      try {
        const response = await fetch('http://localhost:8000/overview');
        if (!response.ok) {
          throw new Error('Failed to fetch overview data');
        }
        const data = await response.json();
        setOverviewData(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchOverviewData();
  }, []);

  if (loading) {
    return <div className="text-center p-4">Loading tournament data...</div>;
  }

  if (error) {
    return <Alert variant="destructive"><AlertDescription>{error}</AlertDescription></Alert>;
  }

  if (!overviewData) {
    return <Alert><AlertDescription>No tournament data available</AlertDescription></Alert>;
  }

  return (
    <div className="space-y-6">
      {/* Tournament Progress Section */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <TournamentProgressCard overviewData={overviewData} />
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Tournament Stats</CardTitle>
            <Activity className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span>Matches Played</span>
                <span className="font-bold">{overviewData.stats?.totalMatches || 0}</span>
              </div>
              <div className="flex justify-between">
                <span>Total Goals</span>
                <span className="font-bold">{overviewData.stats?.totalGoals || 0}</span>
              </div>
              <div className="flex justify-between">
                <span>Avg Goals/Match</span>
                <span className="font-bold">{overviewData.stats?.averageGoals?.toFixed(2) || '0.00'}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {overviewData.topScorer && (
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Top Scorer</CardTitle>
              <Goal className="h-4 w-4 text-blue-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{overviewData.topScorer.name || 'No data'}</div>
              <div className="text-xs text-gray-500">
                {overviewData.topScorer.goals || 0} goals in {overviewData.topScorer.matches || 0} matches
              </div>
              <div className="mt-2 text-sm">
                Averaging {overviewData.topScorer.average?.toFixed(2) || '0.00'} goals per game
              </div>
            </CardContent>
          </Card>
        )}

        {overviewData.bestDefense && (
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Best Defense</CardTitle>
              <Shield className="h-4 w-4 text-blue-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{overviewData.bestDefense.player || 'No data'}</div>
              <div className="text-xs text-gray-500">
                {overviewData.bestDefense.goalsAgainst || 0} goals conceded in {overviewData.bestDefense.matches || 0} matches
              </div>
              <div className="mt-2 text-sm">
                Averaging {overviewData.bestDefense.average?.toFixed(2) || '0.00'} goals per game
              </div>
            </CardContent>
          </Card>
        )}

        {overviewData.cleanSheets && (
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Clean Sheets</CardTitle>
              <Lock className="h-4 w-4 text-blue-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{overviewData.cleanSheets.player || 'No data'}</div>
              <div className="text-xs text-gray-500">
                {overviewData.cleanSheets.count || 0} matches without conceding
              </div>
              <div className="mt-2 text-sm">
                Best defensive record
              </div>
            </CardContent>
          </Card>
        )}

        {overviewData.currentStreak && (
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Hot Streak</CardTitle>
              <TrendingUp className="h-4 w-4 text-blue-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{overviewData.currentStreak.player || 'No data'}</div>
              <div className="text-xs text-gray-500">
                {overviewData.currentStreak.wins || 0} consecutive wins
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Latest Match and Highest Scoring */}
      <div className="grid gap-4 md:grid-cols-2">
        {overviewData.latestMatch && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Trophy className="h-4 w-4" />
                Latest Result
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col items-center space-y-4">
                <div className="text-sm text-gray-500">
                  {overviewData.latestMatch.matchType} - {overviewData.latestMatch.date}
                </div>
                <div className="flex items-center justify-between w-full px-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold">{overviewData.latestMatch.team1 || 'No data'}</div>
                  </div>
                  <div className="text-3xl font-bold">
                    {overviewData.latestMatch.score1 || 0} - {overviewData.latestMatch.score2 || 0}
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold">{overviewData.latestMatch.team2 || 'No data'}</div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {overviewData.highestScoring && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Star className="h-4 w-4" />
                Highest Scoring Match
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col items-center space-y-4">
                <div className="text-sm text-gray-500">{overviewData.highestScoring.date}</div>
                <div className="flex items-center justify-between w-full px-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold">{overviewData.highestScoring.team1 || 'No data'}</div>
                  </div>
                  <div className="text-3xl font-bold">
                    {overviewData.highestScoring.score1 || 0} - {overviewData.highestScoring.score2 || 0}
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold">{overviewData.highestScoring.team2 || 'No data'}</div>
                  </div>
                </div>
                <div className="text-sm text-gray-500">
                  Total Goals: {overviewData.highestScoring.totalGoals || 0}
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};