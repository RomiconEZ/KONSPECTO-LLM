// src/components/GoogleDocViewer.jsx
import React from 'react';
import PropTypes from 'prop-types';

const GoogleDocViewer = ({ fileId, onClose }) => {
  if (!fileId) {
    return null; // Не отображаем ничего, если нет fileId
  }

  // Используем 'preview' для встроенного просмотра
  const embedUrl = `https://drive.google.com/file/d/${fileId}/preview`;
  const docLink = `https://drive.google.com/file/d/${fileId}/view?usp=sharing`;

  return (
    <>
      {/* Overlay */}
      <div className="google-doc-viewer-overlay" onClick={onClose}></div>

      {/* Viewer */}
      <div id="doc-viewer">
        <div className="google-doc-viewer-content">
          <button
            onClick={onClose}
            className="google-doc-viewer-close"
          >
            Close
          </button>
          <a
            href={docLink}
            target="_blank"
            rel="noopener noreferrer"
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition duration-200 m-4 inline-block"
          >
            Open Document in Google Drive
          </a>
          <iframe
            title="Google Document Viewer"
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