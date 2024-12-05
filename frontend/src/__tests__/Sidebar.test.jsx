// frontend/src/__tests__/Sidebar.test.jsx

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import Sidebar from '../components/Sidebar';
import { getConfig } from '../config';

// Мокаем react-router-dom
import * as reactRouterDom from 'react-router-dom';

jest.mock('../config');

// Мокаем Link компонент, если необходимо
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  Link: ({ to, children }) => <a href={to}>{children}</a>,
}));

describe('Sidebar Component', () => {
  const mockProps = {
    isOpen: true,
    toggleSidebar: jest.fn(),
    chats: [
      { id: 1, name: 'Чат 1', messages: [] },
      { id: 2, name: 'Чат 2', messages: [] },
    ],
    addChat: jest.fn(),
    deleteChat: jest.fn(),
    renameChat: jest.fn(),
  };

  beforeEach(() => {
    getConfig.mockReturnValue({
      API_URL: 'http://localhost:3000/api',
    });
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it('renders Sidebar with chats', () => {
    render(
      <MemoryRouter>
        <Sidebar {...mockProps} />
      </MemoryRouter>
    );

    // Проверка заголовка Sidebar
    expect(screen.getByText(/KONSPECTO/i)).toBeInTheDocument();

    // Проверка наличия существующих чатов
    expect(screen.getByText('Чат 1')).toBeInTheDocument();
    expect(screen.getByText('Чат 2')).toBeInTheDocument();

    // Проверка кнопки добавления чата
    expect(screen.getByText(/Добавить чат/i)).toBeInTheDocument();
  });

  it('calls addChat when Add Chat button is clicked', () => {
    render(
      <MemoryRouter>
        <Sidebar {...mockProps} />
      </MemoryRouter>
    );

    const addChatButton = screen.getByText(/Добавить чат/i);
    fireEvent.click(addChatButton);

    expect(mockProps.addChat).toHaveBeenCalledTimes(1);
  });

  it('calls deleteChat when Delete button is clicked', () => {
    render(
      <MemoryRouter>
        <Sidebar {...mockProps} />
      </MemoryRouter>
    );

    const deleteButtons = screen.getAllByLabelText(/Удалить чат/i);
    fireEvent.click(deleteButtons[0]);

    expect(mockProps.deleteChat).toHaveBeenCalledWith(1);
  });

  it('calls renameChat when Rename button is clicked and new name is provided', () => {
    window.prompt = jest.fn().mockReturnValue('Новое имя');

    render(
      <MemoryRouter>
        <Sidebar {...mockProps} />
      </MemoryRouter>
    );

    const renameButtons = screen.getAllByLabelText(/Изменить название чата/i);
    fireEvent.click(renameButtons[0]);

    expect(window.prompt).toHaveBeenCalledWith('Введите новое название чата:', 'Чат 1');
    expect(mockProps.renameChat).toHaveBeenCalledWith(1, 'Новое имя');
  });

  it('toggles Sidebar visibility when toggle button is clicked', () => {
    render(
      <MemoryRouter>
        <Sidebar {...mockProps} />
      </MemoryRouter>
    );

    const toggleButton = screen.getByLabelText(/Скрыть меню/i);
    fireEvent.click(toggleButton);

    expect(mockProps.toggleSidebar).toHaveBeenCalledTimes(1);
  });
});
