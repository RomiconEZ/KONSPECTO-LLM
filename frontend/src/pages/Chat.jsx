// frontend/src/pages/Chat.jsx

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import dayjs from 'dayjs';
import PropTypes from 'prop-types';

function Chat({ chats, setChats, onOpenDoc }) {
  const { chatId } = useParams();
  console.log('Navigated to chat ID:', chatId); // Логирование chatId
  const chat = chats.find((c) => c.id === Number(chatId));
  console.log('Found chat:', chat); // Логирование найденного чата

  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  const handleQueryChange = useCallback((e) => {
    setQuery(e.target.value);
  }, []);

  // Изменение здесь: добавление параметра event и вызов preventDefault()
  const handleQuerySubmit = useCallback(async (e) => {
    e.preventDefault(); // Предотвращение перезагрузки страницы

    if (loading || !query.trim() || !chat) return;

    setLoading(true);
    setError(null);

    const timestamp = new Date().toISOString();
    const userMessage = {
      sender: 'user',
      text: query,
      timestamp,
    };
    const updatedChat = { ...chat, messages: [...chat.messages, userMessage] };
    setChats((prevChats) =>
      prevChats.map((c) => (c.id === chat.id ? updatedChat : c)),
    );
    setQuery('');

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/v1/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query }),
      });

      if (!response.ok) {
        throw new Error(`Ошибка: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();

      if (!data.results || !Array.isArray(data.results)) {
        throw new Error('Неверный формат ответа от API.');
      }

      const agentMessages = data.results.map((item) => ({
        sender: 'agent',
        text: item.text,
        file_id: item.file_id,
        file_name: item.file_name,
        timestamp: new Date().toISOString(),
      }));

      const finalChat = {
        ...updatedChat,
        messages: [...updatedChat.messages, ...agentMessages],
      };

      setChats((prevChats) =>
        prevChats.map((c) => (c.id === chat.id ? finalChat : c)),
      );
      scrollToBottom();
    } catch (err) {
      console.error('API Error:', err);
      setError('Произошла ошибка при обработке вашего запроса.');
    } finally {
      setLoading(false);
    }
  }, [loading, query, chat, setChats, scrollToBottom]);

  const handleKeyDown = useCallback(
    (e) => {
      if (e.key === 'Enter' && !e.ctrlKey && !e.shiftKey) {
        e.preventDefault();
        handleQuerySubmit(e); // Передача события в функцию отправки
      } else if (e.key === 'Enter' && (e.ctrlKey || e.shiftKey)) {
        e.preventDefault();
        const { selectionStart, selectionEnd } = e.target;
        const newValue = query.slice(0, selectionStart) + '\n' + query.slice(selectionEnd);
        setQuery(newValue);
        setTimeout(() => {
          if (textareaRef.current) {
            textareaRef.current.selectionStart = textareaRef.current.selectionEnd = selectionStart + 1;
          }
        }, 0);
      }
    },
    [handleQuerySubmit, query],
  );

  useEffect(() => {
    scrollToBottom();
  }, [chat, scrollToBottom]);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 144)}px`;
    }
  }, [query]);

  if (!chat) {
    console.warn(`Чат с ID ${chatId} не найден.`);
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
    <div className="flex flex-col h-full">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 bg-dark-800 rounded shadow messages-container">
        {chat.messages.map((message, index) => (
          <div
            key={index}
            className={`mb-4 flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-1/2 p-3 rounded-lg ${
                message.sender === 'user' ? 'bg-orange-500 text-white' : 'bg-dark-600 text-dark-50'
              } break-words text-lg`}
            >
              {message.file_name && <div className="font-semibold mb-1">{message.file_name}</div>}
              <pre className="whitespace-pre-wrap">{message.text}</pre>
              {message.sender === 'agent' && message.file_id && (
                <button
                  onClick={() => onOpenDoc(message.file_id)}
                  className="mt-2 bg-orange-600 text-white px-3 py-1 rounded hover:bg-orange-700 transition duration-200"
                >
                  Просмотреть документ
                </button>
              )}
              <div
                className={`text-xs mt-1 text-right ${
                  message.sender === 'user' ? 'text-gray-900' : 'text-gray-100'
                }`}
              >
                {dayjs(message.timestamp).format('HH:mm DD.MM.YYYY')}
              </div>
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Field */}
      <div className="mt-4">
        <form onSubmit={handleQuerySubmit} className="flex items-end">
          <div className="flex-1 relative">
            <textarea
              ref={textareaRef}
              value={query}
              onChange={handleQueryChange}
              onKeyDown={handleKeyDown}
              className="textarea-custom"
              placeholder="Введите ваш запрос"
              rows={1}
              maxLength={500} // Опционально: ограничение ввода
            />
          </div>
          <button
            type="submit"
            className="ml-2 bg-orange-500 text-dark-900 px-3 py-2 rounded hover:bg-orange-600 transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed text-lg flex-shrink-0"
            disabled={loading}
          >
            {loading ? 'Отправка...' : 'Отправить'}
          </button>
        </form>
        {error && <div className="mt-4 text-red-500 text-center text-lg">{error}</div>}
      </div>
    </div>
  );
}

Chat.propTypes = {
  chats: PropTypes.array.isRequired,
  setChats: PropTypes.func.isRequired,
  onOpenDoc: PropTypes.func.isRequired,
};

export default Chat;