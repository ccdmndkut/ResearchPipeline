# Research Assistant - Implementation Guide

## Quick Start Implementation

This guide provides practical steps to implement the improvements outlined in the comprehensive plan.

## 1. Enhanced Orchestrator Implementation

### Step 1: Create Enhanced Orchestrator
```python
# app/orchestrator/enhanced_orchestrator_v2.py

import asyncio
from typing import Dict, List, Any, AsyncGenerator
from dataclasses import dataclass
from enum import Enum
import openai
from datetime import datetime

class QueryIntent(Enum):
    SEARCH = "search"
    SUMMARIZE = "summarize"
    ANALYZE = "analyze"
    VERIFY = "verify"

@dataclass
class ExecutionPlan:
    query: str
    intent: QueryIntent
    parallel_groups: List[List[str]]
    estimated_time: float
    cache_key: str

class SmartOrchestrator:
    def __init__(self):
        self.max_concurrent = 5
        self.semaphore = asyncio.Semaphore(self.max_concurrent)
        self.performance_metrics = {
            "total_queries": 0,
            "avg_response_time": 0,
            "cache_hits": 0
        }
    
    async def process_research_query(
        self, 
        query: str, 
        parameters: Dict[str, Any]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Process query with parallel execution"""
        
        # Step 1: Analyze query
        analysis = await self.analyze_query(query, parameters)
        yield self._event("analysis", "Query analyzed", analysis)
        
        # Step 2: Create execution plan
        plan = await self.create_execution_plan(analysis, parameters)
        yield self._event("planning", "Execution plan created", plan)
        
        # Step 3: Execute in parallel
        results = await self.execute_parallel(plan)
        yield self._event("execution", "Tasks completed", results)
        
        # Step 4: Score and rank results
        scored_results = await self.score_results(results, query)
        yield self._event("scoring", "Results ranked", scored_results)
        
        # Step 5: Format response
        formatted = await self.format_response(scored_results, parameters)
        yield self._event("complete", "Research complete", formatted)
    
    async def execute_parallel(self, plan: ExecutionPlan):
        """Execute tasks in parallel groups"""
        all_results = {}
        
        for group in plan.parallel_groups:
            tasks = []
            for task_id in group:
                tasks.append(self.execute_task(task_id))
            
            # Execute group in parallel
            group_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Collect results
            for task_id, result in zip(group, group_results):
                if isinstance(result, Exception):
                    all_results[task_id] = {"error": str(result)}
                else:
                    all_results[task_id] = result
        
        return all_results
```

### Step 2: Implement Quality Scorer
```python
# app/scoring/quality_scorer.py

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

class ResearchQualityScorer:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.weights = {
            "relevance": 0.35,
            "authority": 0.25,
            "recency": 0.20,
            "completeness": 0.20
        }
    
    def score_papers(self, papers: List[Dict], query: str) -> List[Dict]:
        """Score and rank papers based on quality metrics"""
        
        # Encode query for semantic similarity
        query_embedding = self.model.encode([query])
        
        scored_papers = []
        for paper in papers:
            # Calculate individual scores
            relevance = self._calculate_relevance(paper, query_embedding)
            authority = self._calculate_authority(paper)
            recency = self._calculate_recency(paper)
            completeness = self._calculate_completeness(paper)
            
            # Weighted combination
            total_score = (
                relevance * self.weights["relevance"] +
                authority * self.weights["authority"] +
                recency * self.weights["recency"] +
                completeness * self.weights["completeness"]
            )
            
            paper["quality_score"] = round(total_score, 3)
            paper["score_breakdown"] = {
                "relevance": relevance,
                "authority": authority,
                "recency": recency,
                "completeness": completeness
            }
            scored_papers.append(paper)
        
        # Sort by score
        return sorted(scored_papers, key=lambda x: x["quality_score"], reverse=True)
    
    def _calculate_relevance(self, paper: Dict, query_embedding) -> float:
        """Semantic similarity between paper and query"""
        text = f"{paper.get('title', '')} {paper.get('abstract', '')}"
        paper_embedding = self.model.encode([text])
        similarity = cosine_similarity(query_embedding, paper_embedding)[0][0]
        return float(similarity)
```

## 2. Response Formatter Implementation

