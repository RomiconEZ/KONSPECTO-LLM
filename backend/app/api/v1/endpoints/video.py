# KONSPECTO/backend/app/api/v1/endpoints/video.py

from fastapi import APIRouter, HTTPException, Depends, Response
from pydantic import BaseModel, HttpUrl
import logging

from agent.tools.video_processor import youtube_to_docx
from ....services.redis_service import RedisService
from ....exceptions import InvalidYouTubeURLException, VideoProcessingError  # Добавляем импорт

router = APIRouter()
logger = logging.getLogger("app.api.v1.endpoints.video")


class VideoRequest(BaseModel):
    """
    Модель запроса для конвертации видео.
    """
    youtube_url: HttpUrl


class VideoResponse(BaseModel):
    """
    Модель ответа после конвертации видео.
    """
    docx_key: str


class VideoService:
    """
    Сервисный класс для обработки конвертации видео в DOCX.
    """

    def __init__(self, redis_service: RedisService):
        """
        Инициализация VideoService с заданным RedisService.
        """
        self.redis_service = redis_service

    async def convert_youtube_video(self, youtube_url: str) -> str:
        """
        Конвертирует YouTube видео в DOCX документ и сохраняет в Redis.

        :param youtube_url: Ссылка на YouTube видео.
        :return: Уникальный ключ для доступа к DOCX файлу в Redis.
        """
        logger.info(f"Starting conversion for video: {youtube_url}")
        docx_key = await youtube_to_docx(youtube_url, self.redis_service)
        logger.info(f"DOCX документ сохранён в Redis с ключом: {docx_key}")
        return docx_key

    async def get_docx_file(self, docx_key: str) -> bytes:
        """
        Получает DOCX файл из Redis по заданному ключу.

        :param docx_key: Уникальный ключ для DOCX файла.
        :return: Байтовое содержимое DOCX файла.
        """
        logger.info(f"Fetching DOCX document with key: {docx_key}")
        file_data = await self.redis_service.get_file(docx_key)
        if not file_data:
            logger.warning(f"DOCX документ с ключом '{docx_key}' не найден.")
            raise HTTPException(status_code=404, detail="Документ не найден.")
        return file_data


def get_redis_service():
    """
    Зависимость для получения экземпляра RedisService.

    :return: Экземпляр RedisService.
    """
    return RedisService()


@router.post("/youtube_to_docx", response_model=VideoResponse)
async def convert_youtube_to_docx(
    request: VideoRequest,
    redis_service: RedisService = Depends(get_redis_service)
):
    """
    Конвертирует YouTube видео в DOCX документ с изображениями каждые 5 секунд и сохраняет в Redis.
    Возвращает уникальный ключ для доступа к документу.

    :param request: Объект запроса VideoRequest с полем youtube_url.
    :param redis_service: Экземпляр RedisService.
    :return: Объект ответа VideoResponse с полем docx_key.
    """
    service = VideoService(redis_service)
    try:
        youtube_url_str = str(request.youtube_url)
        docx_key = await service.convert_youtube_video(youtube_url_str)
        return VideoResponse(docx_key=docx_key)
    except InvalidYouTubeURLException as e:
        logger.error(f"Invalid input: {e.detail}")
        raise e
    except VideoProcessingError as e:
        logger.exception("Ошибка при конвертации видео.")
        raise e
    except Exception:
        logger.exception("Неизвестная ошибка при конвертации видео.")
        raise HTTPException(status_code=500, detail="Неизвестная ошибка при обработке видео.")


@router.get("/video/{docx_key}")
async def get_docx_file(
    docx_key: str,
    redis_service: RedisService = Depends(get_redis_service)
):
    """
    Получает DOCX документ из Redis по уникальному ключу и возвращает его пользователю.

    :param docx_key: Уникальный ключ для DOCX файла.
    :param redis_service: Экземпляр RedisService.
    :return: Ответ с содержимым DOCX файла для скачивания.
    """
    service = VideoService(redis_service)
    try:
        file_data = await service.get_docx_file(docx_key)

        # Установка заголовков для скачивания файла
        headers = {
            "Content-Disposition": f'attachment; filename="{docx_key}.docx"',
            "Content-Type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        }

        return Response(
            content=file_data,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers=headers
        )
    except HTTPException as he:
        raise he
    except Exception:
        logger.exception("Ошибка при получении DOCX документа.")
        raise HTTPException(status_code=500, detail="Не удалось получить документ.")