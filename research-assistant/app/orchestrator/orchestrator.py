import asyncio
import json
from typing import AsyncGenerator, Dict, List, Any, Optional
from datetime import datetime
import openai

from app.settings import settings
from app.utils.prompt_loader import load_prompt
from app.agents import SearchAgent, SummarizerAgent, CitationAgent, GraphAgent
from app.tools import PDFParser, VectorSearch, WebFetch, StatsUtil
from app.utils.logging_config import setup_logging

logger = setup_logging(__name__)

class ResearchOrchestrator:
    """
    Main orchestrator that coordinates multiple agents and tools
    for research tasks using OpenAI function calling
    """

    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        try:
            self.system_prompt = load_prompt("orchestrator_prompt.txt")
        except:
            self.system_prompt = "You are a research assistant orchestrator. Help coordinate searches and analysis."

        # Initialize agents
        self.agents = {
            "search": SearchAgent(),
            "summarizer": SummarizerAgent(),
            "citation": CitationAgent(),
            "graph": GraphAgent()
        }

        # Initialize tools
        self.tools = {
            "pdf_parser": PDFParser(),
            "vector_search": VectorSearch(),
            "web_fetch": WebFetch(),
            "stats": StatsUtil()
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

            # Analyze query and create execution plan
            plan = await self._create_execution_plan(query, parameters)

            yield self._create_event(
                "plan",
                "orchestrator",
                "completed",
                "Execution plan created",
                {"plan": plan}
            )

            # Execute plan
            results = []
            for step in plan["steps"]:
                async for event in self._execute_step(step, results):
                    yield event
                    self.active_sessions[session_id]["events"].append(event)

            # Synthesize final results
            final_result = await self._synthesize_results(query, results)

            yield self._create_event(
                "result",
                "orchestrator",
                "completed",
                "Research completed",
                final_result
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

    async def _create_execution_plan(
        self,
        query: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a simple execution plan (simplified for now)
        """
        # Determine search type based on parameters or query
        search_type = "general"
        if "academic" in query.lower() or "research" in query.lower() or "paper" in query.lower():
            search_type = "academic"

        # For now, just do a search - we can make this smarter later
        plan = {
            "query": query,
            "steps": [
                {
                    "agent": "search",
                    "action": "search",
                    "parameters": {
                        "query": query,
                        "search_type": search_type,
                        "max_results": parameters.get("max_results", 20)
                    }
                }
            ]
        }

        # If summarize action is requested, add summarization step
        if parameters.get("action") == "summarize":
            plan["steps"].append({
                "agent": "summarizer",
                "action": "summarize_topic",
                "parameters": {
                    "topic": query
                }
            })

        return plan

    async def _execute_step(
        self,
        step: Dict[str, Any],
        previous_results: List[Dict[str, Any]]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Execute a single step in the plan
        """
        agent_name = step.get("agent")
        tool_name = step.get("tool")
        action = step.get("action")
        params = step.get("parameters", {})

        # Add previous results to context
        params["context"] = previous_results

        try:
            if agent_name and agent_name in self.agents:
                # Execute agent
                agent = self.agents[agent_name]

                yield self._create_event(
                    "agent_call",
                    agent_name,
                    "started",
                    f"Calling {agent_name} agent",
                    params
                )

                result = await agent.execute(action, params)
                previous_results.append(result)

                yield self._create_event(
                    "agent_call",
                    agent_name,
                    "completed",
                    f"{agent_name} agent completed",
                    result
                )

            elif tool_name and tool_name in self.tools:
                # Execute tool
                tool = self.tools[tool_name]

                yield self._create_event(
                    "tool_use",
                    tool_name,
                    "started",
                    f"Using {tool_name} tool",
                    params
                )

                result = await tool.execute(params)
                previous_results.append(result)

                yield self._create_event(
                    "tool_use",
                    tool_name,
                    "completed",
                    f"{tool_name} tool completed",
                    result
                )

        except Exception as e:
            logger.error(f"Error executing step: {str(e)}")
            yield self._create_event(
                "error",
                agent_name or tool_name,
                "error",
                str(e),
                {}
            )

    async def _synthesize_results(
        self,
        query: str,
        results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Synthesize all results into a final answer
        """
        try:
            messages = [
                {"role": "system", "content": "Synthesize the research results into a comprehensive answer."},
                {
                    "role": "user",
                    "content": f"Query: {query}\n\nResults: {json.dumps(results, indent=2)[:2000]}\n\nProvide a comprehensive synthesis."
                }
            ]

            response = await self.client.chat.completions.create(
                model=settings.ORCHESTRATOR_MODEL,
                messages=messages,
                temperature=0.5,
                max_tokens=settings.MAX_TOKENS
            )

            synthesis = response.choices[0].message.content
        except Exception as e:
            logger.warning(f"OpenAI synthesis failed: {e}, using basic synthesis")
            # Basic synthesis without OpenAI
            total_papers = sum(len(r.get("papers", [])) for r in results)
            synthesis = f"Found {total_papers} papers related to '{query}'. The search covered multiple academic databases and returned relevant research papers."

        return {
            "query": query,
            "synthesis": synthesis,
            "sources": self._extract_sources(results),
            "timestamp": datetime.now().isoformat()
        }

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

    def _get_function_definitions(self) -> List[Dict[str, Any]]:
        """
        Get OpenAI function definitions for agents and tools
        """
        functions = []

        # Add agent functions
        for name, agent in self.agents.items():
            functions.append({
                "name": f"call_{name}_agent",
                "description": agent.get_description(),
                "parameters": agent.get_parameters()
            })

        # Add tool functions
        for name, tool in self.tools.items():
            functions.append({
                "name": f"use_{name}_tool",
                "description": tool.get_description(),
                "parameters": tool.get_parameters()
            })

        return functions

    def _extract_sources(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract all sources from results
        """
        sources = []
        for result in results:
            if "sources" in result:
                sources.extend(result["sources"])
            elif "papers" in result:
                sources.extend(result["papers"])
        return sources

    def get_available_agents(self) -> List[str]:
        """
        Get list of available agents
        """
        return list(self.agents.keys())

    def get_available_tools(self) -> List[str]:
        """
        Get list of available tools
        """
        return list(self.tools.keys())

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
        return {
            name: tool.get_description()
            for name, tool in self.tools.items()
        }