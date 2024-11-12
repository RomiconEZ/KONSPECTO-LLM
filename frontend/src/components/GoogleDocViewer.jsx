// src/components/GoogleDocViewer.jsx
import React from 'react';
import PropTypes from 'prop-types';

const GoogleDocViewer = ({ fileId, onClose }) => {
  if (!fileId) {
    return null; // Не отображаем ничего, если нет fileId
  }

  // Конструируем URL для встраивания и просмотра документа
  const embedUrl = `https://drive.google.com/file/d/${fileId}/preview`;
  const docLink = `https://drive.google.com/file/d/${fileId}/view?usp=sharing`;

  return (
    <>
      {/* Overlay */}
      <div
        className="google-doc-viewer-overlay"
        onClick={onClose}
        aria-label="Закрыть просмотр документа"
      ></div>

      {/* Viewer */}
      <div id="doc-viewer" className="transition-transform duration-300 ease-in-out">
        <div className="google-doc-viewer-content">
          <button
            onClick={onClose}
            className="google-doc-viewer-close focus:outline-none"
            aria-label="Закрыть"
          >
            Закрыть
          </button>
          <a
            href={docLink}
            target="_blank"
            rel="noopener noreferrer"
            className="bg-orange-500 text-white px-4 py-2 rounded hover:bg-orange-600 transition duration-200 m-4 inline-block"
          >
            Открыть документ в Google Drive
          </a>
          <iframe
            title="Просмотр документа Google"
            src={embedUrl}
            className="google-doc-viewer-iframe"
          />
        </div>
      </div>
    </>
  );
};

GoogleDocViewer.propTypes = {
  fileId: PropTypes.string.isRequired,
  onClose: PropTypes.func.isRequired,
};

export default GoogleDocViewer;
