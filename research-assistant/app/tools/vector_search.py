import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime
import openai
import pickle
import os

try:
    import faiss
    HAS_FAISS = True
except ImportError:
    HAS_FAISS = False

from app.settings import settings
from app.utils.logging_config import setup_logging

logger = setup_logging(__name__)

class VectorSearch:
    """
    Tool for semantic similarity search using embeddings
    """

    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        self.embedding_model = settings.EMBEDDING_MODEL
        self.index = None
        self.documents = []
        self.dimension = 1536  # Default for OpenAI embeddings

    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform vector search operation
        """
        action = parameters.get("action", "search")

        if action == "index":
            return await self.index_documents(parameters)
        elif action == "search":
            return await self.search_similar(parameters)
        elif action == "add":
            return await self.add_documents(parameters)
        else:
            raise ValueError(f"Unknown action: {action}")

    async def index_documents(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Index documents for search
        """
        documents = parameters.get("documents", [])
        index_type = parameters.get("index_type", "flat")

        try:
            # Extract text from documents
            texts = []
            metadata = []
            for doc in documents:
                if isinstance(doc, dict):
                    texts.append(doc.get("text", ""))
                    metadata.append({
                        "id": doc.get("id", ""),
                        "title": doc.get("title", ""),
                        "metadata": doc.get("metadata", {})
                    })
                else:
                    texts.append(str(doc))
                    metadata.append({})

            # Generate embeddings
            embeddings = await self._generate_embeddings(texts)

            # Create index
            if HAS_FAISS:
                # Create FAISS index
                if index_type == "flat":
                    self.index = faiss.IndexFlatL2(self.dimension)
                elif index_type == "ivf":
                    quantizer = faiss.IndexFlatL2(self.dimension)
                    self.index = faiss.IndexIVFFlat(quantizer, self.dimension, min(100, len(embeddings)))
                    self.index.train(np.array(embeddings).astype('float32'))

                # Add vectors to index
                self.index.add(np.array(embeddings).astype('float32'))
                self.documents = metadata
            else:
                # Simple numpy-based fallback
                self.index = np.array(embeddings)
                self.documents = metadata

            return {
                "status": "success",
                "num_indexed": len(documents),
                "index_type": index_type,
                "dimension": self.dimension,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Indexing error: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def search_similar(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search for similar documents
        """
        query = parameters.get("query", "")
        top_k = parameters.get("top_k", 10)
        threshold = parameters.get("threshold", 0.0)

        if not self.index:
            return {
                "status": "error",
                "error": "No index available. Please index documents first."
            }

        try:
            # Generate query embedding
            query_embedding = await self._generate_embedding(query)

            # Search index
            if HAS_FAISS and hasattr(self.index, 'search'):
                distances, indices = self.index.search(
                    np.array([query_embedding]).astype('float32'),
                    min(top_k, self.index.ntotal)
                )
            else:
                # Numpy fallback - compute distances manually
                query_vec = np.array(query_embedding)
                distances_all = np.sum((self.index - query_vec) ** 2, axis=1)
                indices = np.argsort(distances_all)[:top_k]
                distances = [distances_all[indices].tolist()]
                indices = [indices.tolist()]

            # Format results
            results = []
            for dist, idx in zip(distances[0], indices[0]):
                if idx < len(self.documents) and dist <= threshold if threshold > 0 else True:
                    result = {
                        "score": float(1 / (1 + dist)),  # Convert distance to similarity
                        "distance": float(dist),
                        "document": self.documents[idx]
                    }
                    results.append(result)

            return {
                "status": "success",
                "query": query,
                "num_results": len(results),
                "results": results,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Search error: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def add_documents(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add new documents to existing index
        """
        documents = parameters.get("documents", [])

        if not self.index:
            return await self.index_documents(parameters)

        try:
            texts = []
            metadata = []
            for doc in documents:
                if isinstance(doc, dict):
                    texts.append(doc.get("text", ""))
                    metadata.append({
                        "id": doc.get("id", ""),
                        "title": doc.get("title", ""),
                        "metadata": doc.get("metadata", {})
                    })
                else:
                    texts.append(str(doc))
                    metadata.append({})

            # Generate embeddings
            embeddings = await self._generate_embeddings(texts)

            # Add to index
            self.index.add(np.array(embeddings).astype('float32'))
            self.documents.extend(metadata)

            return {
                "status": "success",
                "num_added": len(documents),
                "total_documents": len(self.documents),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Add documents error: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def _generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text
        """
        response = self.client.embeddings.create(
            model=self.embedding_model,
            input=text[:8000]  # Truncate to avoid token limits
        )
        return response.data[0].embedding

    async def _generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts
        """
        # Process in batches to avoid rate limits
        batch_size = 20
        all_embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            # Truncate each text to avoid token limits
            batch = [text[:8000] for text in batch]

            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=batch
            )

            embeddings = [item.embedding for item in response.data]
            all_embeddings.extend(embeddings)

        return all_embeddings

    def save_index(self, file_path: str):
        """
        Save index to file
        """
        if self.index is not None:
            if HAS_FAISS and hasattr(self.index, 'search'):
                faiss.write_index(self.index, f"{file_path}.index")
            else:
                # Save numpy array
                np.save(f"{file_path}.npy", self.index)

            with open(f"{file_path}.meta", 'wb') as f:
                pickle.dump(self.documents, f)

    def load_index(self, file_path: str):
        """
        Load index from file
        """
        if HAS_FAISS and os.path.exists(f"{file_path}.index"):
            self.index = faiss.read_index(f"{file_path}.index")
        elif os.path.exists(f"{file_path}.npy"):
            self.index = np.load(f"{file_path}.npy")

        with open(f"{file_path}.meta", 'rb') as f:
            self.documents = pickle.load(f)

    def get_description(self) -> str:
        """
        Get tool description
        """
        return "Perform semantic similarity search using embeddings"

    def get_parameters(self) -> Dict[str, Any]:
        """
        Get tool parameters schema
        """
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["index", "search", "add"],
                    "description": "Action to perform"
                },
                "documents": {
                    "type": "array",
                    "description": "Documents to index or add"
                },
                "query": {
                    "type": "string",
                    "description": "Search query"
                },
                "top_k": {
                    "type": "integer",
                    "description": "Number of results to return"
                },
                "threshold": {
                    "type": "number",
                    "description": "Similarity threshold"
                }
            },
            "required": ["action"]
        }