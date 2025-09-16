"""
Test suite for Enhanced Orchestrator
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from app.orchestrator.enhanced_orchestrator import (
    EnhancedOrchestrator,
    TaskStatus,
    TaskPriority,
    AgentCapability
)
from app.orchestrator.query_analyzer import (
    QueryAnalyzer,
    QueryIntent,
    QueryComplexity
)
from app.agents.response_formatter import (
    ResponseFormatterAgent,
    AudienceType,
    FormatType,
    DetailLevel,
    CitationStyle
)


@pytest.fixture
def orchestrator():
    """Create orchestrator instance for testing"""
    return EnhancedOrchestrator()


@pytest.fixture
def query_analyzer():
    """Create query analyzer instance for testing"""
    return QueryAnalyzer()


@pytest.fixture
def response_formatter():
    """Create response formatter instance for testing"""
    return ResponseFormatterAgent()


@pytest.fixture
def sample_query():
    """Sample research query for testing"""
    return {
        "query": "machine learning advances in natural language processing 2024",
        "parameters": {
            "databases": ["arxiv", "semantic_scholar"],
            "max_results": 10,
            "action": "search"
        },
        "session_id": "test_session_123"
    }


@pytest.fixture
def sample_response():
    """Sample response for formatting tests"""
    return {
        "query": "machine learning NLP",
        "synthesis": "Recent advances in machine learning have revolutionized NLP...",
        "sources": [
            {
                "title": "Transformer Models in 2024",
                "authors": ["Smith, J.", "Doe, A."],
                "year": "2024",
                "abstract": "This paper explores...",
                "journal": "AI Review",
                "doi": "10.1234/example",
                "_scores": {
                    "relevance": 95,
                    "completeness": 88,
                    "source_quality": 92,
                    "overall": 91.5
                }
            }
        ],
        "quality_metrics": {
            "avg_relevance": 90,
            "avg_quality": 85,
            "total_sources": 5
        }
    }


class TestEnhancedOrchestrator:
    """Test Enhanced Orchestrator functionality"""
    
    @pytest.mark.asyncio
    async def test_parallel_execution(self, orchestrator, sample_query):
        """Test that tasks execute in parallel"""
        events = []
        
        async for event in orchestrator.process_query(sample_query):
            events.append(event)
            if event.get("event_type") == "complete":
                break
        
        # Check for parallel execution events
        parallel_events = [e for e in events if e.get("event_type") == "parallel_execution"]
        assert len(parallel_events) > 0, "Should have parallel execution events"
        
        # Check for completion
        complete_events = [e for e in events if e.get("event_type") == "complete"]
        assert len(complete_events) == 1, "Should have completion event"
    
    @pytest.mark.asyncio
    async def test_query_analysis_integration(self, orchestrator, sample_query):
        """Test query analysis integration"""
        events = []
        
        async for event in orchestrator.process_query(sample_query):
            events.append(event)
            if event.get("event_type") == "analysis":
                break
        
        # Check for analysis event
        analysis_events = [e for e in events if e.get("event_type") == "analysis"]
        assert len(analysis_events) > 0, "Should have analysis event"
        
        analysis = analysis_events[0].get("data", {}).get("analysis", {})
        assert "intent" in analysis
        assert "complexity" in analysis
        assert "entities" in analysis
    
    @pytest.mark.asyncio
    async def test_quality_scoring(self, orchestrator):
        """Test quality scoring functionality"""
        # Mock results
        results = [
            {
                "title": "Test Paper 1",
                "abstract": "Machine learning test",
                "authors": ["Author A"],
                "year": "2024",
                "journal": "Test Journal",
                "citations": 50
            }
        ]
        
        scored = await orchestrator._score_results("machine learning", results)
        
        assert "results" in scored
        assert "scores" in scored
        assert len(scored["results"]) == 1
        
        # Check that scores were added
        result = scored["results"][0]
        assert "_scores" in result
        assert "relevance" in result["_scores"]
        assert "completeness" in result["_scores"]
        assert "source_quality" in result["_scores"]
        assert "overall" in result["_scores"]
    
    @pytest.mark.asyncio
    async def test_cache_functionality(self, orchestrator, sample_query):
        """Test caching mechanism"""
        # First execution
        events1 = []
        async for event in orchestrator.process_query(sample_query):
            events1.append(event)
            if event.get("event_type") == "complete":
                break
        
        # Second execution (should hit cache)
        events2 = []
        async for event in orchestrator.process_query(sample_query):
            events2.append(event)
            if event.get("event_type") == "cache_hit":
                break
        
        # Check for cache hit
        cache_hits = [e for e in events2 if e.get("event_type") == "cache_hit"]
        assert len(cache_hits) > 0, "Should have cache hit on second query"
    
    @pytest.mark.asyncio
    async def test_retry_mechanism(self, orchestrator):
        """Test retry logic with exponential backoff"""
        # Create a failing step
        failing_step = {
            "id": "test_fail",
            "agent": "nonexistent",
            "action": "test",
            "parameters": {}
        }
        
        with pytest.raises(Exception):
            await orchestrator._execute_step_with_retry(failing_step, [])
        
        # Check that retries were attempted
        # This would need more detailed mocking to verify retry count
    
    def test_parallel_group_identification(self, orchestrator):
        """Test identification of parallel task groups"""
        steps = [
            {"id": "A", "dependencies": []},
            {"id": "B", "dependencies": []},
            {"id": "C", "dependencies": ["A"]},
            {"id": "D", "dependencies": ["B"]},
            {"id": "E", "dependencies": ["C", "D"]}
        ]
        
        groups = orchestrator._identify_parallel_groups(steps)
        
        assert len(groups) == 3, "Should identify 3 parallel groups"
        assert set(groups[0]) == {"A", "B"}, "A and B should be parallel"
        assert set(groups[1]) == {"C", "D"}, "C and D should be parallel"
        assert set(groups[2]) == {"E"}, "E should be alone"
    
    def test_efficiency_calculation(self, orchestrator):
        """Test parallel efficiency calculation"""
        plan = {"steps": [{"id": "1"}, {"id": "2"}, {"id": "3"}]}
        
        # Perfect parallel execution
        efficiency = orchestrator._calculate_efficiency(plan, 2.0)
        assert efficiency <= 100, "Efficiency should not exceed 100%"
        
        # Sequential execution
        efficiency = orchestrator._calculate_efficiency(plan, 6.0)
        assert efficiency < 100, "Sequential execution should have lower efficiency"


class TestQueryAnalyzer:
    """Test Query Analyzer functionality"""
    
    @pytest.mark.asyncio
    async def test_intent_detection(self, query_analyzer):
        """Test intent detection"""
        queries = {
            "find papers about deep learning": "search",
            "summarize recent AI advances": "summarize",
            "analyze the impact of transformers": "analyze",
            "compare BERT and GPT models": "compare",
            "explain how attention works": "explain",
            "verify this citation": "verify",
            "explore trends in ML": "explore"
        }
        
        for query, expected_intent in queries.items():
            analysis = await query_analyzer.analyze(query)
            intent = analysis["intent"]["primary"]
            assert intent == expected_intent, f"Query '{query}' should have intent '{expected_intent}', got '{intent}'"
    
    @pytest.mark.asyncio
    async def test_complexity_assessment(self, query_analyzer):
        """Test complexity assessment"""
        simple_query = "What is machine learning?"
        complex_query = "Analyze the relationship between transformer architectures and their impact on computational linguistics, considering both theoretical frameworks and practical implementations in multilingual NLP systems"
        
        simple_analysis = await query_analyzer.analyze(simple_query)
        complex_analysis = await query_analyzer.analyze(complex_query)
        
        assert simple_analysis["complexity"] == "simple"
        assert complex_analysis["complexity"] == "complex"
    
    @pytest.mark.asyncio
    async def test_entity_extraction(self, query_analyzer):
        """Test entity extraction"""
        query = "Papers by Yann LeCun about deep learning published in 2023 at NYU"
        
        analysis = await query_analyzer.analyze(query)
        entities = analysis["entities"]
        
        assert len(entities["dates"]) > 0, "Should extract date"
        assert "2023" in str(entities["dates"])
        
        # Topics should be extracted
        assert len(entities["topics"]) > 0
    
    @pytest.mark.asyncio
    async def test_requirements_identification(self, query_analyzer):
        """Test requirements identification"""
        query = "Compare and analyze citation networks for transformer papers"
        
        analysis = await query_analyzer.analyze(query)
        requirements = analysis["requirements"]
        
        assert requirements["needs_comparison"] == True
        assert requirements["needs_analysis"] == True
        assert requirements["needs_graph_analysis"] == True
    
    @pytest.mark.asyncio
    async def test_time_estimation(self, query_analyzer):
        """Test processing time estimation"""
        simple_query = "What is NLP?"
        complex_query = "Comprehensive analysis of deep learning evolution with statistical comparison"
        
        simple_analysis = await query_analyzer.analyze(simple_query)
        complex_analysis = await query_analyzer.analyze(complex_query)
        
        assert simple_analysis["estimated_time"] < complex_analysis["estimated_time"]
        assert simple_analysis["estimated_time"] > 0
        assert complex_analysis["estimated_time"] > 0


class TestResponseFormatter:
    """Test Response Formatter functionality"""
    
    @pytest.mark.asyncio
    async def test_audience_adaptation(self, response_formatter, sample_response):
        """Test adaptation for different audiences"""
        audiences = [
            AudienceType.TECHNICAL,
            AudienceType.EXECUTIVE,
            AudienceType.GENERAL
        ]
        
        for audience in audiences:
            formatted = await response_formatter.format_response({
                "response": sample_response,
                "audience": audience.value,
                "format": "summary",
                "detail_level": "medium",
                "citation_style": "apa"
            })
            
            assert "content" in formatted
            assert "_metadata" in formatted
            assert formatted["_metadata"]["audience"] == audience.value
    
    @pytest.mark.asyncio
    async def test_format_types(self, response_formatter, sample_response):
        """Test different format types"""
        formats = [
            FormatType.SUMMARY,
            FormatType.BULLET_POINTS,
            FormatType.REPORT,
            FormatType.PRESENTATION
        ]
        
        for format_type in formats:
            formatted = await response_formatter.format_response({
                "response": sample_response,
                "audience": "general",
                "format": format_type.value,
                "detail_level": "medium",
                "citation_style": "apa"
            })
            
            assert "formatted_content" in formatted
            assert formatted["formatted_content"]["type"] == format_type.value
    
    @pytest.mark.asyncio
    async def test_citation_formatting(self, response_formatter, sample_response):
        """Test citation formatting styles"""
        styles = [
            CitationStyle.APA,
            CitationStyle.MLA,
            CitationStyle.CHICAGO,
            CitationStyle.IEEE
        ]
        
        for style in styles:
            formatted = await response_formatter.format_response({
                "response": sample_response,
                "audience": "academic",
                "format": "detailed",
                "detail_level": "high",
                "citation_style": style.value
            })
            
            assert "citations" in formatted
            assert len(formatted["citations"]) > 0
            
            # Check format-specific patterns
            citation = formatted["citations"][0]
            if style == CitationStyle.APA:
                assert "(" in citation and ")" in citation  # Year in parentheses
            elif style == CitationStyle.IEEE:
                assert "[" in citation  # Numbered references
    
    @pytest.mark.asyncio
    async def test_detail_levels(self, response_formatter, sample_response):
        """Test different detail levels"""
        levels = [DetailLevel.LOW, DetailLevel.MEDIUM, DetailLevel.HIGH]
        
        formatted_contents = []
        for level in levels:
            formatted = await response_formatter.format_response({
                "response": sample_response,
                "audience": "general",
                "format": "summary",
                "detail_level": level.value,
                "citation_style": "plain"
            })
            
            formatted_contents.append(formatted.get("detail_adjusted", {}))
        
        # Low detail should have less content than high detail
        assert len(str(formatted_contents[0])) <= len(str(formatted_contents[2]))
    
    @pytest.mark.asyncio
    async def test_export_formats(self, response_formatter, sample_response):
        """Test export functionality"""
        formatted = await response_formatter.format_response({
            "response": sample_response,
            "audience": "general",
            "format": "summary",
            "detail_level": "medium",
            "citation_style": "apa"
        })
        
        export_formats = ["markdown", "html", "json", "text"]
        
        for export_format in export_formats:
            exported = await response_formatter.export_formatted({
                "formatted_content": formatted.get("formatted_content", {}),
                "export_format": export_format
            })
            
            assert "content" in exported
            assert "metadata" in exported
            assert exported["format"] == export_format
            assert len(exported["content"]) > 0
    
    def test_key_findings_extraction(self, response_formatter):
        """Test extraction of key findings"""
        content = """
        1. Machine learning has advanced significantly.
        2. Transformers are the dominant architecture.
        Research found that attention mechanisms are crucial.
        The study showed that larger models perform better.
        It was discovered that pre-training is essential.
        """
        
        findings = response_formatter._extract_key_findings(content)
        
        assert len(findings) > 0
        assert any("found that" in f.lower() or "showed that" in f.lower() for f in findings)
    
    def test_presentation_slide_generation(self, response_formatter, sample_response):
        """Test presentation slide generation"""
        content = sample_response["synthesis"]
        sources = sample_response["sources"]
        
        presentation = response_formatter._format_as_presentation(content, sources)
        
        assert "slides" in presentation
        assert len(presentation["slides"]) >= 4  # Title, overview, content, conclusion
        assert presentation["slides"][0]["type"] == "title"
        assert presentation["slides"][-1]["type"] == "references"


class TestIntegration:
    """Integration tests for the enhanced system"""
    
    @pytest.mark.asyncio
    async def test_full_pipeline(self, orchestrator, query_analyzer, response_formatter, sample_query):
        """Test the full processing pipeline"""
        # Analyze query
        analysis = await query_analyzer.analyze(
            sample_query["query"],
            sample_query["parameters"]
        )
        
        assert analysis["confidence"] > 0
        
        # Process with orchestrator
        raw_results = None
        async for event in orchestrator.process_query(sample_query):
            if event.get("event_type") == "result":
                raw_results = event.get("data", {})
                break
        
        assert raw_results is not None
        
        # Format response
        if raw_results:
            formatted = await response_formatter.format_response({
                "response": raw_results,
                "audience": "technical",
                "format": "report",
                "detail_level": "high",
                "citation_style": "ieee"
            })
            
            assert "formatted_content" in formatted
            assert "citations" in formatted
            assert "_metadata" in formatted
    
    @pytest.mark.asyncio
    async def test_performance_improvement(self, orchestrator):
        """Test that parallel execution improves performance"""
        import time
        
        query = {
            "query": "test query",
            "parameters": {"max_results": 5},
            "session_id": "perf_test"
        }
        
        # Measure execution time
        start = time.time()
        events = []
        async for event in orchestrator.process_query(query):
            events.append(event)
            if event.get("event_type") == "complete":
                break
        elapsed = time.time() - start
        
        # Check for parallel execution indicators
        parallel_events = [e for e in events if "parallel" in e.get("event_type", "")]
        assert len(parallel_events) > 0, "Should show parallel execution"
        
        # Check performance metrics
        perf_metrics = orchestrator.get_performance_metrics()
        assert len(perf_metrics) > 0


@pytest.mark.asyncio
async def test_websocket_flow():
    """Test WebSocket communication flow"""
    from app.main_enhanced import app
    from fastapi.testclient import TestClient
    
    client = TestClient(app)
    
    # Test health endpoint
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "enhanced" in data["components"]["orchestrator"]
    
    # Test agents endpoint
    response = client.get("/api/agents")
    assert response.status_code == 200
    data = response.json()
    assert "agents" in data
    assert "capabilities" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])