import { useState } from 'react';
import './App.css';

function App() {
  const [username, setUsername] = useState('');
  const [leagues, setLeagues] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    
    try {
      const response = await fetch(`http://localhost:8000/leagues/user/${username}`);
      if (!response.ok) {
        throw new Error('User not found');
      }
      const data = await response.json();
      setLeagues(data);
    } catch (err) {
      setError(err.message);
      setLeagues([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <div className="login-container">
        <h1>Dynasty League Analyzer</h1>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="username">Sleeper Username</label>
            <input
              id="username"
              type="text"
              placeholder="Enter your Sleeper username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />
          </div>
          <button type="submit" className="login-button" disabled={loading || !username}>
            {loading ? 'Loading...' : 'Find Leagues'}
          </button>
          {error && <p className="error-message">{error}</p>}
        </form>
        
        {leagues.length > 0 && (
          <div className="leagues-list">
            <h2>Select a league to analyze</h2>
            <ul>
              {leagues.map((league) => (
                <li key={league.league_id}>
                  {league.name}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
