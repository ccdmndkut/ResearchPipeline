"""
Enhanced Research Orchestrator with Parallel Processing and Intelligent Planning
"""
import asyncio
import json
import hashlib
from typing import AsyncGenerator, Dict, List, Any, Optional, Set, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import openai
from collections import defaultdict
import numpy as np

from app.settings import settings
from app.utils.prompt_loader import load_prompt
from app.agents import SearchAgent, SummarizerAgent, CitationAgent, GraphAgent
from app.tools import PDFParser, VectorSearch, WebFetch, StatsUtil
from app.utils.logging_config import setup_logging

logger = setup_logging(__name__)


class TaskPriority(Enum):
    """Task priority levels for execution planning"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


class AgentCapability(Enum):
    """Agent capabilities for matching tasks"""
    SEARCH = "search"
    SUMMARIZATION = "summarization"
    CITATION_VERIFICATION = "citation_verification"
    GRAPH_ANALYSIS = "graph_analysis"
    PDF_PROCESSING = "pdf_processing"
    WEB_SCRAPING = "web_scraping"
    STATISTICAL_ANALYSIS = "statistical_analysis"
    VECTOR_SEARCH = "vector_search"


@dataclass
class Task:
    """Represents a task to be executed"""
    id: str
    agent_name: str
    action: str
    parameters: Dict[str, Any]
    priority: TaskPriority = TaskPriority.MEDIUM
    dependencies: Set[str] = field(default_factory=set)
    retry_count: int = 0
    max_retries: int = 3
    timeout: float = 30.0
    result: Optional[Any] = None
    error: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


@dataclass
class QueryAnalysis:
    """Analysis result of a research query"""
    intent: str  # search, summarize, analyze, verify
    entities: Dict[str, List[str]]  # topics, authors, dates, etc.
    complexity: int  # 1-10 scale
    suggested_agents: List[str]
    cache_key: str
    requires_web: bool
    requires_pdf: bool
    estimated_time: float


class QueryAnalyzer:
    """Analyzes queries to understand intent and requirements"""
    
    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.intent_keywords = {
            "search": ["find", "search", "look for", "papers about", "research on"],
            "summarize": ["summarize", "summary", "overview", "explain", "describe"],
            "analyze": ["analyze", "compare", "evaluate", "assess", "examine"],
            "verify": ["verify", "check", "validate", "confirm", "fact-check"]
        }
        
    async def analyze(self, query: str, parameters: Dict[str, Any]) -> QueryAnalysis:
        """Analyze query to extract intent and requirements"""
        # Detect intent
        intent = self._detect_intent(query.lower())
        
        # Extract entities using OpenAI
        entities = await self._extract_entities(query)
        
        # Calculate complexity
        complexity = self._calculate_complexity(query, parameters)
        
        # Suggest agents
        suggested_agents = self._suggest_agents(intent, entities, parameters)
        
        # Generate cache key
        cache_key = self._generate_cache_key(query, parameters)
        
        # Check requirements
        requires_web = any(kw in query.lower() for kw in ["website", "blog", "news", "recent"])
        requires_pdf = any(kw in query.lower() for kw in ["pdf", "paper", "document", "thesis"])
        
        # Estimate time
        estimated_time = self._estimate_time(complexity, suggested_agents)
        
        return QueryAnalysis(
            intent=intent,
            entities=entities,
            complexity=complexity,
            suggested_agents=suggested_agents,
            cache_key=cache_key,
            requires_web=requires_web,
            requires_pdf=requires_pdf,
            estimated_time=estimated_time
        )
    
    def _detect_intent(self, query: str) -> str:
        """Detect the primary intent of the query"""
        for intent, keywords in self.intent_keywords.items():
            if any(kw in query for kw in keywords):
                return intent
        return "search"  # default
    
    async def _extract_entities(self, query: str) -> Dict[str, List[str]]:
        """Extract entities from query using OpenAI"""
        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Extract entities from the query. Return JSON with keys: topics, authors, dates, keywords."},
                    {"role": "user", "content": query}
                ],
                temperature=0,
                max_tokens=200
            )
            
            content = response.choices[0].message.content
            entities = json.loads(content)
            return entities
        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
            return {"topics": [], "authors": [], "dates": [], "keywords": []}
    
    def _calculate_complexity(self, query: str, parameters: Dict[str, Any]) -> int:
        """Calculate query complexity on a 1-10 scale"""
        complexity = 1
        
        # Length factor
        if len(query) > 200:
            complexity += 2
        elif len(query) > 100:
            complexity += 1
            
        # Database count
        databases = parameters.get("databases", [])
        complexity += min(len(databases), 3)
        
        # Result count
        max_results = parameters.get("max_results", 20)
        if max_results > 50:
            complexity += 2
        elif max_results > 20:
            complexity += 1
            
        # Action complexity
        action = parameters.get("action", "search")
        if action in ["analyze", "verify"]:
            complexity += 2
        elif action == "summarize":
            complexity += 1
            
        return min(complexity, 10)
    
    def _suggest_agents(self, intent: str, entities: Dict, parameters: Dict) -> List[str]:
        """Suggest appropriate agents based on analysis"""
        agents = []
        
        # Always include search for most queries
        if intent in ["search", "analyze"]:
            agents.append("search")
            
        # Add summarizer for summary requests
        if intent == "summarize" or parameters.get("action") == "summarize":
            agents.append("summarizer")
            
        # Add citation agent if verification needed
        if intent == "verify" or "verify" in parameters.get("action", ""):
            agents.append("citation")
            
        # Add graph agent for network analysis
        if "citation" in str(entities) or "network" in str(entities):
            agents.append("graph")
            
        return agents if agents else ["search"]
    
    def _generate_cache_key(self, query: str, parameters: Dict) -> str:
        """Generate a cache key for the query"""
        key_data = {
            "query": query.lower().strip(),
            "databases": sorted(parameters.get("databases", [])),
            "action": parameters.get("action", "search"),
            "max_results": parameters.get("max_results", 20)
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_str.encode()).hexdigest()
    
    def _estimate_time(self, complexity: int, agents: List[str]) -> float:
        """Estimate execution time in seconds"""
        base_time = 2.0
        complexity_factor = complexity * 0.5
        agent_factor = len(agents) * 1.5
        return base_time + complexity_factor + agent_factor


class TaskPlanner:
    """Plans and optimizes task execution"""
    
    def __init__(self):
        self.agent_registry = self._build_agent_registry()
        self.cost_estimates = self._build_cost_estimates()
        
    def _build_agent_registry(self) -> Dict[str, List[AgentCapability]]:
        """Build registry of agent capabilities"""
        return {
            "search": [AgentCapability.SEARCH],
            "summarizer": [AgentCapability.SUMMARIZATION],
            "citation": [AgentCapability.CITATION_VERIFICATION],
            "graph": [AgentCapability.GRAPH_ANALYSIS],
            "pdf_parser": [AgentCapability.PDF_PROCESSING],
            "vector_search": [AgentCapability.VECTOR_SEARCH],
            "web_fetch": [AgentCapability.WEB_SCRAPING],
            "stats": [AgentCapability.STATISTICAL_ANALYSIS]
        }
    
    def _build_cost_estimates(self) -> Dict[str, float]:
        """Build cost estimates for each agent (in seconds)"""
        return {
            "search": 3.0,
            "summarizer": 2.0,
            "citation": 1.5,
            "graph": 2.5,
            "pdf_parser": 1.0,
            "vector_search": 0.5,
            "web_fetch": 2.0,
            "stats": 0.5
        }
    
    async def create_plan(self, analysis: QueryAnalysis, parameters: Dict) -> Dict[str, Any]:
        """Create an optimized execution plan"""
        tasks = []
        
        # Create tasks based on suggested agents
        for idx, agent in enumerate(analysis.suggested_agents):
            task = Task(
                id=f"task_{idx}_{agent}",
                agent_name=agent,
                action=self._get_agent_action(agent, analysis.intent),
                parameters=self._prepare_parameters(agent, parameters, analysis),
                priority=self._assign_priority(agent, idx),
                timeout=self.cost_estimates.get(agent, 5.0) * 3  # 3x estimated time
            )
            tasks.append(task)
        
        # Add dependencies
        tasks = self._add_dependencies(tasks, analysis)
        
        # Optimize execution order
        execution_groups = self._create_execution_groups(tasks)
        
        return {
            "query_analysis": analysis,
            "tasks": tasks,
            "execution_groups": execution_groups,
            "estimated_time": analysis.estimated_time,
            "parallel_groups": self._identify_parallel_groups(tasks)
        }
    
    def _get_agent_action(self, agent: str, intent: str) -> str:
        """Determine the action for an agent based on intent"""
        action_map = {
            "search": "search",
            "summarizer": "summarize_topic",
            "citation": "verify_citations",
            "graph": "analyze_network"
        }
        return action_map.get(agent, "execute")
    
    def _prepare_parameters(self, agent: str, params: Dict, analysis: QueryAnalysis) -> Dict:
        """Prepare parameters for specific agent"""
        agent_params = params.copy()
        
        if agent == "search":
            agent_params["expanded_query"] = " ".join(
                analysis.entities.get("keywords", [])
            )
        elif agent == "summarizer":
            agent_params["topic"] = " ".join(
                analysis.entities.get("topics", [])
            )
            
        return agent_params
    
    def _assign_priority(self, agent: str, order: int) -> TaskPriority:
        """Assign priority based on agent and order"""
        if agent == "search" and order == 0:
            return TaskPriority.CRITICAL
        elif order < 2:
            return TaskPriority.HIGH
        else:
            return TaskPriority.MEDIUM
    
    def _add_dependencies(self, tasks: List[Task], analysis: QueryAnalysis) -> List[Task]:
        """Add task dependencies"""
        # Summarizer depends on search
        search_tasks = [t.id for t in tasks if t.agent_name == "search"]
        for task in tasks:
            if task.agent_name == "summarizer" and search_tasks:
                task.dependencies.update(search_tasks)
                
        return tasks
    
    def _create_execution_groups(self, tasks: List[Task]) -> List[List[str]]:
        """Create execution groups based on dependencies"""
        groups = []
        executed = set()
        
        while len(executed) < len(tasks):
            group = []
            for task in tasks:
                if task.id not in executed:
                    if not task.dependencies or task.dependencies.issubset(executed):
                        group.append(task.id)
                        executed.add(task.id)
            if group:
                groups.append(group)
                
        return groups
    
    def _identify_parallel_groups(self, tasks: List[Task]) -> List[List[Task]]:
        """Identify tasks that can run in parallel"""
        groups = []
        task_map = {t.id: t for t in tasks}
        
        for group_ids in self._create_execution_groups(tasks):
            group_tasks = [task_map[tid] for tid in group_ids]
            groups.append(group_tasks)
            
        return groups


class ParallelExecutor:
    """Executes tasks in parallel with optimizations"""
    
    def __init__(self, max_concurrent: int = 5):
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.results = {}
        self.errors = {}
        
    async def execute(self, plan: Dict[str, Any], agents: Dict, tools: Dict) -> Dict[str, Any]:
        """Execute plan with parallel processing"""
        results = {}
        parallel_groups = plan["parallel_groups"]
        
        for group_idx, group in enumerate(parallel_groups):
            logger.info(f"Executing parallel group {group_idx + 1}/{len(parallel_groups)}")
            
            # Execute tasks in parallel
            group_tasks = []
            for task in group:
                group_tasks.append(
                    self._execute_task_with_retry(task, agents, tools, results)
                )
            
            # Wait for all tasks in group to complete
            group_results = await asyncio.gather(*group_tasks, return_exceptions=True)
            
            # Process results
            for task, result in zip(group, group_results):
                if isinstance(result, Exception):
                    logger.error(f"Task {task.id} failed: {result}")
                    results[task.id] = {"error": str(result)}
                else:
                    results[task.id] = result
                    
        return results
    
    async def _execute_task_with_retry(
        self, 
        task: Task, 
        agents: Dict, 
        tools: Dict,
        previous_results: Dict
    ) -> Any:
        """Execute a task with retry logic"""
        async with self.semaphore:
            for attempt in range(task.max_retries):
                try:
                    task.start_time = datetime.now()
                    
                    # Get agent or tool
                    executor = agents.get(task.agent_name) or tools.get(task.agent_name)
                    if not executor:
                        raise ValueError(f"No executor found for {task.agent_name}")
                    
                    # Add previous results to context
                    params = task.parameters.copy()
                    params["context"] = previous_results
                    
                    # Execute with timeout
                    result = await asyncio.wait_for(
                        executor.execute(task.action, params),
                        timeout=task.timeout
                    )
                    
                    task.end_time = datetime.now()
                    task.result = result
                    return result
                    
                except asyncio.TimeoutError:
                    logger.warning(f"Task {task.id} timed out (attempt {attempt + 1})")
                    if attempt == task.max_retries - 1:
                        raise
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    
                except Exception as e:
                    logger.error(f"Task {task.id} failed (attempt {attempt + 1}): {e}")
                    if attempt == task.max_retries - 1:
                        raise
                    await asyncio.sleep(2 ** attempt)


class QualityScorer:
    """Scores and ranks results based on quality metrics"""
    
    def __init__(self):
        self.weights = {
            "relevance": 0.3,
            "credibility": 0.2,
            "recency": 0.2,
            "completeness": 0.15,
            "citations": 0.15
        }
        
    async def score(self, results: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Score and rank results"""
        scored_results = []
        
        for task_id, result in results.items():
            if isinstance(result, dict) and "papers" in result:
                papers = result["papers"]
                for paper in papers:
                    score = self._calculate_score(paper, query)
                    paper["quality_score"] = score
                    scored_results.append(paper)
        
        # Sort by score
        scored_results.sort(key=lambda x: x.get("quality_score", 0), reverse=True)
        
        return {
            "scored_results": scored_results,
            "total_results": len(scored_results),
            "average_score": np.mean([r["quality_score"] for r in scored_results]) if scored_results else 0
        }
    
    def _calculate_score(self, paper: Dict, query: str) -> float:
        """Calculate quality score for a paper"""
        scores = {}
        
        # Relevance score (based on title/abstract similarity to query)
        scores["relevance"] = self._calculate_relevance(paper, query)
        
        # Credibility score (based on journal, citations)
        scores["credibility"] = self._calculate_credibility(paper)
        
        # Recency score (based on publication year)
        scores["recency"] = self._calculate_recency(paper)
        
        # Completeness score (based on available metadata)
        scores["completeness"] = self._calculate_completeness(paper)
        
        # Citation score (based on citation count)
        scores["citations"] = self._calculate_citation_score(paper)
        
        # Calculate weighted average
        total_score = sum(scores[metric] * self.weights[metric] for metric in scores)
        return round(total_score, 2)
    
    def _calculate_relevance(self, paper: Dict, query: str) -> float:
        """Calculate relevance score"""
        query_terms = set(query.lower().split())
        title = paper.get("title", "").lower()
        abstract = paper.get("abstract", "").lower()
        
        title_matches = sum(1 for term in query_terms if term in title)
        abstract_matches = sum(1 for term in query_terms if term in abstract)
        
        title_score = min(title_matches / max(len(query_terms), 1), 1.0)
        abstract_score = min(abstract_matches / (len(query_terms) * 2), 1.0)
        
        return (title_score * 0.6 + abstract_score * 0.4)
    
    def _calculate_credibility(self, paper: Dict) -> float:
        """Calculate credibility score"""
        # Check for journal quality indicators
        journal = paper.get("journal", "").lower()
        high_quality_indicators = ["nature", "science", "cell", "ieee", "acm", "springer"]
        
        if any(ind in journal for ind in high_quality_indicators):
            return 0.9
        elif journal:
            return 0.7
        else:
            return 0.5
    
    def _calculate_recency(self, paper: Dict) -> float:
        """Calculate recency score"""
        current_year = datetime.now().year
        pub_year = paper.get("year", 0)
        
        if not pub_year:
            return 0.5
            
        years_old = current_year - pub_year
        if years_old <= 1:
            return 1.0
        elif years_old <= 3:
            return 0.8
        elif years_old <= 5:
            return 0.6
        elif years_old <= 10:
            return 0.4
        else:
            return 0.2
    
    def _calculate_completeness(self, paper: Dict) -> float:
        """Calculate completeness score"""
        required_fields = ["title", "abstract", "authors", "year", "url"]
        present_fields = sum(1 for field in required_fields if paper.get(field))
        return present_fields / len(required_fields)
    
    def _calculate_citation_score(self, paper: Dict) -> float:
        """Calculate citation score"""
        citations = paper.get("citation_count", 0)
        
        if citations >= 100:
            return 1.0
        elif citations >= 50:
            return 0.8
        elif citations >= 20:
            return 0.6
        elif citations >= 10:
            return 0.4
        elif citations >= 5:
            return 0.2
        else:
            return 0.1


