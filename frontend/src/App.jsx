// App.jsx
import PropTypes from 'prop-types';
import { Routes, Route } from 'react-router-dom';

function App() {
  return (
    <div className="min-h-screen bg-gray-100">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-center text-gray-900 mb-8">
          Welcome to KONSPECTO
        </h1>
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
          {/* Добавьте здесь другие маршруты по мере необходимости */}
        </Routes>
      </div>
    </div>
  );
}

export default App;