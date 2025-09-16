"""
Test script for search functionality
"""
import asyncio
import sys
sys.path.insert(0, '.')

from app.agents.search_agent_simple import SimpleSearchAgent

async def test_search():
    """Test the search agent"""
    agent = SimpleSearchAgent()

    try:
        print("Testing arXiv search for 'machine learning'...")
        result = await agent.execute("search", {
            "query": "machine learning",
            "databases": ["arxiv"],
            "max_results": 3
        })

        print(f"\nFound {result['total_results']} results")

        for i, paper in enumerate(result['papers'], 1):
            print(f"\n{i}. {paper['title']}")
            print(f"   Authors: {', '.join(paper['authors'][:3])}")
            print(f"   Year: {paper['year']}")
            print(f"   URL: {paper['url']}")
            print(f"   Abstract: {paper['abstract'][:200]}...")

        return result

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        if agent.session:
            await agent.session.close()

if __name__ == "__main__":
    result = asyncio.run(test_search())
    print("\nTest completed!")