// src/App.jsx
import React, { useState } from 'react';
import { Routes, Route, Link, useNavigate } from 'react-router-dom';
import Chat from './pages/Chat';

function App() {
  const [chats, setChats] = useState([]);
  const [selectedChat, setSelectedChat] = useState(null);
  const navigate = useNavigate();

  const addChat = () => {
    const newChat = { id: Date.now(), name: `Chat ${chats.length + 1}`, messages: [] };
    setChats([...chats, newChat]);
    setSelectedChat(newChat);
    navigate(`/chat/${newChat.id}`);
  };

  const deleteChat = (chatId) => {
    setChats(chats.filter(chat => chat.id !== chatId));
    if (selectedChat && selectedChat.id === chatId) {
      setSelectedChat(null);
      navigate('/');
    }
  };

  const renameChat = (chatId, newName) => {
    setChats(chats.map(chat => chat.id === chatId ? { ...chat, name: newName } : chat));
  };

  return (
    <div className="flex min-h-screen bg-gray-100">
      <nav className="w-64 bg-white shadow-lg p-4">
        <h1 className="text-xl font-bold text-gray-900 mb-4">KONSPECTO</h1>
        <button
          onClick={addChat}
          className="w-full bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition duration-200 mb-4"
        >
          Add Chat
        </button>
        <ul>
          {chats.map(chat => (
            <li key={chat.id} className="mb-2">
              <div className="flex justify-between items-center">
                <Link
                  to={`/chat/${chat.id}`}
                  className="text-gray-700 hover:text-gray-900 transition duration-200"
                  onClick={() => setSelectedChat(chat)}
                >
                  {chat.name}
                </Link>
                <div className="flex space-x-2">
                  <button
                    onClick={() => {
                      const newName = prompt('Enter new chat name:', chat.name);
                      if (newName) renameChat(chat.id, newName);
                    }}
                    className="text-gray-500 hover:text-gray-700"
                  >
                    Rename
                  </button>
                  <button
                    onClick={() => deleteChat(chat.id)}
                    className="text-red-500 hover:text-red-700"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </li>
          ))}
        </ul>
      </nav>

      <div className="flex-1 p-8">
        <Routes>
          <Route
            path="/"
            element={
              <div className="text-center text-gray-700">
                <p className="mb-4">
                  Intelligent agent for working with notes and video lectures
                </p>
                <p>Please select a chat to begin</p>
              </div>
            }
          />
          <Route path="/chat/:chatId" element={<Chat chats={chats} setChats={setChats} />} />
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