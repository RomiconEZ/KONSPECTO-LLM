# KONSPECTO/backend/app/api/v1/endpoints/video.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
import os
import logging

from agent.tools.video_processor import youtube_to_docx  # Обновленный импорт

router = APIRouter()
logger = logging.getLogger("app.api.v1.endpoints.video")

class VideoRequest(BaseModel):
    youtube_url: HttpUrl

class VideoResponse(BaseModel):
    docx_path: str

@router.post("/youtube_to_docx", response_model=VideoResponse, tags=["video"])
async def convert_youtube_to_docx(request: VideoRequest):
    """
    Конвертирует YouTube видео в DOCX документ с изображениями каждые 5 секунд.
    """
    try:
        youtube_url_str = str(request.youtube_url)  # Преобразование в строку
        logger.info(f"Получен запрос на конвертацию видео: {youtube_url_str}")
        docx_path = youtube_to_docx(youtube_url_str)  # Передача строки
        absolute_path = os.path.abspath(docx_path)
        logger.info(f"DOCX документ создан: {absolute_path}")
        return VideoResponse(docx_path=absolute_path)
    except HTTPException as he:
        # Пропускаем HTTPException без изменения
        raise he
    except Exception as e:
        logger.exception(f"Ошибка при конвертации видео: {e}")
        raise HTTPException(status_code=500, detail="Не удалось обработать видео.")