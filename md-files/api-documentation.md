# KONSPECTO API Documentation

KONSPECTO is a platform that provides services for processing educational content, including video transcription, document search, and automated response generation.

## Base URL
```
http://localhost:8000/api/v1
```

## Endpoints

### Agent Service
Handles interaction with AI agent for content processing and explanation.

#### Send Query to Agent
```http
POST /agent/
```

**Request Body:**
```json
{
  "query": "Explain gradient descent and Fourier transform"
}
```

**Response:**
```json
{
  "response": "Detailed explanation in Russian language..."
}
```

### Search Service
Performs semantic search across indexed documents.

#### Search Documents
```http
POST /search/
```

**Request Body:**
```json
{
  "query": "neural networks architecture"
}
```

**Response:**
```json
{
  "results": [
    {
      "modified_at": "2024-02-20T10:00:00Z",
      "file_name": "deep_learning.pdf",
      "file_id": "abc123",
      "text": "Matching text fragment...",
      "score": 0.95,
      "start_char_idx": 0,
      "end_char_idx": 100
    }
  ]
}
```

### Video Processing Service
Processes YouTube videos and generates documents with extracted frames.

#### Convert YouTube Video to DOCX
```http
POST /video/youtube_to_docx
```

**Request Body:**
```json
{
  "youtube_url": "https://www.youtube.com/watch?v=example"
}
```

**Response:**
```json
{
  "docx_key": "docx:123e4567-e89b-12d3-a456-426614174000"
}
```

#### Get Generated DOCX File
```http
GET /video/video/{docx_key}
```

**Response:**
- Content-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document
- Content-Disposition: attachment; filename="{docx_key}.docx"

### Audio Transcription Service
Transcribes audio files to text.

#### Transcribe Audio
```http
POST /transcribe/
```

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Body: file (audio file, MP3 or WAV format)

**Response:**
```json
{
  "transcription": "Transcribed text in Russian..."
}
```

## Error Responses

The API uses standard HTTP status codes:

- `200` - Success
- `400` - Bad Request
- `404` - Not Found
- `422` - Validation Error
- `500` - Internal Server Error

Error Response Format:
```json
{
  "detail": "Error description message"
}
```

## Notes

- All text responses are in Russian language
- Audio files must be in MP3 or WAV format
- YouTube URLs must be valid and publicly accessible
- Document search uses semantic similarity for better results
- Generated DOCX files are available for 24 hours after creation