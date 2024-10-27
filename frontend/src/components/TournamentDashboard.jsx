import React, { useState, useEffect } from 'react';
import { Trophy, Calendar, BarChart3, Plus } from 'lucide-react';
import { Tabs, TabsList, TabsTrigger, TabsContent } from './ui/tabs';
import { Overview } from './sections/Overview';
import { Fixtures } from './sections/Fixtures';
import { Standings } from './sections/Standings';
import { Admin } from './sections/Admin';
import { Alert, AlertDescription } from './ui/alert';

const API_BASE_URL = 'http://localhost:8000';

const TournamentDashboard = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [matches, setMatches] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        // Only fetch matches data as Overview and Standings components handle their own data
        const matchesRes = await fetch(`${API_BASE_URL}/matches`);
        if (!matchesRes.ok) {
          throw new Error('Failed to fetch matches data');
        }
        const matchesData = await matchesRes.json();
        setMatches(matchesData);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl font-semibold">Loading tournament data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Alert variant="destructive">
          <AlertDescription>Error: {error}</AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 p-4">
      <div className="mb-6 text-center">
        <h1 className="text-4xl font-bold">Stony Brook FC 2024</h1>
        <p className="text-gray-600 mt-2">Where Legends Are Made 🏆</p>
      </div>

      <Tabs defaultValue="overview" className="w-full">
        <TabsList className="grid w-full grid-cols-4 mb-8">
          <TabsTrigger value="overview" className="flex items-center gap-2">
            <Trophy size={16} /> Overview
          </TabsTrigger>
          <TabsTrigger value="standings" className="flex items-center gap-2">
            <BarChart3 size={16} /> Standings
          </TabsTrigger>
          <TabsTrigger value="fixtures" className="flex items-center gap-2">
            <Calendar size={16} /> Fixtures and Results
          </TabsTrigger>
          <TabsTrigger value="admin" className="flex items-center gap-2">
            <Plus size={16} /> Admin
          </TabsTrigger>
        </TabsList>

        <TabsContent value="overview">
          <Overview />
        </TabsContent>

        <TabsContent value="standings">
          <Standings />
        </TabsContent>

        <TabsContent value="fixtures">
          <Fixtures matches={matches} />
        </TabsContent>

        <TabsContent value="admin">
          <Admin />
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default TournamentDashboard;