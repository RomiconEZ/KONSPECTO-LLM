// frontend/src/__tests__/App.test.jsx
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import App from '../App';

test('renders welcome message', () => {
  render(
    <BrowserRouter>
      <App />
    </BrowserRouter>
  );
  const welcomeMessage = screen.getByText(/Welcome to KONSPECTO/i);
  expect(welcomeMessage).toBeInTheDocument();
});