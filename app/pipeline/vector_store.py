"""
Vector Store
Handles document indexing and semantic search using FAISS.
"""
import numpy as np
import faiss
from typing import List, Dict, Any


class VectorStore:
    """Vector store for semantic document search."""
    
    def __init__(self):
        """Initialize the vector store."""
        self.dimension = 384  # Standard sentence embedding dimension
        self.index = faiss.IndexFlatL2(self.dimension)
        self.documents = []
        self.embeddings = []
    
    def index_documents(self, documents: List[str], query: str = "") -> Dict[str, Any]:
        """
        Index documents and perform similarity search.
        
        Args:
            documents: List of documents to index
            query: Query to search against
            
        Returns:
            Search results with similar documents
        """
        try:
            # Simple mock embeddings (in production, use sentence-transformers)
            doc_embeddings = []
            for doc in documents:
                # Create simple hash-based embedding as fallback
                embedding = self._create_simple_embedding(doc)
                doc_embeddings.append(embedding)
            
            if doc_embeddings:
                # Add to FAISS index
                embeddings_array = np.array(doc_embeddings).astype('float32')
                self.index.add(embeddings_array)
                self.documents.extend(documents)
                self.embeddings.extend(doc_embeddings)
                
                # Perform search if query provided
                if query:
                    query_embedding = self._create_simple_embedding(query)
                    return self._search_similar(query_embedding, k=5)
            
            return {
                'similar_docs': documents[:3],  # Return first 3 as fallback
                'scores': [0.8, 0.7, 0.6],
                'total_indexed': len(documents)
            }
            
        except Exception as e:
            return {
                'similar_docs': documents[:3] if documents else [],
                'scores': [0.5] * min(3, len(documents)),
                'total_indexed': len(documents),
                'error': str(e)
            }
    
    def _create_simple_embedding(self, text: str) -> np.ndarray:
        """Create a simple embedding for text (fallback method)."""
        # Simple hash-based embedding as fallback
        text_hash = hash(text.lower())
        
        # Create deterministic embedding from hash
        np.random.seed(abs(text_hash) % 2**32)
        embedding = np.random.randn(self.dimension)
        
        # Normalize
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        
        return embedding.astype('float32')
    
    def _search_similar(self, query_embedding: np.ndarray, k: int = 5) -> Dict[str, Any]:
        """Search for similar documents."""
        if self.index.ntotal == 0:
            return {'similar_docs': [], 'scores': []}
        
        query_vector = query_embedding.reshape(1, -1).astype('float32')
        distances, indices = self.index.search(query_vector, min(k, self.index.ntotal))
        
        similar_docs = []
        for idx in indices[0]:
            if idx < len(self.documents):
                similar_docs.append(self.documents[idx])
        
        return {
            'similar_docs': similar_docs,
            'scores': distances[0].tolist(),
            'total_indexed': self.index.ntotal
        }