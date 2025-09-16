import asyncio
import aiohttp
from typing import Dict, List, Any, Optional
from datetime import datetime
import xml.etree.ElementTree as ET
import openai

from app.settings import settings
from app.utils.prompt_loader import load_prompt
from app.utils.logging_config import setup_logging

logger = setup_logging(__name__)

class SearchAgent:
    """
    Agent for searching academic literature across multiple databases
    """

    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        try:
            self.system_prompt = load_prompt("search_agent_prompt.txt")
        except:
            self.system_prompt = "You are a search agent that helps find academic literature."
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def execute(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a search action
        """
        if action == "search":
            return await self.search_literature(parameters)
        elif action == "expand_query":
            return await self.expand_query(parameters)
        elif action == "filter_results":
            return await self.filter_results(parameters)
        else:
            raise ValueError(f"Unknown action: {action}")

    async def search_literature(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search for academic literature
        """
        query = parameters.get("query", "")
        databases = parameters.get("databases", ["arxiv", "semantic_scholar"])
        max_results = parameters.get("max_results", settings.MAX_SEARCH_RESULTS)
        date_range = parameters.get("date_range", None)

        logger.info(f"Searching for: {query} in {databases}")

        # Initialize session if needed
        if not self.session:
            self.session = aiohttp.ClientSession()

        # Expand query using LLM
        expanded_query = await self.expand_query({"query": query})

        # Search each database in parallel
        tasks = []
        if "arxiv" in databases:
            tasks.append(self._search_arxiv(expanded_query["expanded"], max_results))
        if "semantic_scholar" in databases:
            tasks.append(self._search_semantic_scholar(expanded_query["expanded"], max_results))
        if "pubmed" in databases:
            tasks.append(self._search_pubmed(expanded_query["expanded"], max_results))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Combine and deduplicate results
        all_papers = []
        for db_results in results:
            if isinstance(db_results, Exception):
                logger.error(f"Search error: {db_results}")
                continue
            all_papers.extend(db_results)

        # Deduplicate by title
        seen_titles = set()
        unique_papers = []
        for paper in all_papers:
            if paper["title"].lower() not in seen_titles:
                seen_titles.add(paper["title"].lower())
                unique_papers.append(paper)

        # Sort by relevance score
        unique_papers.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)

        return {
            "query": query,
            "expanded_query": expanded_query["expanded"],
            "total_results": len(unique_papers),
            "papers": unique_papers[:max_results],
            "databases_searched": databases,
            "timestamp": datetime.now().isoformat()
        }

    async def expand_query(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Expand search query with synonyms and related terms
        """
        query = parameters.get("query", "")

        messages = [
            {"role": "system", "content": "Expand the search query with synonyms and related terms for academic search."},
            {"role": "user", "content": f"Expand this query: {query}"}
        ]

        response = await self.client.chat.completions.create(
            model=settings.AGENT_MODEL,
            messages=messages,
            temperature=0.3,
            max_tokens=200
        )

        expanded = response.choices[0].message.content

        return {
            "original": query,
            "expanded": expanded,
            "terms": expanded.split(",")
        }

    async def filter_results(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Filter search results based on criteria
        """
        papers = parameters.get("papers", [])
        min_citations = parameters.get("min_citations", 0)
        year_range = parameters.get("year_range", None)
        keywords = parameters.get("keywords", [])

        filtered = []
        for paper in papers:
            # Check citations
            if paper.get("citation_count", 0) < min_citations:
                continue

            # Check year
            if year_range:
                year = paper.get("year", 0)
                if year < year_range[0] or year > year_range[1]:
                    continue

            # Check keywords
            if keywords:
                abstract = paper.get("abstract", "").lower()
                if not any(kw.lower() in abstract for kw in keywords):
                    continue

            filtered.append(paper)

        return {
            "original_count": len(papers),
            "filtered_count": len(filtered),
            "papers": filtered
        }

    async def _search_arxiv(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """
        Search arXiv database
        """
        if not self.session:
            self.session = aiohttp.ClientSession()

        url = settings.ARXIV_API_URL
        params = {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": max_results,
            "sortBy": "relevance"
        }

        try:
            async with self.session.get(url, params=params) as response:
                text = await response.text()
                root = ET.fromstring(text)

                papers = []
                for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
                    paper = {
                        "title": entry.find("{http://www.w3.org/2005/Atom}title").text.strip(),
                        "authors": [
                            author.find("{http://www.w3.org/2005/Atom}name").text
                            for author in entry.findall("{http://www.w3.org/2005/Atom}author")
                        ],
                        "abstract": entry.find("{http://www.w3.org/2005/Atom}summary").text.strip(),
                        "url": entry.find("{http://www.w3.org/2005/Atom}id").text,
                        "published": entry.find("{http://www.w3.org/2005/Atom}published").text,
                        "year": int(entry.find("{http://www.w3.org/2005/Atom}published").text[:4]),
                        "source": "arxiv",
                        "relevance_score": 0.8
                    }
                    papers.append(paper)

                return papers

        except Exception as e:
            logger.error(f"arXiv search error: {e}")
            return []

    async def _search_semantic_scholar(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """
        Search Semantic Scholar database
        """
        if not self.session:
            self.session = aiohttp.ClientSession()

        url = f"{settings.SEMANTIC_SCHOLAR_API_URL}paper/search"
        params = {
            "query": query,
            "limit": max_results,
            "fields": "title,authors,abstract,year,citationCount,url"
        }

        try:
            async with self.session.get(url, params=params) as response:
                data = await response.json()

                papers = []
                for item in data.get("data", []):
                    paper = {
                        "title": item.get("title", ""),
                        "authors": [a.get("name", "") for a in item.get("authors", [])],
                        "abstract": item.get("abstract", ""),
                        "url": item.get("url", ""),
                        "year": item.get("year", 0),
                        "citation_count": item.get("citationCount", 0),
                        "source": "semantic_scholar",
                        "relevance_score": 0.7
                    }
                    papers.append(paper)

                return papers

        except Exception as e:
            logger.error(f"Semantic Scholar search error: {e}")
            return []

    async def _search_pubmed(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """
        Search PubMed database
        """
        # Simplified PubMed search - would need proper implementation
        return []

    def get_description(self) -> str:
        """
        Get agent description
        """
        return "Search for academic literature across multiple databases"

    def get_parameters(self) -> Dict[str, Any]:
        """
        Get agent parameters schema
        """
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["search", "expand_query", "filter_results"]
                },
                "query": {
                    "type": "string",
                    "description": "Search query"
                },
                "databases": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Databases to search"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum results to return"
                }
            },
            "required": ["action"]
        }