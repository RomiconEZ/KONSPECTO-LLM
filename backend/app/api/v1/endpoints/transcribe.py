# backend/app/api/v1/endpoints/transcribe.py
from fastapi import APIRouter, UploadFile, File, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
import aiofiles
import tempfile
import os
import logging
from faster_whisper import WhisperModel

router = APIRouter()
logger = logging.getLogger("app.api.v1.endpoints.transcribe")

def get_whisper_model(request: Request) -> WhisperModel:
    return request.app.state.whisper_model

@router.post("/")
async def transcribe_audio(
    file: UploadFile = File(...),
    model: WhisperModel = Depends(get_whisper_model)  # Using Dependency
):
    """
    Endpoint to transcribe an uploaded audio file using WhisperModel.
    Supports MP3 and WAV formats.
    """
    file_location = None
    try:
        # Validate content type
        if not file.content_type.startswith("audio/"):
            logger.warning(f"Invalid content type: {file.content_type}")
            raise HTTPException(status_code=400, detail="Invalid file type. Audio file required.")

        # Validate file extension
        _, file_ext = os.path.splitext(file.filename)
        if file_ext.lower() not in ['.mp3', '.wav']:
            logger.warning(f"Unsupported file extension: {file_ext}")
            raise HTTPException(status_code=400, detail="Unsupported file format. Use MP3 or WAV.")

        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
            file_location = tmp.name
            async with aiofiles.open(file_location, 'wb') as out_file:
                content = await file.read()  # Asynchronous read
                await out_file.write(content)

        # Check if file is empty
        if os.path.getsize(file_location) == 0:
            logger.error("Uploaded file is empty.")
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")

        # Log file size
        file_size = os.path.getsize(file_location)
        logger.debug(f"Uploaded file size: {file_size} bytes")

        # Transcribe audio using WhisperModel
        logger.debug(f"Starting transcription for file: {file_location}")
        segments, info = model.transcribe(
            file_location,
            task = "transcribe",
            without_timestamps = True,
            beam_size=1,
            language="ru",
            condition_on_previous_text=False
        )

        # Combine segment texts
        transcription = " ".join([segment.text for segment in segments])
        logger.info(f"Transcription completed successfully for file: {file_location}")

        return JSONResponse(content={"transcription": transcription})

    except HTTPException as he:
        raise he  # Propagate HTTPException directly

    except Exception as e:
        logger.exception("Failed to transcribe audio.")
        raise HTTPException(status_code=500, detail="Failed to transcribe audio.")

    finally:
        # Clean up temporary files
        if file_location and os.path.exists(file_location):
            os.remove(file_location)
            logger.debug(f"Removed temporary file: {file_location}")