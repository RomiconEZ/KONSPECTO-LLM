// src/components/GoogleDocViewer.jsx
import React from 'react';
import PropTypes from 'prop-types';

const GoogleDocViewer = ({ fileId, onClose }) => {
  if (!fileId) {
    return null; // Не отображать ничего, если нет fileId
  }

  // Формирование URL для встраивания и просмотра документа
  const embedUrl = `https://drive.google.com/file/d/${fileId}/preview`;

  return (
    <div className="flex flex-col h-full w-full">
      {/* Заголовок с кнопкой закрытия */}
      <div className="flex justify-between items-center p-4 bg-dark-700 border-b border-dark-600">
        <h2 className="text-lg font-semibold text-white">Просмотр документа</h2>
        <button
          onClick={onClose}
          className="bg-orange-500 text-dark-900 px-3 py-1 rounded hover:bg-orange-600 transition duration-200"
          aria-label="Закрыть просмотр документа"
        >
          Закрыть
        </button>
      </div>

      {/* Iframe для предварительного просмотра документа */}
      <iframe
        title="Просмотр документа Google"
        src={embedUrl}
        className="flex-1 border-none w-full h-full text-lg"
      />
    </div>
  );
};

GoogleDocViewer.propTypes = {
  fileId: PropTypes.string.isRequired,
  onClose: PropTypes.func.isRequired,
};

export default GoogleDocViewer;