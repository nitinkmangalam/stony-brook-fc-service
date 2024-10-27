import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from '../../ui/card';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '../../ui/tabs';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '../../ui/table';
import { Button } from '../../ui/button';
import { Input } from '../../ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../../ui/select';
import { Alert, AlertDescription } from '../../ui/alert';
import { PlusCircle, Pencil, Trash2, Calendar, Trophy, Save, X } from 'lucide-react';

const ROUNDS = ['Round 1', 'Round 2', 'Knockouts'];
const MATCH_TYPES = ['1v1', '2v2'];

export const MatchManagement = () => {
  const [matches, setMatches] = useState([]);
  const [players, setPlayers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showAddMatch, setShowAddMatch] = useState(false);
  const [editingMatch, setEditingMatch] = useState(null);
  const [isAddResult, setIsAddResult] = useState(false);
  const [currentTab, setCurrentTab] = useState('schedule');
  
  const emptyMatch = {
    round: 'Round 1',
    match_type: '1v1',
    team1_player1_id: '',
    team1_player2_id: null,
    team2_player1_id: '',
    team2_player2_id: null,
    team1_goals: null,
    team2_goals: null,
    match_date: new Date().toISOString().slice(0, 16)
  };

  const [newMatch, setNewMatch] = useState(emptyMatch);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [matchesRes, playersRes] = await Promise.all([
        fetch('http://localhost:8000/matches'),
        fetch('http://localhost:8000/players')
      ]);

      if (!matchesRes.ok || !playersRes.ok) {
        throw new Error('Failed to fetch data');
      }

      const [matchesData, playersData] = await Promise.all([
        matchesRes.json(),
        playersRes.json()
      ]);

      setMatches(matchesData);
      setPlayers(playersData);
      setLoading(false);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  const ROUND_TYPES = {
    'Round 1': '1v1',
    'Round 2': '2v2',
    'Knockouts': '1v1'
  };

  const ROUNDS = Object.keys(ROUND_TYPES);

  const handleRoundChange = (selectedRound) => {
    setNewMatch(prev => ({
      ...prev,
      round: selectedRound,
      match_type: ROUND_TYPES[selectedRound],
      // Reset second player fields based on match type
      team1_player2_id: ROUND_TYPES[selectedRound] === '2v2' ? '' : null,
      team2_player2_id: ROUND_TYPES[selectedRound] === '2v2' ? '' : null
    }));
  };

  const handleMatchTypeChange = (type) => {
    setNewMatch(prev => ({
      ...prev,
      match_type: type,
      team1_player2_id: type === '2v2' ? '' : null,
      team2_player2_id: type === '2v2' ? '' : null
    }));
  };

  // Add validation before submission
  const validateMatchData = (matchData) => {
    if (matchData.match_type === '2v2') {
      if (!matchData.team1_player1_id || !matchData.team1_player2_id ||
          !matchData.team2_player1_id || !matchData.team2_player2_id) {
        setError('All player positions must be filled for 2v2 matches');
        return false;
      }
      
      // Check for duplicate players
      const players = [
        matchData.team1_player1_id,
        matchData.team1_player2_id,
        matchData.team2_player1_id,
        matchData.team2_player2_id
      ];
      if (new Set(players).size !== 4) {
        setError('Cannot use the same player multiple times');
        return false;
      }
    }
    return true;
  };

  const handleTabChange = (tab) => {
    setCurrentTab(tab);
  };

  const handleAddResult = (match) => {
    setNewMatch({
      round: match.round,
      match_type: match.match_type,
      team1_player1_id: match.team1_player1_id,
      team1_player2_id: match.team1_player2_id,
      team2_player1_id: match.team2_player1_id,
      team2_player2_id: match.team2_player2_id,
      team1_goals: null,
      team2_goals: null,
      match_date: match.match_date
    });
    setShowAddMatch(true);
    setIsAddResult(true);
    setCurrentTab('results');
  };

  const renderPlayerSelect = (teamNumber, playerNumber, value, onChange, disabled = false) => (
    <Select
      value={value?.toString()}
      onValueChange={(val) => onChange(parseInt(val))}
      disabled={disabled}
    >
      <SelectTrigger>
        <SelectValue placeholder={`Team ${teamNumber} Player ${playerNumber}`} />
      </SelectTrigger>
      <SelectContent>
        {players.map(player => (
          <SelectItem 
            key={player.player_id} 
            value={player.player_id.toString()}
          >
            {player.player_name}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );

  const handleMatchSubmit = async (matchData) => {
    try {
      console.log('Original match data:', matchData);

      // Check if goals are being added/updated
      const hasGoals = 
        matchData.team1_goals !== null && matchData.team1_goals !== "" &&
        matchData.team2_goals !== null && matchData.team2_goals !== "";

      const submitData = {
        round: matchData.round,
        match_type: matchData.match_type,
        team1_player1_id: parseInt(matchData.team1_player1_id),
        team2_player1_id: parseInt(matchData.team2_player1_id),
        team1_player2_id: matchData.team1_player2_id ? parseInt(matchData.team1_player2_id) : null,
        team2_player2_id: matchData.team2_player2_id ? parseInt(matchData.team2_player2_id) : null,
        match_date: matchData.match_date,
        team1_goals: hasGoals ? parseInt(matchData.team1_goals) : null,
        team2_goals: hasGoals ? parseInt(matchData.team2_goals) : null,
        status: hasGoals ? 'COMPLETED' : 'SCHEDULED'  // Set status based on goals
      };

      console.log('Formatted submit data:', submitData);

      const url = matchData.id 
        ? `http://localhost:8000/matches/${matchData.id}` 
        : 'http://localhost:8000/matches';

      const response = await fetch(url, {
        method: matchData.id ? 'PUT' : 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(submitData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        console.error('Error response:', errorData);
        throw new Error(errorData.detail || 'Failed to save match');
      }

      setNewMatch(emptyMatch);
      setShowMatchForm(false);
      setEditingMatchId(null);
      fetchData();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleDeleteMatch = async (matchId) => {
    if (!window.confirm('Are you sure you want to delete this match?')) return;

    try {
      const response = await fetch(`http://localhost:8000/matches/${matchId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error('Failed to delete match');
      }

      fetchData();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleMatchUpdate = async (matchId, updatedData) => {
    try {
      const response = await fetch(`http://localhost:8000/matches/${matchId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updatedData),
      });

      if (!response.ok) {
        throw new Error('Failed to update match');
      }

      setEditingMatch(null);
      fetchData();
    } catch (err) {
      setError(err.message);
    }
  };

  const MatchForm = ({ match, onSubmit, onCancel, isEditing = false, isAddResult = false }) => (
    <form onSubmit={onSubmit} className="space-y-6 p-6 border rounded-lg bg-slate-50">
      <div className="grid grid-cols-2 gap-6">
        <div>
          <label className="block font-medium text-gray-700 mb-1">Round</label>
          <Select
            value={match.round}
            onValueChange={(value) => {
              const matchType = ROUND_TYPES[value];
              setNewMatch({
                ...match,
                round: value,
                match_type: matchType,
                team1_player2_id: matchType === '2v2' ? match.team1_player2_id : null,
                team2_player2_id: matchType === '2v2' ? match.team2_player2_id : null
              });
            }}
          >
            <SelectTrigger>
              <SelectValue placeholder="Select Round" />
            </SelectTrigger>
            <SelectContent>
              {ROUNDS.map(round => (
                <SelectItem key={round} value={round}>{round}</SelectItem>
              ))}
            </SelectContent>
          </Select>
          <p className="mt-1 text-sm text-gray-500">
            {match.match_type} match
          </p>
        </div>

        <div>
          <label className="block font-medium text-gray-700 mb-1">Date & Time</label>
          <Input
            type="datetime-local"
            value={match.match_date}
            onChange={(e) => setNewMatch({ ...match, match_date: e.target.value })}
            required
          />
        </div>
      </div>

      {!isAddResult && (
        <div className="grid grid-cols-2 gap-6">
          {/* Team 1 */}
          <div className="space-y-4">
            <div className="font-medium">Team 1</div>
            <div className="space-y-2">
              <div>
                <label className="block text-sm text-gray-600 mb-1">Player 1</label>
                {renderPlayerSelect(1, 1, match.team1_player1_id, 
                  (value) => setNewMatch({ ...match, team1_player1_id: value }))}
              </div>
              {match.match_type === '2v2' && (
                <div>
                  <label className="block text-sm text-gray-600 mb-1">Player 2</label>
                  {renderPlayerSelect(1, 2, match.team1_player2_id,
                    (value) => setNewMatch({ ...match, team1_player2_id: value }))}
                </div>
              )}
            </div>
          </div>

          {/* Team 2 */}
          <div className="space-y-4">
            <div className="font-medium">Team 2</div>
            <div className="space-y-2">
              <div>
                <label className="block text-sm text-gray-600 mb-1">Player 1</label>
                {renderPlayerSelect(2, 1, match.team2_player1_id,
                  (value) => setNewMatch({ ...match, team2_player1_id: value }))}
              </div>
              {match.match_type === '2v2' && (
                <div>
                  <label className="block text-sm text-gray-600 mb-1">Player 2</label>
                  {renderPlayerSelect(2, 2, match.team2_player2_id,
                    (value) => setNewMatch({ ...match, team2_player2_id: value }))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {isAddResult && (
        <div className="grid grid-cols-3 gap-4 items-center">
          <div className="space-y-2">
            {renderPlayerSelect(1, 1, match.team1_player1_id,
              (value) => setNewMatch({ ...match, team1_player1_id: value }))}
            {match.match_type === '2v2' &&
              renderPlayerSelect(1, 2, match.team1_player2_id,
                (value) => setNewMatch({ ...match, team1_player2_id: value }))}
          </div>

          <div className="flex items-center justify-center gap-2">
            <Input
              type="number"
              className="w-20 text-center"
              value={match.team1_goals}
              onChange={(e) => setNewMatch({
                ...match,
                team1_goals: parseInt(e.target.value)
              })}
              min="0"
            />
            <span className="font-bold">-</span>
            <Input
              type="number"
              className="w-20 text-center"
              value={match.team2_goals}
              onChange={(e) => setNewMatch({
                ...match,
                team2_goals: parseInt(e.target.value)
              })}
              min="0"
            />
          </div>

          <div className="space-y-2">
            {renderPlayerSelect(2, 1, match.team2_player1_id,
              (value) => setNewMatch({ ...match, team2_player1_id: value }))}
            {match.match_type === '2v2' &&
              renderPlayerSelect(2, 2, match.team2_player2_id,
                (value) => setNewMatch({ ...match, team2_player2_id: value }))}
          </div>
        </div>
      )}

      <div className="flex justify-end gap-2">
        <Button type="button" variant="outline" onClick={onCancel}>
          Cancel
        </Button>
        <Button type="submit">
          {isEditing ? 'Update Match' : isAddResult ? 'Add Result' : 'Schedule Match'}
        </Button>
      </div>
    </form>
  );
  const renderTeamPlayers = (match, teamNumber) => {
    const player1 = teamNumber === 1 ? match.team1_player1_name : match.team2_player1_name;
    const player2 = teamNumber === 1 ? match.team1_player2_name : match.team2_player2_name;
    if (match.match_type === '2v2' && player2) {
      return (
        <div className="flex flex-col">
          <div className="font-medium">
            <span>{player1}</span>
            <span className="mx-1">&</span>
            <span>{player2}</span>
          </div>
        </div>
      );
    }

    return (
      <div className="font-medium">
        {player1}
      </div>
    );
  };

  return (
    <Tabs defaultValue="schedule" className="w-full" onValueChange={handleTabChange}>
      <TabsList>
        <TabsTrigger value="schedule">
          <Calendar className="h-4 w-4 mr-2" />
          Schedule
        </TabsTrigger>
        <TabsTrigger value="results">
          <Trophy className="h-4 w-4 mr-2" />
          Results
        </TabsTrigger>
      </TabsList>

      <TabsContent value="schedule">
        <Card>
          <CardHeader>
            <div className="flex justify-between items-center">
              <div>
                <CardTitle>Scheduled Matches</CardTitle>
                <CardDescription>Manage upcoming matches</CardDescription>
              </div>
              <Button onClick={() => setShowAddMatch(!showAddMatch)}>
                <PlusCircle className="h-4 w-4 mr-2" />
                Schedule Match
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {showAddMatch && (
              <MatchForm
                match={newMatch}
                onSubmit={(e) => handleMatchSubmit(e, true)}
                onCancel={() => setShowAddMatch(false)}
              />
            )}

            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Date</TableHead>
                  <TableHead>Round</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Team 1</TableHead>
                  <TableHead>Team 2</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {matches
                  .filter(m => m.status === 'SCHEDULED')
                  .map((match) => (
                    <TableRow key={match.id}>
                      {editingMatch?.id === match.id ? (
                        // Editing mode
                        <MatchForm
                          match={editingMatch}
                          onSubmit={(e) => {
                            e.preventDefault();
                            handleMatchUpdate(match.id, editingMatch);
                          }}
                          onCancel={() => setEditingMatch(null)}
                          isEditing
                        />
                      ) : (
                        // View mode
                        <>
                          <TableCell>{new Date(match.match_date).toLocaleString()}</TableCell>
                          <TableCell>{match.round}</TableCell>
                          <TableCell>{match.match_type}</TableCell>
                          <TableCell>{renderTeamPlayers(match, 1)}</TableCell>
                          <TableCell>{renderTeamPlayers(match, 2)}</TableCell>
                          <TableCell>
                            <div className="flex gap-2">
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => setEditingMatch(match)}
                              >
                                <Pencil className="h-4 w-4" />
                              </Button>
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => handleDeleteMatch(match.id)}
                              >
                                <Trash2 className="h-4 w-4" />
                              </Button>
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => handleAddResult(match)}
                              >
                                <Trophy className="h-4 w-4" />
                              </Button>
                            </div>
                          </TableCell>
                        </>
                      )}
                    </TableRow>
                  ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </TabsContent>
      <TabsContent value="results">
        <Card>
          <CardHeader>
            <div className="flex justify-between items-center">
              <div>
                <CardTitle>Match Results</CardTitle>
                <CardDescription>View and manage match results</CardDescription>
              </div>
              <Button onClick={() => setShowAddMatch(!showAddMatch)}>
                <PlusCircle className="h-4 w-4 mr-2" />
                Add Result
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {showAddMatch && (
              <MatchForm
                match={newMatch}
                onSubmit={(e) => handleMatchSubmit(e, false)}
                onCancel={() => setShowAddMatch(false)}
                isAddResult={true}
              />
            )}

            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Date</TableHead>
                  <TableHead>Round</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Team 1</TableHead>
                  <TableHead className="text-center">Score</TableHead>
                  <TableHead>Team 2</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {matches
                  .filter(m => m.status === 'COMPLETED')
                  .map((match) => (
                    <TableRow key={match.id}>
                      {editingMatch?.id === match.id ? (
                        <TableCell colSpan={7}>
                          <form onSubmit={(e) => {
                            e.preventDefault();
                            handleMatchUpdate(match.id, editingMatch);
                          }} 
                          className="space-y-4 p-4">
                            <div className="grid grid-cols-2 gap-4">
                              <Select
                                value={editingMatch.round}
                                onValueChange={(value) => setEditingMatch({ ...editingMatch, round: value })}
                              >
                                <SelectTrigger>
                                  <SelectValue placeholder="Select Round" />
                                </SelectTrigger>
                                <SelectContent>
                                  {ROUNDS.map(round => (
                                    <SelectItem key={round} value={round}>{round}</SelectItem>
                                  ))}
                                </SelectContent>
                              </Select>

                              <Input
                                type="datetime-local"
                                value={editingMatch.match_date.slice(0, 16)}
                                onChange={(e) => setEditingMatch({ 
                                  ...editingMatch, 
                                  match_date: e.target.value 
                                })}
                              />
                            </div>

                            <div className="grid grid-cols-3 gap-4 items-center">
                              <div className="space-y-2">
                                {renderPlayerSelect(1, 1, editingMatch.team1_player1_id,
                                  (value) => setEditingMatch({ ...editingMatch, team1_player1_id: value }))}
                                
                                {editingMatch.match_type === '2v2' &&
                                  renderPlayerSelect(1, 2, editingMatch.team1_player2_id,
                                    (value) => setEditingMatch({ ...editingMatch, team1_player2_id: value }))}
                              </div>

                              <div className="flex items-center justify-center gap-2">
                                <Input
                                  type="number"
                                  className="w-20 text-center"
                                  value={editingMatch.team1_goals}
                                  onChange={(e) => setEditingMatch({
                                    ...editingMatch,
                                    team1_goals: parseInt(e.target.value)
                                  })}
                                  min="0"
                                />
                                <span className="font-bold">-</span>
                                <Input
                                  type="number"
                                  className="w-20 text-center"
                                  value={editingMatch.team2_goals}
                                  onChange={(e) => setEditingMatch({
                                    ...editingMatch,
                                    team2_goals: parseInt(e.target.value)
                                  })}
                                  min="0"
                                />
                              </div>

                              <div className="space-y-2">
                                {renderPlayerSelect(2, 1, editingMatch.team2_player1_id,
                                  (value) => setEditingMatch({ ...editingMatch, team2_player1_id: value }))}
                                
                                {editingMatch.match_type === '2v2' &&
                                  renderPlayerSelect(2, 2, editingMatch.team2_player2_id,
                                    (value) => setEditingMatch({ ...editingMatch, team2_player2_id: value }))}
                              </div>
                            </div>

                            <div className="flex justify-end gap-2">
                              <Button type="button" variant="outline" onClick={() => setEditingMatch(null)}>
                                <X className="h-4 w-4 mr-2" />
                                Cancel
                              </Button>
                              <Button type="submit">
                                <Save className="h-4 w-4 mr-2" />
                                Save Changes
                              </Button>
                            </div>
                          </form>
                        </TableCell>
                      ) : (
                        <>
                          <TableCell>{new Date(match.match_date).toLocaleString()}</TableCell>
                          <TableCell>{match.round}</TableCell>
                          <TableCell>{match.match_type}</TableCell>
                          <TableCell>{renderTeamPlayers(match, 1)}</TableCell>
                          <TableCell className="text-center font-bold">
                            {match.team1_goals} - {match.team2_goals}
                          </TableCell>
                          <TableCell>{renderTeamPlayers(match, 2)}</TableCell>
                          <TableCell>
                            <div className="flex gap-2">
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => setEditingMatch(match)}
                              >
                                <Pencil className="h-4 w-4" />
                              </Button>
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => handleDeleteMatch(match.id)}
                              >
                                <Trash2 className="h-4 w-4" />
                              </Button>
                            </div>
                          </TableCell>
                        </>
                      )}
                    </TableRow>
                  ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </TabsContent>
    </Tabs>
  );
};