import openai
from typing import Dict, List, Any, Optional
from datetime import datetime

from app.settings import settings
from app.utils.prompt_loader import load_prompt
from app.utils.logging_config import setup_logging

logger = setup_logging(__name__)

class SummarizerAgent:
    """
    Agent for summarizing academic papers and research topics
    """

    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.system_prompt = load_prompt("summarizer_prompt.txt")

    async def execute(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a summarization action
        """
        if action == "summarize_paper":
            return await self.summarize_paper(parameters)
        elif action == "summarize_topic":
            return await self.summarize_topic(parameters)
        elif action == "compare_papers":
            return await self.compare_papers(parameters)
        else:
            raise ValueError(f"Unknown action: {action}")

    async def summarize_paper(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Summarize a single academic paper
        """
        paper = parameters.get("paper", {})
        summary_type = parameters.get("summary_type", "executive")

        content = f"""
        Title: {paper.get('title', 'Unknown')}
        Authors: {', '.join(paper.get('authors', []))}
        Abstract: {paper.get('abstract', 'No abstract available')}
        """

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"Create a {summary_type} summary of this paper:\n{content}"}
        ]

        response = await self.client.chat.completions.create(
            model=settings.AGENT_MODEL,
            messages=messages,
            temperature=0.5,
            max_tokens=settings.MAX_TOKENS
        )

        summary_text = response.choices[0].message.content

        return {
            "paper_title": paper.get('title'),
            "summary_type": summary_type,
            "summary": summary_text,
            "main_findings": self._extract_findings(summary_text),
            "timestamp": datetime.now().isoformat()
        }

    async def summarize_topic(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Summarize a research topic from multiple papers
        """
        papers = parameters.get("papers", [])
        topic = parameters.get("topic", "Research Topic")

        papers_text = "\n\n".join([
            f"Paper {i+1}: {p.get('title', 'Unknown')}\n{p.get('abstract', '')[:500]}"
            for i, p in enumerate(papers[:10])
        ])

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"Create a topic overview for '{topic}' based on these papers:\n{papers_text}"}
        ]

        response = await self.client.chat.completions.create(
            model=settings.AGENT_MODEL,
            messages=messages,
            temperature=0.5,
            max_tokens=settings.MAX_TOKENS
        )

        return {
            "topic": topic,
            "num_papers": len(papers),
            "overview": response.choices[0].message.content,
            "key_themes": self._extract_themes(response.choices[0].message.content),
            "timestamp": datetime.now().isoformat()
        }

    async def compare_papers(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare multiple papers
        """
        papers = parameters.get("papers", [])

        comparison_prompt = "Compare these papers:\n"
        for i, paper in enumerate(papers[:5]):
            comparison_prompt += f"\nPaper {i+1}: {paper.get('title', 'Unknown')}\n"
            comparison_prompt += f"Abstract: {paper.get('abstract', '')[:300]}...\n"

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": comparison_prompt}
        ]

        response = await self.client.chat.completions.create(
            model=settings.AGENT_MODEL,
            messages=messages,
            temperature=0.5,
            max_tokens=settings.MAX_TOKENS
        )

        return {
            "num_papers": len(papers),
            "comparison": response.choices[0].message.content,
            "timestamp": datetime.now().isoformat()
        }

    def _extract_findings(self, text: str) -> List[str]:
        """
        Extract key findings from summary text
        """
        findings = []
        lines = text.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in ['finding', 'result', 'conclude', 'show', 'demonstrate']):
                findings.append(line.strip())
        return findings[:5]

    def _extract_themes(self, text: str) -> List[str]:
        """
        Extract key themes from overview text
        """
        themes = []
        lines = text.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in ['theme', 'trend', 'pattern', 'approach']):
                themes.append(line.strip())
        return themes[:5]

    def get_description(self) -> str:
        """
        Get agent description
        """
        return "Summarize academic papers and research topics"

    def get_parameters(self) -> Dict[str, Any]:
        """
        Get agent parameters schema
        """
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["summarize_paper", "summarize_topic", "compare_papers"]
                },
                "paper": {
                    "type": "object",
                    "description": "Paper to summarize"
                },
                "papers": {
                    "type": "array",
                    "description": "Papers to analyze"
                },
                "summary_type": {
                    "type": "string",
                    "enum": ["abstract", "executive", "technical", "comparative"]
                }
            },
            "required": ["action"]
        }