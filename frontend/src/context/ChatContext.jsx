// frontend/src/context/ChatContext.jsx
import React, { createContext, useState, useEffect } from 'react';
import PropTypes from 'prop-types';

export const ChatContext = createContext();

export function ChatProvider({ children }) {
  const [chats, setChats] = useState([]);

  useEffect(() => {
    // Проверяем, что код выполняется в браузере
    if (typeof window !== 'undefined') {
      // Загрузка чатов из localStorage при монтировании компонента
      const storedChats = localStorage.getItem('chats');
      const parsedChats = storedChats ? JSON.parse(storedChats) : [];
      console.log('Loaded chats from localStorage:', parsedChats);
      setChats(parsedChats);
    }
  }, []);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      // Сохранение чатов в localStorage при изменении
      console.log('Saving chats to localStorage:', chats);
      localStorage.setItem('chats', JSON.stringify(chats));
    }
  }, [chats]);

  return (
    <ChatContext.Provider value={{ chats, setChats }}>
      {children}
    </ChatContext.Provider>
  );
}

ChatProvider.propTypes = {
  children: PropTypes.node.isRequired,
};