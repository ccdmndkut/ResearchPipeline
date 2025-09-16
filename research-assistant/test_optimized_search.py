#!/usr/bin/env python3
"""
Test script for optimized search agent
Tests the improved prompts and parsing logic
"""
import asyncio
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.agents.search_agent import SearchAgent
from app.settings import settings

async def test_search_optimization():
    """Test the optimized search functionality"""
    print("🧪 Testing Optimized Search Agent")
    print("=" * 50)

    # Initialize the search agent
    agent = SearchAgent()

    # Test cases with different search types
    test_cases = [
        {
            "query": "Joe Burrow injury status 2024",
            "search_type": "general",
            "description": "General search about current events"
        },
        {
            "query": "machine learning transformers attention mechanism",
            "search_type": "academic",
            "description": "Academic search for research papers"
        },
        {
            "query": "OpenAI GPT-4 latest features",
            "search_type": "technical",
            "description": "Technical documentation search"
        },
        {
            "query": "Federal Reserve interest rate decision",
            "search_type": "news",
            "description": "Recent news search"
        }
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔍 Test {i}: {test_case['description']}")
        print(f"Query: {test_case['query']}")
        print(f"Type: {test_case['search_type']}")
        print("-" * 30)

        try:
            result = await agent.execute("search", {
                "query": test_case["query"],
                "search_type": test_case["search_type"],
                "max_results": 5
            })

            # Analyze the results
            print(f"✅ Search completed successfully")
            print(f"📊 Results:")
            print(f"   • Total results: {result.get('total_results', 0)}")
            print(f"   • Synthesis length: {len(result.get('synthesis', ''))}")
            print(f"   • Has meaningful content: {len(result.get('synthesis', '')) > 100}")

            # Show first result if available
            if result.get('results') and len(result['results']) > 0:
                first_result = result['results'][0]
                print(f"   • First result title: {first_result.get('title', 'No title')[:60]}...")
                print(f"   • First result type: {first_result.get('type', 'Unknown')}")

            # Show synthesis preview
            if result.get('synthesis'):
                synthesis_preview = result['synthesis'][:200].replace('\n', ' ')
                print(f"   • Synthesis preview: {synthesis_preview}...")

            # Check for success indicators
            success_indicators = [
                len(result.get('synthesis', '')) > 100,
                result.get('total_results', 0) > 0,
                'search' in result.get('synthesis', '').lower() or 'information' in result.get('synthesis', '').lower()
            ]

            success_score = sum(success_indicators) / len(success_indicators) * 100
            print(f"   • Success score: {success_score:.0f}%")

            if success_score >= 70:
                print("   ✅ Test PASSED")
            else:
                print("   ⚠️  Test needs improvement")

        except Exception as e:
            print(f"❌ Search failed: {str(e)}")
            import traceback
            traceback.print_exc()

        print()

    print("=" * 50)
    print("🏁 Testing Complete")

async def test_prompt_availability():
    """Test if optimized prompts are available"""
    print("🔧 Testing Prompt Availability")
    print("-" * 30)

    try:
        from optimized_search_prompts import get_web_search_system_prompt
        print("✅ Optimized prompts are available")

        system_prompt = get_web_search_system_prompt()
        print(f"   • System prompt length: {len(system_prompt)}")
        print(f"   • Contains 'search': {'search' in system_prompt.lower()}")
        print(f"   • Contains 'current': {'current' in system_prompt.lower()}")

    except ImportError as e:
        print(f"❌ Optimized prompts not available: {e}")

async def main():
    """Main test function"""
    print("🚀 OpenAI Web Search Optimization Test Suite")
    print(f"API Key configured: {'Yes' if settings.OPENAI_API_KEY else 'No'}")
    print(f"Agent Model: {settings.AGENT_MODEL}")
    print()

    # Test prompt availability first
    await test_prompt_availability()
    print()

    # Run the main search tests
    await test_search_optimization()

if __name__ == "__main__":
    asyncio.run(main())