### Step 1: Create Response Formatter Agent
```python
# app/agents/response_formatter_v2.py

from typing import Dict, List, Any
import jinja2
from pathlib import Path

class ResponseFormatter:
    def __init__(self):
        self.template_dir = Path("templates/responses")
        self.jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.template_dir)
        )
        
        self.audience_configs = {
            "academic": {
                "technical_level": "high",
                "include_methodology": True,
                "citation_style": "APA",
                "length": "detailed"
            },
            "business": {
                "technical_level": "medium",
                "include_summary": True,
                "focus": "actionable_insights",
                "length": "concise"
            },
            "public": {
                "technical_level": "low",
                "use_analogies": True,
                "avoid_jargon": True,
                "length": "brief"
            }
        }
    
    async def format_results(
        self,
        results: Dict[str, Any],
        audience: str = "academic",
        format_type: str = "report"
    ) -> Dict[str, Any]:
        """Format results for specific audience"""
        
        config = self.audience_configs.get(audience, self.audience_configs["academic"])
        
        # Process results based on audience
        processed = await self._process_for_audience(results, config)
        
        # Generate formatted output
        if format_type == "report":
            return await self._generate_report(processed, audience)
        elif format_type == "summary":
            return await self._generate_summary(processed, audience)
        elif format_type == "visualization":
            return await self._generate_visualization(processed)
        else:
            return processed
    
    async def _generate_report(self, data: Dict, audience: str) -> Dict:
        """Generate formatted report"""
        template = self.jinja_env.get_template(f"{audience}_report.html")
        
        sections = []
        
        # Executive Summary
        sections.append({
            "title": "Executive Summary",
            "content": self._create_summary(data),
            "level": 1
        })
        
        # Key Findings
        sections.append({
            "title": "Key Findings",
            "content": self._extract_key_findings(data),
            "bullets": True,
            "level": 1
        })
        
        # Detailed Analysis
        if audience == "academic":
            sections.append({
                "title": "Literature Analysis",
                "content": self._create_literature_review(data),
                "subsections": self._create_paper_summaries(data),
                "level": 1
            })
        
        # Recommendations
        sections.append({
            "title": "Recommendations",
            "content": self._generate_recommendations(data, audience),
            "level": 1
        })
        
        # References
        sections.append({
            "title": "References",
            "content": self._format_citations(data, audience),
            "level": 1
        })
        
        html = template.render(
            title=data.get("query", "Research Report"),
            sections=sections,
            metadata=data.get("metadata", {}),
            generated_at=datetime.now().isoformat()
        )
        
        return {
            "html": html,
            "sections": sections,
            "metadata": {
                "audience": audience,
                "format": "report",
                "word_count": len(html.split()),
                "generated_at": datetime.now().isoformat()
            }
        }
```

### Step 2: Create Templates
```html
<!-- templates/responses/academic_report.html -->
<!DOCTYPE html>
<html>
<head>
    <title>{{ title }}</title>
    <style>
        body { 
            font-family: 'Times New Roman', serif; 
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        h1 { color: #333; border-bottom: 2px solid #333; }
        h2 { color: #555; margin-top: 30px; }
        .citation { font-size: 0.9em; color: #666; }
        .abstract { 
            background: #f5f5f5; 
            padding: 15px; 
            border-left: 4px solid #0066cc;
            margin: 20px 0;
        }
        table { 
            border-collapse: collapse; 
            width: 100%; 
            margin: 20px 0;
        }
        th, td { 
            border: 1px solid #ddd; 
            padding: 12px; 
            text-align: left;
        }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <h1>{{ title }}</h1>
    
    <div class="metadata">
        <p><strong>Generated:</strong> {{ generated_at }}</p>
        <p><strong>Total Papers Analyzed:</strong> {{ metadata.total_papers }}</p>
    </div>
    
    {% for section in sections %}
        <h{{ section.level + 1 }}>{{ section.title }}</h{{ section.level + 1 }}>
        
        {% if section.bullets %}
            <ul>
            {% for item in section.content %}
                <li>{{ item }}</li>
            {% endfor %}
            </ul>
        {% else %}
            <p>{{ section.content }}</p>
        {% endif %}
        
        {% if section.subsections %}
            {% for subsection in section.subsections %}
                <div class="abstract">
                    <h3>{{ subsection.title }}</h3>
                    <p>{{ subsection.content }}</p>
                    <p class="citation">{{ subsection.citation }}</p>
                </div>
            {% endfor %}
        {% endif %}
    {% endfor %}
</body>
</html>
```

## 3. React Frontend Implementation

### Step 1: Set Up React App
```bash
# Create new React app with TypeScript
npx create-react-app research-assistant-ui --template typescript
cd research-assistant-ui

# Install dependencies
npm install @mui/material @emotion/react @emotion/styled
npm install axios socket.io-client
npm install recharts d3
npm install @reduxjs/toolkit react-redux
```

