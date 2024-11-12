// src/pages/Search.jsx
import React, { useState } from 'react';

function Search() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleQueryChange = (e) => {
    setQuery(e.target.value);
  };

  const handleQuerySubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const res = await fetch('http://localhost:8000/v1/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }),
      });

      if (!res.ok) {
        throw new Error(`Error: ${res.status} ${res.statusText}`);
      }

      const data = await res.json();
      setResults(data);
    } catch (err) {
      console.error(err);
      setError('An error occurred while processing your request.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
      <div className="w-full max-w-3xl bg-white p-8 rounded shadow">
        <h1 className="text-3xl font-bold text-center text-gray-900 mb-6">
          Search Documents
        </h1>
        <form onSubmit={handleQuerySubmit} className="mb-6">
          <input
            type="text"
            value={query}
            onChange={handleQueryChange}
            className="border border-gray-300 p-2 mb-4 w-full rounded"
            placeholder="Enter your query"
            required
          />
          <button
            type="submit"
            className="w-full bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition duration-200"
            disabled={loading}
          >
            {loading ? 'Searching...' : 'Search'}
          </button>
        </form>
        {error && (
          <div className="mb-4 text-red-500 text-center">
            {error}
          </div>
        )}
        {results && results.results && results.results.length > 0 ? (
          <div className="mt-6">
            <h2 className="text-2xl font-bold mb-4 text-gray-700">Results</h2>
            <div className="space-y-4">
              {results.results.map((item, index) => (
                <div key={item.file_id} className="border border-gray-200 p-4 rounded shadow-sm">
                  <div className="flex justify-between items-center mb-2">
                    <h3 className="text-xl font-semibold text-gray-800">{item.file_name}</h3>
                    <span className="text-sm text-gray-500">Score: {item.score.toFixed(4)}</span>
                  </div>
                  <p className="text-gray-700 mb-2">
                    <strong>File ID:</strong> {item.file_id}
                  </p>
                  <p className="text-gray-700 mb-2">
                    <strong>Modified At:</strong>{' '}
                    {new Date(item.modified_at).toLocaleString()}
                  </p>
                  <p className="text-gray-700 mb-2">
                    <strong>Text Snippet:</strong> {item.text.substring(0, 200)}...
                  </p>
                  <p className="text-gray-700">
                    <strong>Character Range:</strong> {item.start_char_idx} - {item.end_char_idx}
                  </p>
                </div>
              ))}
            </div>
          </div>
        ) : results && results.results && results.results.length === 0 ? (
          <div className="mt-6 text-center text-gray-700">
            No results found for your query.
          </div>
        ) : null}
      </div>
    </div>
  );
}

export default Search;