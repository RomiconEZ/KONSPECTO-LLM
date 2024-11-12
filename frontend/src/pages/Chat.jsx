// src/pages/Chat.jsx
import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import dayjs from 'dayjs'; // Убедитесь, что dayjs установлен и импортирован правильно
import GoogleDocViewer from '../components/GoogleDocViewer';

function Chat({ chats, setChats }) {
  const { chatId } = useParams();
  const chat = chats.find(c => c.id === parseInt(chatId, 10));
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [docFileId, setDocFileId] = useState('');

  const handleQueryChange = (e) => {
    setQuery(e.target.value);
  };

  const handleQuerySubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    if (!chat) {
      setError('Chat not found.');
      setLoading(false);
      return;
    }

    const timestamp = new Date().toISOString();

    // Создание сообщения от пользователя
    const userMessage = {
      sender: 'user',
      text: query,
      timestamp
    };
    const updatedChat = {
      ...chat,
      messages: [...chat.messages, userMessage],
    };
    setChats(chats.map(c => c.id === chat.id ? updatedChat : c));
    setQuery('');

    try {
      const res = await fetch('http://localhost:8000/v1/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }),
      });

      if (!res.ok) {
        throw new Error(`Error: ${res.status} ${res.statusText}`);
      }

      const data = await res.json();

      // Проверяем, что data.results существует и является массивом
      if (!data.results || !Array.isArray(data.results)) {
        throw new Error('Invalid response format from API.');
      }

      // Создаем сообщения от агента для каждого SearchItem
      const agentMessages = data.results.map(item => ({
        sender: 'agent',
        text: item.text,
        file_id: item.file_id,
        file_name: item.file_name,
        timestamp: new Date().toISOString(),
      }));

      const updatedChatWithResponse = {
        ...updatedChat,
        messages: [...updatedChat.messages, ...agentMessages],
      };
      setChats(chats.map(c => c.id === chat.id ? updatedChatWithResponse : c));
    } catch (err) {
      console.error(err);
      setError('An error occurred while processing your request.');
    } finally {
      setLoading(false);
    }
  };

  const handleOpenDocViewer = (fileId) => {
    setDocFileId(fileId);
  };

  const handleCloseDocViewer = () => {
    setDocFileId('');
  };

  if (!chat) {
    return (
      <div className="text-center text-gray-700">
        <h2 className="text-2xl font-bold mb-4">Chat not found</h2>
        <p>Please select a valid chat.</p>
      </div>
    );
  }

  return (
    <div className="flex h-full relative">
      <div className="flex-1 overflow-y-auto p-4 bg-white rounded shadow mb-4">
        {chat.messages.map((message, index) => (
          <div key={index} className={`mb-4 ${message.sender === 'user' ? 'text-right' : 'text-left'}`}>
            <div className={`inline-block p-2 rounded ${message.sender === 'user' ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-900'}`}>
              {/* Отображение названия файла, если оно есть */}
              {message.file_name && (
                <div className="font-semibold mb-1">{message.file_name}</div>
              )}
              <pre className="whitespace-pre-wrap">{message.text}</pre>
              {/* Отображение кнопки для просмотра документа */}
              {message.sender === 'agent' && message.file_id && (
                <button
                  onClick={() => handleOpenDocViewer(message.file_id)}
                  className="mt-2 bg-green-500 text-white px-2 py-1 rounded hover:bg-green-600 transition duration-200"
                >
                  View Document
                </button>
              )}
              {/* Отображение времени отправки сообщения */}
              <div className="text-xs text-gray-500 mt-1">
                {dayjs(message.timestamp).format('HH:mm DD.MM.YYYY')}
              </div>
            </div>
          </div>
        ))}
      </div>
      <div className="fixed bottom-0 left-0 w-full bg-white p-4 border-t border-gray-300">
        <form onSubmit={handleQuerySubmit} className="flex items-center">
          <input
            type="text"
            value={query}
            onChange={handleQueryChange}
            className="border border-gray-300 p-2 flex-1 rounded"
            placeholder="Enter your query"
            required
          />
          <button
            type="submit"
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition duration-200 ml-2"
            disabled={loading}
          >
            {loading ? 'Sending...' : 'Send'}
          </button>
        </form>
        {error && (
          <div className="mt-4 text-red-500 text-center">
            {error}
          </div>
        )}
      </div>
      {docFileId && (
        <GoogleDocViewer fileId={docFileId} onClose={handleCloseDocViewer} />
      )}
    </div>
  );
}

export default Chat;