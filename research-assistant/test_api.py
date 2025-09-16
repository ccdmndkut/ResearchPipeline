"""
Test the Research Assistant API
"""
import asyncio
import json
import websockets

async def test_websocket():
    uri = "ws://localhost:8000/ws"

    query = {
        "query": "machine learning",
        "parameters": {
            "databases": ["arxiv"],
            "max_results": 5,
            "action": "search"
        },
        "session_id": "test_123"
    }

    async with websockets.connect(uri) as websocket:
        # Send query
        await websocket.send(json.dumps(query))

        # Receive responses
        while True:
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                data = json.loads(response)
                print(f"Event: {data.get('event_type')} - {data.get('message')}")

                if data.get('event_type') == 'complete':
                    break

                if data.get('event_type') == 'error':
                    print(f"Error: {data.get('message')}")
                    break

                if data.get('event_type') == 'result':
                    papers = data.get('data', {}).get('sources', [])
                    print(f"\nFound {len(papers)} papers:")
                    for i, paper in enumerate(papers[:3], 1):
                        print(f"{i}. {paper.get('title', 'No title')}")

            except asyncio.TimeoutError:
                print("Timeout waiting for response")
                break
            except Exception as e:
                print(f"Error: {e}")
                break

if __name__ == "__main__":
    asyncio.run(test_websocket())