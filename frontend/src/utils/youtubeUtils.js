// frontend/src/utils/youtubeUtils.js

/**
 * Проверяет, содержит ли строка ссылку на YouTube.
 * @param {string} text - Текст для проверки.
 * @returns {boolean} - Возвращает true, если ссылка на YouTube найдена.
 */
export const containsYouTubeLink = (text) => {
  return text.includes('https://www.youtube.com');
};