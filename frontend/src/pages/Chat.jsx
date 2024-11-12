// src/pages/Chat.jsx

import React, { useState, useEffect, useRef } from 'react';
import { useParams } from 'react-router-dom';
import dayjs from 'dayjs';
import PropTypes from 'prop-types';

function Chat({ chats, setChats, onOpenDoc }) {
  const { chatId } = useParams();
  const chat = chats.find((c) => c.id === parseInt(chatId, 10));
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  const handleQueryChange = (e) => {
    setQuery(e.target.value);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.ctrlKey && !e.shiftKey) {
      // Submit the form
      e.preventDefault();
      handleQuerySubmit(e);
    } else if (e.key === 'Enter' && (e.ctrlKey || e.shiftKey)) {
      // Insert newline
      e.preventDefault();
      const { selectionStart, selectionEnd } = e.target;
      const newValue =
        query.substring(0, selectionStart) + '\n' + query.substring(selectionEnd);
      setQuery(newValue);
      // Move cursor to the new position
      setTimeout(() => {
        if (textareaRef.current) {
          textareaRef.current.selectionStart = textareaRef.current.selectionEnd =
            selectionStart + 1;
        }
      }, 0);
    }
  };

  const handleQuerySubmit = async (e) => {
    e.preventDefault();
    if (loading) return; // Prevent multiple submissions
    if (!query.trim()) return; // Do not submit empty messages
    setLoading(true);
    setError(null);

    if (!chat) {
      setError('Чат не найден.');
      setLoading(false);
      return;
    }

    const timestamp = new Date().toISOString();

    // Create user message
    const userMessage = {
      sender: 'user',
      text: query,
      timestamp,
    };
    const updatedChat = {
      ...chat,
      messages: [...chat.messages, userMessage],
    };
    setChats(chats.map((c) => (c.id === chat.id ? updatedChat : c)));
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

      // Validate API response format
      if (!data.results || !Array.isArray(data.results)) {
        throw new Error('Неверный формат ответа от API.');
      }

      // Create agent messages
      const agentMessages = data.results.map((item) => ({
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
      setChats(chats.map((c) => (c.id === chat.id ? updatedChatWithResponse : c)));

      // Scroll to bottom after new messages
      scrollToBottom();
    } catch (err) {
      console.error(err);
      setError('Произошла ошибка при обработке вашего запроса.');
    } finally {
      setLoading(false);
    }
  };

  const scrollToBottom = () => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [chat]);

  useEffect(() => {
    if (textareaRef.current) {
      // Reset height
      textareaRef.current.style.height = 'auto';
      // Set height (max 6 lines)
      textareaRef.current.style.height = `${Math.min(
        textareaRef.current.scrollHeight,
        6 * 24
      )}px`; // Assuming line-height is 24px
    }
  }, [query]);

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
    <div className="flex flex-col h-full">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 bg-dark-800 rounded shadow messages-container">
        {chat.messages.map((message, index) => (
          <div
            key={index}
            className={`mb-4 flex ${
              message.sender === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            <div
              className={`max-w-1/2 p-3 rounded-lg ${
                message.sender === 'user'
                  ? 'bg-orange-500 text-white'
                  : 'bg-dark-600 text-dark-50'
              } break-words text-lg`}
            >
              {/* Display file name if present */}
              {message.file_name && (
                <div className="font-semibold mb-1">{message.file_name}</div>
              )}
              <pre className="whitespace-pre-wrap">{message.text}</pre>
              {/* Button to view document */}
              {message.sender === 'agent' && message.file_id && (
                <button
                  onClick={() => onOpenDoc(message.file_id)}
                  className="mt-2 bg-orange-600 text-white px-3 py-1 rounded hover:bg-orange-700 transition duration-200"
                >
                  Просмотреть документ
                </button>
              )}
              {/* Message timestamp */}
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
              style={{ maxHeight: '144px' }} // 6 lines * approx line-height 24px
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
        {/* Display error message */}
        {error && (
          <div className="mt-4 text-red-500 text-center text-lg">{error}</div>
        )}
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