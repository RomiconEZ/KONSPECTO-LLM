// frontend/tailwind.config.js
export default {
  content: [
    './index.html',
    './src/**/*.{js,jsx,ts,tsx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        mist: {
          50: '#f8f7fa',
          100: '#f0eef4',
          200: '#e1dde9',
          300: '#cec7db',
          400: '#b7adc9',
          500: '#9f93b8',
          600: '#8779a7',
          700: '#6f6290',
          800: '#574c74',
          900: '#403858',
        },
        dusk: {
          50: '#f6f6f8',
          100: '#ececf1',
          200: '#d9d9e3',
          300: '#c2c1d1',
          400: '#a9a7bc',
          500: '#908da7',
          600: '#777392',
          700: '#5f5b77',
          800: '#48455c',
          900: '#322f41',
        },
        sage: {
          50: '#f5f7f6',
          100: '#ebefed',
          200: '#d7dfdb',
          300: '#bfcbc5',
          400: '#a5b4ad',
          500: '#8b9c94',
          600: '#71847c',
          700: '#596a63',
          800: '#42504a',
          900: '#2b3631',
        },
      },
      boxShadow: {
        'soft': '0 2px 15px rgba(159, 147, 184, 0.2)',
        'soft-lg': '0 4px 25px rgba(159, 147, 184, 0.25)',
        'inner-soft': 'inset 0 2px 15px rgba(159, 147, 184, 0.15)',
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'soft-pattern': 'url("data:image/svg+xml,%3Csvg width=\'60\' height=\'60\' viewBox=\'0 0 60 60\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cpath d=\'M30 0l25.98 15v30L30 60 4.02 45V15z\' fill-opacity=\'0.03\' fill=\'%239f93b8\'/%3E%3C/svg%3E")',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'background-shine': 'background-shine 2s linear infinite',
      },
      keyframes: {
        'background-shine': {
          from: {
            backgroundPosition: '0 0'
          },
          to: {
            backgroundPosition: '-200% 0'
          }
        }
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
};