class EnhancedOrchestrator:
    """Enhanced orchestrator with parallel processing and intelligent planning"""
    
    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.query_analyzer = QueryAnalyzer()
        self.task_planner = TaskPlanner()
        self.parallel_executor = ParallelExecutor()
        self.quality_scorer = QualityScorer()
        
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
        
        # Performance metrics
        self.metrics = defaultdict(list)
        self.cache = {}  # Simple in-memory cache (replace with Redis in production)
        
    async def process_query(
        self,
        request: Dict[str, Any]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Process a research query with enhanced capabilities"""
        session_id = request.get("session_id", datetime.now().isoformat())
        query = request.get("query", "")
        parameters = request.get("parameters", {})
        
        start_time = datetime.now()
        logger.info(f"Enhanced processing for query: {query} (session: {session_id})")
        
        try:
            # Analyze query
            analysis = await self.query_analyzer.analyze(query, parameters)
            
            yield self._create_event(
                "analysis",
                "orchestrator",
                "completed",
                f"Query analyzed - Complexity: {analysis.complexity}/10, Intent: {analysis.intent}",
                {"analysis": vars(analysis)}
            )
            
            # Check cache
            if analysis.cache_key in self.cache:
                logger.info(f"Cache hit for query: {query}")
                cached_result = self.cache[analysis.cache_key]
                yield self._create_event(
                    "cache_hit",
                    "orchestrator",
                    "completed",
                    "Retrieved from cache",
                    cached_result
                )
                return
            
            # Create execution plan
            plan = await self.task_planner.create_plan(analysis, parameters)
            
            yield self._create_event(
                "plan",
                "orchestrator",
                "completed",
                f"Execution plan created - {len(plan['parallel_groups'])} parallel groups",
                {"plan": {
                    "groups": len(plan['parallel_groups']),
                    "tasks": len(plan['tasks']),
                    "estimated_time": plan['estimated_time']
                }}
            )
            
            # Execute plan in parallel
            results = await self.parallel_executor.execute(plan, self.agents, self.tools)
            
            yield self._create_event(
                "execution",
                "orchestrator",
                "completed",
                f"Executed {len(results)} tasks in parallel",
                {"task_count": len(results)}
            )
            
            # Score and rank results
            scored_results = await self.quality_scorer.score(results, query)
            
            yield self._create_event(
                "scoring",
                "orchestrator",
                "completed",
                f"Scored {scored_results['total_results']} results - Avg score: {scored_results['average_score']:.2f}",
                {"average_score": scored_results['average_score']}
            )
            
            # Synthesize final results
            final_result = await self._synthesize_results(query, scored_results)
            
            # Cache results
            self.cache[analysis.cache_key] = final_result
            
            # Record metrics
            execution_time = (datetime.now() - start_time).total_seconds()
            self.metrics["execution_times"].append(execution_time)
            self.metrics["query_complexity"].append(analysis.complexity)
            
            yield self._create_event(
                "result",
                "orchestrator",
                "completed",
                f"Research completed in {execution_time:.2f}s",
                final_result
            )
            
            # Send performance metrics
            yield self._create_event(
                "metrics",
                "orchestrator",
                "info",
                "Performance metrics",
                {
                    "execution_time": execution_time,
                    "complexity": analysis.complexity,
                    "cache_size": len(self.cache),
                    "avg_execution_time": np.mean(self.metrics["execution_times"]),
                    "parallel_groups": len(plan['parallel_groups'])
                }
            )
            
        except Exception as e:
            logger.error(f"Enhanced orchestrator error: {str(e)}")
            yield self._create_event(
                "error",
                "orchestrator",
                "error",
                f"Error: {str(e)}",
                {"error": str(e), "type": type(e).__name__}
            )
    
    async def _synthesize_results(
        self,
        query: str,
        scored_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Synthesize scored results into final answer"""
        top_results = scored_results["scored_results"][:10]  # Top 10 results
        
        try:
            # Use GPT to synthesize
            messages = [
                {"role": "system", "content": "Synthesize research results into a comprehensive answer. Focus on the highest quality sources."},
                {
                    "role": "user",
                    "content": f"Query: {query}\n\nTop Results:\n{json.dumps(top_results, indent=2)[:3000]}\n\nProvide a comprehensive synthesis highlighting key findings."
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
            logger.warning(f"Synthesis generation failed: {e}")
            synthesis = f"Found {len(top_results)} high-quality results for '{query}'."
        
        return {
            "query": query,
            "synthesis": synthesis,
            "sources": top_results,
            "total_results": scored_results["total_results"],
            "average_quality": scored_results["average_score"],
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
        """Create a standardized event"""
        return {
            "event_type": event_type,
            "agent": agent,
            "status": status,
            "message": message,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        return {
            "total_queries": len(self.metrics["execution_times"]),
            "avg_execution_time": np.mean(self.metrics["execution_times"]) if self.metrics["execution_times"] else 0,
            "avg_complexity": np.mean(self.metrics["query_complexity"]) if self.metrics["query_complexity"] else 0,
            "cache_hit_rate": len(self.cache) / max(len(self.metrics["execution_times"]), 1),
            "cache_size": len(self.cache)
        }