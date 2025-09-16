#!/usr/bin/env python3
"""
Debug script to test OpenAI web search functionality
"""
import asyncio
import openai
import os
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.settings import settings
from app.agents.search_agent import SearchAgent

async def test_openai_direct():
    """Test OpenAI API directly"""
    print("=== Testing OpenAI API Connection ===")

    client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that can search the web."},
                {"role": "user", "content": "Search the web for information about Joe Burrow's recent performance and injuries in 2024. Provide recent facts with sources."}
            ],
            max_tokens=500,
            temperature=0.3
        )

        print("✓ OpenAI API connection successful")
        print(f"Model: {response.model}")
        print(f"Response: {response.choices[0].message.content}")

        return True

    except Exception as e:
        print(f"✗ OpenAI API error: {e}")
        return False

async def test_search_agent():
    """Test the search agent"""
    print("\n=== Testing Search Agent ===")

    agent = SearchAgent()

    try:
        result = await agent.execute("search", {
            "query": "Joe Burrow injury status 2024",
            "search_type": "general",
            "max_results": 5
        })

        print(f"✓ Search agent executed successfully")
        print(f"Query: {result.get('query')}")
        print(f"Total results: {result.get('total_results', 0)}")
        print(f"Results: {len(result.get('results', []))}")
        print(f"Synthesis length: {len(result.get('synthesis', ''))}")

        if result.get('synthesis'):
            print(f"Synthesis preview: {result['synthesis'][:200]}...")

        if result.get('results'):
            print("\nFirst result:")
            print(result['results'][0])

        return result

    except Exception as e:
        print(f"✗ Search agent error: {e}")
        import traceback
        traceback.print_exc()
        return None

async def test_simple_query():
    """Test a very simple query"""
    print("\n=== Testing Simple Query ===")

    client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": "What is the current date and tell me one recent news headline?"}
            ],
            max_tokens=200,
            temperature=0.3
        )

        content = response.choices[0].message.content
        print(f"✓ Simple query response: {content}")

        # Check if the response contains recent information
        if "2024" in content or "recent" in content.lower():
            print("✓ Response appears to contain current information")
            return True
        else:
            print("⚠ Response may not contain current web information")
            return False

    except Exception as e:
        print(f"✗ Simple query error: {e}")
        return False

async def main():
    """Main debug function"""
    print("Research Assistant Search Debug Tool")
    print("=" * 50)

    print(f"OpenAI API Key: {'✓ Set' if settings.OPENAI_API_KEY else '✗ Missing'}")
    print(f"Agent Model: {settings.AGENT_MODEL}")
    print(f"Orchestrator Model: {settings.ORCHESTRATOR_MODEL}")

    # Test 1: Basic API connection
    api_works = await test_openai_direct()

    # Test 2: Simple query for web search capability
    web_works = await test_simple_query()

    # Test 3: Search agent
    search_result = await test_search_agent()

    print("\n" + "=" * 50)
    print("DEBUG SUMMARY:")
    print(f"• OpenAI API: {'✓' if api_works else '✗'}")
    print(f"• Web Search: {'✓' if web_works else '⚠'}")
    print(f"• Search Agent: {'✓' if search_result and search_result.get('synthesis') else '✗'}")

    if not search_result or not search_result.get('synthesis'):
        print("\n🔍 DEBUGGING RECOMMENDATIONS:")
        print("1. Check if web search is enabled for your OpenAI account")
        print("2. Try using gpt-4o-2024-08-06 model specifically")
        print("3. Verify the search prompts are triggering web search")
        print("4. Check for any API usage limits or restrictions")

if __name__ == "__main__":
    asyncio.run(main())