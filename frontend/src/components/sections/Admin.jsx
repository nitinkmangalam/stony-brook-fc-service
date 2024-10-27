import React from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../ui/card';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '../ui/tabs';
import { PlayerManagement } from './admin/PlayerManagement';
import { MatchManagement } from './admin/MatchManagement';
import { UsersIcon, CalendarDaysIcon } from 'lucide-react';

export const Admin = () => {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Admin Panel</h2>
          <p className="text-muted-foreground">
            Manage players, matches, and tournament settings
          </p>
        </div>
      </div>

      <Tabs defaultValue="players" className="space-y-4">
        <TabsList>
          <TabsTrigger value="players" className="flex items-center gap-2">
            <UsersIcon className="h-4 w-4" />
            Players
          </TabsTrigger>
          <TabsTrigger value="matches" className="flex items-center gap-2">
            <CalendarDaysIcon className="h-4 w-4" />
            Matches
          </TabsTrigger>
        </TabsList>

        <TabsContent value="players">
          <PlayerManagement />
        </TabsContent>

        <TabsContent value="matches">
          <MatchManagement />
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default Admin;