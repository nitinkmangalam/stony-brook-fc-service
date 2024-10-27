import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from '../../ui/card';
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
import { PlusCircle, Pencil, Trash2 } from 'lucide-react';
import { Alert, AlertDescription } from '../../ui/alert';

export const PlayerManagement = () => {
  const [players, setPlayers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [editingPlayer, setEditingPlayer] = useState(null);
  const [newPlayerName, setNewPlayerName] = useState('');

  const fetchPlayers = async () => {
    try {
      const response = await fetch('http://localhost:8000/players');
      if (!response.ok) throw new Error('Failed to fetch players');
      const data = await response.json();
      setPlayers(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPlayers();
  }, []);

  const handleAddPlayer = async () => {
    if (!newPlayerName.trim()) return;

    try {
      const response = await fetch('http://localhost:8000/players', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ player_name: newPlayerName }),
      });

      if (!response.ok) throw new Error('Failed to add player');
      
      setNewPlayerName('');
      fetchPlayers();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleUpdatePlayer = async (playerId, updatedName) => {
    try {
      const response = await fetch(`http://localhost:8000/players/${playerId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ player_name: updatedName }),
      });

      if (!response.ok) throw new Error('Failed to update player');
      
      setEditingPlayer(null);
      fetchPlayers();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleDeletePlayer = async (playerId) => {
    if (!window.confirm('Are you sure you want to delete this player?')) return;

    try {
      const response = await fetch(`http://localhost:8000/players/${playerId}`, {
        method: 'DELETE',
      });

      if (!response.ok) throw new Error('Failed to delete player');
      
      fetchPlayers();
    } catch (err) {
      setError(err.message);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) return <div>Loading players...</div>;
  if (error) return <Alert variant="destructive"><AlertDescription>{error}</AlertDescription></Alert>;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Player Management</CardTitle>
        <CardDescription>Add, edit, or remove players from the tournament</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="mb-6 flex gap-4">
          <Input
            placeholder="Enter player name"
            value={newPlayerName}
            onChange={(e) => setNewPlayerName(e.target.value)}
          />
          <Button onClick={handleAddPlayer} className="flex items-center gap-2">
            <PlusCircle className="h-4 w-4" />
            Add Player
          </Button>
        </div>

        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-[40%]">Name</TableHead>
              <TableHead className="w-[40%]">Created At</TableHead>
              <TableHead className="w-[20%] text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {players.map((player) => (
              <TableRow key={player.player_id}>
                <TableCell className="font-medium">
                  {editingPlayer === player.player_id ? (
                    <Input
                      value={player.player_name}
                      onChange={(e) => {
                        const updatedPlayers = players.map(p =>
                          p.player_id === player.player_id
                            ? { ...p, player_name: e.target.value }
                            : p
                        );
                        setPlayers(updatedPlayers);
                      }}
                      onBlur={() => handleUpdatePlayer(player.player_id, player.player_name)}
                      autoFocus
                    />
                  ) : (
                    player.player_name
                  )}
                </TableCell>
                <TableCell>{formatDate(player.created_at)}</TableCell>
                <TableCell className="text-right">
                  <div className="flex justify-end gap-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setEditingPlayer(player.player_id)}
                    >
                      <Pencil className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDeletePlayer(player.player_id)}
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