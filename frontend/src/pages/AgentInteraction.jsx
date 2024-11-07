// src/pages/AgentInteraction.jsx
import React, { useState } from 'react';

function AgentInteraction() {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleQueryChange = (e) => {
    setQuery(e.target.value);
  };

  const handleQuerySubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResponse('');

    try {
      const res = await fetch('http://localhost:8000/v1/agent', {
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
      setResponse(data.response);
    } catch (err) {
      console.error(err);
      setError('An error occurred while processing your request.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      <div className="w-full max-w-md bg-white p-8 rounded shadow">
        <h1 className="text-3xl font-bold text-center text-gray-900 mb-6">
          Interact with KONSPECTO Agent
        </h1>
        <form onSubmit={handleQuerySubmit} className="mb-4">
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
            {loading ? 'Submitting...' : 'Submit'}
          </button>
        </form>
        {error && (
          <div className="mb-4 text-red-500 text-center">
            {error}
          </div>
        )}
        {response && (
          <div className="mt-6 bg-gray-50 p-4 rounded">
            <h2 className="text-2xl font-bold mb-2 text-gray-700">Response</h2>
            <p>{response}</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default AgentInteraction;