"""
Test the full Research Assistant system
"""
import asyncio
import sys
sys.path.insert(0, '.')

from app.orchestrator.orchestrator import ResearchOrchestrator

async def test_orchestrator():
    """Test the orchestrator with a simple query"""

    orchestrator = ResearchOrchestrator()

    request = {
        "query": "machine learning",
        "parameters": {
            "databases": ["arxiv"],
            "max_results": 3,
            "action": "search"
        },
        "session_id": "test_session"
    }

    print("Testing Research Assistant Orchestrator")
    print("="*50)
    print(f"Query: {request['query']}")
    print(f"Databases: {request['parameters']['databases']}")
    print(f"Max results: {request['parameters']['max_results']}")
    print("="*50)

    events = []

    try:
        async for event in orchestrator.process_query(request):
            event_type = event.get('event_type')
            message = event.get('message')
            status = event.get('status')

            print(f"\n[{event_type}] {message}")

            if event_type == 'result':
                data = event.get('data', {})
                sources = data.get('sources', [])
                synthesis = data.get('synthesis', '')

                print(f"\nSynthesis: {synthesis[:200]}...")
                print(f"\nFound {len(sources)} papers:")

                for i, paper in enumerate(sources[:3], 1):
                    print(f"\n{i}. {paper.get('title', 'No title')}")
                    print(f"   Authors: {', '.join(paper.get('authors', [])[:3])}")
                    print(f"   Year: {paper.get('year', 'N/A')}")
                    print(f"   Abstract: {paper.get('abstract', '')[:150]}...")

            events.append(event)

            if event_type == 'complete':
                break

        print("\n[SUCCESS] Orchestrator test completed successfully!")
        return True

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_orchestrator())
    if result:
        print("\nThe Research Assistant is fully operational!")
        print("You can now use it at http://localhost:8000")
    else:
        print("\nThere were errors. Please check the configuration.")