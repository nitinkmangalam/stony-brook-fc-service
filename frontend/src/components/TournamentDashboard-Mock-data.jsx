import React, { useState } from 'react';
import { Trophy, Users, Calendar, BarChart3, Clock, Plus } from 'lucide-react';
import { Tabs, TabsList, TabsTrigger, TabsContent } from './ui/tabs';
import { Overview } from './sections/Overview';
import { Players } from './sections/Players';
import { Fixtures } from './sections/Fixtures';
import { Standings } from './sections/Standings';

const TournamentDashboard = () => {
  // Mock data
  const mockPlayers = [
    {
      player_id: 1,
      player_name: "Alex",
      matches_played: 5,
      wins: 3,
      draws: 1,
      losses: 1,
      goals_scored: 12,
      goals_against: 8,
      goal_difference: 4
    },
    {
      player_id: 2,
      player_name: "Brian",
      matches_played: 5,
      wins: 2,
      draws: 2,
      losses: 1,
      goals_scored: 10,
      goals_against: 9,
      goal_difference: 1
    },
    {
      player_id: 3,
      player_name: "Charlie",
      matches_played: 4,
      wins: 2,
      draws: 1,
      losses: 1,
      goals_scored: 8,
      goals_against: 7,
      goal_difference: 1
    }
  ];

  const mockMatches = [
    {
      id: 1,
      round: "League Phase",
      match_type: "1v1",
      team1_player1_name: "Alex",
      team2_player1_name: "Brian",
      match_date: "2024-02-20T15:00:00",
      team1_goals: 3,
      team2_goals: 2,
      result: "Team1"
    },
    {
      id: 2,
      round: "League Phase",
      match_type: "2v2",
      team1_player1_name: "Alex",
      team1_player2_name: "Charlie",
      team2_player1_name: "Brian",
      team2_player2_name: "David",
      match_date: "2024-02-19T16:00:00",
      team1_goals: 4,
      team2_goals: 3,
      result: "Team1"
    }
  ];

  const mockStandings = mockPlayers.map(player => ({
    ...player,
    points: player.wins * 6 + player.draws * 2
  })).sort((a, b) => b.points - a.points || b.goal_difference - a.goal_difference);

  // Find top scorer from mock data
  const topScorer = mockPlayers.reduce((prev, current) => 
    prev.goals_scored > current.goals_scored ? prev : current
  );

  // Get latest match
  const latestMatch = mockMatches[0];

  return (
    <div className="min-h-screen bg-gray-100 p-4">
      <div className="mb-6 text-center">
        <h1 className="text-4xl font-bold">Stony Brook FC 2024</h1>
        <p className="text-gray-600 mt-2">Where Legends Are Made 🏆</p>
      </div>

      <Tabs defaultValue="overview" className="w-full">
        <TabsList className="grid w-full grid-cols-6 mb-8">
          <TabsTrigger value="overview" className="flex items-center gap-2">
            <Trophy size={16} /> Overview
          </TabsTrigger>
          <TabsTrigger value="players" className="flex items-center gap-2">
            <Users size={16} /> Players
          </TabsTrigger>
          <TabsTrigger value="fixtures" className="flex items-center gap-2">
            <Calendar size={16} /> Fixtures
          </TabsTrigger>
          <TabsTrigger value="standings" className="flex items-center gap-2">
            <BarChart3 size={16} /> Standings
          </TabsTrigger>
          <TabsTrigger value="upcoming" className="flex items-center gap-2">
            <Clock size={16} /> Upcoming
          </TabsTrigger>
          <TabsTrigger value="admin" className="flex items-center gap-2">
            <Plus size={16} /> Admin
          </TabsTrigger>
        </TabsList>

        <TabsContent value="overview">
          <Overview 
            topScorer={{ name: topScorer.player_name, goals: topScorer.goals_scored }}
            latestMatch={{
              team1: latestMatch.team1_player1_name,
              team2: latestMatch.team2_player1_name,
              score1: latestMatch.team1_goals,
              score2: latestMatch.team2_goals
            }}
          />
        </TabsContent>

        <TabsContent value="players">
          <Players players={mockPlayers} />
        </TabsContent>

        <TabsContent value="fixtures">
          <Fixtures matches={mockMatches} />
        </TabsContent>

        <TabsContent value="standings">
          <Standings standings={mockStandings} />
        </TabsContent>

        <TabsContent value="upcoming">
          <div className="text-center p-4">Coming soon...</div>
        </TabsContent>

        <TabsContent value="admin">
          <div className="text-center p-4">Admin panel coming soon...</div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default TournamentDashboard;