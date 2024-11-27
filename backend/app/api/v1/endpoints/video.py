# backend/app/api/v1/endpoints/video.py

from fastapi import APIRouter, HTTPException, Depends, Response
from pydantic import BaseModel, HttpUrl
import os
import logging
from typing import Optional

from agent.tools.video_processor import youtube_to_docx

from ....services.redis_service import RedisService

router = APIRouter()
logger = logging.getLogger("app.api.v1.endpoints.video")


class VideoRequest(BaseModel):
    youtube_url: HttpUrl


class VideoResponse(BaseModel):
    docx_key: str


@router.post("/youtube_to_docx", response_model=VideoResponse, tags=["video"])
async def convert_youtube_to_docx(
    request: VideoRequest,
    redis_service: RedisService = Depends(lambda: RedisService())
):
    """
    Конвертирует YouTube видео в DOCX документ с изображениями каждые 5 секунд и сохраняет в Redis.
    Возвращает уникальный ключ для доступа к документу.
    """
    try:
        youtube_url_str = str(request.youtube_url)
        logger.info(f"Получен запрос на конвертацию видео: {youtube_url_str}")
        docx_key = await youtube_to_docx(youtube_url_str, redis_service)
        logger.info(f"DOCX документ сохранен в Redis с ключом: {docx_key}")
        return VideoResponse(docx_key=docx_key)
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.exception(f"Ошибка при конвертации видео: {e}")
        raise HTTPException(status_code=500, detail="Не удалось обработать видео.")


@router.get("/video/{docx_key}", response_model=None, tags=["video"])
async def get_docx_file(
    docx_key: str,
    redis_service: RedisService = Depends(lambda: RedisService())
):
    """
    Получает DOCX документ из Redis по уникальному ключу и возвращает его пользователю.
    """
    try:
        logger.info(f"Запрос на получение DOCX документа с ключом: {docx_key}")
        file_data = await redis_service.get_file(docx_key)
        if not file_data:
            logger.warning(f"DOCX документ с ключом '{docx_key}' не найден.")
            raise HTTPException(status_code=404, detail="Документ не найден.")

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
    except Exception as e:
        logger.exception(f"Ошибка при получении DOCX документа: {e}")
        raise HTTPException(status_code=500, detail="Не удалось получить документ.")