// frontend/src/__tests__/App.test.jsx
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import App from '../App';
import { getConfig } from '../config';

// Мокаем react-router-dom
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => jest.fn(),
  useParams: () => ({ chatId: '1' }),
}));

jest.mock('../config');

describe('App Component', () => {
  beforeEach(() => {
    localStorage.clear();
    getConfig.mockReturnValue({
      API_URL: 'http://localhost:3000/api',
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('renders Sidebar and main content', () => {
    render(
      <MemoryRouter>
        <App />
      </MemoryRouter>
    );

    expect(screen.getByLabelText(/Скрыть меню/i)).toBeInTheDocument();
    expect(
      screen.getByText(/Интеллектуальный агент для работы с заметками и видео лекциями/i)
    ).toBeInTheDocument();
  });

  it('adds a new chat', () => {
    render(
      <MemoryRouter>
        <App />
      </MemoryRouter>
    );

    const addChatButton = screen.getByText(/Добавить чат/i);
    fireEvent.click(addChatButton);

    expect(localStorage.getItem('chats')).toBeTruthy();
    const savedChats = JSON.parse(localStorage.getItem('chats'));
    expect(savedChats).toHaveLength(1);
    expect(savedChats[0].name).toMatch(/Чат 1/);
  });

  it('toggles sidebar visibility', () => {
    render(
      <MemoryRouter>
        <App />
      </MemoryRouter>
    );

    const toggleButton = screen.getByLabelText(/Скрыть меню/i);
    const sidebar = screen.getByRole('navigation');

    expect(sidebar).toHaveClass('w-64');
    fireEvent.click(toggleButton);
    expect(sidebar).toHaveClass('w-16');
  });
});
