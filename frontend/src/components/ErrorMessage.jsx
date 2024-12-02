// frontend/src/components/ErrorMessage.jsx
import React from 'react';
import PropTypes from 'prop-types';
import { FaExclamationTriangle } from 'react-icons/fa';

const ErrorMessage = React.memo(({ message }) => (
  <div className="absolute top-4 left-1/2 transform -translate-x-1/2 glass-effect bg-rose-500/20 text-rose-200 px-6 py-3 rounded-lg shadow-soft-lg flex items-center space-x-3 z-50 border border-rose-500/20">
    <FaExclamationTriangle className="text-xl" />
    <span className="text-sm font-medium">{message}</span>
  </div>
));

ErrorMessage.propTypes = {
  message: PropTypes.string.isRequired,
};

export default ErrorMessage;