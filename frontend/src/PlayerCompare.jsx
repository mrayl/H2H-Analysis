import React, { useState, useEffect } from 'react';
import axios from 'axios';
import StatsTable from './StatsTable';

const API_URL = 'http://127.0.0.1:8080/api';

function PlayerCompare() {
  
  const [playerList, setPlayerList] = useState([]);
  
  // Store the selected player IDs
  const [playerAId, setPlayerAId] = useState("");
  const [playerBId, setPlayerBId] = useState("");
  
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
        console.log("Player List API Response:", response.data);

        let players = [];
        if (Array.isArray(response.data)) {
            players = response.data;
        } else if (response.data && Array.isArray(response.data.results)) {
            players = response.data.results;
        } else {
            console.error("Unexpected API response format:", response.data);
            setError('Received invalid data format from server for player list.');
            return; 
        }
        setPlayerList(players);
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
    <div className="container">
      <header className="app-header">
        <h1>NBA Head-to-Head Analyzer</h1>
        <p>For a School Project</p>
      </header>
      
      {/* Controls */}
      <div className="controls-container">
        <div className="control-group">
            <label>Player A</label>
            <select 
            onChange={(e) => setPlayerAId(e.target.value)} 
            value={playerAId}
            >
            <option value="" disabled>Select Player A</option>
            {Array.isArray(playerList) && playerList.length > 0 ? (
                playerList.map(player => (
                    <option key={player.api_id} value={player.api_id}>
                    {player.first_name} {player.last_name}
                    </option>
                ))
            ) : (
                <option value="" disabled>Loading players...</option>
            )}
            </select>
        </div>

        <div className="control-group">
            <label>Player B</label>
            <select 
            onChange={(e) => setPlayerBId(e.target.value)} 
            value={playerBId}
            >
            <option value="" disabled>Select Player B</option>
            {Array.isArray(playerList) && playerList.length > 0 ? (
                playerList.map(player => (
                    <option key={player.api_id} value={player.api_id}>
                    {player.first_name} {player.last_name}
                    </option>
                ))
            ) : (
                <option value="" disabled>Loading players...</option>
            )}
            </select>
        </div>

        <div className="control-group">
            <label>Season</label>
            <input 
            type="text"
            value={season}
            onChange={(e) => setSeason(e.target.value)}
            placeholder="e.g., 2025-26"
            />
        </div>

        <button className="compare-btn" onClick={handleCompare} disabled={loading}>
          {loading ? 'Analyzing...' : 'COMPARE'}
        </button>
      </div>

      {/* Error Message */}
      {error && <div className="error-message">{error}</div>}
      
      {/* Results */}
      {comparisonData && (
        <div className="results-container">
            <h2 className="comparison-title">
                {comparisonData.player_a_details.first_name} {comparisonData.player_a_details.last_name} 
                <span className="vs"> vs </span> 
                {comparisonData.player_b_details.first_name} {comparisonData.player_b_details.last_name}
            </h2>
            <p className="season-subtitle">Season: {comparisonData.season}</p>

            <div className="tables-wrapper">
                {/* Season Stats Table */}
                <StatsTable 
                    title="Regular Season Stats"
                    playerAName={comparisonData.player_a_details.last_name}
                    playerBName={comparisonData.player_b_details.last_name}
                    statsA={comparisonData.season_stats.player_a}
                    statsB={comparisonData.season_stats.player_b}
                />

                {/* H2H Stats Table */}
                <StatsTable 
                    title="Head-to-Head Matchups"
                    playerAName={comparisonData.player_a_details.last_name}
                    playerBName={comparisonData.player_b_details.last_name}
                    statsA={comparisonData.h2h_stats.player_a}
                    statsB={comparisonData.h2h_stats.player_b}
                />
            </div>
        </div>
      )}
    </div>
  );
}

export default PlayerCompare;