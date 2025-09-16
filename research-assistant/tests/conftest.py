import pytest
import asyncio
from typing import Generator
from unittest.mock import Mock, AsyncMock
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.settings import settings
from app.orchestrator.orchestrator import ResearchOrchestrator
from app.agents import SearchAgent, SummarizerAgent, CitationAgent, GraphAgent
from app.tools import PDFParser, VectorSearch, WebFetch, StatsUtil


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_settings(monkeypatch):
    """Mock settings for testing"""
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(settings, "DEBUG", True)
    monkeypatch.setattr(settings, "CACHE_ENABLED", False)
    return settings


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client"""
    client = AsyncMock()
    client.chat.completions.create = AsyncMock(
        return_value=Mock(
            choices=[
                Mock(
                    message=Mock(content="Test response"),
                    function_call=None
                )
            ]
        )
    )
    return client


@pytest.fixture
def orchestrator(mock_openai_client):
    """Create orchestrator instance with mocked dependencies"""
    orch = ResearchOrchestrator()
    orch.client = mock_openai_client
    return orch


@pytest.fixture
def search_agent(mock_openai_client):
    """Create search agent instance"""
    agent = SearchAgent()
    agent.client = mock_openai_client
    return agent


@pytest.fixture
def summarizer_agent(mock_openai_client):
    """Create summarizer agent instance"""
    agent = SummarizerAgent()
    agent.client = mock_openai_client
    return agent


@pytest.fixture
def citation_agent(mock_openai_client):
    """Create citation agent instance"""
    agent = CitationAgent()
    agent.client = mock_openai_client
    return agent


@pytest.fixture
def graph_agent(mock_openai_client):
    """Create graph agent instance"""
    agent = GraphAgent()
    agent.client = mock_openai_client
    return agent


@pytest.fixture
def pdf_parser():
    """Create PDF parser instance"""
    return PDFParser()


@pytest.fixture
def vector_search(mock_openai_client):
    """Create vector search instance"""
    search = VectorSearch()
    search.client = mock_openai_client
    return search


@pytest.fixture
def web_fetch():
    """Create web fetch instance"""
    return WebFetch()


@pytest.fixture
def stats_util():
    """Create stats util instance"""
    return StatsUtil()


@pytest.fixture
def sample_papers():
    """Sample paper data for testing"""
    return [
        {
            "id": "paper1",
            "title": "Deep Learning for NLP",
            "authors": ["John Doe", "Jane Smith"],
            "abstract": "This paper explores deep learning techniques for natural language processing.",
            "year": 2023,
            "citation_count": 150,
            "url": "https://example.com/paper1",
            "references": ["paper2", "paper3"]
        },
        {
            "id": "paper2",
            "title": "Transformer Architecture",
            "authors": ["Alice Johnson", "Bob Wilson"],
            "abstract": "A comprehensive study of transformer architectures in machine learning.",
            "year": 2022,
            "citation_count": 300,
            "url": "https://example.com/paper2",
            "references": ["paper3"]
        },
        {
            "id": "paper3",
            "title": "Attention Is All You Need",
            "authors": ["Original Authors"],
            "abstract": "The foundational paper on attention mechanisms.",
            "year": 2017,
            "citation_count": 10000,
            "url": "https://example.com/paper3",
            "references": []
        }
    ]


@pytest.fixture
def sample_query():
    """Sample research query"""
    return {
        "query": "deep learning for natural language processing",
        "parameters": {
            "databases": ["arxiv", "semantic_scholar"],
            "max_results": 10,
            "action": "search"
        },
        "session_id": "test_session_123"
    }