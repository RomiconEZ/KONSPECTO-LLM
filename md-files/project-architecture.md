# Архитектура Проекта KONSPECTO

## Структура Проекта

```plaintext
KONSPECTO/
├── frontend/
├── backend/
├── agent/
├── docs/
├── docker/
├── tests/
├── .gitignore
├── docker-compose.yml
├── README.md
└── LICENSE
```

### Root Directory Description

- **frontend/**: Contains all the source code and configuration for the frontend part of the application.
- **backend/**: Contains the source code and configuration for the backend part of the application, including the API.
- **agent/**: Contains the code and tools related to the AI agent, including models, request processing, and integration with other services.
- **docs/**: Stores technical documentation, instructions, and other related documentation.
- **docker/**: Contains Docker files and configurations for various services.
- **tests/**: Contains general tests, if applicable.
- **.gitignore**: File specifying which files and folders Git should ignore.
- **docker-compose.yml**: Docker Compose configuration file for orchestrating services.
- **README.md**: Main project documentation with descriptions, installation, and usage instructions.
- **LICENSE**: Project license agreement.


---

## frontend
```plaintext
frontend/
├── public/
│   ├── index.html
│   └── favicon.ico
├── src/
│   ├── assets/
│   ├── components/
│   ├── pages/
│   ├── services/
│   ├── styles/
│   ├── App.jsx
│   └── index.jsx
├── .env
├── .eslintrc.js
├── package.json
├── tailwind.config.js
├── postcss.config.js
└── vite.config.js
```

### Description of Folders and Files

- **public/**: Contains static files such as `index.html`, icons, and other resources that are not processed by the bundler.
  - `index.html`: Main HTML file of the application.
  - `favicon.ico`: Website icon.

- **src/**: Main directory containing the frontend source code.
  - **assets/**: Contains images, fonts, and other media files.
  - **components/**: Reusable React components.
  - **pages/**: Application pages representing different routes.
  - **services/**: Functions and modules for interacting with APIs and other services.
  - **styles/**: Application styling, including TailwindCSS and additional CSS/SCSS files.
  - `App.jsx`: Main application component containing routing and common components.
  - `index.jsx`: Entry point of the application, rendering the React tree.

- **.env**: Environment file for setting up environment variables (e.g., API URL).

- **.eslintrc.js**: ESLint configuration to ensure coding style adherence.

- **package.json**: Dependency and script file for the frontend.

- **tailwind.config.js**: TailwindCSS configuration for setting up utility classes.

- **postcss.config.js**: PostCSS configuration for processing CSS.

- **vite.config.js**: Vite configuration used as the bundler and development server.

---

## backend

```plaintext
backend/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   │   ├── users.py
│   │   │   │   ├── notes.py
│   │   │   │   └── lectures.py
│   │   │   └── __init__.py
│   │   └── __init__.py
│   ├── core/
│   │   ├── config.py
│   │   └── __init__.py
│   ├── services/
│   │   ├── api_search.py
│   │   └── __init__.py
│   ├── utils/
│   │   ├── helpers.py
│   │   └── __init__.py
│   ├── main.py
│   └── __init__.py
├── tests/
│   ├── api/
│   ├── models/
│   ├── schemas/
│   └── conftest.py
├── requirements.txt
├── Dockerfile
└── .env
```

### Description of Folders and Files

### Description of Folders and Files

- **app/**: Main backend directory.
  - **api/**: Implementation of the application API.
    - **v1/**: Version 1 of the API.
      - **endpoints/**: API endpoints organized by functional areas.
        - `users.py`: Endpoints related to users.
        - `notes.py`: Endpoints for managing notes.
        - `lectures.py`: Endpoints for managing video lectures.
      - `__init__.py`: Initialization of the API version.
    - `__init__.py`: API initialization.

  - **core/**: Core configurations and settings of the application.
    - `config.py`: Application configuration settings.
    - `__init__.py`: Core initialization.

  - **services/**: Business logic and interactions with external services.
    - `api_search.py`: Logic for searching notes via the API.
    - `__init__.py`: Services initialization.

  - **utils/**: Helper functions and utilities.
    - `helpers.py`: General helper functions.
    - `__init__.py`: Utilities initialization.

  - `main.py`: Entry point of the backend application, setting up FastAPI and running the server.

  - `__init__.py`: Application initialization.

- **tests/**: Backend tests.
  - **api/**: Tests for API endpoints.
  - **models/**: Tests for application models.
  - **schemas/**: Tests for Pydantic schemas.
  - `conftest.py`: Test configurations and fixtures.

- **requirements.txt**: List of Python dependencies for the backend.

- **Dockerfile**: Instructions for building the backend service Docker image.

- **.env**: Environment file for setting up environment variables.

---

## agent

```plaintext
agent/
├── models/
│   ├── llm_model.py
│   └── __init__.py
├── services/
│   ├── search_service.py
│   ├── merge_notes_service.py
│   ├── video_processing_service.py
│   └── __init__.py
├── tasks/
│   ├── video_tasks.py
│   ├── merge_tasks.py
│   └── __init__.py
├── utils/
│   ├── llm_helpers.py
│   └── __init__.py
├── config.py
├── main.py
└── __init__.py
```

### Description of Folders and Files

- **models/**: Definition and initialization of AI agent models.
  - `llm_model.py`: Local LLM (LLM Studio) model for text processing.
  - `__init__.py`: Models initialization.

- **services/**: Services and logic related to agent functionality.
  - `search_service.py`: Service for searching information in notes using LLM.
  - `merge_notes_service.py`: Service for merging notes based on topics and content.
  - `video_processing_service.py`: Service for converting video lectures into slides using FFmpeg.
  - `__init__.py`: Services initialization.

- **tasks/**: Asynchronous tasks handled by Celery related to the agent.
  - `video_tasks.py`: Tasks for video processing and slide creation.
  - `merge_tasks.py`: Tasks for merging notes.
  - `__init__.py`: Tasks initialization.

- **utils/**: Helper functions and utilities for the agent.
  - `llm_helpers.py`: Helper functions for working with LLM.
  - `__init__.py`: Utilities initialization.

- `config.py`: Agent configuration settings, including model and service parameters.

- `main.py`: Entry point to run the AI agent, setting up services and interacting with other components.

- `__init__.py`: Agent initialization.

---


## docs

```plaintext
docs/
├── architecture.md
├── api_documentation.md
├── installation.md
├── user_guide.md
├── developer_guide.md
└── images/
    └── architecture_diagram.png
```

### Description of Folders and Files

- **architecture.md**: Detailed description of the system architecture, component interactions, and technologies used.
- **api_documentation.md**: API documentation, including endpoint descriptions, methods, parameters, and example requests/responses.
- **installation.md**: Installation and setup instructions for the project on local machines and production environments.
- **user_guide.md**: User guide for using the application, describing functionality and usage examples.
- **developer_guide.md**: Developer guide for making code changes, running local development, and setting up the environment.
- **images/**: Folder for storing images and diagrams used in documentation.
  - `architecture_diagram.png`: Project architecture diagram.

---

## docker

```plaintext
docker/
├── frontend/
│   └── Dockerfile
├── backend/
│   └── Dockerfile
├── agent/
│   └── Dockerfile
├── nginx/
│   └── nginx.conf
└── volumes/
    └── data/
```

### Description of Folders and Files

- **frontend/Dockerfile**: Instructions for building the frontend service Docker image.
- **backend/Dockerfile**: Instructions for building the backend service Docker image.
- **agent/Dockerfile**: Instructions for building the AI agent Docker image.
- **nginx/nginx.conf**: Nginx configuration file for proxying requests and serving static files.
- **volumes/data/**: Folder for storing data used by Docker containers.

---


## tests

```plaintext
tests/
├── frontend/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── backend/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── agent/
│   ├── unit/
│   ├── integration/
│   └── e2e/
└── shared/
    └── fixtures/
```

### Description of Folders and Files

- **frontend/**: Tests for the frontend part.
  - **unit/**: Unit tests for individual components and functions.
  - **integration/**: Integration tests for verifying component interactions.
  - **e2e/**: End-to-End tests for verifying the complete application functionality.

- **backend/**: Tests for the backend part.
  - **unit/**: Unit tests for individual modules and functions.
  - **integration/**: Integration tests for verifying component interactions (e.g., API and services).
  - **e2e/**: End-To-End tests for verifying the complete API functionality.

- **agent/**: Tests for the AI agent.
  - **unit/**: Unit tests for individual agent services and functions.
  - **integration/**: Integration tests for verifying agent interactions with other components.
  - **e2e/**: End-To-End tests for verifying the complete agent functionality.

- **shared/**: Shared resources for tests.
  - **fixtures/**: Fixtures and data used in tests.

---