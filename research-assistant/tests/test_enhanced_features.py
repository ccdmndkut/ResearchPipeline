import pytest
from unittest.mock import AsyncMock, patch
from app.orchestrator.enhanced_orchestrator import EnhancedOrchestrator
from app.utils.redis_cache import ResearchCache
from app.feedback.feedback_system import FeedbackLoop
from app.experiments.ab_testing import ABTestingFramework

@pytest.fixture
def orchestrator():
    """Fixture for the EnhancedOrchestrator."""
    return EnhancedOrchestrator()

@pytest.mark.asyncio
async def test_redis_caching(orchestrator: EnhancedOrchestrator):
    """Tests the Redis caching functionality."""
    with patch.object(ResearchCache, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = {"result": "cached_data"}
        request = {
            "query": "test query",
            "parameters": {},
            "session_id": "test_session"
        }
        
        events = [event async for event in orchestrator.process_query(request)]
        
        assert any(event['event_type'] == 'cache_hit' for event in events)
        assert any(event['data']['result'] == 'cached_data' for event in events if event['event_type'] == 'result')

@pytest.mark.asyncio
async def test_feedback_loop(orchestrator: EnhancedOrchestrator):
    """Tests the feedback loop functionality."""
    with patch.object(FeedbackLoop, 'store_feedback', new_callable=AsyncMock) as mock_store:
        session_id = "test_session"
        feedback = {"rating": 5, "comment": "Excellent!"}
        
        await orchestrator.feedback_loop.store_feedback(session_id, feedback)
        
        mock_store.assert_called_once_with(session_id, feedback)

def test_ab_testing_framework():
    """Tests the A/B testing framework."""
    framework = ABTestingFramework()
    user_id = "test_user"
    
    # Test feature flag access
    assert framework.should_use_feature('parallel_processing', user_id) == True
    assert framework.should_use_feature('new_ui', user_id) == False