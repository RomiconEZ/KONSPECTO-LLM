# Development Guidelines for the KONSPECTO Project

## 1. General Rules

### 1.1. Project Structure
- **Directory Organization:** Clearly structure the project by separating the frontend, backend, documentation, and other components.
- **File and Folder Naming:** Use clear and descriptive names, adhering to naming conventions (e.g., `snake_case` for Python, `kebab-case` for JavaScript).

### 1.2. Comments and Documentation
- **File Header:** At the beginning of each file, add a comment indicating the path to the current file, starting from the project root.
  - **Example for Python:**
    ```python
    # /backend/app/api/users.py
    ```
  - **Example for JavaScript:**
    ```javascript
    // /frontend/src/components/Header.jsx
    ```
- **Function and Class Documentation:**
  - Write docstrings for all functions, methods, and classes.
  - Use [Google Style](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html) or [NumPy Style](https://numpydoc.readthedocs.io/en/latest/format.html) for formatting docstrings.

### 1.3. Version Control
- **Using Git:** Follow Git Flow principles for branching and merging changes.
- **Commit Messages:** Write informative commit messages that describe the changes made.
  - **Format:** `<type>: <short description>`
  - **Example Types:** `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

## 2. Language and Library Versions

To ensure compatibility and project stability, the following versions of programming languages and major libraries are used:

### 2.1. Python
- **Version:** Python 3.11
- **Package Manager:** `poetry`

### 2.2. Frontend
- **React.js:** 18.2.0
- **TailwindCSS:** 3.3.2
- **Node.js:** 18.x
- **npm:** 9.x

### 2.3. Backend
- **FastAPI:** 0.95.1
- **Celery:** 5.3.0
- **Redis:** 6.2.6

### 2.4. Voice and Text Processing
- **Lightning Whisper-MLX:** Latest stable version from [repository](https://github.com/mustafaaljadery/lightning-whisper-mlx)
- **LLM Studio:** 1.2.3

### 2.5. Video Processing
- **FFmpeg:** 4.4.1

### 2.6. Search Functionality
- **Options for Document Search:**
  - **LlamaIndex:** Utilize [LlamaIndex](https://github.com/jerryjliu/llama_index) for building and querying indices over document collections.
  - **ElasticSearch:** Implement search capabilities using [ElasticSearch](https://www.elastic.co/elasticsearch/) for scalable and efficient full-text search.

### 2.7. Infrastructure
- **Docker:** 24.0.0
- **Docker Compose:** 2.18.1

## 3. Coding Standards

### 3.1. Python
- **Code Style:** PEP 8
- **Linter:** `flake8`
- **Formatter:** `black` (version 23.1.0)
- **Typing:** Use type annotations for all functions and methods.

### 3.2. JavaScript/TypeScript
- **Code Style:** Airbnb JavaScript Style Guide
- **Linter:** `ESLint` (version 8.40.0)
- **Formatter:** `Prettier` (version 2.8.8)
- **Typing:** Use TypeScript for all new components.

## 4. Development Practices

### 4.1. Containerization
- **Docker:** All services (frontend, backend) must be containerized using Docker.
- **Docker Compose:** Use `docker-compose.yml` to orchestrate services in the local development environment.

### 4.2. Testing
- **Code Coverage:** Aim for at least 80% code coverage with tests.
- **Testing Frameworks:**
  - **Python:** `pytest` (version 7.3.1)
- **Types of Tests:** Write unit, integration, and E2E tests for all critical components.

### 4.3. CI/CD
- **Integration:** Set up CI/CD pipelines for automatic testing and deployment.
- **Tools:** GitHub Actions or GitLab CI/CD.

### 4.4. Security
- **Dependencies:** Regularly update dependencies and check for vulnerabilities.
- **Environment Variables:** Store sensitive data in environment variables and do not include them in the repository.

## 5. Documentation Management

### 5.1. Technical Documentation
- **Tools:** Sphinx for Python, Storybook for frontend.
- **Storage:** Documentation should be stored in the `/docs` directory.

### 5.2. API Documentation
- **FastAPI:** Automatically generates Swagger UI documentation.
- **Maintenance:** Update documentation when API changes.

## 6. Evaluation Criteria
- **Compliance with coding standards.**
- **Presence of tests for new features.**
- **Documentation of changes.**
- **Code optimization and efficiency.**

---
