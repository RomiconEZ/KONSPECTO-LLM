# KONSPECTO/backend/agent/tools/video_processor.py

import os
import tempfile
import logging
from fastapi import HTTPException
import re

from pytubefix import YouTube
from pytubefix.cli import on_progress
import cv2
from PIL import Image
from docx import Document
from docx.shared import Inches
from urllib.error import HTTPError
import numpy as np
from skimage.metrics import structural_similarity as ssim

logger = logging.getLogger("app.agent.tools.video_processor")


def sanitize_filename(filename: str) -> str:
    """
    Очищает имя файла, заменяя пробелы на подчеркивания и удаляя нежелательные символы.

    :param filename: Исходное имя файла.
    :return: Очищенное имя файла.
    """
    # Заменяем пробелы и другие нежелательные символы на подчеркивания
    filename = re.sub(r'\s+', '_', filename)
    # Удаляем любые символы, кроме букв, цифр, подчеркиваний, дефисов и точек
    filename = re.sub(r'[^\w\-_\.]', '', filename)
    return filename


def are_images_different_ssim(img_path1: str, img_path2: str, threshold: float = 0.98) -> bool:
    """
    Сравнивает два изображения с использованием SSIM и определяет, отличаются ли они более чем на заданный порог.

    :param img_path1: Путь к первому изображению.
    :param img_path2: Путь ко второму изображению.
    :param threshold: Пороговое значение SSIM (по умолчанию 0.98).
                      Чем ниже значение, тем более отличными считаются изображения.
    :return: True, если SSIM ниже порога, иначе False.
    """
    try:
        img1 = Image.open(img_path1).convert("L")  # Преобразование в градации серого
        img2 = Image.open(img_path2).convert("L")

        # Приведение изображений к одному размеру
        if img1.size != img2.size:
            img2 = img2.resize(img1.size)

        arr1 = np.array(img1)
        arr2 = np.array(img2)

        # Вычисление SSIM
        similarity, _ = ssim(arr1, arr2, full=True)
        logger.debug(f"SSIM similarity between '{img_path1}' and '{img_path2}': {similarity}")

        return similarity < threshold

    except Exception as e:
        logger.exception(f"Ошибка при сравнении изображений с использованием SSIM: {e}")
        # В случае ошибки считаем изображения различными
        return True


def youtube_to_docx(youtube_url: str) -> str:
    """
    Загружает YouTube видео, извлекает изображения каждые 5 секунд,
    удаляет схожие изображения и создает DOCX-документ с уникальными изображениями.

    :param youtube_url: Ссылка на YouTube видео.
    :return: Путь до созданного DOCX файла.
    """
    try:
        logger.info(f"Начало обработки видео по ссылке: {youtube_url}")

        # Создание временной директории для хранения видео и кадров
        with tempfile.TemporaryDirectory() as temp_dir:
            logger.debug(f"Создана временная директория: {temp_dir}")

            # Загрузка видео с YouTube
            yt = YouTube(youtube_url, on_progress_callback=on_progress)
            try:
                stream = yt.streams.get_highest_resolution()
                if not stream:
                    logger.error("Не удалось найти подходящий поток для загрузки.")
                    raise ValueError("Не удалось найти подходящий поток для загрузки.")

                video_path = os.path.join(temp_dir, "video.mp4")
                logger.info(f"Загрузка видео: {yt.title}")
                stream.download(output_path=temp_dir, filename="video.mp4")
                logger.info(f"Видео загружено по пути: {video_path}")
            except HTTPError as http_err:
                logger.error(f"HTTP ошибка при загрузке видео: {http_err}")
                raise HTTPException(
                    status_code=403,
                    detail="Доступ к видео запрещен (HTTP 403). Проверьте ссылку или ограничения видео."
                )
            except Exception as e:
                logger.exception(f"Не удалось загрузить видео: {e}")
                raise HTTPException(status_code=500, detail="Не удалось загрузить видео.")

            # Извлечение изображений каждые 5 секунд
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            if fps == 0:
                logger.error("Не удалось определить FPS видео.")
                raise ValueError("Не удалось определить FPS видео.")

            frame_interval = int(fps * 5)  # Интервал кадров для каждых 5 секунд
            logger.debug(f"FPS видео: {fps}, интервал кадров: {frame_interval}")

            frame_count = 0
            extracted_images = []
            last_image_path = None

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                if frame_count % frame_interval == 0:
                    # Конвертация кадра из BGR (OpenCV) в RGB (Pillow)
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    img = Image.fromarray(frame_rgb)

                    img_path = os.path.join(temp_dir, f"frame_{frame_count}.png")
                    img.save(img_path)
                    logger.info(f"Извлечено изображение: {img_path}")

                    # Проверка на схожесть с последним сохраненным изображением
                    if last_image_path:
                        if are_images_different_ssim(last_image_path, img_path, threshold=0.98):
                            extracted_images.append(img_path)
                            last_image_path = img_path
                            logger.debug(f"Изображение {img_path} отличается более чем на 2% (SSIM < 0.98) от предыдущего. Сохранено.")
                        else:
                            logger.debug(f"Изображение {img_path} схоже с предыдущим (SSIM >= 0.98). Пропущено.")
                            os.remove(img_path)  # Удаляем схожее изображение
                    else:
                        extracted_images.append(img_path)
                        last_image_path = img_path
                        logger.debug(f"Первое изображение {img_path} сохранено.")

                frame_count += 1

            cap.release()
            logger.info(f"Всего извлечено изображений: {len(extracted_images)}")

            if not extracted_images:
                logger.warning("Не было извлечено ни одного изображения.")
                raise ValueError("Не было извлечено ни одного изображения.")

            # Создание DOCX документа непосредственно в /app/generated_docs
            output_dir = os.path.join(os.getcwd(), "generated_docs")
            os.makedirs(output_dir, exist_ok=True)

            # Очищаем и упрощаем название файла
            sanitized_title = sanitize_filename(yt.title)
            docx_filename = f"{sanitized_title}.docx"
            docx_path = os.path.join(output_dir, docx_filename)

            doc = Document()
            doc.add_heading(yt.title, 0)

            for img_path in extracted_images:
                doc.add_picture(img_path, width=Inches(6))

            # Сохранение DOCX файла напрямую в /app/generated_docs
            doc.save(docx_path)
            logger.info(f"DOCX документ создан по пути: {docx_path}")

            return docx_path

    except HTTPException as he:
        # Пропускаем HTTPException без изменения
        raise he
    except Exception as e:
        logger.exception(f"Ошибка при обработке видео: {e}")
        raise HTTPException(status_code=500, detail="Не удалось обработать видео.")