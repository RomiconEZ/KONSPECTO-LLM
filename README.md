# 🎓 KONSPECTO - LLM Agent for Note Management

## 📋 Project Description

KONSPECTO is an intelligent agent based on a local LLM model, offering the following capabilities:

🔍 **Search Through Notes**

- Semantic search across the notes database
- Generation of structured responses based on the retrieved information
- Ability to view original documents

🎥 **Video Processing**

- Extraction of keyframes from YouTube videos
- Creation of DOCX documents with images
- Filtering of similar frames

🎤 **Voice Input**

- Transcription of voice messages using Whisper
- Support for the Russian language
- Ability to combine voice and text input

## Presentation

[Presentation KONSPECTO](https://github.com/RomiconEZ/KONSPECTO-LLM/blob/develop/presentation/KONSPECTO_LLM_base.pdf)

## 🛠 Tech Stack

### Frontend

- ⚛️ React + Vite
- 🎨 TailwindCSS
- 🔄 React Router
- ✨ React Icons

### Backend

- 🚀 FastAPI
- 🤖 LangChain
- 🔍 LlamaIndex
- 📝 Whisper
- 🎥 OpenCV
- 🗄️ Redis Stack

## 📦 Installation

### Prerequisites

- Docker and Docker Compose
- Node.js 18+
- Python 3.11+
- Poetry
- pre-commit

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/RomiconEZ/KONSPECTO
cd KONSPECTO
```

### 2️⃣ Configure Settings

Create configuration files in the `backend/app/config/` directory:

**.env**

```env
FOLDER_ID=your_google_drive_folder_id
GOOGLE_SERVICE_ACCOUNT_KEY_PATH=config/service_account_key.json

TRANSCRIPTION_MODEL=whisper
WHISPER_MODEL_SIZE=large-v3

LLM_STUDIO_BASE_URL=http://localhost:1234/v1

EMBEDDING_MODEL_NAME="intfloat/multilingual-e5-large"
EMBEDDING_BATCH_SIZE=16
EMBEDDING_DIMENSION=1024
```

**service_account_key.json**

```json
{
  // Your Google service account credentials
  // Obtain them from the Google Cloud Console
}
```

### 3️⃣ Install Dependencies

Frontend:

```bash
cd frontend
npm install
```

Backend:

```bash
cd backend
poetry install
```

### 4️⃣ Set Up pre-commit Hooks

```bash
pre-commit install --install-hooks
pre-commit run --all-files
```

### 5️⃣ Run Tests

Frontend tests:

```bash
cd frontend
npm run test
```

Backend tests:

```bash
cd backend
bash tests/run_tests.sh
```

### 6️⃣ Launch the Application

```bash
docker compose up --build
```

The application will be available at the following addresses:

- Frontend: [http://localhost:80](http://localhost:80)
- Backend API: [http://localhost:8000](http://localhost:8000)
- Redis Stack: [http://localhost:8001](http://localhost:8001)

## 🔄 Workflow

1. **Information Search**

   - The user sends a request through the UI
   - The agent analyzes the request and determines the necessary tools
   - A search is performed across the knowledge base and a response is generated

2. **Video Processing**

   - Uploading a YouTube video
   - Extracting frames every 5 seconds
   - Filtering similar images
   - Creating a DOCX document

3. **Voice Input**
   - Recording audio via the browser
   - Transcription using Whisper
   - Adding the text to the current query

## 📜 License

Apache License

## ⭐️ Support the Project

If you like the project, give it a star on GitHub!
