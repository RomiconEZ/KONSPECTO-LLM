// KONSPECTO/frontend/src/pages/Chat.jsx
import React, { useState, useEffect, useRef, useCallback, useContext } from 'react';
import { useParams } from 'react-router-dom';
import dayjs from 'dayjs';
import PropTypes from 'prop-types';
import { FaMicrophone, FaCircle } from 'react-icons/fa';
import { getConfig } from '../config';
import { containsYouTubeLink } from '../utils/youtubeUtils';
import DownloadButton from '../components/DownloadButton';
import ErrorMessage from '../components/ErrorMessage';
import { ChatContext } from '../context/ChatContext';

function Chat({ onOpenDoc }) {
  const { API_URL } = getConfig();
  const { chats, setChats } = useContext(ChatContext);
  const { chatId } = useParams();
  console.log('ChatId:', chatId);
  console.log('All chats:', chats);

  const chat = chats.find((c) => c.id === chatId);
  console.log('Current chat:', chat);

  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [recordError, setRecordError] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const recordingStartTimeRef = useRef(null);
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  const triggerRecordError = useCallback((message = 'Произошла ошибка при записи.') => {
    setErrorMessage(message);
    setRecordError(true);
    setTimeout(() => {
      setErrorMessage('');
      setRecordError(false);
    }, 4000);
  }, []);

  const handleQueryChange = useCallback((e) => {
    setQuery(e.target.value);
  }, []);

  const handleQuerySubmit = useCallback(
    async (e) => {
      e.preventDefault();

      if (loading || !query.trim() || !chat || isTranscribing) return;

      const hasYouTube = containsYouTubeLink(query);
      setLoading(true);

      const timestamp = new Date().toISOString();
      const userMessage = {
        sender: 'user',
        text: query,
        timestamp,
      };
      const updatedChat = { ...chat, messages: [...chat.messages, userMessage] };
      setChats((prevChats) => prevChats.map((c) => (c.id === chat.id ? updatedChat : c)));
      setQuery('');

      try {
        if (hasYouTube) {
          // Если есть YouTube ссылка, отправляем только запрос агенту
          const agentResponse = await fetch(`${API_URL}/agent/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query }),
          });

          if (!agentResponse.ok) {
            throw new Error(`Ошибка агента: ${agentResponse.status} ${agentResponse.statusText}`);
          }

          const agentData = await agentResponse.json();
          const agentText = agentData.response;

          if (agentText.includes('docx:')) {
            const docxMatch = agentText.match(/docx:[a-zA-Z0-9-]+/);
            if (!docxMatch) {
              throw new Error('Некорректный формат ответа агента');
            }
            const docxKey = docxMatch[0]; // Сохраняем префикс 'docx:'

            try {
              const videoResponse = await fetch(`${API_URL}/video/video/${docxKey}`);

              if (!videoResponse.ok) {
                if (videoResponse.status === 404) {
                  throw new Error('Файл не найден.');
                }
                throw new Error(
                  `Ошибка при получении файла: ${videoResponse.status} ${videoResponse.statusText}`
                );
              }

              const fileBlob = await videoResponse.blob();
              const fileUrl = URL.createObjectURL(fileBlob);
              const fileName = `${docxKey}.docx`;

              const fileMessage = {
                sender: 'agent',
                text: 'Документ готов для скачивания.',
                file_url: fileUrl,
                file_name: fileName,
                timestamp: new Date().toISOString(),
              };

              const finalChat = {
                ...updatedChat,
                messages: [...updatedChat.messages, fileMessage],
              };
              setChats((prevChats) => prevChats.map((c) => (c.id === chat.id ? finalChat : c)));
            } catch (err) {
              console.error('File Fetch Error:', err);
              const errorAgentMessage = {
                sender: 'agent',
                text: 'Файл не найден.',
                timestamp: new Date().toISOString(),
              };
              const finalChat = {
                ...updatedChat,
                messages: [...updatedChat.messages, errorAgentMessage],
              };
              setChats((prevChats) => prevChats.map((c) => (c.id === chat.id ? finalChat : c)));
            }
          } else {
            const agentMessage = {
              sender: 'agent',
              text: agentText,
              timestamp: new Date().toISOString(),
            };
            const finalChat = {
              ...updatedChat,
              messages: [...updatedChat.messages, agentMessage],
            };
            setChats((prevChats) => prevChats.map((c) => (c.id === chat.id ? finalChat : c)));
          }
        } else {
          // Если нет YouTube ссылки, сначала отправляем запрос на поиск
          const searchResponse = await fetch(`${API_URL}/search`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query }),
          });

          if (!searchResponse.ok) {
            throw new Error(`Ошибка поиска: ${searchResponse.status} ${searchResponse.statusText}`);
          }

          const searchData = await searchResponse.json();

          if (!searchData.results || !Array.isArray(searchData.results)) {
            throw new Error('Неверный формат ответа поиска.');
          }

          const searchMessages = searchData.results.map((item, index) => ({
            sender: 'search',
            text: item.text,
            file_id: item.file_id,
            file_name: item.file_name,
            score: item.score,
            start_char_idx: item.start_char_idx,
            end_char_idx: item.end_char_idx,
            timestamp: new Date().toISOString(),
            id: `search-${index}-${Date.now()}`,
          }));

          const updatedChatWithSearch = {
            ...updatedChat,
            messages: [...updatedChat.messages, ...searchMessages],
          };
          setChats((prevChats) => prevChats.map((c) => (c.id === chat.id ? updatedChatWithSearch : c)));
          scrollToBottom();

          // Теперь отправляем запрос агенту
          const agentResponse = await fetch(`${API_URL}/agent/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query }),
          });

          if (!agentResponse.ok) {
            throw new Error(`Ошибка агента: ${agentResponse.status} ${agentResponse.statusText}`);
          }

          const agentData = await agentResponse.json();

          const agentMessage = {
            sender: 'agent',
            text: agentData.response,
            timestamp: new Date().toISOString(),
          };

          const finalChat = {
            ...updatedChatWithSearch,
            messages: [...updatedChatWithSearch.messages, agentMessage],
          };
          setChats((prevChats) => prevChats.map((c) => (c.id === chat.id ? finalChat : c)));
        }
      } catch (err) {
        console.error('Processing Error:', err);
        triggerRecordError(err.message || 'Произошла неизвестная ошибка.');
      } finally {
        setLoading(false);
        scrollToBottom();
      }
    },
    [
      loading,
      query,
      chat,
      setChats,
      API_URL,
      isTranscribing,
      triggerRecordError,
      scrollToBottom,
    ]
  );

  const handleKeyDown = useCallback(
    (e) => {
      if (e.key === 'Enter' && !e.ctrlKey && !e.shiftKey) {
        e.preventDefault();
        handleQuerySubmit(e);
      } else if (e.key === 'Enter' && (e.ctrlKey || e.shiftKey)) {
        e.preventDefault();
        const { selectionStart, selectionEnd } = e.target;
        const newValue = `${query.slice(0, selectionStart)}\n${query.slice(selectionEnd)}`;
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

  const startRecording = useCallback(async () => {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      triggerRecordError('В вашем браузере не поддерживается запись аудио.');
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
        const duration = (recordingEndTime - recordingStartTimeRef.current) / 1000;

        if (duration < 0.2) {
          console.warn('Запись слишком короткая, не отправляем на сервер.');
          triggerRecordError('Запись слишком короткая.');
          return;
        }

        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/mp3' });
        const formData = new FormData();
        formData.append('file', audioBlob, 'recording.mp3');

        try {
          setLoading(true);
          setIsTranscribing(true);
          const response = await fetch(`${API_URL}/transcribe`, {
            method: 'POST',
            body: formData,
          });

          if (!response.ok) {
            throw new Error('Ошибка при транскрипции аудио.');
          }

          const data = await response.json();

          setQuery((prev) => {
            const newQuery = prev + data.transcription;
            setTimeout(() => {
              if (textareaRef.current) {
                textareaRef.current.selectionStart = textareaRef.current.selectionEnd = newQuery.length;
                textareaRef.current.focus();
              }
            }, 0);
            return newQuery;
          });
          scrollToBottom();
        } catch (err) {
          console.error('Transcription Error:', err);
          triggerRecordError('Ошибка при транскрипции аудио.');
        } finally {
          setLoading(false);
          setIsTranscribing(false);
        }
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (err) {
      console.error('Recording Error:', err);
      triggerRecordError('Не удалось начать запись.');
    }
  }, [API_URL, triggerRecordError, scrollToBottom]);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current.stream.getTracks().forEach((track) => track.stop());
      setIsRecording(false);
    }
  }, [isRecording]);

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
    return (
      <div className="flex items-center justify-center h-full text-center">
        <div className="text-gray-400">
          <h2 className="text-2xl font-bold mb-4">Чат не найден</h2>
          <p>Пожалуйста, выберите существующий чат или создайте новый.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      {errorMessage && <ErrorMessage message={errorMessage} />}

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
                message.sender === 'user' ? 'bg-blue-500 text-gray-50' : 'bg-dark-700 text-gray-50'
              } break-words text-lg`}
            >
              {message.file_name && <div className="font-semibold mb-1">{message.file_name}</div>}
              <pre className="whitespace-pre-wrap">{message.text}</pre>

              {message.file_url && (
                <DownloadButton fileUrl={message.file_url} fileName={message.file_name} />
              )}

              {(message.sender === 'agent' || message.sender === 'search') && message.file_id && (
                <button
                  onClick={() => onOpenDoc(message.file_id)}
                  className="mt-2 bg-blue-600 text-gray-50 px-3 py-1 rounded hover:bg-blue-700 transition duration-200"
                >
                  Просмотреть документ
                </button>
              )}
              <div
                className={`text-xs mt-1 text-right ${
                  message.sender === 'user' ? 'text-gray-200' : 'text-gray-100'
                }`}
              >
                {dayjs(message.timestamp).format('HH:mm DD.MM.YYYY')}
              </div>
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      <div className="mt-4 flex items-center">
        <form onSubmit={handleQuerySubmit} className="flex-1 flex items-center">
          <div className="flex-1 relative">
            <textarea
              ref={textareaRef}
              value={query}
              onChange={handleQueryChange}
              onKeyDown={handleKeyDown}
              className={`textarea-custom ${recordError ? 'border-2 border-red-500' : ''}`}
              placeholder="Введите ваш запрос"
              rows={1}
              maxLength={500}
              disabled={isTranscribing || loading}
            />
          </div>
          <button
            type="button"
            onMouseDown={!isTranscribing ? startRecording : null}
            onMouseUp={!isTranscribing ? stopRecording : null}
            onTouchStart={!isTranscribing ? startRecording : null}
            onTouchEnd={!isTranscribing ? stopRecording : null}
            className={`ml-2 p-2 rounded-full flex items-center justify-center transition duration-200 ${
              isRecording ? 'bg-red-500 animate-pulse border-2 border-red-600' : 'bg-blue-500'
            } ${
              recordError ? 'border-2 border-red-500' : ''
            } text-gray-50 hover:bg-red-600 focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed`}
            aria-label={isRecording ? 'Запись...' : 'Начать запись'}
            disabled={isTranscribing || loading}
          >
            {isRecording ? <FaCircle className="text-white animate-pulse" /> : <FaMicrophone />}
          </button>
          <button
            type="submit"
            className="ml-2 bg-blue-500 text-gray-50 px-4 py-2 rounded hover:bg-blue-600 transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed text-lg flex-shrink-0 h-12"
            disabled={loading || isTranscribing}
          >
            {loading ? 'Отправка...' : 'Отправить'}
          </button>
        </form>
      </div>
    </div>
  );
}

Chat.propTypes = {
  onOpenDoc: PropTypes.func.isRequired,
};

export default Chat;