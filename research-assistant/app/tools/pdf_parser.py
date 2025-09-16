import io
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
import PyPDF2
import pdfplumber

from app.utils.logging_config import setup_logging

logger = setup_logging(__name__)

class PDFParser:
    """
    Tool for extracting text and metadata from PDF documents
    """

    def __init__(self):
        self.max_pages = 100  # Limit for processing

    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract content from PDF
        """
        file_path = parameters.get("file_path")
        file_bytes = parameters.get("file_bytes")
        extract_images = parameters.get("extract_images", False)
        extract_tables = parameters.get("extract_tables", False)
        max_pages = parameters.get("max_pages", self.max_pages)

        try:
            if file_path:
                return await self._parse_from_file(file_path, extract_images, extract_tables, max_pages)
            elif file_bytes:
                return await self._parse_from_bytes(file_bytes, extract_images, extract_tables, max_pages)
            else:
                raise ValueError("Either file_path or file_bytes must be provided")

        except Exception as e:
            logger.error(f"PDF parsing error: {e}")
            return {
                "error": str(e),
                "status": "failed"
            }

    async def _parse_from_file(
        self,
        file_path: str,
        extract_images: bool,
        extract_tables: bool,
        max_pages: int
    ) -> Dict[str, Any]:
        """
        Parse PDF from file path
        """
        metadata = {}
        text_content = []
        tables = []

        # Extract metadata and text with PyPDF2
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)

            # Extract metadata
            if pdf_reader.metadata:
                metadata = {
                    "title": pdf_reader.metadata.get('/Title', ''),
                    "author": pdf_reader.metadata.get('/Author', ''),
                    "subject": pdf_reader.metadata.get('/Subject', ''),
                    "creator": pdf_reader.metadata.get('/Creator', ''),
                    "creation_date": str(pdf_reader.metadata.get('/CreationDate', '')),
                    "modification_date": str(pdf_reader.metadata.get('/ModDate', ''))
                }

            # Extract text
            num_pages = min(len(pdf_reader.pages), max_pages)
            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                text_content.append({
                    "page": page_num + 1,
                    "text": text
                })

        # Extract tables with pdfplumber if requested
        if extract_tables:
            with pdfplumber.open(file_path) as pdf:
                for page_num in range(min(len(pdf.pages), max_pages)):
                    page = pdf.pages[page_num]
                    page_tables = page.extract_tables()
                    if page_tables:
                        tables.append({
                            "page": page_num + 1,
                            "tables": page_tables
                        })

        # Extract structured information
        full_text = " ".join([p["text"] for p in text_content])
        structured_info = self._extract_structured_info(full_text)

        return {
            "status": "success",
            "metadata": metadata,
            "num_pages": num_pages,
            "text_content": text_content,
            "tables": tables,
            "structured_info": structured_info,
            "word_count": len(full_text.split()),
            "timestamp": datetime.now().isoformat()
        }

    async def _parse_from_bytes(
        self,
        file_bytes: bytes,
        extract_images: bool,
        extract_tables: bool,
        max_pages: int
    ) -> Dict[str, Any]:
        """
        Parse PDF from bytes
        """
        pdf_file = io.BytesIO(file_bytes)
        pdf_reader = PyPDF2.PdfReader(pdf_file)

        # Similar processing as _parse_from_file
        # but using bytes input
        metadata = {}
        text_content = []

        if pdf_reader.metadata:
            metadata = {
                "title": pdf_reader.metadata.get('/Title', ''),
                "author": pdf_reader.metadata.get('/Author', ''),
                "creation_date": str(pdf_reader.metadata.get('/CreationDate', ''))
            }

        num_pages = min(len(pdf_reader.pages), max_pages)
        for page_num in range(num_pages):
            page = pdf_reader.pages[page_num]
            text = page.extract_text()
            text_content.append({
                "page": page_num + 1,
                "text": text
            })

        full_text = " ".join([p["text"] for p in text_content])
        structured_info = self._extract_structured_info(full_text)

        return {
            "status": "success",
            "metadata": metadata,
            "num_pages": num_pages,
            "text_content": text_content,
            "structured_info": structured_info,
            "word_count": len(full_text.split()),
            "timestamp": datetime.now().isoformat()
        }

    def _extract_structured_info(self, text: str) -> Dict[str, Any]:
        """
        Extract structured information from text
        """
        info = {}

        # Extract DOI
        doi_pattern = r'10\.\d{4,9}/[-._;()/:\w]+'
        doi_matches = re.findall(doi_pattern, text)
        if doi_matches:
            info["doi"] = doi_matches[0]

        # Extract email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            info["emails"] = list(set(emails))

        # Extract sections
        sections = self._extract_sections(text)
        if sections:
            info["sections"] = sections

        # Extract references section
        references = self._extract_references(text)
        if references:
            info["num_references"] = len(references)
            info["references_preview"] = references[:5]

        return info

    def _extract_sections(self, text: str) -> List[str]:
        """
        Extract section headings
        """
        section_patterns = [
            r'^(?:Abstract|Introduction|Methods?|Results?|Discussion|Conclusion|References)',
            r'^\d+\.?\s+[A-Z][A-Za-z\s]+',  # Numbered sections
            r'^[A-Z][A-Z\s]+$'  # All caps headings
        ]

        sections = []
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            for pattern in section_patterns:
                if re.match(pattern, line) and len(line) < 100:
                    sections.append(line)
                    break

        return sections[:20]  # Limit to first 20 sections

    def _extract_references(self, text: str) -> List[str]:
        """
        Extract references from text
        """
        references = []

        # Find references section
        ref_start = -1
        for pattern in [r'References', r'REFERENCES', r'Bibliography']:
            match = re.search(pattern, text)
            if match:
                ref_start = match.start()
                break

        if ref_start > 0:
            ref_text = text[ref_start:]
            # Simple extraction of numbered references
            ref_pattern = r'\[\d+\].*?(?=\[\d+\]|$)'
            references = re.findall(ref_pattern, ref_text, re.DOTALL)[:50]

        return references

    def get_description(self) -> str:
        """
        Get tool description
        """
        return "Extract text and metadata from PDF documents"

    def get_parameters(self) -> Dict[str, Any]:
        """
        Get tool parameters schema
        """
        return {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to PDF file"
                },
                "file_bytes": {
                    "type": "string",
                    "description": "PDF file as base64 bytes"
                },
                "extract_images": {
                    "type": "boolean",
                    "description": "Extract images from PDF"
                },
                "extract_tables": {
                    "type": "boolean",
                    "description": "Extract tables from PDF"
                },
                "max_pages": {
                    "type": "integer",
                    "description": "Maximum pages to process"
                }
            },
            "oneOf": [
                {"required": ["file_path"]},
                {"required": ["file_bytes"]}
            ]
        }