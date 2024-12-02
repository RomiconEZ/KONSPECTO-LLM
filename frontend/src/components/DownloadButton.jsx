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
      className="mt-2 bg-green-500 text-gray-50 px-3 py-1 rounded hover:bg-green-600 transition duration-200"
      aria-label={`Скачать файл ${fileName}`}
    >
      Скачать файл
    </button>
  );
});

DownloadButton.propTypes = {
  fileUrl: PropTypes.string.isRequired,
  fileName: PropTypes.string.isRequired,
};

export default DownloadButton;
