// frontend/src/pages/Chat.jsx
import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import dayjs from 'dayjs';
import PropTypes from 'prop-types';
import { FaMicrophone, FaMicrophoneSlash, FaCircle } from 'react-icons/fa'; // Добавлен FaCircle для анимации записи

function Chat({ chats, setChats, onOpenDoc }) {
  const { chatId } = useParams();
  console.log('Navigated to chat ID:', chatId); // Debugging
  const chat = chats.find((c) => c.id === Number(chatId));
  console.log('Found chat:', chat); // Debugging

  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false); // Recording state
  const [isTranscribing, setIsTranscribing] = useState(false); // Transcription state
  const [recordError, setRecordError] = useState(false); // Recording error state

  const mediaRecorderRef = useRef(null); // MediaRecorder reference
  const audioChunksRef = useRef([]); // Store audio chunks
  const recordingStartTimeRef = useRef(null); // Recording start time

  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  const handleQueryChange = useCallback((e) => {
    setQuery(e.target.value);
  }, []);

  const handleQuerySubmit = useCallback(async (e) => {
    e.preventDefault(); // Prevent page reload

    if (loading || !query.trim() || !chat || isTranscribing) return;

    setLoading(true);
    setIsTranscribing(true);

    const timestamp = new Date().toISOString();
    const userMessage = {
      sender: 'user',
      text: query,
      timestamp,
    };
    const updatedChat = { ...chat, messages: [...chat.messages, userMessage] };
    setChats((prevChats) =>
      prevChats.map((c) => (c.id === chat.id ? updatedChat : c))
    );
    setQuery('');

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/search`, {
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
        prevChats.map((c) => (c.id === chat.id ? finalChat : c))
      );
      scrollToBottom();
    } catch (err) {
      console.error('API Error:', err);
      // Здесь мы не устанавливаем setError, вместо этого показываем красную рамку
      triggerRecordError();
    } finally {
      setLoading(false);
      setIsTranscribing(false);
    }
  }, [loading, query, chat, setChats, scrollToBottom, isTranscribing]);

  const handleKeyDown = useCallback(
    (e) => {
      if (e.key === 'Enter' && !e.ctrlKey && !e.shiftKey) {
        e.preventDefault();
        handleQuerySubmit(e);
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
    [handleQuerySubmit, query]
  );

  // Recording Handlers
  const startRecording = useCallback(async () => {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      triggerRecordError();
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];
      recordingStartTimeRef.current = Date.now();

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const recordingEndTime = Date.now();
        const duration = (recordingEndTime - recordingStartTimeRef.current) / 1000; // in seconds

        if (duration < 0.2) {
          console.warn('Запись слишком короткая, не отправляем на сервер.');
          // Здесь можно добавить эффект для слишком короткой записи
          triggerRecordError();
          return;
        }

        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/mp3' });
        const formData = new FormData();
        formData.append('file', audioBlob, 'recording.mp3');

        // Отправка аудио файла на сервер
        try {
          setLoading(true);
          setIsTranscribing(true);
          const response = await fetch(`${import.meta.env.VITE_API_URL}/transcribe`, {
            method: 'POST',
            body: formData,
          });

          if (!response.ok) {
            throw new Error('Ошибка при транскрипции аудио.');
          }

          const data = await response.json();
          setQuery((prev) => prev + data.transcription);
          scrollToBottom();
        } catch (err) {
          console.error('Transcription Error:', err);
          triggerRecordError();
        } finally {
          setLoading(false);
          setIsTranscribing(false);
        }
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (err) {
      console.error('Recording Error:', err);
      triggerRecordError();
    }
  }, [scrollToBottom]);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current.stream.getTracks().forEach((track) => track.stop());
      setIsRecording(false);
    }
  }, [isRecording]);

  const triggerRecordError = useCallback(() => {
    setRecordError(true);
    setTimeout(() => {
      setRecordError(false);
    }, 2000); // Красная рамка исчезнет через 2 секунды
  }, []);

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
            className={`mb-4 flex ${
              message.sender === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            <div
              className={`max-w-1/2 p-3 rounded-lg ${
                message.sender === 'user'
                  ? 'bg-blue-500 text-gray-50'
                  : 'bg-dark-700 text-gray-50'
              } break-words text-lg`}
            >
              {message.file_name && (
                <div className="font-semibold mb-1">{message.file_name}</div>
              )}
              <pre className="whitespace-pre-wrap">{message.text}</pre>
              {message.sender === 'agent' && message.file_id && (
                <button
                  onClick={() => onOpenDoc(message.file_id)}
                  className="mt-2 bg-blue-600 text-gray-50 px-3 py-1 rounded hover:bg-blue-700 transition duration-200"
                >
                  Просмотреть документ
                </button>
              )}
              <div
                className={`text-xs mt-1 text-right ${
                  message.sender === 'user'
                    ? 'text-gray-200'
                    : 'text-gray-100'
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
      <div className="mt-4 flex items-center">
        <form onSubmit={handleQuerySubmit} className="flex-1 flex items-center">
          <div className="flex-1 relative">
            <textarea
              ref={textareaRef}
              value={query}
              onChange={handleQueryChange}
              onKeyDown={handleKeyDown}
              className="textarea-custom"
              placeholder="Введите ваш запрос"
              rows={1}
              maxLength={500} // Optional: Input limit
              disabled={isTranscribing} // Отключение при транскрипции
            />
          </div>
          {/* Microphone Button */}
          <button
            type="button"
            onMouseDown={!isTranscribing ? startRecording : null}
            onMouseUp={!isTranscribing ? stopRecording : null}
            onTouchStart={!isTranscribing ? startRecording : null}
            onTouchEnd={!isTranscribing ? stopRecording : null}
            className={`ml-2 p-2 rounded-full flex items-center justify-center transition duration-200 ${
              isRecording
                ? 'bg-red-500 animate-pulse border-2 border-red-600'
                : 'bg-blue-500'
            } ${
              recordError ? 'border-2 border-red-500' : ''
            } text-gray-50 hover:bg-red-600 focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed`}
            aria-label={isRecording ? 'Запись...' : 'Начать запись'}
            disabled={isTranscribing || loading} // Отключение при транскрипции или загрузке
          >
            {isRecording ? <FaCircle className="text-white animate-pulse" /> : <FaMicrophone />}
          </button>
          {/* Send Button */}
          <button
            type="submit"
            className="ml-2 bg-blue-500 text-gray-50 px-4 py-2 rounded hover:bg-blue-600 transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed text-lg flex-shrink-0 h-12"
            disabled={loading || isTranscribing}
          >
            {loading ? 'Отправка...' : 'Отправить'}
          </button>
        </form>
        {/* Удалено сообщение об ошибке */}
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