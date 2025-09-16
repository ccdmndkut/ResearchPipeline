# Gemini Project Context: ResearchPipeline

This file provides context for the Gemini AI assistant to understand the `ResearchPipeline` project.

## Project Overview

This repository contains a multi-part system designed for financial research and analysis. It combines a data processing pipeline with an AI-powered research assistant. The project is divided into three main components:

1.  **`app` (Flask Pipeline):** A modular data pipeline built with Flask. It's designed for tasks like data loading, cleaning, feature engineering, and vector store management. The core logic is located in the `app/pipeline/` directory.

2.  **`research-assistant` (FastAPI):** A sophisticated research assistant powered by FastAPI and the OpenAI API. It uses a multi-agent system to automate literature reviews, including fetching papers, summarizing content, and managing citations.

3.  **`GenAIPlanPilot` (Experimental UI):** A full-stack prototype featuring a React front-end and a FastAPI back-end. It's designed to explore advanced user interfaces for planning and interacting with the research pipelines.

## Key Technologies

*   **Backend:** Python, Flask, FastAPI
*   **Frontend:** React, Vite
*   **AI:** OpenAI API
*   **Package Management:** pip/uv, npm

## Building and Running

### 1. Flask Pipeline (`app`)

To run the Flask data pipeline:

1.  **Activate virtual environment:**
    ```bash
    # On Windows
    .venv\Scripts\activate
    ```
2.  **Run the application:**
    ```bash
    python -m app.main
    ```
The application will be available at `http://localhost:5000`.

### 2. Research Assistant (`research-assistant`)

To run the research assistant:

1.  **Navigate to the directory:**
    ```bash
    cd research-assistant
    ```
2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv .venv
    # On Windows
    .venv\Scripts\activate
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configure OpenAI API Key:**
    *   Copy `.env.example` to `.env`.
    *   Add your `OPENAI_API_KEY` to the `.env` file.
5.  **Run the server:**
    ```bash
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    ```
The assistant will be available at `http://localhost:8000`.

### 3. GenAIPlanPilot (Experimental UI)

To run the experimental UI:

*   Follow the instructions in the `GenAIPlanPilot/README.md` file. This involves running a FastAPI server and a Vite development server for the React client.

## Development Conventions

*   **Virtual Environments:** Each Python-based component (`app`, `research-assistant`) uses its own virtual environment.
*   **Configuration:** Configuration is managed through `.env` files (for secrets like API keys) and directly within the Python modules for pipeline settings.
*   **Testing:** `pytest` is the designated testing framework for the Python components. The `GenAIPlanPilot` project uses `npm test` or `vitest`.
*   **Contribution:** The project follows a standard fork-and-pull-request model for contributions.
