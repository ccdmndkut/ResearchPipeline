"""
Response Formatter Agent - Formats research results for different audiences
"""
import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum
import openai
from dataclasses import dataclass

from app.settings import settings
from app.utils.logging_config import setup_logging

logger = setup_logging(__name__)


class AudienceType(Enum):
    """Different audience types for content formatting"""
    ACADEMIC = "academic"
    BUSINESS = "business" 
    STUDENT = "student"
    JOURNALIST = "journalist"
    GENERAL = "general"


class FormatType(Enum):
    """Different output format types"""
    SUMMARY = "summary"
    DETAILED = "detailed"
    BULLET_POINTS = "bullet_points"
    NARRATIVE = "narrative"
    TECHNICAL = "technical"
    VISUAL = "visual"


class CitationStyle(Enum):
    """Academic citation styles"""
    APA = "apa"
    MLA = "mla"
    CHICAGO = "chicago"
    IEEE = "ieee"
    HARVARD = "harvard"


@dataclass
class FormattedResponse:
    """Container for formatted response"""
    content: str
    metadata: Dict[str, Any]
    citations: List[str]
    key_insights: List[str]
    visual_suggestions: List[Dict[str, Any]]
    related_topics: List[str]
    confidence_score: float
    reading_time: int  # minutes


class ResponseFormatterAgent:
    """
    Formats research results for different audiences with adaptive content
    """
    
    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.templates = self._load_templates()
        self.citation_formatter = CitationFormatter()
        self.insight_extractor = InsightExtractor()
        
    def _load_templates(self) -> Dict[str, Dict[str, str]]:
        """Load content templates for different audiences and formats"""
        return {
            AudienceType.ACADEMIC: {
                FormatType.SUMMARY: "Provide a concise academic abstract with methodology and findings.",
                FormatType.DETAILED: "Present comprehensive analysis with literature review, methodology, results, and discussion.",
                FormatType.TECHNICAL: "Include technical details, formulas, statistical analysis, and methodological considerations."
            },
            AudienceType.BUSINESS: {
                FormatType.SUMMARY: "Executive summary with key insights and actionable recommendations.",
                FormatType.BULLET_POINTS: "Key takeaways, ROI implications, and strategic recommendations.",
                FormatType.NARRATIVE: "Business case narrative with market context and competitive analysis."
            },
            AudienceType.STUDENT: {
                FormatType.SUMMARY: "Clear explanation with examples and learning objectives.",
                FormatType.DETAILED: "Step-by-step explanation with examples, diagrams, and practice questions.",
                FormatType.VISUAL: "Visual learning aids with infographics and concept maps."
            },
            AudienceType.JOURNALIST: {
                FormatType.SUMMARY: "News-style lead with who, what, when, where, why.",
                FormatType.NARRATIVE: "Story format with quotes, context, and human interest angle.",
                FormatType.BULLET_POINTS: "Key facts, quotes, and story angles."
            },
            AudienceType.GENERAL: {
                FormatType.SUMMARY: "Accessible overview avoiding jargon.",
                FormatType.DETAILED: "Comprehensive but approachable explanation.",
                FormatType.NARRATIVE: "Engaging narrative with real-world applications."
            }
        }
    
    async def format_response(
        self,
        results: Dict[str, Any],
        audience: AudienceType = AudienceType.GENERAL,
        format_type: FormatType = FormatType.SUMMARY,
        citation_style: CitationStyle = CitationStyle.APA,
        include_visuals: bool = True,
        max_length: Optional[int] = None
    ) -> FormattedResponse:
        """
        Format research results for specific audience
        
        Args:
            results: Raw research results
            audience: Target audience type
            format_type: Desired output format
            citation_style: Citation formatting style
            include_visuals: Whether to suggest visual elements
            max_length: Maximum content length in words
            
        Returns:
            FormattedResponse with adapted content
        """
        try:
            # Extract key insights
            insights = await self.insight_extractor.extract(results)
            
            # Format citations
            citations = self.citation_formatter.format_citations(
                results.get("sources", []),
                citation_style
            )
            
            # Generate main content
            content = await self._generate_content(
                results, audience, format_type, insights, max_length
            )
            
            # Suggest visual elements if requested
            visual_suggestions = []
            if include_visuals:
                visual_suggestions = await self._suggest_visuals(results, audience)
            
            # Extract related topics
            related_topics = await self._extract_related_topics(results)
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence(results)
            
            # Estimate reading time
            reading_time = self._estimate_reading_time(content)
            
            # Create metadata
            metadata = {
                "audience": audience.value,
                "format": format_type.value,
                "citation_style": citation_style.value,
                "word_count": len(content.split()),
                "source_count": len(results.get("sources", [])),
                "generated_at": datetime.now().isoformat()
            }
            
            return FormattedResponse(
                content=content,
                metadata=metadata,
                citations=citations,
                key_insights=insights,
                visual_suggestions=visual_suggestions,
                related_topics=related_topics,
                confidence_score=confidence_score,
                reading_time=reading_time
            )
            
        except Exception as e:
            logger.error(f"Response formatting failed: {e}")
            raise
    
    async def _generate_content(
        self,
        results: Dict[str, Any],
        audience: AudienceType,
        format_type: FormatType,
        insights: List[str],
        max_length: Optional[int]
    ) -> str:
        """Generate formatted content using GPT"""
        
        # Get appropriate template
        template = self.templates[audience].get(
            format_type,
            self.templates[audience][FormatType.SUMMARY]
        )
        
        # Build prompt
        prompt = f"""
        Format the following research results for a {audience.value} audience.
        
        Style: {template}
        
        Key Insights:
        {json.dumps(insights, indent=2)}
        
        Research Results:
        {json.dumps(results, indent=2)[:5000]}
        
        Requirements:
        - Use appropriate language for {audience.value} audience
        - Format as {format_type.value}
        - Include key findings and implications
        {"- Maximum " + str(max_length) + " words" if max_length else ""}
        
        Generate the formatted content:
        """
        
        response = await self.client.chat.completions.create(
            model=settings.AGENT_MODEL,
            messages=[
                {"role": "system", "content": f"You are a content formatter specializing in {audience.value} communication."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=max_length // 4 if max_length else settings.MAX_TOKENS
        )
        
        return response.choices[0].message.content
    
    async def _suggest_visuals(
        self,
        results: Dict[str, Any],
        audience: AudienceType
    ) -> List[Dict[str, Any]]:
        """Suggest appropriate visual elements"""
        
        visuals = []
        
        # Analyze data for visualization opportunities
        if "statistics" in str(results):
            visuals.append({
                "type": "bar_chart",
                "title": "Statistical Comparison",
                "description": "Compare key metrics across studies",
                "priority": "high"
            })
        
        if "timeline" in str(results) or "year" in str(results):
            visuals.append({
                "type": "timeline",
                "title": "Research Timeline",
                "description": "Show evolution of research over time",
                "priority": "medium"
            })
        
        if "network" in str(results) or "citation" in str(results):
            visuals.append({
                "type": "network_graph",
                "title": "Citation Network",
                "description": "Visualize connections between papers",
                "priority": "medium"
            })
        
        # Audience-specific visuals
        if audience == AudienceType.STUDENT:
            visuals.append({
                "type": "concept_map",
                "title": "Concept Overview",
                "description": "Visual map of key concepts and relationships",
                "priority": "high"
            })
        elif audience == AudienceType.BUSINESS:
            visuals.append({
                "type": "dashboard",
                "title": "Executive Dashboard",
                "description": "Key metrics and KPIs at a glance",
                "priority": "high"
            })
        
        return visuals
    
    async def _extract_related_topics(self, results: Dict[str, Any]) -> List[str]:
        """Extract related topics for further exploration"""
        
        try:
            prompt = f"""
            Based on these research results, identify 5 related topics for further exploration:
            {json.dumps(results, indent=2)[:2000]}
            
            Return as a JSON list of topic strings.
            """
            
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Extract related research topics."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=200
            )
            
            topics = json.loads(response.choices[0].message.content)
            return topics[:5]
            
        except Exception as e:
            logger.warning(f"Related topic extraction failed: {e}")
            return []
    
    def _calculate_confidence(self, results: Dict[str, Any]) -> float:
        """Calculate confidence score based on result quality"""
        
        score = 0.5  # Base score
        
        # Factor in source count
        source_count = len(results.get("sources", []))
        if source_count > 10:
            score += 0.2
        elif source_count > 5:
            score += 0.1
        
        # Factor in quality scores if available
        if "average_quality" in results:
            score += results["average_quality"] * 0.3
        
        # Factor in citation counts
        citations = sum(
            s.get("citation_count", 0) 
            for s in results.get("sources", [])
        )
        if citations > 100:
            score += 0.1
        
        return min(score, 1.0)
    
    def _estimate_reading_time(self, content: str) -> int:
        """Estimate reading time in minutes"""
        words = len(content.split())
        # Average reading speed: 200-250 words per minute
        return max(1, words // 225)


class CitationFormatter:
    """Formats citations in various academic styles"""
    
    def format_citations(
        self,
        sources: List[Dict[str, Any]],
        style: CitationStyle
    ) -> List[str]:
        """Format sources according to citation style"""
        
        citations = []
        for source in sources:
            if style == CitationStyle.APA:
                citation = self._format_apa(source)
            elif style == CitationStyle.MLA:
                citation = self._format_mla(source)
            elif style == CitationStyle.CHICAGO:
                citation = self._format_chicago(source)
            elif style == CitationStyle.IEEE:
                citation = self._format_ieee(source, len(citations) + 1)
            else:
                citation = self._format_harvard(source)
            
            citations.append(citation)
        
        return citations
    
    def _format_apa(self, source: Dict[str, Any]) -> str:
        """Format in APA style"""
        authors = self._format_authors_apa(source.get("authors", []))
        year = source.get("year", "n.d.")
        title = source.get("title", "Untitled")
        journal = source.get("journal", "")
        
        if journal:
            return f"{authors} ({year}). {title}. {journal}."
        else:
            return f"{authors} ({year}). {title}."
    
    def _format_mla(self, source: Dict[str, Any]) -> str:
        """Format in MLA style"""
        authors = self._format_authors_mla(source.get("authors", []))
        title = f'"{source.get("title", "Untitled")}"'
        journal = source.get("journal", "")
        year = source.get("year", "")
        
        if journal:
            return f'{authors}. {title} {journal}, {year}.'
        else:
            return f'{authors}. {title} {year}.'
    
    def _format_chicago(self, source: Dict[str, Any]) -> str:
        """Format in Chicago style"""
        authors = self._format_authors_chicago(source.get("authors", []))
        title = f'"{source.get("title", "Untitled")}"'
        journal = source.get("journal", "")
        year = source.get("year", "")
        
        if journal:
            return f'{authors}. {title} {journal} ({year}).'
        else:
            return f'{authors}. {title} {year}.'
    
    def _format_ieee(self, source: Dict[str, Any], number: int) -> str:
        """Format in IEEE style"""
        authors = self._format_authors_ieee(source.get("authors", []))
        title = f'"{source.get("title", "Untitled")}"'
        journal = source.get("journal", "")
        year = source.get("year", "")
        
        if journal:
            return f'[{number}] {authors}, {title} {journal}, {year}.'
        else:
            return f'[{number}] {authors}, {title} {year}.'
    
    def _format_harvard(self, source: Dict[str, Any]) -> str:
        """Format in Harvard style"""
        authors = self._format_authors_harvard(source.get("authors", []))
        year = source.get("year", "n.d.")
        title = source.get("title", "Untitled")
        journal = source.get("journal", "")
        
        if journal:
            return f"{authors} {year}, '{title}', {journal}."
        else:
            return f"{authors} {year}, '{title}'."
    
    def _format_authors_apa(self, authors: List[str]) -> str:
        """Format authors in APA style"""
        if not authors:
            return "Anonymous"
        
        if len(authors) == 1:
            return self._get_last_name(authors[0]) + ", " + self._get_initials(authors[0])
        elif len(authors) == 2:
            return (self._get_last_name(authors[0]) + ", " + self._get_initials(authors[0]) +
                   ", & " + self._get_last_name(authors[1]) + ", " + self._get_initials(authors[1]))
        else:
            return self._get_last_name(authors[0]) + ", " + self._get_initials(authors[0]) + ", et al."
    
    def _format_authors_mla(self, authors: List[str]) -> str:
        """Format authors in MLA style"""
        if not authors:
            return "Anonymous"
        
        if len(authors) == 1:
            return authors[0]
        elif len(authors) == 2:
            return authors[0] + " and " + authors[1]
        else:
            return authors[0] + ", et al"
    
    def _format_authors_chicago(self, authors: List[str]) -> str:
        """Format authors in Chicago style"""
        if not authors:
            return "Anonymous"
        
        if len(authors) <= 3:
            return " and ".join(authors)
        else:
            return authors[0] + " et al"
    
    def _format_authors_ieee(self, authors: List[str]) -> str:
        """Format authors in IEEE style"""
        if not authors:
            return "Anonymous"
        
        formatted = []
        for author in authors[:3]:
            parts = author.split()
            if len(parts) >= 2:
                formatted.append(f"{parts[0][0]}. {parts[-1]}")
            else:
                formatted.append(author)
        
        if len(authors) > 3:
            formatted.append("et al.")
        
        return ", ".join(formatted)
    
    def _format_authors_harvard(self, authors: List[str]) -> str:
        """Format authors in Harvard style"""
        if not authors:
            return "Anonymous"
        
        if len(authors) == 1:
            return self._get_last_name(authors[0])
        elif len(authors) == 2:
            return self._get_last_name(authors[0]) + " & " + self._get_last_name(authors[1])
        else:
            return self._get_last_name(authors[0]) + " et al."
    
    def _get_last_name(self, full_name: str) -> str:
        """Extract last name from full name"""
        parts = full_name.strip().split()
        return parts[-1] if parts else full_name
    
    def _get_initials(self, full_name: str) -> str:
        """Extract initials from full name"""
        parts = full_name.strip().split()
        if len(parts) < 2:
            return ""
        
        initials = []
        for part in parts[:-1]:  # All except last name
            if part:
                initials.append(part[0].upper() + ".")
        
        return " ".join(initials)


class InsightExtractor:
    """Extracts key insights from research results"""
    
    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def extract(self, results: Dict[str, Any]) -> List[str]:
        """Extract key insights from results"""
        
        try:
            prompt = f"""
            Extract 5-7 key insights from these research results.
            Focus on:
            - Major findings
            - Surprising discoveries
            - Practical implications
            - Future directions
            - Contradictions or debates
            
            Results:
            {json.dumps(results, indent=2)[:3000]}
            
            Return as a JSON list of insight strings.
            Each insight should be a complete, standalone sentence.
            """
            
            response = await self.client.chat.completions.create(
                model=settings.AGENT_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert at identifying key research insights."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=500
            )
            
            content = response.choices[0].message.content
            
            # Try to parse as JSON
            try:
                insights = json.loads(content)
                if isinstance(insights, list):
                    return insights[:7]
            except json.JSONDecodeError:
                # Fallback: split by newlines
                insights = [
                    line.strip().lstrip("-•*").strip()
                    for line in content.split("\n")
                    if line.strip() and len(line.strip()) > 20
                ]
                return insights[:7]
            
        except Exception as e:
            logger.error(f"Insight extraction failed: {e}")
            return [
                "Analysis complete with multiple sources identified.",
                "Further investigation may be warranted.",
                "Results show varied perspectives on the topic."
            ]


class TemplateManager:
    """Manages content templates for different formats"""
    
    def __init__(self):
        self.templates = self._load_all_templates()
    
    def _load_all_templates(self) -> Dict[str, Any]:
        """Load all content templates"""
        return {
            "email": {
                "subject": "Research Summary: {query}",
                "greeting": "Dear {recipient},",
                "body": "{content}",
                "closing": "Best regards,\nResearch Assistant"
            },
            "report": {
                "title": "Research Report: {query}",
                "executive_summary": "{summary}",
                "methodology": "{methodology}",
                "findings": "{findings}",
                "conclusions": "{conclusions}",
                "references": "{references}"
            },
            "presentation": {
                "title_slide": "{query}",
                "overview": ["Background", "Methodology", "Key Findings", "Implications"],
                "content_slides": "{content}",
                "conclusion": "{conclusions}",
                "questions": "Questions?"
            },
            "social_media": {
                "twitter": "{headline} 🧵 Thread: {summary} #research #science",
                "linkedin": "New Research Insights: {headline}\n\n{summary}\n\n{hashtags}",
                "blog": {
                    "title": "{headline}",
                    "intro": "{hook}",
                    "body": "{content}",
                    "conclusion": "{takeaways}"
                }
            }
        }
    
    def get_template(self, template_type: str, format_type: str) -> Dict[str, Any]:
        """Get specific template"""
        return self.templates.get(template_type, {}).get(format_type, {})
    
    def format_with_template(
        self,
        template_type: str,
        format_type: str,
        data: Dict[str, Any]
    ) -> str:
        """Format data using template"""
        template = self.get_template(template_type, format_type)
        
        if isinstance(template, dict):
            formatted = {}
            for key, value in template.items():
                if isinstance(value, str):
                    formatted[key] = value.format(**data)
                else:
                    formatted[key] = value
            return json.dumps(formatted, indent=2)
        elif isinstance(template, str):
            return template.format(**data)
        else:
            return str(template)


# Export classes
__all__ = [
    'ResponseFormatterAgent',
    'AudienceType',
    'FormatType',
    'CitationStyle',
    'FormattedResponse',
    'CitationFormatter',
    'InsightExtractor',
    'TemplateManager'
]