// frontend/src/__tests__/Sidebar.test.jsx

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import Sidebar from '../components/Sidebar';
import { ChatContext } from '../context/ChatContext';
import { getConfig } from '../config';

jest.mock('../config');

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  Link: ({ to, children }) => <a href={to}>{children}</a>,
  useNavigate: () => jest.fn(),
}));

describe('Sidebar Component', () => {
  const mockChats = [
    { id: '1', name: 'Чат 1', messages: [] },
    { id: '2', name: 'Чат 2', messages: [] },
  ];

  let mockSetChats;

  beforeEach(() => {
    mockSetChats = jest.fn();
    getConfig.mockReturnValue({
      API_URL: 'http://localhost:3000/api',
    });
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  const renderSidebar = (props = {}, chats = mockChats, setChats = mockSetChats) => {
    const defaultProps = {
      isOpen: true,
      toggleSidebar: jest.fn(),
      ...props,
    };

    return render(
      <MemoryRouter>
        <ChatContext.Provider value={{ chats, setChats }}>
          <Sidebar {...defaultProps} />
        </ChatContext.Provider>
      </MemoryRouter>
    );
  };

  it('renders Sidebar with chats', () => {
    renderSidebar();

    // Проверка заголовка Sidebar
    expect(screen.getByText(/KONSPECTO/i)).toBeInTheDocument();

    // Проверка наличия существующих чатов
    expect(screen.getByText('Чат 1')).toBeInTheDocument();
    expect(screen.getByText('Чат 2')).toBeInTheDocument();

    // Проверка кнопки добавления чата
    expect(screen.getByText(/Добавить чат/i)).toBeInTheDocument();
  });

  it('calls setChats when Add Chat button is clicked', () => {
    renderSidebar();

    const addChatButton = screen.getByText(/Добавить чат/i);
    fireEvent.click(addChatButton);

    expect(mockSetChats).toHaveBeenCalledTimes(1);
  });

  it('calls setChats when Delete button is clicked', () => {
    window.confirm = jest.fn().mockReturnValue(true);

    renderSidebar();

    const deleteButtons = screen.getAllByLabelText(/Удалить чат/i);
    fireEvent.click(deleteButtons[0]);

    expect(window.confirm).toHaveBeenCalled();
    expect(mockSetChats).toHaveBeenCalledTimes(1);
  });

  it('calls setChats when Rename button is clicked and new name is provided', () => {
    window.prompt = jest.fn().mockReturnValue('Новое имя');

    renderSidebar();

    const renameButtons = screen.getAllByLabelText(/Изменить название чата/i);
    fireEvent.click(renameButtons[0]);

    expect(window.prompt).toHaveBeenCalledWith('Введите новое название чата:', 'Чат 1');
    expect(mockSetChats).toHaveBeenCalledTimes(1);
  });

  it('toggles Sidebar visibility when toggle button is clicked', () => {
    const toggleSidebar = jest.fn();
    renderSidebar({ toggleSidebar });

    const toggleButton = screen.getByLabelText(/Скрыть меню/i);
    fireEvent.click(toggleButton);

    expect(toggleSidebar).toHaveBeenCalledTimes(1);
  });
});
