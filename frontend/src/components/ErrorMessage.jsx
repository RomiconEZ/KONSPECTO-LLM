// frontend/src/components/ErrorMessage.jsx
import React from 'react';
import PropTypes from 'prop-types';
import { FaExclamationTriangle } from 'react-icons/fa';

const ErrorMessage = React.memo(({ message }) => (
  <div className="absolute top-4 left-1/2 transform -translate-x-1/2 bg-red-500 text-gray-50 px-4 py-2 rounded shadow-lg flex items-center space-x-2 z-50">
    <FaExclamationTriangle className="text-xl" />
    <span>{message}</span>
  </div>
));

ErrorMessage.propTypes = {
  message: PropTypes.string.isRequired,
};

export default ErrorMessage;