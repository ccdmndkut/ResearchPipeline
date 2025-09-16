"""
Simplified orchestrator that works without OpenAI API
"""
import asyncio
from typing import AsyncGenerator, Dict, List, Any
from datetime import datetime

from app.agents.search_agent_simple import SimpleSearchAgent
from app.utils.logging_config import setup_logging

logger = setup_logging(__name__)

class SimpleResearchOrchestrator:
    """
    Simplified orchestrator that doesn't require OpenAI
    """

    def __init__(self):
        # Initialize only the simple search agent
        self.agents = {
            "search": SimpleSearchAgent()
        }
        self.active_sessions = {}

    async def process_query(
        self,
        request: Dict[str, Any]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Process a research query and stream events
        """
        session_id = request.get("session_id", datetime.now().isoformat())
        query = request.get("query", "")
        parameters = request.get("parameters", {})

        logger.info(f"Processing query: {query} (session: {session_id})")

        try:
            # Initialize session
            self.active_sessions[session_id] = {
                "query": query,
                "start_time": datetime.now(),
                "events": []
            }

            # Yield start event
            yield self._create_event(
                "start",
                "orchestrator",
                "started",
                f"Processing research query: {query}",
                {"session_id": session_id}
            )

            # Simple execution plan - just search
            plan = {
                "query": query,
                "steps": [
                    {
                        "agent": "search",
                        "action": "search",
                        "parameters": {
                            "query": query,
                            "databases": parameters.get("databases", ["arxiv"]),
                            "max_results": parameters.get("max_results", 10)
                        }
                    }
                ]
            }

            yield self._create_event(
                "plan",
                "orchestrator",
                "completed",
                "Execution plan created",
                {"plan": plan}
            )

            # Execute search
            search_agent = self.agents["search"]

            yield self._create_event(
                "agent_call",
                "search",
                "started",
                "Searching academic databases",
                plan["steps"][0]["parameters"]
            )

            try:
                result = await search_agent.execute("search", plan["steps"][0]["parameters"])

                yield self._create_event(
                    "agent_call",
                    "search",
                    "completed",
                    f"Found {result.get('total_results', 0)} papers",
                    result
                )

                # Final result
                final_result = {
                    "query": query,
                    "synthesis": f"Found {result.get('total_results', 0)} papers related to '{query}'",
                    "sources": result.get("papers", []),
                    "timestamp": datetime.now().isoformat()
                }

                yield self._create_event(
                    "result",
                    "orchestrator",
                    "completed",
                    "Research completed",
                    final_result
                )

            except Exception as e:
                logger.error(f"Search error: {str(e)}")
                yield self._create_event(
                    "error",
                    "search",
                    "error",
                    f"Search error: {str(e)}",
                    {}
                )

            yield self._create_event(
                "complete",
                "orchestrator",
                "completed",
                "Query processing completed",
                {}
            )

        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            yield self._create_event(
                "error",
                "orchestrator",
                "error",
                f"Error: {str(e)}",
                {}
            )

        finally:
            # Clean up session
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]

            # Clean up agent sessions
            for agent in self.agents.values():
                if hasattr(agent, 'session') and agent.session:
                    await agent.session.close()

    def _create_event(
        self,
        event_type: str,
        agent: str,
        status: str,
        message: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a standardized event
        """
        return {
            "event_type": event_type,
            "agent": agent,
            "status": status,
            "message": message,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }

    def get_available_agents(self) -> List[str]:
        """
        Get list of available agents
        """
        return list(self.agents.keys())

    def get_available_tools(self) -> List[str]:
        """
        Get list of available tools
        """
        return []  # No separate tools in simple version

    def get_agent_descriptions(self) -> Dict[str, str]:
        """
        Get descriptions of all agents
        """
        return {
            name: agent.get_description()
            for name, agent in self.agents.items()
        }

    def get_tool_descriptions(self) -> Dict[str, str]:
        """
        Get descriptions of all tools
        """
        return {}  # No separate tools in simple version