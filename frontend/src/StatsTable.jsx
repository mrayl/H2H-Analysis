import React from 'react';

const StatsTable = ({ title, playerAName, playerBName, statsA, statsB }) => {
    // Won't render the full table if there is an error/stats missing
    if (!statsA || !statsB || statsA.error || statsB.error) {
      return (
          <div className="stats-table-container">
              <h3>{title}</h3>
              <p>Data not available for comparison.</p>
              {statsA?.error && <p style={{color: 'red'}}>Player A: {statsA.error}</p>}
              {statsB?.error && <p style={{color: 'red'}}>Player B: {statsB.error}</p>}
          </div>
      )
  }
  
  // Formats numbers
  const formatVal = (key, val) => {
      if (typeof val !== 'number') return val;
      if (key.includes('PCT') || key.includes('pct')) return (val * 100).toFixed(1) + '%';
      return val;
  };

  // Get stat keys
  const avgKeys = Object.keys(statsA.avg_stats || {});
  
  const advKeys = Object.keys(statsA.advanced_stats || {});

  return (
    <div className="stats-table-container">
      <h3>{title}</h3>
      <table className="stats-table">
        <thead>
          <tr>
            <th className="stat-label">Stat</th>
            <th>{playerAName}</th>
            <th>{playerBName}</th>
          </tr>
        </thead>
        <tbody>
            {/* Render Game Count Row */}
            <tr className="section-header">
                <td>Games Played</td>
                <td>{statsA.game_count}</td>
                <td>{statsB.game_count}</td>
            </tr>

            {/* Render Average Stats */}
            {avgKeys.map(key => (
            <tr key={key}>
              <td className="stat-label">{key}</td>
              <td className={statsA.avg_stats[key] > statsB.avg_stats[key] ? 'winner' : ''}>
                  {formatVal(key, statsA.avg_stats[key])}
              </td>
              <td className={statsB.avg_stats[key] > statsA.avg_stats[key] ? 'winner' : ''}>
                  {formatVal(key, statsB.avg_stats[key])}
              </td>
            </tr>
          ))}

          {/* Render Advanced Stats Header */}
           <tr className="section-header">
                <td colSpan="3">Advanced Stats</td>
            </tr>

          {/* Render Advanced Stats */}
          {advKeys.map(key => (
            <tr key={key}>
              <td className="stat-label">{key.replace('_', ' ').toUpperCase()}</td>
              <td className={statsA.advanced_stats[key] > statsB.advanced_stats[key] ? 'winner' : ''}>
                  {formatVal(key, statsA.advanced_stats[key])}
              </td>
              <td className={statsB.advanced_stats[key] > statsA.advanced_stats[key] ? 'winner' : ''}>
                  {formatVal(key, statsB.advanced_stats[key])}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default StatsTable;