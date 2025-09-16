import pytest
import asyncio
import numpy as np
from unittest.mock import Mock, patch, mock_open


@pytest.mark.asyncio
async def test_stats_util_descriptive_stats(stats_util):
    """Test descriptive statistics calculation"""
    data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    result = await stats_util.execute({
        "operation": "describe",
        "data": data
    })

    assert result["status"] == "success"
    assert result["count"] == 10
    assert result["mean"] == 5.5
    assert result["median"] == 5.5
    assert "std_dev" in result
    assert "percentiles" in result


@pytest.mark.asyncio
async def test_stats_util_correlation(stats_util):
    """Test correlation analysis"""
    result = await stats_util.execute({
        "operation": "correlation",
        "x_data": [1, 2, 3, 4, 5],
        "y_data": [2, 4, 6, 8, 10],
        "method": "pearson"
    })

    assert result["status"] == "success"
    assert result["correlation"] == pytest.approx(1.0, rel=1e-5)
    assert result["significant"] == True


@pytest.mark.asyncio
async def test_stats_util_hypothesis_test(stats_util):
    """Test hypothesis testing"""
    result = await stats_util.execute({
        "operation": "hypothesis_test",
        "test_type": "t_test",
        "data1": [1, 2, 3, 4, 5],
        "data2": [2, 3, 4, 5, 6],
        "alpha": 0.05
    })

    assert result["status"] == "success"
    assert "test_statistic" in result
    assert "p_value" in result
    assert "reject_null_hypothesis" in result


@pytest.mark.asyncio
async def test_stats_util_trend_analysis(stats_util):
    """Test trend analysis"""
    result = await stats_util.execute({
        "operation": "trend_analysis",
        "values": [1, 2, 3, 4, 5],
        "timestamps": [1, 2, 3, 4, 5]
    })

    assert result["status"] == "success"
    assert "trend" in result
    assert "slope" in result
    assert "r_squared" in result


@pytest.mark.asyncio
async def test_vector_search_index_documents(vector_search):
    """Test document indexing"""
    documents = [
        {"text": "Document 1", "id": "1", "title": "Title 1"},
        {"text": "Document 2", "id": "2", "title": "Title 2"}
    ]

    result = await vector_search.execute({
        "action": "index",
        "documents": documents
    })

    assert result["status"] == "success"
    assert result["num_indexed"] == 2


@pytest.mark.asyncio
async def test_vector_search_search_similar(vector_search):
    """Test similarity search"""
    # First index some documents
    documents = [
        {"text": "Machine learning is great", "id": "1"},
        {"text": "Deep learning is powerful", "id": "2"}
    ]

    await vector_search.execute({
        "action": "index",
        "documents": documents
    })

    # Then search
    result = await vector_search.execute({
        "action": "search",
        "query": "machine learning",
        "top_k": 5
    })

    assert "results" in result
    assert result["status"] in ["success", "error"]


@pytest.mark.asyncio
async def test_web_fetch_fetch_page(web_fetch):
    """Test web page fetching"""
    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_response = Mock()
        mock_response.status = 200
        mock_response.headers = {"Content-Type": "text/html"}
        mock_response.text = AsyncMock(return_value="<html><body>Test content</body></html>")
        mock_get.return_value.__aenter__.return_value = mock_response

        result = await web_fetch.execute({
            "url": "https://example.com",
            "action": "fetch",
            "extract_text": True
        })

        assert "text" in result
        assert "status_code" in result
        assert result["status_code"] == 200


@pytest.mark.asyncio
async def test_web_fetch_extract_structured_data(web_fetch):
    """Test structured data extraction"""
    html_content = """
    <html>
        <head><title>Test Article</title></head>
        <body>
            <h1>Main Title</h1>
            <div class="author">John Doe</div>
            <article>Article content here</article>
        </body>
    </html>
    """

    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_response = Mock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=html_content)
        mock_get.return_value.__aenter__.return_value = mock_response

        result = await web_fetch.execute({
            "url": "https://example.com",
            "action": "extract_data",
            "schema": "article"
        })

        assert result["status"] == "success"
        assert "data" in result


def test_pdf_parser_extract_structured_info(pdf_parser):
    """Test PDF structured info extraction"""
    text = """
    This is a research paper.
    DOI: 10.1234/example.2023.001
    Email: author@example.com

    Abstract
    This is the abstract.

    Introduction
    This is the introduction.

    References
    [1] First reference
    [2] Second reference
    """

    info = pdf_parser._extract_structured_info(text)

    assert "doi" in info
    assert info["doi"] == "10.1234/example.2023.001"
    assert "emails" in info
    assert "author@example.com" in info["emails"]
    assert "sections" in info


def test_tool_descriptions():
    """Test that all tools have proper descriptions"""
    tools = [PDFParser(), VectorSearch(), WebFetch(), StatsUtil()]

    for tool in tools:
        desc = tool.get_description()
        assert isinstance(desc, str)
        assert len(desc) > 0

        params = tool.get_parameters()
        assert isinstance(params, dict)
        assert "properties" in params


@pytest.mark.asyncio
async def test_tool_error_handling(stats_util):
    """Test tool error handling"""
    result = await stats_util.execute({
        "operation": "describe",
        "data": []  # Empty data should cause an error
    })

    assert result["status"] == "error"
    assert "error" in result