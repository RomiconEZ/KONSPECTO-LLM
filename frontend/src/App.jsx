import React, { useState, useCallback } from 'react';
import { Routes, Route, useNavigate } from 'react-router-dom';
import Chat from './pages/Chat';
import GoogleDocViewer from './components/GoogleDocViewer';
import { ResizableBox } from 'react-resizable';
import 'react-resizable/css/styles.css';
import Sidebar from './components/Sidebar';
import { ChatProvider } from './context/ChatContext'; // Removed .jsx extension

function App() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [docFileId, setDocFileId] = useState('');
  const [docViewerWidth, setDocViewerWidth] = useState(400);
  const navigate = useNavigate();

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
    <ChatProvider>
      <div className="flex h-screen bg-dark-900 text-gray-50 overflow-hidden">
        {/* Sidebar */}
        <Sidebar isOpen={isSidebarOpen} toggleSidebar={toggleSidebar} />

        {/* Main Content Area (Chat and Document Viewer) */}
        <div className="flex-1 flex overflow-hidden">
          {/* Chat Area */}
          <main className="flex-1 p-4 bg-dark-700 flex flex-col overflow-hidden">
            <Routes>
              <Route
                path="/"
                element={
                  <div className="flex items-center justify-center h-full text-center">
                    <div className="text-blue-200">
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
                element={<Chat onOpenDoc={handleOpenDocViewer} />}
              />
              {/* Handle non-existing routes */}
              <Route
                path="*"
                element={
                  <div className="flex items-center justify-center h-full text-center">
                    <div className="text-red-400">
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
              className="bg-dark-800 shadow-lg z-50 flex flex-col transition-all duration-300 ease-in-out"
            >
              <GoogleDocViewer fileId={docFileId} onClose={handleCloseDocViewer} />
            </ResizableBox>
          )}
        </div>
      </div>
    </ChatProvider>
  );
}

export default App;