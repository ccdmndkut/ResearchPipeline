"""
Text Cleaners
Handles text preprocessing, cleaning, and chunking operations.
"""
import re
import numpy as np
from typing import List, Dict, Any


class TextCleaner:
    """Cleans and preprocesses text for the research pipeline."""
    
    def __init__(self):
        """Initialize the text cleaner."""
        self.chunk_size = 1000
        self.chunk_overlap = 200
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text content.
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\;\:]', ' ', text)
        
        # Normalize case for better processing
        text = text.strip()
        
        return text
    
    def detect_language(self, text: str) -> str:
        """
        Detect the language of the text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Language code (simplified - always returns 'en' for now)
        """
        # Simplified language detection - would use proper library in production
        return 'en'
    
    def chunk_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Split text into chunks for processing.
        
        Args:
            text: Text to chunk
            
        Returns:
            List of text chunks with metadata
        """
        if not text:
            return []
        
        chunks = []
        words = text.split()
        
        # Simple word-based chunking
        for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
            chunk_words = words[i:i + self.chunk_size]
            chunk_text = ' '.join(chunk_words)
            
            chunk = {
                'text': chunk_text,
                'start_index': i,
                'end_index': min(i + self.chunk_size, len(words)),
                'word_count': len(chunk_words),
                'character_count': len(chunk_text)
            }
            
            chunks.append(chunk)
            
            # Stop if we've covered all words
            if i + self.chunk_size >= len(words):
                break
        
        return chunks