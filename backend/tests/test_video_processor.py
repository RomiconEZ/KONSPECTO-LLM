# tests/test_video_processor.py

from unittest.mock import AsyncMock, patch

import pytest

from fastapi import HTTPException

from agent.tools.video_processor import (
    InvalidYouTubeURLException,
    VideoProcessingError,
    youtube_to_docx,
)


@pytest.mark.asyncio
@patch("agent.tools.video_processor.VideoToDocxConverter", autospec=True)
async def test_youtube_to_docx_processing_error(mock_converter_class):
    """
    Test that VideoProcessingError is raised when VideoToDocxConverter.process encounters an error.
    """
    # Configure the mock instance
    mock_converter_instance = mock_converter_class.return_value
    mock_converter_instance.process = AsyncMock(side_effect=VideoProcessingError())

    # Define test inputs
    youtube_url = "https://www.youtube.com/watch?v=Mf_nGEPIsQ8"
    redis_service = AsyncMock()  # Use AsyncMock if redis_service methods are async

    # Execute the function and verify that VideoProcessingError is raised
    with pytest.raises(VideoProcessingError):
        await youtube_to_docx(youtube_url, redis_service)

    # Verify that VideoToDocxConverter was instantiated with the correct arguments
    mock_converter_class.assert_called_once_with(
        youtube_url=youtube_url,
        redis_service=redis_service,
        difference_checker=None,
        expire_seconds=86400,
    )

    # Verify that the 'process' method was awaited exactly once
    mock_converter_instance.process.assert_awaited_once()


@pytest.mark.asyncio
@patch("agent.tools.video_processor.VideoToDocxConverter", autospec=True)
async def test_youtube_to_docx_invalid_url(mock_converter_class):
    """
    Test that InvalidYouTubeURLException is raised when an invalid YouTube URL is provided.
    """
    # Configure the mock instance
    mock_converter_instance = mock_converter_class.return_value
    mock_converter_instance.process = AsyncMock(side_effect=InvalidYouTubeURLException())

    # Define test inputs
    youtube_url = "invalid_url"
    redis_service = AsyncMock()  # Use AsyncMock if redis_service methods are async

    # Execute the function and verify that InvalidYouTubeURLException is raised
    with pytest.raises(InvalidYouTubeURLException):
        await youtube_to_docx(youtube_url, redis_service)

    # Verify that VideoToDocxConverter was instantiated with the correct arguments
    mock_converter_class.assert_called_once_with(
        youtube_url=youtube_url,
        redis_service=redis_service,
        difference_checker=None,
        expire_seconds=86400,
    )

    # Verify that the 'process' method was awaited exactly once
    mock_converter_instance.process.assert_awaited_once()