### Step 2: Create Main Components
```typescript
// src/components/ResearchDashboard.tsx

import React, { useState, useEffect } from 'react';
import {
    Box,
    Paper,
    TextField,
    Button,
    Grid,
    Typography,
    LinearProgress,
    Chip,
    Card,
    CardContent
} from '@mui/material';
import { Search, FilterList, Download } from '@mui/icons-material';
import { useWebSocket } from '../hooks/useWebSocket';
import ResultsList from './ResultsList';
import FilterPanel from './FilterPanel';
import VisualizationPanel from './VisualizationPanel';

interface ResearchDashboardProps {
    onExport: (format: string) => void;
}

const ResearchDashboard: React.FC<ResearchDashboardProps> = ({ onExport }) => {
    const [query, setQuery] = useState('');
    const [filters, setFilters] = useState({
        databases: ['arxiv', 'semantic_scholar'],
        dateRange: null,
        minCitations: 0
    });
    const [results, setResults] = useState([]);
    const [loading, setLoading] = useState(false);
    const [progress, setProgress] = useState(0);
    
    const { messages, sendMessage, isConnected } = useWebSocket(
        'ws://localhost:8000/ws'
    );
    
    useEffect(() => {
        // Handle incoming WebSocket messages
        if (messages.length > 0) {
            const lastMessage = messages[messages.length - 1];
            handleWebSocketMessage(lastMessage);
        }
    }, [messages]);
    
    const handleWebSocketMessage = (message: any) => {
        switch (message.event_type) {
            case 'progress':
                setProgress(message.data.percentage);
                break;
            case 'result':
                setResults(message.data.papers);
                setLoading(false);
                break;
            case 'error':
                console.error('Search error:', message.message);
                setLoading(false);
                break;
        }
    };
    
    const handleSearch = () => {
        setLoading(true);
        setProgress(0);
        
        sendMessage({
            query,
            parameters: {
                ...filters,
                mode: 'parallel',
                quality_threshold: 0.7
            },
            session_id: Date.now().toString()
        });
    };
    
    return (
        <Box sx={{ flexGrow: 1, p: 3 }}>
            <Grid container spacing={3}>
                {/* Search Bar */}
                <Grid item xs={12}>
                    <Paper sx={{ p: 2 }}>
                        <Box display="flex" gap={2}>
                            <TextField
                                fullWidth
                                variant="outlined"
                                placeholder="Enter your research query..."
                                value={query}
                                onChange={(e) => setQuery(e.target.value)}
                                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                                InputProps={{
                                    startAdornment: <Search sx={{ mr: 1 }} />
                                }}
                            />
                            <Button
                                variant="contained"
                                onClick={handleSearch}
                                disabled={loading || !query}
                                sx={{ minWidth: 120 }}
                            >
                                {loading ? 'Searching...' : 'Search'}
                            </Button>
                        </Box>
                        
                        {/* Database Chips */}
                        <Box mt={2} display="flex" gap={1}>
                            {filters.databases.map(db => (
                                <Chip
                                    key={db}
                                    label={db}
                                    color="primary"
                                    variant="outlined"
                                />
                            ))}
                        </Box>
                    </Paper>
                </Grid>
                
                {/* Progress Bar */}
                {loading && (
                    <Grid item xs={12}>
                        <Paper sx={{ p: 2 }}>
                            <Typography variant="body2" gutterBottom>
                                Processing your query...
                            </Typography>
                            <LinearProgress variant="determinate" value={progress} />
                        </Paper>
                    </Grid>
                )}
                
                {/* Main Content Area */}
                <Grid item xs={12} md={3}>
                    <FilterPanel
                        filters={filters}
                        onFiltersChange={setFilters}
                    />
                </Grid>
                
                <Grid item xs={12} md={6}>
                    <ResultsList
                        results={results}
                        loading={loading}
                    />
                </Grid>
                
                <Grid item xs={12} md={3}>
                    <VisualizationPanel
                        data={results}
                        onExport={onExport}
                    />
                </Grid>
            </Grid>
        </Box>
    );
};

export default ResearchDashboard;
```

