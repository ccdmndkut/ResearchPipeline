"""
Enhanced FastAPI application with improved WebSocket handling and feature flags
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import json
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

from app.settings import settings
from app.orchestrator.enhanced_orchestrator import EnhancedOrchestrator
from app.orchestrator.orchestrator import ResearchOrchestrator
from app.agents.response_formatter import (
    ResponseFormatterAgent,
    AudienceType,
    FormatType,
    CitationStyle
)
from app.utils.logging_config import setup_logging

logger = setup_logging(__name__)

# Feature flags
FEATURE_FLAGS = {
    "enhanced_orchestrator": True,
    "response_formatter": True,
    "parallel_processing": True,
    "quality_scoring": True,
    "caching": True,
    "metrics_tracking": True,
    "a_b_testing": False,  # Enable when ready
    "feedback_loop": False  # Enable when ready
}


class ConnectionManager:
    """Manages WebSocket connections with improved error handling"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.session_data: Dict[str, Dict[str, Any]] = {}
        
    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept new WebSocket connection"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.session_data[client_id] = {
            "connected_at": datetime.now(),
            "request_count": 0,
            "last_activity": datetime.now()
        }
        logger.info(f"Client {client_id} connected")
        
    def disconnect(self, client_id: str):
        """Remove WebSocket connection"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        if client_id in self.session_data:
            del self.session_data[client_id]
        logger.info(f"Client {client_id} disconnected")
        
    async def send_personal_message(self, message: str, client_id: str):
        """Send message to specific client"""
        if client_id in self.active_connections:
            websocket = self.active_connections[client_id]
            await websocket.send_text(message)
            self.session_data[client_id]["last_activity"] = datetime.now()
            
    async def broadcast(self, message: str, exclude: Optional[str] = None):
        """Broadcast message to all connected clients"""
        disconnected_clients = []
        for client_id, connection in self.active_connections.items():
            if client_id != exclude:
                try:
                    await connection.send_text(message)
                except:
                    disconnected_clients.append(client_id)
                    
        # Clean up disconnected clients
        for client_id in disconnected_clients:
            self.disconnect(client_id)
            
    def get_active_sessions(self) -> List[Dict[str, Any]]:
        """Get information about active sessions"""
        return [
            {
                "client_id": client_id,
                "connected_at": data["connected_at"].isoformat(),
                "request_count": data["request_count"],
                "last_activity": data["last_activity"].isoformat()
            }
            for client_id, data in self.session_data.items()
        ]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting Enhanced Research Assistant API")
    logger.info(f"Feature flags: {FEATURE_FLAGS}")
    
    # Initialize services
    app.state.connection_manager = ConnectionManager()
    
    if FEATURE_FLAGS["enhanced_orchestrator"]:
        app.state.orchestrator = EnhancedOrchestrator()
        logger.info("Using Enhanced Orchestrator with parallel processing")
    else:
        app.state.orchestrator = ResearchOrchestrator()
        logger.info("Using Standard Orchestrator")
        
    if FEATURE_FLAGS["response_formatter"]:
        app.state.formatter = ResponseFormatterAgent()
        logger.info("Response Formatter Agent enabled")
        
    yield
    
    logger.info("Shutting down Enhanced Research Assistant API")


app = FastAPI(
    title="Enhanced Research Assistant API",
    description="Multi-agent system with parallel processing and adaptive formatting",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    """Serve the main application page"""
    with open("app/templates/index.html") as f:
        return HTMLResponse(content=f.read())


@app.get("/health")
async def health_check(request: Request):
    """Enhanced health check with system status"""
    orchestrator = request.app.state.orchestrator
    
    health_data = {
        "status": "healthy",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "features": FEATURE_FLAGS,
        "agents": orchestrator.agents.keys() if hasattr(orchestrator, 'agents') else [],
        "tools": orchestrator.tools.keys() if hasattr(orchestrator, 'tools') else [],
        "active_sessions": len(request.app.state.connection_manager.active_connections)
    }
    
    # Add performance metrics if available
    if FEATURE_FLAGS["metrics_tracking"] and hasattr(orchestrator, 'get_performance_metrics'):
        health_data["metrics"] = orchestrator.get_performance_metrics()
        
    return health_data


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Enhanced WebSocket endpoint with connection management"""
    client_id = str(uuid.uuid4())
    manager = app.state.connection_manager
    
    await manager.connect(websocket, client_id)
    
    try:
        await websocket.send_json({
            "event_type": "connection",
            "message": "Connected to Enhanced Research Assistant",
            "client_id": client_id,
            "features": FEATURE_FLAGS
        })
        
        while True:
            # Receive message with timeout
            try:
                data = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=300.0  # 5 minute timeout
                )
            except asyncio.TimeoutError:
                await websocket.send_json({
                    "event_type": "ping",
                    "message": "Keep-alive ping"
                })
                continue
                
            request = json.loads(data)
            
            # Update session data
            manager.session_data[client_id]["request_count"] += 1
            manager.session_data[client_id]["last_activity"] = datetime.now()
            
            # Process request
            await process_research_request(websocket, request, client_id)
            
    except WebSocketDisconnect:
        manager.disconnect(client_id)
        logger.info(f"WebSocket disconnected for client {client_id}")
    except Exception as e:
        logger.error(f"WebSocket error for client {client_id}: {str(e)}")
        await websocket.send_json({
            "event_type": "error",
            "message": str(e)
        })
        manager.disconnect(client_id)


