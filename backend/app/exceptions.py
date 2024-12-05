from fastapi import HTTPException
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR


class InvalidYouTubeURLException(HTTPException):
    def __init__(self, detail: str = "Недопустимый URL YouTube."):
        super().__init__(status_code=HTTP_400_BAD_REQUEST, detail=detail)


class VideoProcessingError(HTTPException):
    def __init__(self, detail: str = "Не удалось обработать видео."):
        super().__init__(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)
