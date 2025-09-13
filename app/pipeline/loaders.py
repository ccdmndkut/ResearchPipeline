"""
Document Loaders
Handles loading and validation of various document formats.
"""
import json
from typing import List, Dict, Any


class DocumentLoader:
    """Loads and validates documents from various sources."""
    
    def __init__(self):
        """Initialize the document loader."""
        self.supported_formats = ['txt', 'json', 'html']
    
    def load_documents(self, sources: List[str]) -> List[Dict[str, Any]]:
        """
        Load documents from various sources.
        
        Args:
            sources: List of file paths, URLs, or content strings
            
        Returns:
            List of document dictionaries with content and metadata
        """
        documents = []
        
        for source in sources:
            try:
                # Simple text content loading for now
                if source.startswith(('http://', 'https://')):
                    # URL source - would integrate with web retrieval
                    doc = {
                        'source': source,
                        'content': f'Content from {source}',
                        'type': 'url',
                        'metadata': {'url': source}
                    }
                else:
                    # Text content
                    doc = {
                        'source': 'text_input',
                        'content': source,
                        'type': 'text',
                        'metadata': {'length': len(source)}
                    }
                
                documents.append(doc)
                
            except Exception as e:
                print(f"Error loading document from {source}: {e}")
                continue
        
        return documents
    
    def validate_schema(self, document: Dict[str, Any]) -> bool:
        """
        Validate document schema.
        
        Args:
            document: Document dictionary to validate
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ['source', 'content', 'type']
        
        for field in required_fields:
            if field not in document:
                return False
        
        if not isinstance(document['content'], str):
            return False
        
        return True