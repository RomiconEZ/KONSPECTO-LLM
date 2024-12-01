// frontend/jest.setup.js
import '@testing-library/jest-dom/extend-expect';

// Мокаем scrollIntoView
Element.prototype.scrollIntoView = jest.fn();

// Подавляем предупреждения React Router
const consoleWarn = console.warn;
beforeAll(() => {
  console.warn = (message, ...args) => {
    if (
      !message.includes('React Router Future Flag Warning') &&
      !message.includes('Relative route resolution within Splat routes is changing in v7')
    ) {
      consoleWarn(message, ...args);
    }
  };
});

// Мокаем localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  clear: jest.fn(),
};
global.localStorage = localStorageMock;

// Мокаем MediaDevices
global.navigator.mediaDevices = {
  getUserMedia: jest.fn().mockResolvedValue({
    getTracks: () => [{
      stop: jest.fn()
    }]
  })
};

afterAll(() => {
  console.warn = consoleWarn;
});