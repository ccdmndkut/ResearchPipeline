import aiohttp
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from bs4 import BeautifulSoup
import json

from app.settings import settings
from app.utils.logging_config import setup_logging

logger = setup_logging(__name__)

class WebFetch:
    """
    Tool for fetching and processing web content
    """

    def __init__(self):
        self.session = None
        self.timeout = aiohttp.ClientTimeout(total=30)
        self.headers = {
            'User-Agent': 'ResearchAssistant/1.0 (Academic Research Tool)'
        }

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(timeout=self.timeout, headers=self.headers)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute web fetch operation
        """
        url = parameters.get("url", "")
        action = parameters.get("action", "fetch")

        if action == "fetch":
            return await self.fetch_page(url, parameters)
        elif action == "fetch_multiple":
            return await self.fetch_multiple(parameters)
        elif action == "extract_data":
            return await self.extract_structured_data(url, parameters)
        else:
            raise ValueError(f"Unknown action: {action}")

    async def fetch_page(self, url: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fetch a single web page
        """
        extract_text = parameters.get("extract_text", True)
        extract_links = parameters.get("extract_links", False)
        extract_metadata = parameters.get("extract_metadata", False)

        if not self.session:
            self.session = aiohttp.ClientSession(timeout=self.timeout, headers=self.headers)

        try:
            async with self.session.get(url) as response:
                content = await response.text()
                soup = BeautifulSoup(content, 'html.parser')

                result = {
                    "url": url,
                    "status_code": response.status,
                    "content_type": response.headers.get('Content-Type', ''),
                    "timestamp": datetime.now().isoformat()
                }

                if extract_text:
                    # Remove script and style elements
                    for script in soup(["script", "style"]):
                        script.decompose()

                    text = soup.get_text()
                    lines = (line.strip() for line in text.splitlines())
                    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                    text = ' '.join(chunk for chunk in chunks if chunk)

                    result["text"] = text
                    result["word_count"] = len(text.split())

                if extract_links:
                    links = []
                    for link in soup.find_all('a', href=True):
                        links.append({
                            "text": link.get_text().strip(),
                            "href": link['href']
                        })
                    result["links"] = links[:100]  # Limit to 100 links

                if extract_metadata:
                    metadata = {}

                    # Title
                    title = soup.find('title')
                    if title:
                        metadata["title"] = title.get_text().strip()

                    # Meta tags
                    for meta in soup.find_all('meta'):
                        if meta.get('name'):
                            metadata[meta['name']] = meta.get('content', '')
                        elif meta.get('property'):
                            metadata[meta['property']] = meta.get('content', '')

                    result["metadata"] = metadata

                return result

        except asyncio.TimeoutError:
            logger.error(f"Timeout fetching {url}")
            return {
                "url": url,
                "status": "error",
                "error": "Request timeout"
            }
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return {
                "url": url,
                "status": "error",
                "error": str(e)
            }

    async def fetch_multiple(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fetch multiple URLs concurrently
        """
        urls = parameters.get("urls", [])
        max_concurrent = parameters.get("max_concurrent", 5)

        if not self.session:
            self.session = aiohttp.ClientSession(timeout=self.timeout, headers=self.headers)

        semaphore = asyncio.Semaphore(max_concurrent)

        async def fetch_with_semaphore(url):
            async with semaphore:
                return await self.fetch_page(url, parameters)

        tasks = [fetch_with_semaphore(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        successful = []
        failed = []
        for url, result in zip(urls, results):
            if isinstance(result, Exception):
                failed.append({
                    "url": url,
                    "error": str(result)
                })
            elif result.get("status") == "error":
                failed.append(result)
            else:
                successful.append(result)

        return {
            "total_urls": len(urls),
            "successful": len(successful),
            "failed": len(failed),
            "results": successful,
            "errors": failed,
            "timestamp": datetime.now().isoformat()
        }

    async def extract_structured_data(self, url: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract structured data from a web page
        """
        selectors = parameters.get("selectors", {})
        schema = parameters.get("schema", "article")

        if not self.session:
            self.session = aiohttp.ClientSession(timeout=self.timeout, headers=self.headers)

        try:
            async with self.session.get(url) as response:
                content = await response.text()
                soup = BeautifulSoup(content, 'html.parser')

                extracted_data = {}

                # Extract based on schema
                if schema == "article":
                    extracted_data = self._extract_article(soup)
                elif schema == "research_paper":
                    extracted_data = self._extract_research_paper(soup)
                elif schema == "custom" and selectors:
                    for key, selector in selectors.items():
                        element = soup.select_one(selector)
                        if element:
                            extracted_data[key] = element.get_text().strip()

                # Extract JSON-LD structured data
                json_ld = soup.find('script', type='application/ld+json')
                if json_ld:
                    try:
                        extracted_data["structured_data"] = json.loads(json_ld.string)
                    except json.JSONDecodeError:
                        pass

                return {
                    "url": url,
                    "status": "success",
                    "schema": schema,
                    "data": extracted_data,
                    "timestamp": datetime.now().isoformat()
                }

        except Exception as e:
            logger.error(f"Error extracting data from {url}: {e}")
            return {
                "url": url,
                "status": "error",
                "error": str(e)
            }

    def _extract_article(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        Extract article-like content
        """
        data = {}

        # Title
        title = soup.find('h1') or soup.find('title')
        if title:
            data["title"] = title.get_text().strip()

        # Author
        author = soup.find(class_=re.compile('author', re.I)) or \
                soup.find('meta', {'name': 'author'})
        if author:
            if author.name == 'meta':
                data["author"] = author.get('content', '')
            else:
                data["author"] = author.get_text().strip()

        # Date
        date = soup.find('time') or \
               soup.find(class_=re.compile('date|time', re.I))
        if date:
            data["date"] = date.get_text().strip()

        # Main content
        content = soup.find('article') or \
                 soup.find(class_=re.compile('content|article|post', re.I)) or \
                 soup.find('main')
        if content:
            data["content"] = content.get_text().strip()[:5000]  # Limit content

        return data

    def _extract_research_paper(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        Extract research paper metadata
        """
        data = {}

        # Title
        title = soup.find('h1', class_=re.compile('title', re.I)) or soup.find('h1')
        if title:
            data["title"] = title.get_text().strip()

        # Authors
        authors = soup.find_all(class_=re.compile('author', re.I))
        if authors:
            data["authors"] = [a.get_text().strip() for a in authors]

        # Abstract
        abstract = soup.find(class_=re.compile('abstract', re.I))
        if abstract:
            data["abstract"] = abstract.get_text().strip()

        # DOI
        doi = soup.find(text=re.compile(r'10\.\d{4,9}/[-._;()/:\w]+'))
        if doi:
            data["doi"] = doi.strip()

        return data

    def get_description(self) -> str:
        """
        Get tool description
        """
        return "Fetch and extract content from web pages"

    def get_parameters(self) -> Dict[str, Any]:
        """
        Get tool parameters schema
        """
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["fetch", "fetch_multiple", "extract_data"],
                    "description": "Action to perform"
                },
                "url": {
                    "type": "string",
                    "description": "URL to fetch"
                },
                "urls": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "URLs to fetch"
                },
                "extract_text": {
                    "type": "boolean",
                    "description": "Extract text content"
                },
                "extract_links": {
                    "type": "boolean",
                    "description": "Extract links"
                },
                "extract_metadata": {
                    "type": "boolean",
                    "description": "Extract metadata"
                },
                "schema": {
                    "type": "string",
                    "enum": ["article", "research_paper", "custom"],
                    "description": "Data extraction schema"
                }
            },
            "required": ["action"]
        }