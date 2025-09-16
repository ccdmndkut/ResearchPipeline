# ResearchPipeline


## Table of Contents
- [ResearchPipeline](#researchpipeline)
  - [Table of Contents](#table-of-contents)
  - [Highlights](#highlights)
  - [Repository Layout](#repository-layout)
  - [Prerequisites](#prerequisites)
  - [Quick Start](#quick-start)
    - [Clone and Bootstrap](#clone-and-bootstrap)
    - [Run the Flask Pipeline](#run-the-flask-pipeline)
    - [Run the Research Assistant](#run-the-research-assistant)
  - [Configuration](#configuration)
  - [Testing](#testing)
  - [Roadmap](#roadmap)
  - [Contributing](#contributing)
  - [License](#license)
  - [Disclaimer](#disclaimer)

## Highlights
- **Dual workflow support**: experiment with market data locally while querying the AI assistant for papers, summaries, and citations.
- **Composable pipeline**: the `app/pipeline/` package breaks strategy research into loaders, cleaners, feature builders, and vector-store utilities you can extend.
- **Full-stack assistant**: `research-assistant/` hosts a FastAPI + WebSocket service with multi-agent orchestration for automated literature reviews.
- **Extensible UI pilots**: the `GenAIPlanPilot/` directory contains an experimental client/server interface to explore richer planning experiences.

## Repository Layout
```
ResearchPipeline/
├─ app/                   # Flask entry-point and modular research pipeline
│  ├─ main.py             # Application factory and dev runner
│  └─ pipeline/           # Loaders, cleaners, graph builder, orchestration, vector store helpers
├─ research-assistant/    # FastAPI research assistant (OpenAI + multi-agent system)
├─ GenAIPlanPilot/        # Experimental full-stack prototype (React + FastAPI)
├─ pyproject.toml         # Root Python project definition
├─ uv.lock                # uv resolver lockfile
└─ README.md
```

## Prerequisites
- Python 3.11+ (the assistant targets 3.11; the Flask app runs on 3.8+ but match 3.11 for simplicity)
- `uv` or `pip` for dependency management
- Optional: Node 18+ if you plan to run the GenAIPlanPilot client
- An OpenAI API key exported as `OPENAI_API_KEY` for the research assistant
- (Optional) PostgreSQL and Redis for production-grade deployments of the assistant

## Quick Start

### Clone and Bootstrap
```bash
# Clone the repository
git clone https://github.com/ccdmndkut/ResearchPipeline.git
cd ResearchPipeline

# Create a base virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate

# Install core Python dependencies (Flask pipeline)
pip install -r requirements.txt  # or: uv pip install -r requirements.txt
```

### Run the Flask Pipeline
```bash
# From the project root with the virtualenv active
python -m app.main
```
The Flask server exposes routes defined in `app/routes.py`. Visit http://localhost:5000 to interact with the pipeline interface or wire it into your own orchestration scripts. Customize behavior by editing modules under `app/pipeline/`.

### Run the Research Assistant
```bash
cd research-assistant
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and set OPENAI_API_KEY plus any optional service URLs
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Open http://localhost:8000 to launch the assistant UI or connect via the REST/WebSocket APIs documented in `research-assistant/README.md`.

If you would like to explore the experimental planning UI, boot the FastAPI server in `GenAIPlanPilot/server/` and the Vite client in `GenAIPlanPilot/client/`. Refer to the README files within that directory for details.

## Configuration
- Adjust pipeline settings, symbols, and feature options inside `app/pipeline/*.py` modules or by introducing configuration files in `config/` (create the folder if needed).
- Create `.env` files for each service you run (`research-assistant/.env`, optional `.env` for Flask) and avoid committing secrets.
- Swap out vector store, storage, or messaging integrations by implementing additional helpers in `app/pipeline/` or `research-assistant/app/tools/` and registering them in the orchestration layer.

## Testing
Run the Python tests with `pytest` in each component:
```bash
# Flask pipeline tests (if present)
pytest

# Research assistant tests
cd research-assistant
pytest tests/
```
For the GenAIPlanPilot prototype, use `npm test` or `vite`/`vitest` commands as described in its sub-README.

## Roadmap
- Harden the Flask pipeline with sample data loaders, feature notebooks, and CLI entry points.
- Provide docker-compose definitions for unified local bring-up.
- Document recommended experiment tracking and storage patterns.
- Expand automated tests covering multi-agent orchestration flows.

## Contributing
1. Fork the repository and create a feature branch.
2. Implement your changes along with relevant tests or notebooks.
3. Run the component-specific test suites and linters.
4. Submit a pull request summarizing motivation, approach, and validation steps.

We welcome ideas for new agents, integrations, or visualizations that improve the research workflow.

## License
MIT License. See `LICENSE` for the full text.

## Disclaimer
This project is provided for educational and research purposes only and does not constitute financial advice. Use the tools and outputs responsibly.
