import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import openai
import json
import re
import sys
from pathlib import Path

# Add prompts directory to path
sys.path.append(str(Path(__file__).parent.parent.parent / "prompts"))

from app.settings import settings
from app.utils.prompt_loader import load_prompt
from app.utils.logging_config import setup_logging

# Import optimized prompts
try:
    from optimized_search_prompts import (
        get_web_search_system_prompt,
        get_optimized_prompt,
        add_urgency_indicators,
        add_date_context,
        add_source_requirements
    )
    OPTIMIZED_PROMPTS_AVAILABLE = True
except ImportError:
    OPTIMIZED_PROMPTS_AVAILABLE = False

logger = setup_logging(__name__)

class SearchAgent:
    """
    Agent for searching using OpenAI's web search capabilities
    Note: Web search is automatically enabled in certain OpenAI models
    """

    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

        # Use optimized system prompt if available
        if OPTIMIZED_PROMPTS_AVAILABLE:
            self.system_prompt = get_web_search_system_prompt()
            logger.info("Using optimized web search prompts")
        else:
            try:
                self.system_prompt = load_prompt("search_agent_prompt.txt")
            except:
                self.system_prompt = """You are a research assistant with web search capabilities.
                When answering questions, search the web for current, relevant information.
                Focus on authoritative and reliable sources.
                For academic queries, prioritize scholarly articles and research papers.
                Always provide sources and citations when available."""
            logger.warning("Optimized prompts not available, using default prompts")

    async def execute(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a search action
        """
        if action == "search":
            return await self.search_web(parameters)
        elif action == "search_academic":
            return await self.search_academic(parameters)
        elif action == "expand_query":
            return await self.expand_query(parameters)
        else:
            raise ValueError(f"Unknown action: {action}")

    async def search_web(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search the web using OpenAI's built-in web search capabilities
        Web search is automatically enabled in gpt-4o models
        """
        query = parameters.get("query", "")
        max_results = parameters.get("max_results", 10)
        search_type = parameters.get("search_type", "general")

        logger.info(f"Web searching for: {query} (type: {search_type})")

        try:
            # Use optimized prompts if available
            if OPTIMIZED_PROMPTS_AVAILABLE:
                search_prompt = get_optimized_prompt(query, search_type)
                # Add enhancement features
                search_prompt = add_urgency_indicators(search_prompt)
                search_prompt = add_date_context(search_prompt)
                search_prompt = add_source_requirements(search_prompt)
                logger.info(f"Using optimized {search_type} search prompt")
            else:
                # Fallback to basic prompts
                if search_type == "academic":
                    search_prompt = f"""Search the web for academic papers, research articles, and scholarly content about: {query}

                    Please find and summarize:
                    1. Recent academic papers or research articles
                    2. Key findings and methodologies
                    3. Authors and institutions
                    4. Publication dates and journals

                    Provide the information in a structured format with proper citations."""
                else:
                    search_prompt = f"""Search the web for current information about: {query}

                    Please find and provide:
                    1. Recent and relevant information
                    2. Key facts and developments
                    3. Authoritative sources
                    4. Multiple perspectives if applicable

                    Include sources and dates for all information."""
                logger.warning("Using fallback basic prompts")

            # Call OpenAI with web search (automatically enabled in gpt-4o models)
            response = await self.client.chat.completions.create(
                model="gpt-4o",  # This model has web search built-in
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": search_prompt}
                ],
                temperature=0.1,  # Lower temperature for more consistent results
                max_tokens=3000   # Increased for more detailed responses
            )

            # Extract the response
            content = response.choices[0].message.content

            # Parse the response to extract structured information
            search_results = self._parse_search_results(content, search_type)

            return {
                "query": query,
                "search_type": search_type,
                "total_results": len(search_results),
                "results": search_results[:max_results],
                "synthesis": content,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Web search error: {e}")
            return {
                "query": query,
                "error": str(e),
                "results": [],
                "synthesis": f"Error performing search: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }

    async def search_academic(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search specifically for academic content
        """
        parameters["search_type"] = "academic"
        return await self.search_web(parameters)

    async def expand_query(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Expand search query with synonyms and related terms
        """
        query = parameters.get("query", "")

        messages = [
            {"role": "system", "content": "You are an expert at expanding search queries with relevant synonyms, related terms, and alternative phrasings to improve search results."},
            {"role": "user", "content": f"""Expand this search query with related terms and synonyms: "{query}"

            Provide:
            1. Alternative phrasings
            2. Related technical terms
            3. Broader and narrower terms
            4. Common abbreviations or full forms

            Format as a comma-separated list of terms."""}
        ]

        response = await self.client.chat.completions.create(
            model=settings.AGENT_MODEL,
            messages=messages,
            temperature=0.5,
            max_tokens=300
        )

        expanded = response.choices[0].message.content

        return {
            "original": query,
            "expanded": expanded,
            "terms": [term.strip() for term in expanded.split(",")]
        }

    def _parse_search_results(self, content: str, search_type: str) -> List[Dict[str, Any]]:
        """
        Enhanced parsing of AI response to extract structured search results
        """
        results = []

        if not content or len(content.strip()) < 10:
            logger.warning("Empty or very short content received from search")
            return results

        # Enhanced parsing patterns based on search type
        if search_type == "academic":
            results = self._parse_academic_results(content)
        elif search_type == "news":
            results = self._parse_news_results(content)
        elif search_type == "technical":
            results = self._parse_technical_results(content)
        else:
            results = self._parse_general_results(content)

        # If no structured results found, create intelligent fallback
        if not results:
            results = self._create_fallback_results(content, search_type)

        # Ensure each result has required fields
        for result in results:
            if "timestamp" not in result:
                result["timestamp"] = datetime.now().isoformat()
            if "source" not in result:
                result["source"] = "OpenAI Web Search"
            if "type" not in result:
                result["type"] = search_type

        return results

    def _parse_academic_results(self, content: str) -> List[Dict[str, Any]]:
        """Parse academic search results"""
        results = []

        # Look for structured academic content
        title_patterns = [
            r'\*\*Title\*\*:\s*([^\n]+)',  # **Title**: format
            r'Title:\s*([^\n]+)',          # Title: format
            r'[""]([^""]{20,})[""]',       # Long quoted titles
            r'^\d+\.\s*([^\.]{20,}?)(?:\s*\(|\s*by|\s*-)', # Numbered papers
        ]

        author_patterns = [
            r'\*\*Authors?\*\*:\s*([^\n]+)',
            r'Authors?:\s*([^\n]+)',
            r'by\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+et\s+al\.?)?)',
        ]

        journal_patterns = [
            r'\*\*Journal/Venue\*\*:\s*([^\n]+)',
            r'Journal:\s*([^\n]+)',
            r'Published in:\s*([^\n]+)',
        ]

        # Extract structured academic results
        titles = []
        for pattern in title_patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            titles.extend([m.strip() for m in matches if len(m.strip()) > 15])

        for i, title in enumerate(titles[:5]):  # Limit to 5 results
            result = {
                "title": title,
                "type": "academic_paper",
                "authors": "",
                "journal": "",
                "excerpt": self._extract_context(content, title)
            }

            # Try to find corresponding author and journal
            context = self._extract_context(content, title, window=300)
            for pattern in author_patterns:
                author_match = re.search(pattern, context, re.IGNORECASE)
                if author_match:
                    result["authors"] = author_match.group(1).strip()
                    break

            for pattern in journal_patterns:
                journal_match = re.search(pattern, context, re.IGNORECASE)
                if journal_match:
                    result["journal"] = journal_match.group(1).strip()
                    break

            results.append(result)

        return results

    def _parse_news_results(self, content: str) -> List[Dict[str, Any]]:
        """Parse news search results"""
        results = []

        # Look for news headlines and articles
        headline_patterns = [
            r'###?\s*([^\n]{20,})',  # Headlines with ###
            r'•\s*([^\n]{20,})\s*-\s*([^\n]+)',  # Bullet points with source
            r'^\d+\.\s*([^\n]{20,})',  # Numbered headlines
        ]

        for pattern in headline_patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            for match in matches[:5]:
                if isinstance(match, tuple):
                    headline, source = match
                else:
                    headline = match
                    source = "Unknown"

                results.append({
                    "title": headline.strip(),
                    "type": "news_article",
                    "source": source.strip() if source != "Unknown" else "News Source",
                    "excerpt": self._extract_context(content, headline)
                })

        return results

    def _parse_technical_results(self, content: str) -> List[Dict[str, Any]]:
        """Parse technical search results"""
        results = []

        # Look for technical documentation and resources
        doc_patterns = [
            r'•\s*([^\n]+)\s*-\s*([^\n]+)',  # Bullet with description
            r'\*\*([^*]+)\*\*:\s*([^\n]+)', # Bold title with description
        ]

        for pattern in doc_patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            for match in matches[:5]:
                if isinstance(match, tuple) and len(match) == 2:
                    title, description = match
                    results.append({
                        "title": title.strip(),
                        "type": "technical_doc",
                        "description": description.strip(),
                        "excerpt": self._extract_context(content, title)
                    })

        return results

    def _parse_general_results(self, content: str) -> List[Dict[str, Any]]:
        """Parse general search results"""
        results = []

        # Look for structured sections
        section_patterns = [
            r'###?\s*([^\n]+)',  # Section headers
            r'^\d+\.\s*([^\n]+)', # Numbered items
            r'•\s*([^\n]{20,})', # Bullet points
        ]

        for pattern in section_patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            for match in matches[:5]:
                if len(match.strip()) > 15:  # Meaningful content
                    results.append({
                        "title": match.strip(),
                        "type": "general_info",
                        "excerpt": self._extract_context(content, match)
                    })

        return results

    def _create_fallback_results(self, content: str, search_type: str) -> List[Dict[str, Any]]:
        """Create fallback results when structured parsing fails"""
        results = []

        # Split content into meaningful chunks
        sections = content.split('\n\n')
        meaningful_sections = [s.strip() for s in sections if len(s.strip()) > 100]

        for i, section in enumerate(meaningful_sections[:3]):
            # Extract first sentence as title
            sentences = section.split('. ')
            title = sentences[0][:100] + "..." if len(sentences[0]) > 100 else sentences[0]

            results.append({
                "title": title,
                "content": section,
                "type": f"{search_type}_info",
                "source": "Web Search Results",
                "confidence": 0.7  # Lower confidence for fallback results
            })

        return results

    def _extract_context(self, content: str, match: str, window: int = 200) -> str:
        """
        Extract context around a matched string with configurable window size
        """
        try:
            index = content.find(match)
            if index == -1:
                return ""

            # Get characters before and after based on window size
            half_window = window // 2
            start = max(0, index - half_window)
            end = min(len(content), index + len(match) + half_window)

            excerpt = content[start:end]
            if start > 0:
                excerpt = "..." + excerpt
            if end < len(content):
                excerpt = excerpt + "..."

            return excerpt.strip()
        except:
            return ""

    def get_description(self) -> str:
        """
        Get agent description
        """
        return "Search the web for current information using OpenAI's web search capabilities"

    def get_parameters(self) -> Dict[str, Any]:
        """
        Get agent parameters schema
        """
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["search", "search_academic", "expand_query"],
                    "description": "The search action to perform"
                },
                "query": {
                    "type": "string",
                    "description": "Search query"
                },
                "search_type": {
                    "type": "string",
                    "enum": ["general", "academic", "news", "technical"],
                    "description": "Type of search to perform"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum results to return",
                    "default": 10
                }
            },
            "required": ["action", "query"]
        }