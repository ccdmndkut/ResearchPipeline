import openai
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import networkx as nx
import json

from app.settings import settings
from app.utils.prompt_loader import load_prompt
from app.utils.logging_config import setup_logging

logger = setup_logging(__name__)

class GraphAgent:
    """
    Agent for analyzing citation networks and research trends
    """

    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.system_prompt = load_prompt("graph_agent_prompt.txt")

    async def execute(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a graph analysis action
        """
        if action == "build_network":
            return await self.build_citation_network(parameters)
        elif action == "analyze_trends":
            return await self.analyze_trends(parameters)
        elif action == "find_communities":
            return await self.find_communities(parameters)
        elif action == "calculate_metrics":
            return await self.calculate_metrics(parameters)
        else:
            raise ValueError(f"Unknown action: {action}")

    async def build_citation_network(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build a citation network from papers
        """
        papers = parameters.get("papers", [])
        depth = parameters.get("depth", 1)

        # Create directed graph
        G = nx.DiGraph()

        # Add nodes for each paper
        for paper in papers:
            paper_id = paper.get("id", paper.get("title", "Unknown"))
            G.add_node(
                paper_id,
                title=paper.get("title", "Unknown"),
                year=paper.get("year", 0),
                authors=paper.get("authors", []),
                citations=paper.get("citation_count", 0)
            )

            # Add edges for citations
            for cited in paper.get("references", []):
                G.add_edge(paper_id, cited)

        # Calculate basic metrics
        metrics = {
            "nodes": G.number_of_nodes(),
            "edges": G.number_of_edges(),
            "density": nx.density(G) if G.number_of_nodes() > 0 else 0,
            "avg_degree": sum(dict(G.degree()).values()) / G.number_of_nodes() if G.number_of_nodes() > 0 else 0
        }

        # Find most cited papers
        in_degrees = dict(G.in_degree())
        top_cited = sorted(in_degrees.items(), key=lambda x: x[1], reverse=True)[:10]

        return {
            "network_stats": metrics,
            "top_cited_papers": [
                {
                    "id": node,
                    "citations": degree,
                    "title": G.nodes[node].get("title", "Unknown") if node in G.nodes else "External"
                }
                for node, degree in top_cited
            ],
            "graph_data": self._serialize_graph(G),
            "timestamp": datetime.now().isoformat()
        }

    async def analyze_trends(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze research trends over time
        """
        papers = parameters.get("papers", [])
        time_window = parameters.get("time_window", "yearly")

        # Group papers by year
        papers_by_year = {}
        for paper in papers:
            year = paper.get("year", 0)
            if year not in papers_by_year:
                papers_by_year[year] = []
            papers_by_year[year].append(paper)

        # Analyze topics per year using LLM
        trends = {}
        for year, year_papers in papers_by_year.items():
            if year_papers:
                topics = await self._extract_topics(year_papers)
                trends[year] = {
                    "paper_count": len(year_papers),
                    "topics": topics,
                    "avg_citations": sum(p.get("citation_count", 0) for p in year_papers) / len(year_papers)
                }

        # Calculate growth rate
        years = sorted(papers_by_year.keys())
        if len(years) >= 2:
            growth_rate = (len(papers_by_year[years[-1]]) - len(papers_by_year[years[0]])) / len(papers_by_year[years[0]])
        else:
            growth_rate = 0

        return {
            "time_window": time_window,
            "trends_by_year": trends,
            "growth_rate": growth_rate,
            "total_papers": len(papers),
            "year_range": [min(years), max(years)] if years else [0, 0],
            "timestamp": datetime.now().isoformat()
        }

    async def find_communities(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Find research communities in the network
        """
        papers = parameters.get("papers", [])
        method = parameters.get("method", "louvain")

        # Build collaboration network
        G = nx.Graph()

        # Add edges between co-authors
        for paper in papers:
            authors = paper.get("authors", [])
            for i in range(len(authors)):
                for j in range(i + 1, len(authors)):
                    if G.has_edge(authors[i], authors[j]):
                        G[authors[i]][authors[j]]["weight"] += 1
                    else:
                        G.add_edge(authors[i], authors[j], weight=1)

        # Find communities
        if G.number_of_nodes() > 0:
            communities = list(nx.community.greedy_modularity_communities(G))
        else:
            communities = []

        # Analyze each community
        community_info = []
        for i, community in enumerate(communities[:10]):  # Limit to top 10
            members = list(community)
            # Find papers by community members
            community_papers = [
                p for p in papers
                if any(author in members for author in p.get("authors", []))
            ]

            # Extract main topics for this community
            if community_papers:
                topics = await self._extract_topics(community_papers[:10])
            else:
                topics = []

            community_info.append({
                "id": i + 1,
                "size": len(members),
                "key_members": members[:5],
                "main_topics": topics[:3],
                "paper_count": len(community_papers)
            })

        return {
            "num_communities": len(communities),
            "communities": community_info,
            "network_modularity": nx.community.modularity(G, communities) if communities else 0,
            "timestamp": datetime.now().isoformat()
        }

    async def calculate_metrics(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate various network metrics
        """
        papers = parameters.get("papers", [])
        metrics_type = parameters.get("metrics_type", "all")

        # Build graph
        G = nx.DiGraph()
        for paper in papers:
            paper_id = paper.get("id", paper.get("title", "Unknown"))
            G.add_node(paper_id, **paper)
            for ref in paper.get("references", []):
                G.add_edge(paper_id, ref)

        metrics = {}

        if metrics_type in ["all", "centrality"]:
            # Calculate centrality metrics
            if G.number_of_nodes() > 0:
                metrics["centrality"] = {
                    "degree": dict(nx.degree_centrality(G)),
                    "betweenness": dict(nx.betweenness_centrality(G)),
                    "closeness": dict(nx.closeness_centrality(G)),
                    "pagerank": dict(nx.pagerank(G)) if G.number_of_edges() > 0 else {}
                }

        if metrics_type in ["all", "clustering"]:
            # Calculate clustering metrics
            metrics["clustering"] = {
                "avg_clustering": nx.average_clustering(G.to_undirected()) if G.number_of_nodes() > 0 else 0,
                "transitivity": nx.transitivity(G.to_undirected())
            }

        if metrics_type in ["all", "connectivity"]:
            # Calculate connectivity metrics
            metrics["connectivity"] = {
                "is_connected": nx.is_weakly_connected(G) if G.number_of_nodes() > 0 else False,
                "num_components": nx.number_weakly_connected_components(G),
                "largest_component_size": len(max(nx.weakly_connected_components(G), key=len)) if G.number_of_nodes() > 0 else 0
            }

        return {
            "metrics_type": metrics_type,
            "metrics": metrics,
            "num_nodes": G.number_of_nodes(),
            "num_edges": G.number_of_edges(),
            "timestamp": datetime.now().isoformat()
        }

    async def _extract_topics(self, papers: List[Dict[str, Any]]) -> List[str]:
        """
        Extract main topics from papers using LLM
        """
        abstracts = "\n".join([
            p.get("abstract", "")[:200]
            for p in papers[:10]
        ])

        messages = [
            {"role": "system", "content": "Extract the main research topics from these abstracts."},
            {"role": "user", "content": f"Abstracts:\n{abstracts}\n\nList the top 5 main topics:"}
        ]

        response = await self.client.chat.completions.create(
            model=settings.AGENT_MODEL,
            messages=messages,
            temperature=0.3,
            max_tokens=200
        )

        topics_text = response.choices[0].message.content
        topics = [line.strip() for line in topics_text.split('\n') if line.strip()]
        return topics[:5]

    def _serialize_graph(self, G: nx.Graph) -> Dict[str, Any]:
        """
        Serialize NetworkX graph to JSON-compatible format
        """
        return {
            "nodes": [
                {
                    "id": node,
                    "attributes": G.nodes[node]
                }
                for node in G.nodes()
            ],
            "edges": [
                {
                    "source": source,
                    "target": target,
                    "attributes": G.edges[source, target]
                }
                for source, target in G.edges()
            ]
        }

    def get_description(self) -> str:
        """
        Get agent description
        """
        return "Analyze citation networks and research trends"

    def get_parameters(self) -> Dict[str, Any]:
        """
        Get agent parameters schema
        """
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["build_network", "analyze_trends", "find_communities", "calculate_metrics"]
                },
                "papers": {
                    "type": "array",
                    "description": "Papers to analyze"
                },
                "depth": {
                    "type": "integer",
                    "description": "Network depth"
                },
                "time_window": {
                    "type": "string",
                    "enum": ["yearly", "monthly", "quarterly"]
                },
                "metrics_type": {
                    "type": "string",
                    "enum": ["all", "centrality", "clustering", "connectivity"]
                }
            },
            "required": ["action", "papers"]
        }