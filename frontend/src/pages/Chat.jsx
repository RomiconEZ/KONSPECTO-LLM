// src/pages/Chat.jsx
import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import dayjs from 'dayjs';
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
    if (loading) return; // Предотвращаем множественные отправки
    setLoading(true);
    setError(null);

    if (!chat) {
      setError('Чат не найден.');
      setLoading(false);
      return;
    }

    const timestamp = new Date().toISOString();

    // Создаем сообщение от пользователя
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
        throw new Error(`Ошибка: ${res.status} ${res.statusText}`);
      }

      const data = await res.json();

      // Проверяем формат ответа API
      if (!data.results || !Array.isArray(data.results)) {
        throw new Error('Неверный формат ответа от API.');
      }

      // Создаем сообщения от агента
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
      setError('Произошла ошибка при обработке вашего запроса.');
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
      <div className="flex items-center justify-center h-full text-center text-dark-700">
        <div>
          <h2 className="text-2xl font-bold mb-4">Чат не найден</h2>
          <p>Пожалуйста, выберите действительный чат.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full relative">
      <div className="flex-1 overflow-y-auto p-4 bg-dark-800 rounded shadow mb-16">
        {chat.messages.map((message, index) => (
          <div
            key={index}
            className={`mb-4 flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-md p-3 rounded-lg ${
                message.sender === 'user'
                  ? 'bg-orange-500 text-white'
                  : 'bg-dark-600 text-dark-50'
              }`}
            >
              {/* Отображение названия файла, если есть */}
              {message.file_name && (
                <div className="font-semibold mb-1">{message.file_name}</div>
              )}
              <pre className="whitespace-pre-wrap">{message.text}</pre>
              {/* Кнопка для просмотра документа */}
              {message.sender === 'agent' && message.file_id && (
                <button
                  onClick={() => handleOpenDocViewer(message.file_id)}
                  className="mt-2 bg-orange-600 text-white px-3 py-1 rounded hover:bg-orange-700 transition duration-200"
                >
                  Просмотреть документ
                </button>
              )}
              {/* Время отправки сообщения */}
              <div className="text-xs text-dark-400 mt-1 text-right">
                {dayjs(message.timestamp).format('HH:mm DD.MM.YYYY')}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Строка ввода текста */}
      <div className="fixed bottom-0 left-0 w-full bg-dark-800 p-4 border-t border-dark-600">
        <form onSubmit={handleQuerySubmit} className="flex items-center">
          <input
            type="text"
            value={query}
            onChange={handleQueryChange}
            className="border border-dark-600 p-2 flex-1 rounded bg-dark-700 text-white placeholder-dark-400 focus:outline-none focus:ring-2 focus:ring-orange-500"
            placeholder="Введите ваш запрос"
            required
          />
          <button
            type="submit"
            className="bg-orange-500 text-dark-900 px-4 py-2 rounded hover:bg-orange-600 transition duration-200 ml-2 disabled:opacity-50 disabled:cursor-not-allowed"
            disabled={loading}
          >
            {loading ? 'Отправка...' : 'Отправить'}
          </button>
        </form>
        {/* Отображение сообщения об ошибке */}
        {error && (
          <div className="mt-4 text-red-500 text-center">
            {error}
          </div>
        )}
      </div>

      {/* Просмотр документа Google */}
      {docFileId && (
        <GoogleDocViewer fileId={docFileId} onClose={handleCloseDocViewer} />
      )}
    </div>
  );
}

export default Chat;