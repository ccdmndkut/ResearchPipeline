"""
Knowledge Graph Builder
Extracts entities and relationships to build knowledge graphs.
"""
import networkx as nx
import re
from typing import List, Dict, Any


class GraphBuilder:
    """Builds knowledge graphs from text documents."""
    
    def __init__(self):
        """Initialize the graph builder."""
        self.graph = nx.Graph()
    
    def build_graph(self, documents: List[str]) -> Dict[str, Any]:
        """
        Build a knowledge graph from documents.
        
        Args:
            documents: List of text documents
            
        Returns:
            Dictionary containing entities and relationships
        """
        entities = []
        relationships = []
        
        for doc in documents:
            # Simple entity extraction (capitalized words/phrases)
            doc_entities = self._extract_entities(doc)
            entities.extend(doc_entities)
            
            # Simple relationship extraction
            doc_relationships = self._extract_relationships(doc, doc_entities)
            relationships.extend(doc_relationships)
        
        # Remove duplicates
        unique_entities = list(set(entities))
        unique_relationships = list(set(tuple(r.items()) for r in relationships))
        unique_relationships = [dict(r) for r in unique_relationships]
        
        return {
            'entities': unique_entities[:50],  # Limit for performance
            'relationships': unique_relationships[:50],
            'graph_stats': {
                'total_entities': len(unique_entities),
                'total_relationships': len(unique_relationships)
            }
        }
    
    def _extract_entities(self, text: str) -> List[str]:
        """Extract potential entities from text."""
        # Simple regex for capitalized words (proper nouns)
        entities = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        
        # Filter common words
        stop_words = {'The', 'This', 'That', 'And', 'Or', 'But', 'In', 'On', 'At'}
        entities = [e for e in entities if e not in stop_words and len(e) > 2]
        
        return entities
    
    def _extract_relationships(self, text: str, entities: List[str]) -> List[Dict[str, str]]:
        """Extract relationships between entities."""
        relationships = []
        
        # Simple pattern matching for relationships
        relation_patterns = [
            r'(\w+)\s+is\s+(\w+)',
            r'(\w+)\s+has\s+(\w+)',
            r'(\w+)\s+works\s+for\s+(\w+)',
            r'(\w+)\s+created\s+(\w+)'
        ]
        
        for pattern in relation_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                subject, obj = match.groups()
                if subject in entities and obj in entities:
                    relationships.append({
                        'subject': subject,
                        'predicate': 'related_to',
                        'object': obj
                    })
        
        return relationships