// frontend/src/components/DownloadButton.jsx
import React, { useEffect } from 'react';
import PropTypes from 'prop-types';

const DownloadButton = React.memo(({ fileUrl, fileName }) => {
  useEffect(() => {
    return () => {
      URL.revokeObjectURL(fileUrl);
    };
  }, [fileUrl]);

  const handleDownload = () => {
    const link = document.createElement('a');
    link.href = fileUrl;
    link.download = fileName;
    link.click();
  };

  return (
    <button
      onClick={handleDownload}
      className="btn-action mt-2 flex items-center gap-2"
      aria-label={`Скачать файл ${fileName}`}
    >
      <svg
        className="w-4 h-4"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
        />
      </svg>
      Скачать файл
    </button>
  );
});

DownloadButton.propTypes = {
  fileUrl: PropTypes.string.isRequired,
  fileName: PropTypes.string.isRequired,
};

export default DownloadButton;