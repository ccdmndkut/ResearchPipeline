from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import json
import asyncio
from pathlib import Path

from app.settings import settings
from app.orchestrator.orchestrator import ResearchOrchestrator
from app.utils.logging_config import setup_logging

logger = setup_logging(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Research Assistant API")
    yield
    logger.info("Shutting down Research Assistant API")

app = FastAPI(
    title="Research Assistant API",
    description="Multi-agent system for academic research assistance",
    version="1.0.0",
    lifespan=lifespan
)

app.mount("/static", StaticFiles(directory="static"), name="static")

orchestrator = ResearchOrchestrator()

@app.get("/")
async def root():
    with open("app/templates/index.html") as f:
        return HTMLResponse(content=f.read())

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "agents": orchestrator.get_available_agents(),
        "tools": orchestrator.get_available_tools()
    }

@app.websocket("/ws")
async def research_websocket(websocket: WebSocket):
    await websocket.accept()
    logger.info("WebSocket connection established")

    try:
        while True:
            data = await websocket.receive_text()
            request = json.loads(data)

            await websocket.send_json({
                "event_type": "acknowledgment",
                "message": f"Processing request: {request.get('query', 'No query provided')}"
            })

            async for event in orchestrator.process_query(request):
                await websocket.send_json(event)
                await asyncio.sleep(0.01)

            await websocket.send_json({
                "event_type": "complete",
                "message": "Research query completed"
            })

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await websocket.send_json({
            "event_type": "error",
            "message": str(e)
        })

@app.post("/api/research")
async def research_query(query: dict):
    """
    Synchronous endpoint for research queries
    """
    results = []
    async for event in orchestrator.process_query(query):
        results.append(event)

    return {
        "query": query,
        "results": results,
        "status": "completed"
    }

@app.get("/api/agents")
async def list_agents():
    """
    List all available agents and their capabilities
    """
    return orchestrator.get_agent_descriptions()

@app.get("/api/tools")
async def list_tools():
    """
    List all available tools and their parameters
    """
    return orchestrator.get_tool_descriptions()

@app.get("/api/test")
async def test_search():
    """
    Test endpoint to verify search functionality
    """
    from app.agents import SearchAgent

    agent = SearchAgent()
    try:
        # Simple test search
        result = await agent.execute("search", {
            "query": "machine learning",
            "databases": ["arxiv"],
            "max_results": 5
        })
        return {"status": "success", "result": result}
    except Exception as e:
        return {"status": "error", "error": str(e)}
    finally:
        if agent.session:
            await agent.session.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )