# KONSPECTO/backend/agent/tools/video_processor.py

import logging
import os
import shutil
import tempfile
import uuid
from abc import ABC, abstractmethod
from io import BytesIO
from typing import Optional
from urllib.error import HTTPError

import cv2
import numpy as np
from docx import Document
from docx.shared import Inches
from PIL import Image
from pytubefix import YouTube
from pytubefix.cli import on_progress
from pytubefix.exceptions import RegexMatchError
from skimage.metrics import structural_similarity as ssim

from app.exceptions import InvalidYouTubeURLException, VideoProcessingError
from app.services.redis_service import RedisService

logger = logging.getLogger("agent.tools.video_processor")


class ImageDifferenceChecker(ABC):
    """
    Абстрактный класс для проверки различий между двумя изображениями.
    """

    @abstractmethod
    def are_images_different(self, img_path1: str, img_path2: str) -> bool:
        """
        Определяет, отличаются ли два изображения.

        :param img_path1: Путь к первому изображению.
        :param img_path2: Путь ко второму изображению.
        :return: True, если изображения отличаются, иначе False.
        """
        pass


class SSIMImageDifferenceChecker(ImageDifferenceChecker):
    """
    Класс для проверки различий между изображениями с использованием SSIM.
    """

    SSIM_THRESHOLD = 0.98

    def are_images_different(self, img_path1: str, img_path2: str) -> bool:
        """
        Сравнивает два изображения с использованием SSIM и определяет,
        отличаются ли они более чем на заданный порог.

        :param img_path1: Путь к первому изображению.
        :param img_path2: Путь ко второму изображению.
        :return: True, если изображения отличаются, иначе False.
        """
        try:
            img1 = Image.open(img_path1).convert("L")
            img2 = Image.open(img_path2).convert("L")

            if img1.size != img2.size:
                img2 = img2.resize(img1.size)

            arr1 = np.array(img1)
            arr2 = np.array(img2)

            similarity = ssim(arr1, arr2)
            logger.debug(
                f"SSIM similarity between '{img_path1}' and '{img_path2}': {similarity}"
            )

            return similarity < self.SSIM_THRESHOLD

        except Exception as e:
            logger.exception(f"Error comparing images using SSIM: {e}")
            return True


