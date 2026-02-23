// frontend/src/__tests__/Chat.test.jsx
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import Chat from '../pages/Chat';
import { ChatContext } from '../context/ChatContext';
import { getConfig } from '../config';

// Мокаем react-router-dom с useParams
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useParams: () => ({
    chatId: '1',
  }),
}));

// Мокаем config
jest.mock('../config');

describe('Chat Component', () => {
  beforeEach(() => {
    getConfig.mockReturnValue({
      API_URL: 'http://localhost:3000/api',
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  const mockChats = [
    {
      id: '1',
      name: 'Чат 1',
      messages: [
        {
          sender: 'user',
          text: 'Hello',
          timestamp: '2023-10-01T12:00:00Z',
        },
        {
          sender: 'agent',
          text: 'Hi there!',
          timestamp: '2023-10-01T12:00:05Z',
          file_id: '12345',
          file_name: 'test.pdf',
        },
      ],
    },
  ];

  const renderChat = (chats = mockChats, setChats = jest.fn(), onOpenDoc = jest.fn()) => {
    return render(
      <MemoryRouter>
        <ChatContext.Provider value={{ chats, setChats }}>
          <Chat onOpenDoc={onOpenDoc} />
        </ChatContext.Provider>
      </MemoryRouter>
    );
  };

  it('renders messages correctly', () => {
    renderChat();

    expect(screen.getByText('Hello')).toBeInTheDocument();
    expect(screen.getByText('Hi there!')).toBeInTheDocument();
    expect(screen.getByText('test.pdf')).toBeInTheDocument();
  });

  it('handles user input and sends query', async () => {
    const mockSetChats = jest.fn();
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: true,
        json: () =>
          Promise.resolve({
            results: [{ text: 'Response from API' }],
          }),
      })
    );

    renderChat(mockChats, mockSetChats);

    const textarea = screen.getByPlaceholderText(/Введите ваш запрос/i);
    fireEvent.change(textarea, { target: { value: 'Test query' } });

    const sendButton = screen.getByText(/Отправить/i);
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:3000/api/search',
        expect.any(Object)
      );
    });
  });

  it('handles API errors gracefully', async () => {
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
      })
    );

    renderChat();

    const textarea = screen.getByPlaceholderText(/Введите ваш запрос/i);
    fireEvent.change(textarea, { target: { value: 'Test query' } });

    const sendButton = screen.getByText(/Отправить/i);
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalled();
    });
  });

  it('opens document viewer when button is clicked', () => {
    const mockOnOpenDoc = jest.fn();

    renderChat(mockChats, jest.fn(), mockOnOpenDoc);

    const viewDocButton = screen.getByText(/Просмотреть документ/i);
    fireEvent.click(viewDocButton);

    expect(mockOnOpenDoc).toHaveBeenCalledWith('12345');
  });
});
