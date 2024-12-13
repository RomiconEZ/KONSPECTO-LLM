# Project Planning for KONSPECTO

## 1. Defining the Vision and Goals of the Project

### Vision

Create an intelligent agent based on a local LLM model capable of efficiently searching, analyzing, and transforming information from notes and video lectures, providing users with convenient tools for managing and processing educational materials.

### Goals

- **Project Objectives:**

  - Develop an agent for searching information within notes with the ability to output full and summarized results.
  - Implement the transformation of video lectures into a set of slides for use in presentations.
  - Ensure support for input queries via both text and voice.

- **Target Outcomes:**

  - Increase the efficiency of students and teachers in working with educational materials.
  - Improve the accessibility of information and ease of use.
  - Reduce the time required for preparing and analyzing educational materials.

- **User Needs and Business Value:**
  - Users need quick access to relevant information from notes and video lectures.
  - The business value lies in creating a product that can be used in educational institutions to enhance the quality of teaching and learning.

## 2. Creating Detailed Specifications

### Functional Requirements

- **Information Search within Notes:**

  - Ability to input text and voice queries.
  - Search for relevant information within the notes.
  - Output results in both full and summarized formats with source references.

- **Video Lecture to Slides Conversion:**

  - Upload video lectures.
  - Extract key frames at specified time intervals.
  - Generate a set of images (slides) without text.

- **Support for Voice and Text Input:**
  - Recognize voice queries.
  - Process text queries.

### Nonfunctional Requirements

- **Performance:**

  - Fast processing of queries and generation of results.
  - Handle asynchronous tasks without delays for the user.

- **Security:**

  - Protect user data.
  - Secure storage of notes and processing results.

- **Usability:**
  - Intuitive interface.
  - Responsive design for various devices.

### Technical Specifications

- **Technology Stack:**

  - **Frontend:** React.js, HTML/CSS, TailwindCSS.
  - **Backend:** Python, FastAPI, Redis.
  - **Voice Processing:** Faster_Whisper.
  - **Text Processing Model:** LLM Studio.
  - **Infrastructure:** Docker.

- **Architecture:**

  - Client-server architecture with separation of frontend and backend.
  - Use of containerization for deploying all components.
  - Interaction between components via API.

- **Integration Points:**
  - Integrate frontend with backend via FastAPI.

### Acceptance Criteria

- The agent successfully processes text and voice queries.
- Search within notes returns relevant results in both formats.
- Video lecture to slides conversion works without errors.
- The user interface meets usability and responsiveness requirements.
- All components function correctly in a containerized Docker environment.

## 3. Developing Initial Documentation

### Project Charter

**Project Name:** KONSPECTO (LLM Agent for Working with Notes)

**Project Objective:** Develop an intelligent agent based on a local LLM model for searching, analyzing, and transforming information from notes and video lectures.

**Project Scope:**

- Create functionality for searching and converting videos to slides.
- Develop a user interface for interacting with the agent.
- Ensure support for voice and text input queries.

**Stakeholders:**

- **Clients:** Students, teachers, educational institutions.
- **Development Team:** Frontend and Backend developers, voice processing specialists, DevOps engineers.
- **Users:** End-users of the product.

### Requirements Document

**Functional Requirements:**

- Description of search, merging notes, video conversion, and query input support functions.

**Nonfunctional Requirements:**

- Performance, security, and usability.

**Constraints:**

- Use only a local LLM model.
- Containerize all components using Docker.

### Technical Documentation

**Architecture Description:**

- Detailed description of frontend, backend, processing models, and infrastructure components.

**API Documentation:**

- Description of FastAPI endpoints, methods, and data formats.

**Deployment Instructions:**

- Step-by-step guide for cloning the repository, installing dependencies, and running via Docker.

---
