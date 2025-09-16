"""
Simple search agent that works without OpenAI API
"""
import asyncio
import aiohttp
from typing import Dict, List, Any, Optional
from datetime import datetime
import xml.etree.ElementTree as ET

from app.settings import settings
from app.utils.logging_config import setup_logging

logger = setup_logging(__name__)

class SimpleSearchAgent:
    """
    Simplified search agent that doesn't require OpenAI
    """

    def __init__(self):
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
        else:
            raise ValueError(f"Unknown action: {action}")

    async def search_literature(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search for academic literature
        """
        query = parameters.get("query", "")
        databases = parameters.get("databases", ["arxiv"])
        max_results = parameters.get("max_results", 10)

        logger.info(f"Searching for: {query} in {databases}")

        # Initialize session if needed
        if not self.session:
            self.session = aiohttp.ClientSession()

        # Search each database
        all_papers = []

        if "arxiv" in databases:
            try:
                arxiv_results = await self._search_arxiv(query, max_results)
                all_papers.extend(arxiv_results)
            except Exception as e:
                logger.error(f"ArXiv search error: {e}")

        return {
            "query": query,
            "total_results": len(all_papers),
            "papers": all_papers,
            "databases_searched": databases,
            "timestamp": datetime.now().isoformat()
        }

    async def _search_arxiv(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """
        Search arXiv database
        """
        if not self.session:
            self.session = aiohttp.ClientSession()

        url = "http://export.arxiv.org/api/query"
        params = {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": min(max_results, 10),
            "sortBy": "relevance"
        }

        try:
            async with self.session.get(url, params=params) as response:
                text = await response.text()
                root = ET.fromstring(text)

                papers = []
                for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
                    try:
                        title_elem = entry.find("{http://www.w3.org/2005/Atom}title")
                        summary_elem = entry.find("{http://www.w3.org/2005/Atom}summary")
                        id_elem = entry.find("{http://www.w3.org/2005/Atom}id")
                        published_elem = entry.find("{http://www.w3.org/2005/Atom}published")

                        authors = []
                        for author in entry.findall("{http://www.w3.org/2005/Atom}author"):
                            name_elem = author.find("{http://www.w3.org/2005/Atom}name")
                            if name_elem is not None:
                                authors.append(name_elem.text)

                        paper = {
                            "title": title_elem.text.strip() if title_elem is not None else "No title",
                            "authors": authors,
                            "abstract": summary_elem.text.strip()[:500] if summary_elem is not None else "No abstract",
                            "url": id_elem.text if id_elem is not None else "",
                            "published": published_elem.text if published_elem is not None else "",
                            "year": int(published_elem.text[:4]) if published_elem is not None and published_elem.text else 2024,
                            "source": "arxiv",
                            "relevance_score": 0.8
                        }
                        papers.append(paper)
                    except Exception as e:
                        logger.error(f"Error parsing entry: {e}")
                        continue

                return papers

        except Exception as e:
            logger.error(f"arXiv API error: {e}")
            return []

    def get_description(self) -> str:
        """
        Get agent description
        """
        return "Search for academic literature (simplified version)"

    def get_parameters(self) -> Dict[str, Any]:
        """
        Get agent parameters schema
        """
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["search"]
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
            "required": ["action", "query"]
        }