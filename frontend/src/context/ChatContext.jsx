// frontend/src/context/ChatContext.jsx
import React, { createContext, useState, useEffect } from 'react';
import PropTypes from 'prop-types';

export const ChatContext = createContext();

export function ChatProvider({ children }) {
  const [chats, setChats] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      try {
        const storedChats = localStorage.getItem('chats');
        const parsedChats = storedChats ? JSON.parse(storedChats) : [];
        setChats(parsedChats);
      } catch (error) {
        console.error('Error loading chats:', error);
      } finally {
        setLoading(false);
      }
    }
  }, []);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('chats', JSON.stringify(chats));
    }
  }, [chats]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="glass-effect p-8 rounded-lg">
          <div className="text-mist-200 text-lg">Загрузка...</div>
        </div>
      </div>
    );
  }

  return (
    <ChatContext.Provider value={{ chats, setChats }}>
      {children}
    </ChatContext.Provider>
  );
}

ChatProvider.propTypes = {
  children: PropTypes.node.isRequired,
};