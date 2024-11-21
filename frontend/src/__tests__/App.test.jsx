// frontend/src/__tests__/App.test.jsx
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import App from '../App';

test('renders initial welcome message', () => {
  render(
    <BrowserRouter>
      <App />
    </BrowserRouter>
  );

  const welcomeMessage = screen.getByText(/Интеллектуальный агент для работы с заметками и видео лекциями/i);
  expect(welcomeMessage).toBeInTheDocument();
});