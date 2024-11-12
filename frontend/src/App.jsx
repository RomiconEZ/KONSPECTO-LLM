// src/App.jsx

import React, { useState, useEffect } from 'react';
import { Routes, Route, Link, useNavigate } from 'react-router-dom';
import { FaChevronLeft, FaChevronRight, FaEdit, FaTrash } from 'react-icons/fa';
import Chat from './pages/Chat';
import GoogleDocViewer from './components/GoogleDocViewer';
import { ResizableBox } from 'react-resizable';
import 'react-resizable/css/styles.css';

function App() {
  const [chats, setChats] = useState([]);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [docFileId, setDocFileId] = useState('');
  const [docViewerWidth, setDocViewerWidth] = useState(400); // Initial width in pixels
  const [windowHeight, setWindowHeight] = useState(window.innerHeight);
  const navigate = useNavigate();

  useEffect(() => {
    const handleResize = () => {
      setWindowHeight(window.innerHeight);
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const addChat = () => {
    const newChat = { id: Date.now(), name: `Чат ${chats.length + 1}`, messages: [] };
    setChats([...chats, newChat]);
    navigate(`/chat/${newChat.id}`);
  };

  const deleteChat = (chatId) => {
    setChats(chats.filter(chat => chat.id !== chatId));
    navigate('/');
  };

  const renameChat = (chatId, newName) => {
    setChats(chats.map(chat => chat.id === chatId ? { ...chat, name: newName } : chat));
  };

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  const handleOpenDocViewer = (fileId) => {
    setDocFileId(fileId);
  };

  const handleCloseDocViewer = () => {
    setDocFileId('');
  };

  // Handle resizing by updating the width state
  const handleResize = (event, { size }) => {
    setDocViewerWidth(size.width);
  };

  return (
    <div className="flex h-screen bg-dark-900 text-dark-50 overflow-hidden">
      {/* Sidebar */}
      <nav
        className={`bg-dark-800 shadow-lg p-4 flex flex-col transition-all duration-300 ease-in-out ${
          isSidebarOpen ? 'w-64' : 'w-16'
        }`}
      >
        {/* Toggle Sidebar Button */}
        <button
          onClick={toggleSidebar}
          className="mb-4 text-orange-400 focus:outline-none"
          aria-label={isSidebarOpen ? 'Скрыть меню' : 'Показать меню'}
        >
          {isSidebarOpen ? <FaChevronLeft /> : <FaChevronRight />}
        </button>
        {isSidebarOpen && (
          <>
            <h1 className="text-2xl font-bold text-orange-400 mb-4">KONSPECTO</h1>
            <button
              onClick={addChat}
              className="bg-orange-500 text-dark-900 px-4 py-2 rounded hover:bg-orange-600 transition duration-200 mb-4"
            >
              Добавить чат
            </button>
            <ul className="flex-1 space-y-4 overflow-y-auto">
              {chats.map(chat => (
                <li key={chat.id} className="flex justify-between items-center">
                  <Link
                    to={`/chat/${chat.id}`}
                    className="text-orange-300 hover:text-orange-400 transition duration-200 font-medium flex-1 truncate"
                  >
                    {chat.name}
                  </Link>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => {
                        const newName = prompt('Введите новое название чата:', chat.name);
                        if (newName) renameChat(chat.id, newName);
                      }}
                      className="text-orange-300 hover:text-orange-400 focus:outline-none"
                      aria-label="Изменить название чата"
                      title="Изменить название чата"
                    >
                      <FaEdit />
                    </button>
                    <button
                      onClick={() => deleteChat(chat.id)}
                      className="text-red-500 hover:text-red-600 focus:outline-none"
                      aria-label="Удалить чат"
                      title="Удалить чат"
                    >
                      <FaTrash />
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          </>
        )}
      </nav>

      {/* Main Content Area (Chat and Document Viewer) */}
      <div className="flex-1 flex overflow-hidden">
        {/* Chat Area */}
        <main className="flex-1 p-4 bg-dark-700 flex flex-col overflow-hidden">
          <Routes>
            <Route
              path="/"
              element={
                <div className="flex items-center justify-center h-full text-center">
                  <div className="text-orange-300">
                    <p className="mb-4 text-xl">
                      Интеллектуальный агент для работы с заметками и видео лекциями
                    </p>
                    <p>Пожалуйста, выберите чат для начала</p>
                  </div>
                </div>
              }
            />
            <Route
              path="/chat/:chatId"
              element={<Chat chats={chats} setChats={setChats} onOpenDoc={handleOpenDocViewer} />}
            />
            {/* Handle Non-Existent Routes */}
            <Route
              path="*"
              element={
                <div className="flex items-center justify-center h-full text-center">
                  <div className="text-red-500">
                    <h2 className="text-2xl font-bold mb-4">404 - Не найдено</h2>
                    <p>Страница, которую вы ищете, не существует.</p>
                  </div>
                </div>
              }
            />
          </Routes>
        </main>

        {/* Document Viewer Area */}
        {docFileId && (
          <ResizableBox
            width={docViewerWidth}
            height={windowHeight}
            minConstraints={[300, windowHeight]}
            maxConstraints={[window.innerWidth / 2, windowHeight]}
            axis="x"
            resizeHandles={['w']} // Resize from the west (left) side
            handle={
              <span
                className="react-resizable-handle react-resizable-handle-w"
                aria-label="Resize document viewer"
              />
            }
            onResize={handleResize}
            className="bg-dark-800 shadow-lg z-50 flex flex-col"
          >
            <GoogleDocViewer fileId={docFileId} onClose={handleCloseDocViewer} />
          </ResizableBox>
        )}
      </div>
    </div>
  );
}

export default App;