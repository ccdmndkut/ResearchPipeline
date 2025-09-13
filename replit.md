# Overview

This is an AI-powered research pipeline that orchestrates multiple components to answer research questions. The system takes a user query and processes it through web retrieval, knowledge graph construction, vector-based semantic search, and LLM-powered response synthesis to provide comprehensive research results with citations.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Web Application Framework
- **Flask-based web application** with a simple HTML frontend
- Single-page interface for submitting research queries
- RESTful API endpoints for processing requests
- Development server configured for Replit hosting (0.0.0.0:5000)

## Pipeline Architecture
- **Modular pipeline design** with separate components for each processing stage
- **Orchestrator pattern** that coordinates workflow between all components
- **Sequential processing** through distinct stages: retrieval → cleaning → graph building → vector search → synthesis

## Core Components

### Document Processing
- **DocumentLoader**: Handles various input formats (text, JSON, HTML, URLs)
- **TextCleaner**: Preprocesses text with cleaning, normalization, and chunking
- **Validation system** for input schemas and content types

### Knowledge Extraction
- **GraphBuilder**: Extracts entities and relationships using NetworkX
- **Simple NLP techniques** for entity recognition (capitalized words/phrases)
- **Knowledge graph construction** with entity-relationship mapping

### Vector-Based Search
- **FAISS integration** for efficient similarity search
- **384-dimensional embeddings** (standard sentence transformer size)
- **Fallback hash-based embeddings** when proper models unavailable
- **In-memory vector indexing** with document storage

### Web Retrieval
- **Web scraping capabilities** using Trafilatura for content extraction
- **Mock search functionality** with Wikipedia endpoints for development
- **Content summarization** and source citation tracking
- **Timeout and result limiting** for performance control

### Response Synthesis
- **OpenAI GPT integration** for intelligent response composition
- **Fallback text assembly** when LLM unavailable
- **Citation management** linking sources to generated content
- **Context preparation** from multiple information sources

## Configuration Management
- **Environment variable support** for API keys and settings
- **JSON configuration files** with environment overrides
- **Caching utilities** for performance optimization
- **Development/production mode switching**

## Error Handling
- **Graceful degradation** when external services fail
- **Try-catch blocks** around all external API calls
- **Fallback mechanisms** for core functionality
- **Comprehensive logging** for debugging

# External Dependencies

## Required Services
- **OpenAI API** - GPT models for response synthesis and text generation
- **Web content sources** - Currently mocked with Wikipedia URLs for development

## Python Libraries
- **Flask** - Web framework for API and frontend
- **NetworkX** - Graph construction and analysis
- **FAISS** - Vector similarity search and indexing
- **Trafilatura** - Web content extraction and cleaning
- **OpenAI Python client** - GPT API integration
- **NumPy** - Numerical operations for embeddings
- **Requests** - HTTP client for web retrieval

## Planned Integrations
- **Sentence Transformers** - Proper semantic embeddings (currently using hash-based fallback)
- **Search APIs** - Real web search instead of mock results
- **Redis** - Production caching system
- **PostgreSQL** - Persistent data storage (may be added by code agent)

## Development Environment
- **Replit hosting** - Configured for cloud development environment
- **Environment variables** - API key and configuration management
- **Debug mode** - Enabled for development with auto-reload