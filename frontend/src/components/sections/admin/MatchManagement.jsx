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
  const [showMatchForm, setShowMatchForm] = useState(false);
  const [editingMatchId, setEditingMatchId] = useState(null);

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
      // Print the data being sent for debugging
      console.log('Submitting match data:', matchData);

      const url = matchData.id 
        ? `http://localhost:8000/matches/${matchData.id}` 
        : 'http://localhost:8000/matches';

      // Ensure all numeric fields are properly converted
      const submitData = {
        round: matchData.round,
        match_type: matchData.match_type,
        team1_player1_id: parseInt(matchData.team1_player1_id),
        team2_player1_id: parseInt(matchData.team2_player1_id),
        team1_player2_id: matchData.team1_player2_id ? parseInt(matchData.team1_player2_id) : null,
        team2_player2_id: matchData.team2_player2_id ? parseInt(matchData.team2_player2_id) : null,
        match_date: matchData.match_date,
        team1_goals: matchData.team1_goals !== "" && matchData.team1_goals !== null 
          ? parseInt(matchData.team1_goals) 
          : null,
        team2_goals: matchData.team2_goals !== "" && matchData.team2_goals !== null 
          ? parseInt(matchData.team2_goals) 
          : null,
        status: matchData.status || 'SCHEDULED'
      };

      console.log('Formatted submit data:', submitData);

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

      const result = await response.json();
      console.log('Save successful:', result);

      setNewMatch(emptyMatch);
      setShowMatchForm(false);
      setEditingMatchId(null);
      fetchData();
    } catch (err) {
      console.error('Error in handleMatchSubmit:', err);
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

  // const handleMatchUpdate = async (matchId, updatedData) => {
  //   try {
  //     const response = await fetch(`http://localhost:8000/matches/${matchId}`, {
  //       method: 'PUT',
  //       headers: {
  //         'Content-Type': 'application/json',
  //       },
  //       body: JSON.stringify(updatedData),
  //     });

  //     if (!response.ok) {
  //       throw new Error('Failed to update match');
  //     }

  //     // Update the matches array with the updated data
  //     setMatches((prevMatches) =>
  //       prevMatches.map((match) =>
  //         match.id === matchId ? { ...match, ...updatedData } : match
  //       )
  //     );

  //     setEditingMatchId(null);
  //   } catch (err) {
  //     setError(err.message);
  //   }
  // };

  // const renderEditableCell = (match, field, onChange) => {
  //   if (editingMatchId === match.id && (field === 'match_date' || field === 'round' || field === 'team1_player1_id' || field === 'team1_player2_id' || field === 'team2_player1_id' || field === 'team2_player2_id')) {
  //     return (
  //       <TableCell>
  //         {field === 'match_date' ? (
  //           <Input
  //             type="datetime-local"
  //             value={match[field]}
  //             onChange={(e) => onChange({ [field]: e.target.value })}
  //           />
  //         ) : field === 'round' ? (
  //           <Select
  //             value={match[field]}
  //             onValueChange={(value) => onChange({ [field]: value })}
  //           >
  //             <SelectTrigger>
  //               <SelectValue placeholder="Select Round" />
  //             </SelectTrigger>
  //             <SelectContent>
  //               {ROUNDS.map((round) => (
  //                 <SelectItem key={round} value={round}>
  //                   {round}
  //                 </SelectItem>
  //               ))}
  //             </SelectContent>
  //           </Select>
  //         ) : (
  //           <Select
  //             value={match[field]?.toString()}
  //             onValueChange={(value) => onChange({ [field]: parseInt(value) })}
  //           >
  //             <SelectTrigger>
  //               <SelectValue placeholder={`Team ${field.slice(-1)} Player ${field.slice(-1)}`} />
  //             </SelectTrigger>
  //             <SelectContent>
  //               {players.map((player) => (
  //                 <SelectItem key={player.player_id} value={player.player_id.toString()}>
  //                   {player.player_name}
  //                 </SelectItem>
  //               ))}
  //             </SelectContent>
  //           </Select>
  //         )}
  //       </TableCell>
  //     );
  //   } else {
  //     return <TableCell>{match[field]}</TableCell>;
  //   }
  // };

  // const handleAddResult = (match) => {
  //   setNewMatch({
  //     round: match.round,
  //     match_type: match.match_type,
  //     team1_player1_id: match.team1_player1_id,
  //     team1_player2_id: match.team1_player2_id,
  //     team2_player1_id: match.team2_player1_id,
  //     team2_player2_id: match.team2_player2_id,
  //     team1_goals: null,
  //     team2_goals: null,
  //     match_date: match.match_date
  //   });
  //   setShowAddMatch(true);
  //   setIsAddResult(true);
  // };

  const MatchForm = ({ match = emptyMatch, onSubmit }) => {
    // Use local state for form data
    const [formData, setFormData] = useState(match);

    // Update form data when match prop changes
    useEffect(() => {
      setFormData(match);
    }, [match]);

    const handleFormChange = (field, value) => {
      setFormData(prev => ({
        ...prev,
        [field]: value
      }));
    };

    return (
      <form
        onSubmit={(e) => {
          e.preventDefault();
          onSubmit(formData);
        }}
        className="space-y-6 p-6 border rounded-lg bg-slate-50"
      >
        <div className="grid grid-cols-2 gap-6">
          <div>
            <label className="block font-medium text-gray-700 mb-1">Round</label>
            <Select
              value={formData.round}
              onValueChange={(value) => {
                const matchType = ROUND_TYPES[value];
                setFormData(prev => ({
                  ...prev,
                  round: value,
                  match_type: matchType,
                  team1_player2_id: matchType === '2v2' ? prev.team1_player2_id : null,
                  team2_player2_id: matchType === '2v2' ? prev.team2_player2_id : null
                }));
              }}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select Round" />
              </SelectTrigger>
              <SelectContent>
                {ROUNDS.map((round) => (
                  <SelectItem key={round} value={round}>
                    {round}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <p className="mt-1 text-sm text-gray-500">{formData.match_type} match</p>
          </div>

          <div>
            <label className="block font-medium text-gray-700 mb-1">Date & Time</label>
            <Input
              type="datetime-local"
              value={formData.match_date}
              onChange={(e) => handleFormChange('match_date', e.target.value)}
              required
            />
          </div>
        </div>

        <div className="flex justify-between items-start gap-6">
          {/* Team 1 */}
          <div className="flex-1 space-y-4">
            <div>
              <label className="block text-sm text-gray-600 mb-1">Team 1 Player 1</label>
              <Select
                value={formData.team1_player1_id?.toString() || ''}
                onValueChange={(value) => handleFormChange('team1_player1_id', parseInt(value))}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select Player" />
                </SelectTrigger>
                <SelectContent>
                  {players.map((player) => (
                    <SelectItem key={player.player_id} value={player.player_id.toString()}>
                      {player.player_name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            {formData.match_type === '2v2' && (
              <div>
                <label className="block text-sm text-gray-600 mb-1">Team 1 Player 2</label>
                <Select
                  value={formData.team1_player2_id?.toString() || ''}
                  onValueChange={(value) => handleFormChange('team1_player2_id', parseInt(value))}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select Player" />
                  </SelectTrigger>
                  <SelectContent>
                    {players.map((player) => (
                      <SelectItem key={player.player_id} value={player.player_id.toString()}>
                        {player.player_name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            )}
          </div>

          {/* Scores in the middle */}
          <div className="flex items-end gap-4 pb-2">
            <div>
              <label className="block text-sm text-gray-600 mb-1">Score</label>
              <div className="flex items-center gap-2">
                <Input
                  type="number"
                  className="w-16 text-center"
                  value={formData.team1_goals ?? ''}
                  onChange={(e) => handleFormChange('team1_goals', 
                    e.target.value ? parseInt(e.target.value) : null
                  )}
                  min="0"
                />
                <span className="text-xl font-medium">-</span>
                <Input
                  type="number"
                  className="w-16 text-center"
                  value={formData.team2_goals ?? ''}
                  onChange={(e) => handleFormChange('team2_goals',
                    e.target.value ? parseInt(e.target.value) : null
                  )}
                  min="0"
                />
              </div>
            </div>
          </div>

          {/* Team 2 */}
          <div className="flex-1 space-y-4">
            <div>
              <label className="block text-sm text-gray-600 mb-1">Team 2 Player 1</label>
              <Select
                value={formData.team2_player1_id?.toString() || ''}
                onValueChange={(value) => handleFormChange('team2_player1_id', parseInt(value))}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select Player" />
                </SelectTrigger>
                <SelectContent>
                  {players.map((player) => (
                    <SelectItem key={player.player_id} value={player.player_id.toString()}>
                      {player.player_name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            {formData.match_type === '2v2' && (
              <div>
                <label className="block text-sm text-gray-600 mb-1">Team 2 Player 2</label>
                <Select
                  value={formData.team2_player2_id?.toString() || ''}
                  onValueChange={(value) => handleFormChange('team2_player2_id', parseInt(value))}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select Player" />
                  </SelectTrigger>
                  <SelectContent>
                    {players.map((player) => (
                      <SelectItem key={player.player_id} value={player.player_id.toString()}>
                        {player.player_name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            )}
          </div>
        </div>

        <div className="flex justify-end gap-2 mt-4">
          <Button type="button" variant="outline" onClick={() => {
            setShowMatchForm(false);
            setEditingMatchId(null);
            setNewMatch(emptyMatch);
          }}>
            Cancel
          </Button>
          <Button type="submit">
            {formData.id ? 'Update Match' : 'Add Match'}
          </Button>
        </div>
      </form>
    );
  };

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
    <Card>
      <CardHeader>
        <div className="flex justify-between items-center">
          <div>
            <CardTitle>Scheduled Matches</CardTitle>
            <CardDescription>Manage upcoming matches</CardDescription>
          </div>
          <Button onClick={() => setShowMatchForm(true)}>
            <PlusCircle className="h-4 w-4 mr-2" />
            Add Match Data
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {showMatchForm && (
          <MatchForm
            match={editingMatchId ? matches.find((m) => m.id === editingMatchId) : emptyMatch}
            onSubmit={handleMatchSubmit}
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
              <TableHead>Score</TableHead>
              <TableHead>Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {matches
              .filter((m) => m.status === 'SCHEDULED')
              .map((match) => (
                <TableRow key={match.id}>
                  <TableCell>{new Date(match.match_date).toLocaleString()}</TableCell>
                  <TableCell>{match.round}</TableCell>
                  <TableCell>{match.match_type}</TableCell>
                  <TableCell>{renderTeamPlayers(match, 1)}</TableCell>
                  <TableCell>{renderTeamPlayers(match, 2)}</TableCell>
                  <TableCell>
                    {match.team1_goals !== null && match.team2_goals !== null ? (
                      `${match.team1_goals} - ${match.team2_goals}`
                    ) : (
                      '-'
                    )}
                  </TableCell>
                  <TableCell>
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => {
                          // Make sure to properly convert all values
                          const matchToEdit = {
                            ...match,
                            team1_goals: match.team1_goals ?? null,
                            team2_goals: match.team2_goals ?? null,
                            team1_player2_id: match.team1_player2_id ?? null,
                            team2_player2_id: match.team2_player2_id ?? null,
                          };
                          setNewMatch(matchToEdit);
                          setEditingMatchId(match.id);
                          setShowMatchForm(true);
                        }}
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
                </TableRow>
              ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
};