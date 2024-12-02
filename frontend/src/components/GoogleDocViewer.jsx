// frontend/src/components/GoogleDocViewer.jsx
import React from 'react';
import PropTypes from 'prop-types';

const GoogleDocViewer = React.memo(({ fileId, onClose }) => {
  if (!fileId) {
    return null;
  }

  const embedUrl = `https://drive.google.com/file/d/${fileId}/preview`;

  return (
    <div className="flex flex-col h-full w-full relative">
      <div className="flex justify-between items-center p-4 glass-effect border-b border-mist-700/20">
        <h2 className="text-lg font-semibold text-mist-100">Просмотр документа</h2>
        <button
          onClick={onClose}
          className="btn-action"
          aria-label="Закрыть просмотр документа"
        >
          Закрыть
        </button>
      </div>

      <iframe
        title="Просмотр документа Google"
        src={embedUrl}
        className="flex-1 border-none w-full h-full bg-white"
        loading="lazy"
      />

      {/* Добавляем визуальный индикатор для ползунка */}
      <div className="absolute left-0 top-1/2 -translate-y-1/2 h-40 w-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
        <div className="h-full w-full rounded-full bg-mist-500/20"></div>
      </div>
    </div>
  );
});

GoogleDocViewer.propTypes = {
  fileId: PropTypes.string.isRequired,
  onClose: PropTypes.func.isRequired,
};

export default GoogleDocViewer;