### Step 3: Create WebSocket Hook
```typescript
// src/hooks/useWebSocket.ts

import { useState, useEffect, useCallback } from 'react';
import io, { Socket } from 'socket.io-client';

interface UseWebSocketReturn {
    messages: any[];
    sendMessage: (data: any) => void;
    isConnected: boolean;
    error: Error | null;
}

export const useWebSocket = (url: string): UseWebSocketReturn => {
    const [socket, setSocket] = useState<Socket | null>(null);
    const [messages, setMessages] = useState<any[]>([]);
    const [isConnected, setIsConnected] = useState(false);
    const [error, setError] = useState<Error | null>(null);
    
    useEffect(() => {
        const newSocket = io(url, {
            transports: ['websocket'],
            reconnection: true,
            reconnectionAttempts: 5,
            reconnectionDelay: 1000
        });
        
        newSocket.on('connect', () => {
            console.log('WebSocket connected');
            setIsConnected(true);
            setError(null);
        });
        
        newSocket.on('disconnect', () => {
            console.log('WebSocket disconnected');
            setIsConnected(false);
        });
        
        newSocket.on('message', (data) => {
            setMessages(prev => [...prev, data]);
        });
        
        newSocket.on('error', (err) => {
            setError(err);
        });
        
        setSocket(newSocket);
        
        return () => {
            newSocket.close();
        };
    }, [url]);
    
    const sendMessage = useCallback((data: any) => {
        if (socket && isConnected) {
            socket.emit('message', data);
        }
    }, [socket, isConnected]);
    
    return {
        messages,
        sendMessage,
        isConnected,
        error
    };
};
```

## 4. Testing Implementation

### Step 1: Create Test Suite
```python
# tests/test_enhanced_features.py

import pytest
import asyncio
from app.orchestrator.enhanced_orchestrator_v2 import SmartOrchestrator
from app.agents.response_formatter_v2 import ResponseFormatter

@pytest.fixture
def orchestrator():
    return SmartOrchestrator()

@pytest.fixture
def formatter():
    return ResponseFormatter()

@pytest.mark.asyncio
async def test_parallel_execution(orchestrator):
    """Test parallel task execution"""
    query = "machine learning in healthcare"
    parameters = {
        "databases": ["arxiv", "pubmed"],
        "max_results": 10
    }
    
    results = []
    async for event in orchestrator.process_research_query(query, parameters):
        results.append(event)
    
    assert len(results) > 0
    assert results[-1]["event_type"] == "complete"

@pytest.mark.asyncio
async def test_response_formatting(formatter):
    """Test response formatting for different audiences"""
    test_results = {
        "papers": [
            {
                "title": "Deep Learning in Medical Imaging",
                "abstract": "A comprehensive study...",
                "authors": ["Smith, J.", "Doe, A."],
                "year": 2024,
                "quality_score": 0.85
            }
        ],
        "query": "medical AI"
    }
    
    # Test academic formatting
    academic_report = await formatter.format_results(
        test_results, 
        audience="academic",
        format_type="report"
    )
    assert "Literature Analysis" in academic_report["html"]
    
    # Test business formatting
    business_report = await formatter.format_results(
        test_results,
        audience="business",
        format_type="summary"
    )
    assert len(business_report["sections"]) > 0
```

## 5. Deployment Configuration

### Docker Setup
```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose
```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - DATABASE_URL=postgresql://user:pass@db:5432/research
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
  
  frontend:
    build: ./research-assistant-ui
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8000
  
  db:
    image: postgres:14
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=research
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

## Quick Implementation Checklist

### Week 1: Core Backend
- [ ] Implement EnhancedOrchestrator
- [ ] Add parallel execution
- [ ] Create quality scorer
- [ ] Set up Redis caching

### Week 2: Response Formatter
- [ ] Build ResponseFormatter class
- [ ] Create audience templates
- [ ] Add export functionality
- [ ] Test formatting outputs

### Week 3: Frontend
- [ ] Set up React app
- [ ] Create dashboard components
- [ ] Implement WebSocket connection
- [ ] Add visualizations

### Week 4: Integration
- [ ] Connect frontend to backend
- [ ] Test end-to-end flow
- [ ] Add error handling
- [ ] Performance optimization

### Week 5: Deployment
- [ ] Set up Docker containers
- [ ] Configure CI/CD pipeline
- [ ] Deploy to staging
- [ ] Production rollout

## Commands to Get Started

```bash
# Backend setup
cd research-assistant
pip install -r requirements.txt
python -m pytest tests/

# Frontend setup
cd research-assistant-ui
npm install
npm start

# Docker deployment
docker-compose up -d

# Run tests
pytest tests/ --cov=app --cov-report=html
```

This implementation guide provides concrete code examples and steps to transform your Research Assistant with the proposed improvements.