# KONSPECTO Project Architecture

## Project Structure Overview

The project is organized into two main components: frontend and backend, with supporting Docker configurations.

```plaintext
KONSPECTO/
├── frontend/
├── backend/
└── docker/
```

## Backend Structure

```plaintext
backend/
├── agent/
│   ├── tools/
│   │   ├── video_processor.py
│   │   ├── search.py
│   │   └── __init__.py
│   ├── react_agent.py
│   └── __init__.py
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── agent.py
│   │       │   ├── search.py
│   │       │   ├── transcribe.py
│   │       │   └── video.py
│   │       └── api.py
│   ├── core/
│   │   ├── config.py
│   │   └── logging_config.py
│   ├── models/
│   │   ├── search.py
│   │   └── transcription.py
│   ├── services/
│   │   ├── llm/
│   │   │   └── llm_studio_client.py
│   │   ├── transcription/
│   │   │   ├── base.py
│   │   │   └── whisper_model.py
│   │   ├── index_service.py
│   │   ├── redis_service.py
│   │   └── vector_db.py
│   ├── exceptions.py
│   └── main.py
├── tests/
│   ├── conftest.py
│   ├── test_agent_endpoint.py
│   ├── test_agent_search.py
│   ├── test_main.py
│   ├── test_search.py
│   ├── test_transcribe_endpoint.py
│   ├── test_transcription.py
│   ├── test_video_api.py
│   └── test_video_processor.py
├── pyproject.toml
└── setup.cfg
```

### Backend Components Description

#### Agent Module
- **tools/**: Contains specialized tools for the agent
  - `video_processor.py`: Handles YouTube video processing and DOCX generation
  - `search.py`: Implements search functionality
- `react_agent.py`: Core agent implementation using ReAct framework

#### App Module
- **api/v1/**: API version 1 implementation
  - `endpoints/`: Contains all API endpoint handlers
- **core/**: Core configurations and logging
- **models/**: Data models and schemas
- **services/**: Business logic implementation
  - `llm/`: Language model client
  - `transcription/`: Audio transcription services
  - `index_service.py`: Vector store index management
  - `redis_service.py`: Redis interaction
  - `vector_db.py`: Vector database operations

#### Tests
- Comprehensive test suite for all major components
- Includes configuration and fixtures in `conftest.py`

## Frontend Structure

```plaintext
frontend/
├── src/
│   ├── components/
│   │   ├── DownloadButton.jsx
│   │   ├── ErrorMessage.jsx
│   │   ├── GoogleDocViewer.jsx
│   │   └── Sidebar.jsx
│   ├── context/
│   │   └── ChatContext.jsx
│   ├── pages/
│   │   └── Chat.jsx
│   ├── utils/
│   │   └── youtubeUtils.js
│   ├── App.jsx
│   └── main.jsx
├── __tests__/
│   ├── App.test.jsx
│   ├── Chat.test.jsx
│   ├── GoogleDocViewer.test.jsx
│   └── Sidebar.test.jsx
├── __mocks__/
│   ├── config.js
│   └── fileMock.js
├── .eslintrc.js
├── .prettierrc
├── babel.config.js
├── index.html
├── jest.config.js
├── jest.setup.js
├── package.json
├── postcss.config.js
├── tailwind.config.js
└── vite.config.js
```

### Frontend Components Description

#### Source Files
- **components/**: Reusable UI components
  - `DownloadButton.jsx`: Component for file downloads
  - `ErrorMessage.jsx`: Error display component
  - `GoogleDocViewer.jsx`: Document viewer component
  - `Sidebar.jsx`: Navigation sidebar component
- **context/**: React context providers
- **pages/**: Main application pages
- **utils/**: Utility functions

#### Testing
- **__tests__/**: Test files for components
- **__mocks__/**: Mock files for testing

#### Configuration
- Various configuration files for:
  - ESLint
  - Prettier
  - Babel
  - Jest
  - PostCSS
  - Tailwind
  - Vite

## Docker Configuration

```plaintext
docker/
├── backend/
│   └── Dockerfile
└── frontend/
    ├── Dockerfile
    └── nginx.conf
```

### Docker Components Description

#### Backend Docker
- Dockerfile for Python backend service
- Multi-stage build for optimized image size
- Includes FFmpeg and other necessary dependencies

#### Frontend Docker
- Dockerfile for React frontend
- Nginx configuration for serving static files
- Production-ready setup with multi-stage build

---

## Docker Configuration

### Docker Compose Overview

The project uses Docker Compose for orchestrating multiple services:

```plaintext
services:
  ├── frontend
  ├── backend
  └── redis-stack
```

### Service Descriptions

#### Frontend Service
- Built using multi-stage Dockerfile
- Served via Nginx
- Exposed on port 80
- Environment configurations:
  - NODE_ENV=production
  - VITE_API_URL for API endpoint configuration

#### Backend Service
- Python-based FastAPI application
- Exposed on port 8000
- Volumes:
  - Logs directory
  - Configuration files
  - Hugging Face cache
- Environment configurations:
  - Python environment settings
  - Redis connection
  - LLM Studio configuration
- Health check implementation
- Dependencies on Redis Stack service

#### Redis Stack Service
- Uses official Redis Stack image
- Exposed ports:
  - 6379 for Redis
  - 8001 for RedisInsight
- Persistent volume for data storage
- Health check implementation

### Docker Volumes
- `redis_stack_data`: Persistent storage for Redis
- `huggingface_cache`: Cache for Hugging Face models

## Project Configuration

### Pre-commit Configuration

The project uses comprehensive pre-commit hooks for code quality:

#### General Checks
- YAML/JSON/TOML validation
- File size limits
- End of file fixing
- Trailing whitespace removal
- Merge conflict detection
- Private key detection

#### Python-specific
- Black formatting
- isort import sorting
- Flake8 linting
- Mypy type checking
- Jupyter notebook formatting

#### JavaScript/React
- Prettier formatting
- ESLint checking
- Tailwind CSS plugin

#### Docker
- Hadolint for Dockerfile linting

#### Local Hooks
- Frontend dependency installation and testing
- Backend dependency installation and testing
- Docker Compose validation

### Project Settings (pyproject.toml)

The project uses Poetry for dependency management with specific configurations:

#### Tool Configurations
- Black: 90 character line length, Python 3.11 target
- isort: Black profile compatibility
- Flake8: Customized rule set
- Mypy: Strict type checking
- Pytest: Coverage reporting

#### Dependencies
- Production dependencies managed via Poetry
- Development dependencies including:
  - pre-commit
  - Testing tools (pytest)
  - Code formatters (black, isort)
  - Linters (flake8, mypy, pylint)

This configuration ensures:
- Consistent code formatting
- Type safety
- Code quality standards
- Automated testing
- Clean git commits