class VideoToDocxConverter:
    """
    Класс, инкапсулирующий процесс конвертации видео YouTube в DOCX документ.
    """

    FRAME_INTERVAL_SECONDS: int = 5

    def __init__(
        self,
        youtube_url: str,
        redis_service: RedisService,
        difference_checker: ImageDifferenceChecker,
        expire_seconds: int,
    ):
        self.youtube_url: str = youtube_url
        self.redis_service: RedisService = redis_service
        self.difference_checker: ImageDifferenceChecker = difference_checker
        self.expire_seconds: int = expire_seconds
        self.temp_dir: Optional[str] = None
        self.video_path: Optional[str] = None
        self.extracted_images: list[str] = []
        self.unique_key: Optional[str] = None
        self.video_title: Optional[str] = None

    async def process(self) -> str:
        """
        Выполняет полный процесс конвертации видео и сохранения DOCX документа в Redis.

        :return: Уникальный ключ для доступа к DOCX файлу в Redis.
        """
        try:
            logger.info(f"Starting video processing for URL: {self.youtube_url}")
            await self.download_video()
            self.extract_images()
            docx_bytes = self.create_docx()
            await self.save_to_redis(docx_bytes)
            return self.unique_key
        except InvalidYouTubeURLException:
            raise
        except VideoProcessingError:
            raise
        except Exception as e:
            logger.exception(f"Video processing failed: {e}")
            raise VideoProcessingError()
        finally:
            self.cleanup()

    async def download_video(self):
        """
        Загрузка видео с YouTube во временную директорию.
        """
        self.temp_dir = tempfile.mkdtemp()
        logger.debug(f"Created temporary directory: {self.temp_dir}")

        try:
            yt = YouTube(self.youtube_url, on_progress_callback=on_progress)
            self.video_title = yt.title
            stream = yt.streams.get_highest_resolution()
            if not stream:
                logger.error(f"No suitable stream found for URL: {self.youtube_url}")
                raise VideoProcessingError(
                    "Не удалось найти подходящий поток для загрузки."
                )

            self.video_path = os.path.join(self.temp_dir, "video.mp4")
            logger.info(f"Downloading video: {self.video_title}")
            stream.download(output_path=self.temp_dir, filename="video.mp4")
            logger.info(f"Video downloaded to: {self.video_path}")

        except RegexMatchError:
            logger.error(f"Invalid YouTube URL: {self.youtube_url}")
            raise InvalidYouTubeURLException()
        except HTTPError as http_err:
            logger.error(f"HTTP error while downloading video: {http_err}")
            raise VideoProcessingError(
                "Доступ к видео запрещен (HTTP 403). Проверьте ссылку или ограничения видео."
            )
        except (InvalidYouTubeURLException, VideoProcessingError):
            raise
        except Exception as e:
            logger.exception(f"Failed to download video: {e}")
            raise VideoProcessingError("Не удалось загрузить видео.")

    def extract_images(self):
        """
        Извлечение изображений из видео каждые 5 секунд, удаление схожих изображений.
        """
        cap = cv2.VideoCapture(self.video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps == 0:
            logger.error(f"Failed to determine FPS for video: {self.video_path}")
            raise VideoProcessingError("Не удалось определить FPS видео.")

        frame_interval = int(fps * self.FRAME_INTERVAL_SECONDS)
        logger.debug(f"Video FPS: {fps}, frame interval: {frame_interval}")

        frame_count = 0
        last_image_path = None

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_count % frame_interval == 0:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)

                img_path = os.path.join(self.temp_dir, f"frame_{frame_count}.png")
                img.save(img_path)
                logger.info(f"Extracted image: {img_path}")

                if last_image_path:
                    if self.difference_checker.are_images_different(
                        last_image_path, img_path
                    ):
                        self.extracted_images.append(img_path)
                        last_image_path = img_path
                        logger.debug(f"Image {img_path} differs from previous, saved.")
                    else:
                        logger.debug(
                            f"Image {img_path} is similar to previous, skipped."
                        )
                        os.remove(img_path)
                else:
                    self.extracted_images.append(img_path)
                    last_image_path = img_path
                    logger.debug(f"First image {img_path} saved.")

            frame_count += 1

        cap.release()
        logger.info(f"Total images extracted: {len(self.extracted_images)}")

        if not self.extracted_images:
            logger.warning(f"No images extracted from video: {self.video_path}")
            raise VideoProcessingError("Не было извлечено ни одного изображения.")

    def create_docx(self) -> bytes:
        """
        Создание DOCX документа с извлеченными изображениями.

        :return: Байтовое представление DOCX документа.
        """
        doc = Document()
        doc.add_heading(self.video_title, 0)

        for img_path in self.extracted_images:
            doc.add_picture(img_path, width=Inches(6))

        doc_io = BytesIO()
        doc.save(doc_io)
        doc_bytes = doc_io.getvalue()
        logger.info(f"DOCX document created with {len(self.extracted_images)} images.")
        return doc_bytes

    async def save_to_redis(self, doc_bytes: bytes):
        """
        Сохранение DOCX документа в Redis с уникальным ключом.

        :param doc_bytes: Байтовое представление DOCX документа.
        """
        self.unique_key = f"docx:{uuid.uuid4()}"

        await self.redis_service.set_file(
            self.unique_key, doc_bytes, expire=self.expire_seconds
        )

        logger.info(f"DOCX document saved to Redis with key: {self.unique_key}")

    def cleanup(self):
        """
        Очистка временных файлов и директорий.
        """
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            logger.debug(f"Removed temporary directory: {self.temp_dir}")


async def youtube_to_docx(
    youtube_url: str,
    redis_service: RedisService,
    difference_checker: Optional[ImageDifferenceChecker] = None,
    expire_seconds: int = 86400,
) -> str:
    """
    Обертка для конвертации YouTube видео в DOCX документ и сохранения его в Redis.

    :param youtube_url: Ссылка на YouTube видео.
    :param redis_service: Экземпляр RedisService для взаимодействия с Redis.
    :param difference_checker: Объект для определения различий между изображениями.
    :param expire_seconds: Время в секундах, после которого документ истечет в Redis.
    :return: Уникальный ключ для доступа к DOCX файлу в Redis.
    """
    converter = VideoToDocxConverter(
        youtube_url=youtube_url,
        redis_service=redis_service,
        difference_checker=difference_checker or SSIMImageDifferenceChecker(),
        expire_seconds=expire_seconds,
    )
    return await converter.process()
