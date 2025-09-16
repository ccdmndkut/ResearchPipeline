# Research Assistant

A sophisticated multi-agent system for academic research assistance, powered by OpenAI and featuring real-time WebSocket communication.

## Features

- **Multi-Agent Architecture**: Specialized agents for different research tasks
  - Search Agent: Literature search across academic databases
  - Summarizer Agent: Paper and topic summarization
  - Citation Agent: Citation verification and fact-checking
  - Graph Agent: Citation network analysis

- **Advanced Tools**
  - PDF parsing and analysis
  - Vector similarity search
  - Web content extraction
  - Statistical analysis

- **Real-time Interface**: WebSocket-based UI with live progress updates

## Setup

### Prerequisites

- Python 3.11+
- OpenAI API key
- PostgreSQL (optional, for production)
- Redis (optional, for caching)

### Installation

1. Clone the repository:
```bash
cd research-assistant
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file from example:
```bash
cp .env.example .env
```

5. Edit `.env` and add your API keys:
```
OPENAI_API_KEY=your-openai-api-key
```

## Running the Application

### Development Mode

```bash
python -m app.main
```

Or with auto-reload:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

Using Docker:
```bash
docker-compose -f docker/docker-compose.yml up -d
```

## API Endpoints

- `GET /` - Web interface
- `GET /health` - Health check
- `WS /ws/research` - WebSocket endpoint for research queries
- `POST /api/research` - REST endpoint for research queries
- `GET /api/agents` - List available agents
- `GET /api/tools` - List available tools

## Usage

### Web Interface

1. Open http://localhost:8000 in your browser
2. Enter a research query
3. Select databases and action type
4. Click Search to start processing
5. View real-time progress and results

### WebSocket API

Connect to `ws://localhost:8000/ws/research` and send:

```json
{
  "query": "deep learning for NLP",
  "parameters": {
    "databases": ["arxiv", "semantic_scholar"],
    "action": "search",
    "max_results": 20
  },
  "session_id": "unique-session-id"
}
```

### REST API

```bash
curl -X POST http://localhost:8000/api/research \
  -H "Content-Type: application/json" \
  -d '{
    "query": "transformer architectures",
    "parameters": {
      "databases": ["arxiv"],
      "max_results": 10
    }
  }'
```

## Testing

Run tests with pytest:
```bash
pytest tests/
```

Run with coverage:
```bash
pytest --cov=app tests/
```

## Deployment

### Docker Deployment

Build and run with Docker Compose:
```bash
cd docker
docker-compose up -d
```

### Kubernetes Deployment

Apply Kubernetes manifests:
```bash
kubectl apply -f k8s/
```

### Environment Variables

Key environment variables:

- `OPENAI_API_KEY`: OpenAI API key (required)
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `DEBUG`: Debug mode (default: false)
- `LOG_LEVEL`: Logging level (default: INFO)

## Architecture

```
research-assistant/
├─ app/
│  ├─ orchestrator/     # Main coordination logic
│  ├─ agents/           # Specialized agents
│  ├─ tools/            # Utility tools
│  └─ utils/            # Helper utilities
├─ prompts/             # System prompts
├─ static/              # Frontend assets
└─ tests/               # Test suite
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details