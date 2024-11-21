// frontend/tailwind.config.js
export default {
  content: [
    './index.html',
    './src/**/*.{js,jsx,ts,tsx}',
  ],
  darkMode: 'class', // Enables dark mode
  theme: {
    extend: {
      colors: {
        dark: {
          50: '#f9fafb',
          100: '#f3f4f6',
          200: '#e5e7eb',
          300: '#d1d5db',
          400: '#9ca3af',
          500: '#6b7280',
          600: '#4b5563',
          700: '#374151',
          800: '#1f2937',
          900: '#111827',
        },
        orange: {
          50: '#fff7ed',
          100: '#ffedd5',
          200: '#fed7aa',
          300: '#fdba74',
          400: '#fb923c',
          500: '#f97316',
          600: '#ea580c',
          700: '#c2410c',
          800: '#9a3412',
          900: '#7c2d12',
        },
      },
      maxWidth: {
        '1/2': '50%',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
};