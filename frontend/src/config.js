// frontend/src/config.js
export const getConfig = () => {
  console.log('Environment Mode:', import.meta.env.MODE);
  console.log('VITE_API_URL:', import.meta.env.VITE_API_URL);

  if (import.meta.env.MODE === 'test') {
    return {
      API_URL: 'http://localhost:3000/api',
    };
  }

  return {
    API_URL: import.meta.env.VITE_API_URL || '/api',
  };
};
