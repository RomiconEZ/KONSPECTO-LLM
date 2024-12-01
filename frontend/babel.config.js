// frontend/babel.config.js
module.exports = {
  presets: [
    ['@babel/preset-env', { targets: { node: 'current' } }],
    ['@babel/preset-react', { runtime: 'automatic' }],
  ],
  plugins: [
    'babel-plugin-transform-import-meta',
    'babel-plugin-transform-vite-meta-env',
  ],
};