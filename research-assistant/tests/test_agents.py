import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch


@pytest.mark.asyncio
async def test_search_agent_execute(search_agent, sample_papers):
    """Test search agent execution"""
    parameters = {
        "query": "deep learning",
        "databases": ["arxiv"],
        "max_results": 10
    }

    # Mock the search methods
    with patch.object(search_agent, "_search_arxiv") as mock_arxiv:
        mock_arxiv.return_value = sample_papers

        result = await search_agent.execute("search", parameters)

        assert "papers" in result
        assert "query" in result
        assert "expanded_query" in result
        assert len(result["papers"]) <= parameters["max_results"]


@pytest.mark.asyncio
async def test_search_agent_expand_query(search_agent):
    """Test query expansion"""
    result = await search_agent.expand_query({"query": "NLP"})

    assert "original" in result
    assert "expanded" in result
    assert result["original"] == "NLP"


@pytest.mark.asyncio
async def test_search_agent_filter_results(search_agent, sample_papers):
    """Test result filtering"""
    parameters = {
        "papers": sample_papers,
        "min_citations": 200,
        "year_range": [2020, 2024]
    }

    result = await search_agent.filter_results(parameters)

    assert "filtered_count" in result
    assert "papers" in result
    assert all(p["citation_count"] >= 200 for p in result["papers"])


@pytest.mark.asyncio
async def test_summarizer_agent_summarize_paper(summarizer_agent, sample_papers):
    """Test paper summarization"""
    parameters = {
        "paper": sample_papers[0],
        "summary_type": "executive"
    }

    result = await summarizer_agent.execute("summarize_paper", parameters)

    assert "summary" in result
    assert "paper_title" in result
    assert "summary_type" in result
    assert result["summary_type"] == "executive"


@pytest.mark.asyncio
async def test_summarizer_agent_compare_papers(summarizer_agent, sample_papers):
    """Test paper comparison"""
    parameters = {"papers": sample_papers}

    result = await summarizer_agent.execute("compare_papers", parameters)

    assert "comparison" in result
    assert "num_papers" in result


@pytest.mark.asyncio
async def test_citation_agent_verify_citations(citation_agent):
    """Test citation verification"""
    parameters = {
        "text": "According to Smith et al. (2023), machine learning is important.",
        "citations": []
    }

    result = await citation_agent.execute("verify_citations", parameters)

    assert "total_citations" in result
    assert "verified" in result
    assert "credibility_score" in result


@pytest.mark.asyncio
async def test_citation_agent_check_facts(citation_agent, sample_papers):
    """Test fact checking"""
    parameters = {
        "claims": ["Deep learning improves NLP tasks"],
        "sources": sample_papers
    }

    result = await citation_agent.execute("check_facts", parameters)

    assert "claims_checked" in result
    assert "results" in result


@pytest.mark.asyncio
async def test_graph_agent_build_network(graph_agent, sample_papers):
    """Test citation network building"""
    parameters = {"papers": sample_papers, "depth": 1}

    result = await graph_agent.execute("build_network", parameters)

    assert "network_stats" in result
    assert "top_cited_papers" in result
    assert "graph_data" in result


@pytest.mark.asyncio
async def test_graph_agent_analyze_trends(graph_agent, sample_papers):
    """Test trend analysis"""
    parameters = {
        "papers": sample_papers,
        "time_window": "yearly"
    }

    result = await graph_agent.execute("analyze_trends", parameters)

    assert "trends_by_year" in result
    assert "growth_rate" in result
    assert "total_papers" in result


@pytest.mark.asyncio
async def test_graph_agent_find_communities(graph_agent, sample_papers):
    """Test community detection"""
    parameters = {
        "papers": sample_papers,
        "method": "louvain"
    }

    result = await graph_agent.execute("find_communities", parameters)

    assert "num_communities" in result
    assert "communities" in result


@pytest.mark.asyncio
async def test_graph_agent_calculate_metrics(graph_agent, sample_papers):
    """Test network metrics calculation"""
    parameters = {
        "papers": sample_papers,
        "metrics_type": "all"
    }

    result = await graph_agent.execute("calculate_metrics", parameters)

    assert "metrics" in result
    assert "num_nodes" in result
    assert "num_edges" in result


def test_agent_descriptions():
    """Test that all agents have proper descriptions"""
    agents = [SearchAgent(), SummarizerAgent(), CitationAgent(), GraphAgent()]

    for agent in agents:
        desc = agent.get_description()
        assert isinstance(desc, str)
        assert len(desc) > 0

        params = agent.get_parameters()
        assert isinstance(params, dict)
        assert "properties" in params


@pytest.mark.asyncio
async def test_agent_error_handling(search_agent):
    """Test agent error handling"""
    with pytest.raises(ValueError):
        await search_agent.execute("invalid_action", {})