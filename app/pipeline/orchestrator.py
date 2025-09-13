"""
Research Pipeline Orchestrator
Coordinates the entire research workflow including document processing,
knowledge graph building, vector search, and response composition.
"""
import asyncio
import json
from typing import Dict, Any, List
from app.pipeline.loaders import DocumentLoader
from app.pipeline.cleaners import TextCleaner
from app.pipeline.graph_builder import GraphBuilder
from app.pipeline.vector_store import VectorStore
from app.pipeline.retrieval import WebRetriever
from app.pipeline.composer import ResponseComposer


class ResearchOrchestrator:
    """Main orchestrator for the research pipeline workflow."""
    
    def __init__(self):
        """Initialize the orchestrator with all pipeline components."""
        self.loader = DocumentLoader()
        self.cleaner = TextCleaner()
        self.graph_builder = GraphBuilder()
        self.vector_store = VectorStore()
        self.retriever = WebRetriever()
        self.composer = ResponseComposer()
    
    def run_pipeline(self, query: str) -> Dict[str, Any]:
        """
        Run the complete research pipeline for a given query.
        
        Args:
            query: The research question to process
            
        Returns:
            Dict containing the research results with citations and analysis
        """
        try:
            # Step 1: Clean and process the query
            cleaned_query = self.cleaner.clean_text(query)
            
            # Step 2: Retrieve relevant information from web sources
            web_results = self.retriever.web_search(cleaned_query)
            
            # Step 3: Process documents and build knowledge graph
            if web_results.get('documents'):
                # Clean the retrieved text
                cleaned_docs = [
                    self.cleaner.clean_text(doc.get('content', '')) 
                    for doc in web_results['documents']
                ]
                
                # Build knowledge graph from documents
                graph_data = self.graph_builder.build_graph(cleaned_docs)
                
                # Index documents in vector store for semantic search
                vector_results = self.vector_store.index_documents(cleaned_docs, cleaned_query)
            else:
                graph_data = {'entities': [], 'relationships': []}
                vector_results = {'similar_docs': [], 'scores': []}
            
            # Step 4: Compose final response with all gathered information
            final_response = self.composer.compose_response(
                query=cleaned_query,
                web_results=web_results,
                graph_data=graph_data,
                vector_results=vector_results
            )
            
            return {
                'answer': final_response['answer'],
                'sources': final_response['sources'],
                'entities': graph_data['entities'][:10],  # Top 10 entities
                'confidence': final_response.get('confidence', 0.8),
                'processing_steps': [
                    'Query cleaning and preprocessing',
                    'Web search and content retrieval',
                    'Knowledge graph construction',
                    'Vector similarity analysis',
                    'Response synthesis with citations'
                ]
            }
            
        except Exception as e:
            return {
                'answer': f'Error processing query: {str(e)}',
                'sources': [],
                'entities': [],
                'confidence': 0.0,
                'processing_steps': ['Error occurred during processing']
            }
    
    async def run_pipeline_async(self, query: str) -> Dict[str, Any]:
        """
        Asynchronous version of the pipeline for improved performance.
        """
        # This could be expanded to run multiple steps in parallel
        return self.run_pipeline(query)
    
    def plan_workflow(self, documents: List[str]) -> Dict[str, Any]:
        """
        Plan the optimal workflow for processing given documents.
        """
        return {
            'steps': [
                'load_documents',
                'clean_text',
                'build_graph',
                'index_vectors',
                'compose_response'
            ],
            'estimated_time': len(documents) * 2,  # seconds
            'parallel_steps': ['build_graph', 'index_vectors']
        }