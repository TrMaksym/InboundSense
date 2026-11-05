import { useState } from 'react';

function App() {
  const [query, setQuery] = useState('');
  const [limit, setLimit] = useState(5);
  const [results, setResults] = useState([]);
  const [searchLoading, setSearchLoading] = useState(false);
  const [searchError, setSearchError] = useState(null);

  const [eventText, setEventText] = useState('');
  const [eventLoading, setEventLoading] = useState(false);
  const [eventStatus, setEventStatus] = useState(null);
  const [eventError, setEventError] = useState(null);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setSearchLoading(true);
    setSearchError(null);

    try {
      const response = await fetch('http://localhost:8000/api/v1/search/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: query, limit: Number(limit) }),
      });

      if (!response.ok) throw new Error(`Server error: ${response.status}`);

      const data = await response.json();
      setResults(data.results || []);
    } catch (err) {
      setSearchError(err.message);
    } finally {
      setSearchLoading(false);
    }
  };

  const handleCreateEvent = async (e) => {
    e.preventDefault();
    if (!eventText.trim()) return;

    setEventLoading(true);
    setEventStatus(null);
    setEventError(null);

    try {
      const response = await fetch('http://localhost:8000/api/v1/events/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: eventText }),
      });

      if (!response.ok) throw new Error(`Server error: ${response.status}`);

      const data = await response.json();
      setEventStatus(`Indexed event ID: ${data.id || data.event_id || 'OK'}`);
      setEventText('');
    } catch (err) {
      setEventError(err.message);
    } finally {
      setEventLoading(false);
    }
  };

  return (
    <div className="container">
      <header className="header">
        <h1>⚡ InboundSense Pipeline</h1>
      </header>

      {/* 1. Ingestion */}
      <section className="card">
        <h2 className="card-title">1. Ingest Payload</h2>
        <form onSubmit={handleCreateEvent} style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <textarea
            className="input-field"
            rows={3}
            placeholder="Type long-form text or event data..."
            value={eventText}
            onChange={(e) => setEventText(e.target.value)}
          />
          <button type="submit" disabled={eventLoading} className="btn btn-accent" style={{ alignSelf: 'flex-start' }}>
            {eventLoading ? 'Processing...' : 'Send Event'}
          </button>
        </form>
        {eventStatus && <p style={{ color: '#34d399', fontSize: '13px', marginTop: '10px' }}>{eventStatus}</p>}
        {eventError && <p style={{ color: '#f87171', fontSize: '13px', marginTop: '10px' }}>Error: {eventError}</p>}
      </section>

      {/* 2. Semantic Search */}
      <section className="card">
        <h2 className="card-title">2. Semantic Vector Search</h2>
        <form onSubmit={handleSearch} style={{ display: 'flex', gap: '10px', marginBottom: '16px' }}>
          <input
            type="text"
            className="input-field"
            placeholder="Search by meaning..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <select
            className="input-field"
            style={{ width: '80px', cursor: 'pointer' }}
            value={limit}
            onChange={(e) => setLimit(e.target.value)}
          >
            <option value={3}>3</option>
            <option value={5}>5</option>
            <option value={10}>10</option>
          </select>
          <button type="submit" disabled={searchLoading} className="btn btn-primary">
            {searchLoading ? '...' : 'Search'}
          </button>
        </form>
        {searchError && <p style={{ color: '#f87171', fontSize: '13px' }}>Error: {searchError}</p>}
      </section>

      {/* Results */}
      <div>
        {results.length > 0 ? (
          results.map((item, index) => (
            <div key={item.chunk_id || index} className="result-card">
              <div className="result-meta">
                <span>ID: {item.chunk_id ? `${item.chunk_id.slice(0, 8)}...` : index}</span>
                {item.similarity !== undefined && (
                  <span className="badge-similarity">Similarity: {Number(item.similarity).toFixed(4)}</span>
                )}
              </div>
              <p className="result-text">
                {item.content || item.text || item.chunk_text || JSON.stringify(item)}
              </p>
            </div>
          ))
        ) : (
          !searchLoading && <p style={{ color: 'var(--text-muted)', fontSize: '14px' }}>No results yet.</p>
        )}
      </div>
    </div>
  );
}

export default App;