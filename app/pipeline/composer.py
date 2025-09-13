"""
Response Composer
Synthesizes final responses using LLM with citations and analysis.
"""
import os
import json
from typing import Dict, Any, List
# Using python_openai integration - from blueprint:python_openai
from openai import OpenAI


class ResponseComposer:
    """Composes final research responses using LLM synthesis."""
    
    def __init__(self):
        """Initialize the response composer."""
        # From python_openai blueprint
        self.openai_client = None
        try:
            OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
            if OPENAI_API_KEY:
                self.openai_client = OpenAI(api_key=OPENAI_API_KEY)
        except Exception as e:
            print(f"OpenAI client initialization failed: {e}")
            self.openai_client = None
    
    def compose_response(self, query: str, web_results: Dict[str, Any], 
                        graph_data: Dict[str, Any], vector_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compose final response using all gathered information.
        
        Args:
            query: Original research query
            web_results: Results from web search
            graph_data: Knowledge graph information
            vector_results: Vector similarity results
            
        Returns:
            Synthesized response with citations
        """
        try:
            # Prepare context for LLM
            context = self._prepare_context(web_results, graph_data, vector_results)
            
            if self.openai_client:
                # Use OpenAI for response synthesis
                response = self._call_llm(query, context)
            else:
                # Fallback response composition without LLM
                response = self._compose_fallback_response(query, web_results, graph_data)
            
            # Format sources
            sources = self._format_sources(web_results.get('sources', []))
            
            return {
                'answer': response,
                'sources': sources,
                'confidence': self._calculate_confidence(web_results, graph_data),
                'method': 'llm_synthesis' if self.openai_client else 'template_based'
            }
            
        except Exception as e:
            return {
                'answer': f'Error composing response: {str(e)}',
                'sources': [],
                'confidence': 0.0,
                'method': 'error_fallback'
            }
    
    def _call_llm(self, query: str, context: str) -> str:
        """Call OpenAI LLM for response synthesis."""
        try:
            prompt = f"""You are a research assistant. Based on the following context information, provide a comprehensive answer to the research query. Include relevant details and maintain accuracy.

Query: {query}

Context Information:
{context}

Please provide a well-structured, informative response that directly answers the query using the provided context. Be specific and cite relevant information where appropriate."""

            # the newest OpenAI model is "gpt-5" which was released August 7, 2025.
            # do not change this unless explicitly requested by the user
            if not self.openai_client:
                return "OpenAI client not available. Using fallback response."
                
            response = self.openai_client.chat.completions.create(
                model="gpt-5",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.7
            )
            
            return response.choices[0].message.content or "No response generated"
            
        except Exception as e:
            return f"LLM synthesis failed: {str(e)}. Using fallback response composition."
    
    def _prepare_context(self, web_results: Dict[str, Any], 
                        graph_data: Dict[str, Any], vector_results: Dict[str, Any]) -> str:
        """Prepare context string for LLM."""
        context_parts = []
        
        # Add web search results
        if web_results.get('documents'):
            context_parts.append("Web Search Results:")
            for doc in web_results['documents'][:3]:
                context_parts.append(f"- {doc.get('title', 'Unknown')}: {doc.get('summary', doc.get('content', '')[:200])}")
        
        # Add key entities from knowledge graph
        if graph_data.get('entities'):
            context_parts.append(f"\\nKey Entities: {', '.join(graph_data['entities'][:10])}")
        
        # Add similar documents from vector search
        if vector_results.get('similar_docs'):
            context_parts.append("\\nRelevant Documents:")
            for doc in vector_results['similar_docs'][:2]:
                context_parts.append(f"- {doc[:150]}...")
        
        return "\\n".join(context_parts)
    
    def _compose_fallback_response(self, query: str, web_results: Dict[str, Any], 
                                 graph_data: Dict[str, Any]) -> str:
        """Compose response without LLM as fallback."""
        response_parts = []
        
        response_parts.append(f"# Research Analysis: {query.title()}")
        response_parts.append("")  # Empty line for spacing
        
        if web_results.get('documents'):
            response_parts.append("## Key Findings")
            response_parts.append("")
            
            for i, doc in enumerate(web_results['documents'][:3], 1):
                title = doc.get('title', f'Source {i}').replace('_', ' ').title()
                content = doc.get('content', doc.get('summary', 'No content available'))
                
                # Get meaningful excerpt instead of just the summary
                if len(content) > 200:
                    # Find sentence boundaries for better excerpts
                    sentences = content.split('. ')
                    excerpt = sentences[0]
                    if len(excerpt) < 100 and len(sentences) > 1:
                        excerpt += '. ' + sentences[1]
                    if not excerpt.endswith('.'):
                        excerpt += '...'
                else:
                    excerpt = content
                
                response_parts.append(f"### {title}")
                response_parts.append(excerpt.strip())
                response_parts.append("")  # Space between sections
        
        if graph_data.get('entities'):
            response_parts.append("## Key Entities & Concepts")
            entities = graph_data['entities'][:8]  # More entities for better coverage
            # Group entities in a more readable way
            entity_list = []
            for entity in entities:
                if len(entity) > 2:  # Filter out very short entities
                    entity_list.append(f"• {entity}")
            
            if entity_list:
                response_parts.extend(entity_list)
                response_parts.append("")
        
        response_parts.append("---")
        response_parts.append("*Analysis completed using web search, knowledge graph extraction, and vector similarity matching.*")
        
        return "\n".join(response_parts)
    
    def _format_sources(self, sources: List[Dict[str, Any]]) -> List[str]:
        """Format sources for citation."""
        formatted_sources = []
        for i, source in enumerate(sources, 1):
            formatted_sources.append(f"[{i}] {source.get('title', 'Unknown Source')} - {source.get('url', 'N/A')}")
        
        return formatted_sources
    
    def _calculate_confidence(self, web_results: Dict[str, Any], graph_data: Dict[str, Any]) -> float:
        """Calculate confidence score based on available data."""
        score = 0.5  # Base score
        
        if web_results.get('documents'):
            score += 0.2 * min(len(web_results['documents']), 3) / 3
        
        if graph_data.get('entities'):
            score += 0.1 * min(len(graph_data['entities']), 10) / 10
        
        if web_results.get('total_results', 0) > 0:
            score += 0.2
        
        return min(score, 1.0)