async def process_research_request(
    websocket: WebSocket,
    request: Dict[str, Any],
    client_id: str
):
    """Process research request with enhanced features"""
    
    orchestrator = app.state.orchestrator
    formatter = app.state.formatter if FEATURE_FLAGS["response_formatter"] else None
    
    # Add client_id to request
    request["client_id"] = client_id
    
    # Send acknowledgment
    await websocket.send_json({
        "event_type": "acknowledgment",
        "message": f"Processing request: {request.get('query', 'No query provided')}",
        "request_id": request.get("session_id", "unknown")
    })
    
    try:
        # Process with orchestrator
        results_collected = []
        async for event in orchestrator.process_query(request):
            # Send event to client
            await websocket.send_json(event)
            
            # Collect results for formatting
            if event.get("event_type") == "result":
                results_collected.append(event)
            
            # Small delay to prevent overwhelming client
            await asyncio.sleep(0.01)
        
        # Format response if enabled
        if FEATURE_FLAGS["response_formatter"] and formatter and results_collected:
            await format_and_send_response(
                websocket,
                formatter,
                results_collected[-1],  # Use final result
                request
            )
        
        # Send completion event
        await websocket.send_json({
            "event_type": "complete",
            "message": "Research query completed",
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        await websocket.send_json({
            "event_type": "error",
            "message": f"Processing error: {str(e)}",
            "timestamp": datetime.now().isoformat()
        })


async def format_and_send_response(
    websocket: WebSocket,
    formatter: ResponseFormatterAgent,
    result: Dict[str, Any],
    request: Dict[str, Any]
):
    """Format and send response based on audience"""
    
    try:
        # Get formatting parameters from request
        audience = AudienceType(request.get("audience", "general"))
        format_type = FormatType(request.get("format", "summary"))
        citation_style = CitationStyle(request.get("citation_style", "apa"))
        
        # Format response
        formatted = await formatter.format_response(
            result.get("data", {}),
            audience=audience,
            format_type=format_type,
            citation_style=citation_style
        )
        
        # Send formatted response
        await websocket.send_json({
            "event_type": "formatted_response",
            "message": "Response formatted for audience",
            "data": {
                "content": formatted.content,
                "metadata": formatted.metadata,
                "citations": formatted.citations,
                "key_insights": formatted.key_insights,
                "visual_suggestions": formatted.visual_suggestions,
                "related_topics": formatted.related_topics,
                "confidence_score": formatted.confidence_score,
                "reading_time": formatted.reading_time
            },
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Formatting error: {str(e)}")
        # Fail gracefully - user still has raw results


@app.post("/api/research")
async def research_query(query_data: Dict[str, Any], request: Request):
    """REST endpoint for research queries with enhanced processing"""
    
    orchestrator = request.app.state.orchestrator
    formatter = request.app.state.formatter if FEATURE_FLAGS["response_formatter"] else None
    
    # Process query
    results = []
    formatted_response = None
    
    try:
        async for event in orchestrator.process_query(query_data):
            results.append(event)
            
            # Capture final result for formatting
            if event.get("event_type") == "result" and formatter:
                formatted_response = await formatter.format_response(
                    event.get("data", {}),
                    audience=AudienceType(query_data.get("audience", "general")),
                    format_type=FormatType(query_data.get("format", "summary"))
                )
        
        response_data = {
            "query": query_data,
            "results": results,
            "status": "completed",
            "timestamp": datetime.now().isoformat()
        }
        
        if formatted_response:
            response_data["formatted"] = {
                "content": formatted_response.content,
                "insights": formatted_response.key_insights,
                "citations": formatted_response.citations
            }
            
        return response_data
        
    except Exception as e:
        logger.error(f"API error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/features")
async def get_features():
    """Get current feature flags"""
    return {
        "features": FEATURE_FLAGS,
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/features")
async def update_features(updates: Dict[str, bool]):
    """Update feature flags (admin endpoint)"""
    # TODO: Add authentication for production
    
    for key, value in updates.items():
        if key in FEATURE_FLAGS:
            FEATURE_FLAGS[key] = value
            logger.info(f"Feature flag '{key}' set to {value}")
            
    return {
        "features": FEATURE_FLAGS,
        "updated": list(updates.keys()),
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/sessions")
async def get_active_sessions(request: Request):
    """Get information about active WebSocket sessions"""
    manager = request.app.state.connection_manager
    return {
        "sessions": manager.get_active_sessions(),
        "total": len(manager.active_connections),
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/metrics")
async def get_metrics(request: Request):
    """Get performance metrics"""
    
    if not FEATURE_FLAGS["metrics_tracking"]:
        return {"error": "Metrics tracking is disabled"}
        
    orchestrator = request.app.state.orchestrator
    
    if hasattr(orchestrator, 'get_performance_metrics'):
        metrics = orchestrator.get_performance_metrics()
        return {
            "metrics": metrics,
            "timestamp": datetime.now().isoformat()
        }
    else:
        return {"error": "Metrics not available for current orchestrator"}


@app.get("/api/agents")
async def list_agents(request: Request):
    """List available agents with descriptions"""
    orchestrator = request.app.state.orchestrator
    
    if hasattr(orchestrator, 'get_agent_descriptions'):
        return orchestrator.get_agent_descriptions()
    else:
        return {"agents": list(orchestrator.agents.keys())}


@app.get("/api/tools")
async def list_tools(request: Request):
    """List available tools with descriptions"""
    orchestrator = request.app.state.orchestrator
    
    if hasattr(orchestrator, 'get_tool_descriptions'):
        return orchestrator.get_tool_descriptions()
    else:
        return {"tools": list(orchestrator.tools.keys())}


@app.post("/api/format")
async def format_content(
    content_data: Dict[str, Any],
    request: Request
):
    """Format content for specific audience"""
    
    if not FEATURE_FLAGS["response_formatter"]:
        raise HTTPException(
            status_code=400,
            detail="Response formatter is disabled"
        )
        
    formatter = request.app.state.formatter
    
    try:
        formatted = await formatter.format_response(
            content_data.get("results", {}),
            audience=AudienceType(content_data.get("audience", "general")),
            format_type=FormatType(content_data.get("format", "summary")),
            citation_style=CitationStyle(content_data.get("citation_style", "apa"))
        )
        
        return {
            "content": formatted.content,
            "metadata": formatted.metadata,
            "citations": formatted.citations,
            "insights": formatted.key_insights,
            "confidence": formatted.confidence_score,
            "reading_time": formatted.reading_time
        }
        
    except Exception as e:
        logger.error(f"Formatting error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/test")
async def test_system(request: Request):
    """Test endpoint to verify system functionality"""
    
    test_results = {
        "timestamp": datetime.now().isoformat(),
        "tests": {}
    }
    
    # Test orchestrator
    orchestrator = request.app.state.orchestrator
    test_results["tests"]["orchestrator"] = {
        "type": "Enhanced" if FEATURE_FLAGS["enhanced_orchestrator"] else "Standard",
        "status": "ready"
    }
    
    # Test agents
    if hasattr(orchestrator, 'agents'):
        test_results["tests"]["agents"] = {
            "count": len(orchestrator.agents),
            "list": list(orchestrator.agents.keys())
        }
    
    # Test formatter
    if FEATURE_FLAGS["response_formatter"]:
        formatter = request.app.state.formatter
        test_results["tests"]["formatter"] = {
            "status": "ready",
            "audiences": [a.value for a in AudienceType],
            "formats": [f.value for f in FormatType]
        }
    
    # Test WebSocket connections
    manager = request.app.state.connection_manager
    test_results["tests"]["websocket"] = {
        "active_connections": len(manager.active_connections),
        "sessions": len(manager.session_data)
    }
    
    return test_results


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main_enhanced:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )