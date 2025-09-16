import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch


@pytest.mark.asyncio
async def test_orchestrator_process_query(orchestrator, sample_query):
    """Test orchestrator query processing"""
    events = []
    async for event in orchestrator.process_query(sample_query):
        events.append(event)
        if len(events) > 10:  # Prevent infinite loop
            break

    assert len(events) > 0
    assert any(e["event_type"] == "start" for e in events)


@pytest.mark.asyncio
async def test_orchestrator_create_execution_plan(orchestrator, sample_query):
    """Test execution plan creation"""
    plan = await orchestrator._create_execution_plan(
        sample_query["query"],
        sample_query["parameters"]
    )

    assert "query" in plan
    assert "steps" in plan
    assert plan["query"] == sample_query["query"]


@pytest.mark.asyncio
async def test_orchestrator_synthesize_results(orchestrator, sample_papers):
    """Test result synthesis"""
    results = [
        {"papers": sample_papers[:2]},
        {"summary": "Test summary of papers"}
    ]

    synthesis = await orchestrator._synthesize_results(
        "test query",
        results
    )

    assert "query" in synthesis
    assert "synthesis" in synthesis
    assert "sources" in synthesis
    assert "timestamp" in synthesis


def test_orchestrator_create_event(orchestrator):
    """Test event creation"""
    event = orchestrator._create_event(
        "test_type",
        "test_agent",
        "running",
        "Test message",
        {"key": "value"}
    )

    assert event["event_type"] == "test_type"
    assert event["agent"] == "test_agent"
    assert event["status"] == "running"
    assert event["message"] == "Test message"
    assert event["data"]["key"] == "value"
    assert "timestamp" in event


def test_orchestrator_extract_sources(orchestrator, sample_papers):
    """Test source extraction"""
    results = [
        {"sources": sample_papers[:1]},
        {"papers": sample_papers[1:2]},
        {"other_data": "test"}
    ]

    sources = orchestrator._extract_sources(results)
    assert len(sources) == 2


def test_orchestrator_get_available_agents(orchestrator):
    """Test getting available agents"""
    agents = orchestrator.get_available_agents()
    assert "search" in agents
    assert "summarizer" in agents
    assert "citation" in agents
    assert "graph" in agents


def test_orchestrator_get_agent_descriptions(orchestrator):
    """Test getting agent descriptions"""
    descriptions = orchestrator.get_agent_descriptions()
    assert len(descriptions) == 4
    assert all(isinstance(desc, str) for desc in descriptions.values())


@pytest.mark.asyncio
async def test_orchestrator_execute_step_agent(orchestrator, sample_papers):
    """Test executing an agent step"""
    step = {
        "agent": "search",
        "action": "search",
        "parameters": {"query": "test"}
    }

    # Mock the search agent
    with patch.object(orchestrator.agents["search"], "execute") as mock_execute:
        mock_execute.return_value = {"papers": sample_papers}

        events = []
        async for event in orchestrator._execute_step(step, []):
            events.append(event)

        assert len(events) == 2  # started and completed
        assert events[0]["status"] == "started"
        assert events[1]["status"] == "completed"


@pytest.mark.asyncio
async def test_orchestrator_execute_step_tool(orchestrator):
    """Test executing a tool step"""
    step = {
        "tool": "stats",
        "parameters": {"operation": "describe", "data": [1, 2, 3, 4, 5]}
    }

    events = []
    async for event in orchestrator._execute_step(step, []):
        events.append(event)

    assert len(events) == 2
    assert events[0]["event_type"] == "tool_use"
    assert events[1]["status"] == "completed"


@pytest.mark.asyncio
async def test_orchestrator_error_handling(orchestrator):
    """Test error handling in query processing"""
    bad_query = {
        "query": None,  # Invalid query
        "parameters": {}
    }

    events = []
    async for event in orchestrator.process_query(bad_query):
        events.append(event)
        if event["event_type"] == "error":
            break

    error_events = [e for e in events if e["event_type"] == "error"]
    assert len(error_events) > 0