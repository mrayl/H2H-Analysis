import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = 'http://127.0.0.1:8080/api';

function PlayerCompare() {
  
  const [playerList, setPlayerList] = useState([]);
  
  // Store the selected player IDs
  const [playerAId, setPlayerAId] = useState(null);
  const [playerBId, setPlayerBId] = useState(null);
  
  // Store season
  const [season, setSeason] = useState('2025-26'); 
  
  // Store final comparison
  const [comparisonData, setComparisonData] = useState(null);
  
  // UI state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);


  // Fetch all Players
  useEffect(() => {
    const fetchPlayers = async () => {
      try {
        const response = await axios.get(`${API_URL}/players/`);
        setPlayerList(response.data);
      } catch (err) {
        console.error("Error fetching player list:", err);
        setError('Could not load player list.');
      }
    };
    fetchPlayers();
  }, []);

  // Handle Compare
  const handleCompare = async () => {
    if (!playerAId || !playerBId) {
      setError('Please select two players to compare.');
      return;
    }
    
    setLoading(true);
    setError(null);
    setComparisonData(null);

    try {
      const params = {
        player_a_id: playerAId,
        player_b_id: playerBId,
        season: season,
      };
      const queryString = new URLSearchParams(params).toString();
      
      const response = await axios.get(`${API_URL}/compare/?${queryString}`);
      setComparisonData(response.data);

    } catch (err) {
      console.error("Error fetching comparison data:", err);
      setError('Failed to fetch comparison data.');
    } finally {
      setLoading(false);
    }
  };

  
  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1>NBA Head-to-Head Analyzer</h1>
      
      {/* --- Controls --- */}
      <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
        {/* Player A Selector */}
        <select 
          onChange={(e) => setPlayerAId(e.target.value)} 
          defaultValue=""
        >
          <option value="" disabled>Select Player A</option>
          {playerList.map(player => (
            <option key={player.api_id} value={player.api_id}>
              {player.first_name} {player.last_name}
            </option>
          ))}
        </select>

        {/* Player B Selector */}
        <select 
          onChange={(e) => setPlayerBId(e.target.value)} 
          defaultValue=""
        >
          <option value="" disabled>Select Player B</option>
          {playerList.map(player => (
            <option key={player.api_id} value={player.api_id}>
              {player.first_name} {player.last_name}
            </option>
          ))}
        </select>

        {/* Season Input */}
        <input 
          type="text"
          value={season}
          onChange={(e) => setSeason(e.target.value)}
          placeholder="e.g., 2025-26"
        />

        <button onClick={handleCompare} disabled={loading}>
          {loading ? 'Comparing...' : 'Compare'}
        </button>
      </div>

      {/* --- Results --- */}
      {error && <div style={{ color: 'red' }}>{error}</div>}
      
      {comparisonData && (
        <div>
          <h2>Comparison Results</h2>
          <h3>I will make this readable later</h3>
          <pre style={{ background: '#f4f4f4', padding: '10px' }}>
            {JSON.stringify(comparisonData, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}

export default PlayerCompare;