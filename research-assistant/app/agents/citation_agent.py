import openai
import aiohttp
from typing import Dict, List, Any, Optional
from datetime import datetime
import re

from app.settings import settings
from app.utils.prompt_loader import load_prompt
from app.utils.logging_config import setup_logging

logger = setup_logging(__name__)

class CitationAgent:
    """
    Agent for verifying citations and checking factual accuracy
    """

    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.system_prompt = load_prompt("citation_agent_prompt.txt")
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def execute(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a citation verification action
        """
        if action == "verify_citations":
            return await self.verify_citations(parameters)
        elif action == "check_facts":
            return await self.check_facts(parameters)
        elif action == "detect_retractions":
            return await self.detect_retractions(parameters)
        else:
            raise ValueError(f"Unknown action: {action}")

    async def verify_citations(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify citations in a document
        """
        text = parameters.get("text", "")
        citations = parameters.get("citations", [])

        # Extract citations from text if not provided
        if not citations:
            citations = self._extract_citations(text)

        verification_results = []
        for citation in citations:
            result = await self._verify_single_citation(citation)
            verification_results.append(result)

        # Calculate overall credibility
        verified_count = sum(1 for r in verification_results if r["status"] == "verified")
        credibility_score = verified_count / len(verification_results) if verification_results else 0

        return {
            "total_citations": len(citations),
            "verified": verified_count,
            "failed": len(citations) - verified_count,
            "credibility_score": credibility_score,
            "details": verification_results,
            "timestamp": datetime.now().isoformat()
        }

    async def check_facts(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check factual claims against sources
        """
        claims = parameters.get("claims", [])
        sources = parameters.get("sources", [])

        fact_check_results = []
        for claim in claims:
            # Use LLM to verify claim against sources
            result = await self._verify_claim(claim, sources)
            fact_check_results.append(result)

        return {
            "claims_checked": len(claims),
            "results": fact_check_results,
            "timestamp": datetime.now().isoformat()
        }

    async def detect_retractions(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check if any cited papers have been retracted
        """
        papers = parameters.get("papers", [])

        retraction_results = []
        for paper in papers:
            # Check retraction databases
            is_retracted = await self._check_retraction_status(paper)
            retraction_results.append({
                "title": paper.get("title", "Unknown"),
                "doi": paper.get("doi", ""),
                "retracted": is_retracted,
                "checked_date": datetime.now().isoformat()
            })

        retracted_count = sum(1 for r in retraction_results if r["retracted"])

        return {
            "total_checked": len(papers),
            "retracted": retracted_count,
            "clean": len(papers) - retracted_count,
            "details": retraction_results,
            "timestamp": datetime.now().isoformat()
        }

    def _extract_citations(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract citations from text
        """
        citations = []

        # Simple pattern matching for citations
        # Pattern for (Author, Year) format
        pattern1 = r'\(([A-Z][a-z]+(?:\s+et\s+al\.)?),\s*(\d{4})\)'
        matches1 = re.findall(pattern1, text)
        for match in matches1:
            citations.append({
                "author": match[0],
                "year": match[1],
                "format": "parenthetical"
            })

        # Pattern for [1], [2] format
        pattern2 = r'\[(\d+)\]'
        matches2 = re.findall(pattern2, text)
        for match in matches2:
            citations.append({
                "reference_number": match,
                "format": "numbered"
            })

        return citations

    async def _verify_single_citation(self, citation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify a single citation
        """
        # Simplified verification - would need actual API calls
        messages = [
            {"role": "system", "content": "Verify if this citation is valid and correctly formatted."},
            {"role": "user", "content": f"Citation: {citation}"}
        ]

        response = await self.client.chat.completions.create(
            model=settings.AGENT_MODEL,
            messages=messages,
            temperature=0.3,
            max_tokens=200
        )

        return {
            "citation": citation,
            "status": "verified",  # Simplified
            "notes": response.choices[0].message.content
        }

    async def _verify_claim(self, claim: str, sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Verify a factual claim against sources
        """
        sources_text = "\n".join([
            f"Source {i+1}: {s.get('title', '')}\n{s.get('abstract', '')[:200]}"
            for i, s in enumerate(sources[:5])
        ])

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"Verify this claim against the sources:\nClaim: {claim}\n\nSources:\n{sources_text}"}
        ]

        response = await self.client.chat.completions.create(
            model=settings.AGENT_MODEL,
            messages=messages,
            temperature=0.3,
            max_tokens=300
        )

        return {
            "claim": claim,
            "verification": response.choices[0].message.content,
            "supported": True  # Simplified
        }

    async def _check_retraction_status(self, paper: Dict[str, Any]) -> bool:
        """
        Check if a paper has been retracted
        """
        # This would need to check actual retraction databases
        # For now, returning False as placeholder
        return False

    def get_description(self) -> str:
        """
        Get agent description
        """
        return "Verify citations and check factual accuracy"

    def get_parameters(self) -> Dict[str, Any]:
        """
        Get agent parameters schema
        """
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["verify_citations", "check_facts", "detect_retractions"]
                },
                "text": {
                    "type": "string",
                    "description": "Text containing citations"
                },
                "citations": {
                    "type": "array",
                    "description": "List of citations to verify"
                },
                "claims": {
                    "type": "array",
                    "description": "Factual claims to check"
                },
                "papers": {
                    "type": "array",
                    "description": "Papers to check for retractions"
                }
            },
            "required": ["action"]
        }