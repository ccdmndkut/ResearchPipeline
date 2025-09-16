"""
Test OpenAI API connection
"""
import asyncio
import os
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv('.env')

async def test_openai():
    """Test OpenAI API connection"""

    # Get API key from environment
    api_key = os.getenv('OPENAI_API_KEY')

    if not api_key or api_key == 'sk-xxxxx':
        print("❌ No valid OpenAI API key found in .env file")
        print("Please ensure OPENAI_API_KEY is set in .env file")
        return False

    print(f"✓ API Key found: {api_key[:7]}...{api_key[-4:]}")

    # Initialize OpenAI client
    client = openai.AsyncOpenAI(api_key=api_key)

    try:
        print("\nTesting OpenAI API connection...")

        # Simple test call
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",  # Using cheaper model for test
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'Hello, API is working!' in exactly 5 words."}
            ],
            max_tokens=50,
            temperature=0
        )

        result = response.choices[0].message.content
        print(f"✓ Response: {result}")

        # Test with a research-related query
        print("\nTesting research query expansion...")
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Expand the search query with related terms for academic search. Reply with comma-separated terms only."},
                {"role": "user", "content": "machine learning"}
            ],
            max_tokens=100,
            temperature=0.3
        )

        expanded = response.choices[0].message.content
        print(f"✓ Query expansion: {expanded}")

        # Test model listing
        print("\nChecking available models...")
        models = await client.models.list()
        gpt_models = [m.id for m in models.data if 'gpt' in m.id.lower()]
        print(f"✓ Available GPT models: {', '.join(gpt_models[:5])}")

        print("\n✅ OpenAI API is working correctly!")
        return True

    except openai.AuthenticationError as e:
        print(f"\n❌ Authentication Error: {e}")
        print("Please check your API key is valid")
        return False

    except openai.RateLimitError as e:
        print(f"\n❌ Rate Limit Error: {e}")
        print("API key is valid but you've hit rate limits")
        return False

    except openai.APIError as e:
        print(f"\n❌ API Error: {e}")
        return False

    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_search_agent():
    """Test the search agent with OpenAI"""
    from app.agents.search_agent import SearchAgent

    print("\n" + "="*50)
    print("Testing Search Agent with OpenAI")
    print("="*50)

    agent = SearchAgent()

    try:
        # Test query expansion
        print("\nTesting query expansion...")
        result = await agent.expand_query({"query": "neural networks"})
        print(f"✓ Original: {result['original']}")
        print(f"✓ Expanded: {result['expanded']}")

        # Test search
        print("\nTesting search with expanded query...")
        search_result = await agent.execute("search", {
            "query": "neural networks",
            "databases": ["arxiv"],
            "max_results": 3
        })

        print(f"✓ Found {search_result['total_results']} papers")
        print(f"✓ Expanded query used: {search_result.get('expanded_query', 'N/A')}")

        for i, paper in enumerate(search_result.get('papers', [])[:2], 1):
            print(f"\nPaper {i}:")
            print(f"  Title: {paper.get('title', 'N/A')}")
            print(f"  Year: {paper.get('year', 'N/A')}")

        print("\n✅ Search Agent is working with OpenAI!")
        return True

    except Exception as e:
        print(f"\n❌ Search Agent Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if hasattr(agent, 'session') and agent.session:
            await agent.session.close()

async def main():
    """Run all tests"""
    print("Testing OpenAI Integration")
    print("="*50)

    # Test basic OpenAI connection
    openai_works = await test_openai()

    if openai_works:
        # Test search agent
        await test_search_agent()
    else:
        print("\n⚠️  Fix OpenAI API connection first before testing agents")

if __name__ == "__main__":
    asyncio.run(main())