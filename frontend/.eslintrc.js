// frontend/.eslintrc.js
module.exports = {
  env: {
    browser: true,
    es2023: true,
    node: true,
    jest: true,
  },
  extends: [
    'airbnb',
    'airbnb/hooks',
    'plugin:react/recommended',
    'plugin:jsx-a11y/recommended',
    'plugin:import/errors',
    'plugin:import/warnings',
    'plugin:import/react',
    'plugin:prettier/recommended',
  ],
  parserOptions: {
    ecmaVersion: 2023,
    sourceType: 'module',
    ecmaFeatures: {
      jsx: true,
    },
  },
  plugins: ['react', 'react-hooks', 'prettier', 'import', 'jsx-a11y'],
  rules: {
    'prettier/prettier': ['error'],
    'react/react-in-jsx-scope': 'off',
    'react/prop-types': 'off', // Consider using TypeScript for type checking
    'react/jsx-props-no-spreading': ['error', {
      custom: 'ignore',
      exceptions: ['Component']
    }],
    'react-hooks/rules-of-hooks': 'error',
    'react-hooks/exhaustive-deps': 'warn',
    'no-console': ['warn', { allow: ['warn', 'error'] }],
    'import/prefer-default-export': 'off',
    'import/no-extraneous-dependencies': [
      'error',
      { devDependencies: ['**/*.test.js', '**/*.test.jsx', '**/*.spec.js', '**/*.spec.jsx', '**/jest.setup.js'] },
    ],
    'import/extensions': [
      'error',
      'ignorePackages',
      {
        js: 'never',
        jsx: 'never',
        ts: 'never',
        tsx: 'never',
      },
    ],
    'jsx-a11y/anchor-is-valid': [
      'error',
      {
        components: ['Link'],
        specialLink: ['to'],
        aspects: ['invalidHref', 'preferButton'],
      },
    ],
  },
  settings: {
    react: {
      version: 'detect',
    },
    'import/resolver': {
      node: {
        extensions: ['.js', '.jsx'],
      },
      alias: {
        map: [['@', './src']],
        extensions: ['.js', '.jsx'],
      },
    },
  },
  overrides: [
    {
      files: ['**/*.test.js', '**/*.test.jsx', '**/*.spec.js', '**/*.spec.jsx', '**/jest.setup.js'],
      env: {
        jest: true,
      },
    },
  ],
};