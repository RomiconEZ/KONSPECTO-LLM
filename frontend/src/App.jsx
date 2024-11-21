// frontend/src/App.jsx
import React, { useState, useCallback, useEffect } from 'react';
import { Routes, Route, useNavigate } from 'react-router-dom';
import Chat from './pages/Chat';
import GoogleDocViewer from './components/GoogleDocViewer';
import { ResizableBox } from 'react-resizable';
import 'react-resizable/css/styles.css';
import Sidebar from './components/Sidebar';

function App() {
  // Загрузка чатов из localStorage при инициализации
  const [chats, setChats] = useState(() => {
    const storedChats = localStorage.getItem('chats');
    const parsedChats = storedChats ? JSON.parse(storedChats) : [];
    console.log('Loaded chats from localStorage:', parsedChats);
    return parsedChats;
  });

  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [docFileId, setDocFileId] = useState('');
  const [docViewerWidth, setDocViewerWidth] = useState(400);
  const navigate = useNavigate();

  // Сохранение чатов в localStorage при их изменении
  useEffect(() => {
    console.log('Saving chats to localStorage:', chats);
    localStorage.setItem('chats', JSON.stringify(chats));
  }, [chats]);

  const addChat = useCallback(() => {
    const newChat = { id: Date.now(), name: `Чат ${chats.length + 1}`, messages: [] };
    console.log('Adding new chat:', newChat);
    setChats((prevChats) => [...prevChats, newChat]);
    navigate(`/chat/${newChat.id}`);
  }, [chats.length, navigate]);

  const deleteChat = useCallback(
    (chatId) => {
      console.log(`Deleting chat with ID: ${chatId}`);
      setChats((prevChats) => prevChats.filter((chat) => chat.id !== chatId));
      navigate('/');
    },
    [navigate],
  );

  const renameChat = useCallback(
    (chatId, newName) => {
      console.log(`Renaming chat ID ${chatId} to ${newName}`);
      setChats((prevChats) =>
        prevChats.map((chat) =>
          chat.id === chatId ? { ...chat, name: newName } : chat,
        ),
      );
    },
    [],
  );

  const toggleSidebar = useCallback(() => {
    setIsSidebarOpen((prev) => !prev);
  }, []);

  const handleOpenDocViewer = useCallback((fileId) => {
    console.log(`Opening document viewer for file ID: ${fileId}`);
    setDocFileId(fileId);
  }, []);

  const handleCloseDocViewer = useCallback(() => {
    console.log('Closing document viewer.');
    setDocFileId('');
  }, []);

  const handleResize = useCallback((event, { size }) => {
    console.log(`Resizing document viewer to width: ${size.width}`);
    setDocViewerWidth(size.width);
  }, []);

  return (
    <div className="flex h-screen bg-dark-900 text-dark-50 overflow-hidden">
      {/* Sidebar */}
      <Sidebar
        isOpen={isSidebarOpen}
        toggleSidebar={toggleSidebar}
        chats={chats}
        addChat={addChat}
        deleteChat={deleteChat}
        renameChat={renameChat}
      />

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
            height={document.body.clientHeight}
            minConstraints={[300, 300]}
            maxConstraints={[window.innerWidth / 2, window.innerHeight]}
            axis="x"
            resizeHandles={['w']}
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