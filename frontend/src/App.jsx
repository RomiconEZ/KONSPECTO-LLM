// src/App.jsx
import React from 'react';
import { Routes, Route, Link } from 'react-router-dom';
import AgentInteraction from './pages/AgentInteraction';
import Search from './pages/Search';

function App() {
  return (
    <div className="min-h-screen bg-gray-100">
      <nav className="bg-white shadow">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-xl font-bold text-gray-900">KONSPECTO</h1>
          <div className="space-x-4">
            <Link
              to="/"
              className="text-gray-700 hover:text-gray-900 transition duration-200"
            >
              Home
            </Link>
            <Link
              to="/agent"
              className="text-gray-700 hover:text-gray-900 transition duration-200"
            >
              Agent Interaction
            </Link>
            <Link
              to="/search"
              className="text-gray-700 hover:text-gray-900 transition duration-200"
            >
              Search
            </Link>
          </div>
        </div>
      </nav>

      <div className="container mx-auto px-4 py-8">
        <Routes>
          <Route
            path="/"
            element={
              <div className="text-center text-gray-700">
                <p className="mb-4">
                  Intelligent agent for working with notes and video lectures
                </p>
                <p>Please select an option to begin</p>
              </div>
            }
          />
          <Route path="/agent" element={<AgentInteraction />} />
          <Route path="/search" element={<Search />} />
          {/* Обработка несуществующих маршрутов */}
          <Route
            path="*"
            element={
              <div className="text-center text-gray-700">
                <h2 className="text-2xl font-bold mb-4">404 - Not Found</h2>
                <p>The page you are looking for does not exist.</p>
              </div>
            }
          />
        </Routes>
      </div>
    </div>
  );
}

export default App;