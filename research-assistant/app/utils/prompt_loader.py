from pathlib import Path
from typing import Dict, Optional
import os

from app.settings import settings

class PromptLoader:
    """
    Utility for loading and managing prompts from files
    """

    def __init__(self):
        self.prompts_dir = settings.PROMPTS_DIR
        self._cache: Dict[str, str] = {}

    def load(self, prompt_file: str, variables: Optional[Dict[str, str]] = None) -> str:
        """
        Load a prompt from file and optionally substitute variables
        """
        # Check cache first
        if prompt_file in self._cache and not variables:
            return self._cache[prompt_file]

        # Build file path
        file_path = self.prompts_dir / prompt_file
        if not file_path.exists():
            # Try with .txt extension
            file_path = self.prompts_dir / f"{prompt_file}.txt"

        if not file_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_file}")

        # Read prompt
        with open(file_path, 'r', encoding='utf-8') as f:
            prompt_text = f.read()

        # Substitute variables if provided
        if variables:
            for key, value in variables.items():
                placeholder = f"{{{key}}}"
                prompt_text = prompt_text.replace(placeholder, value)
        else:
            # Cache only if no variables
            self._cache[prompt_file] = prompt_text

        return prompt_text

    def reload(self):
        """
        Clear the cache to reload prompts
        """
        self._cache.clear()

    def list_prompts(self) -> list:
        """
        List all available prompt files
        """
        if not self.prompts_dir.exists():
            return []

        prompts = []
        for file_path in self.prompts_dir.glob("*.txt"):
            prompts.append(file_path.stem)

        return sorted(prompts)

    def get_prompt_metadata(self, prompt_file: str) -> Dict[str, str]:
        """
        Extract metadata from prompt file (if present in header comments)
        """
        file_path = self.prompts_dir / prompt_file
        if not file_path.exists():
            file_path = self.prompts_dir / f"{prompt_file}.txt"

        if not file_path.exists():
            return {}

        metadata = {}
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.startswith('#'):
                    break
                if ':' in line:
                    key, value = line[1:].split(':', 1)
                    metadata[key.strip()] = value.strip()

        return metadata


# Singleton instance
_prompt_loader = PromptLoader()


def load_prompt(prompt_file: str, variables: Optional[Dict[str, str]] = None) -> str:
    """
    Load a prompt from file

    Args:
        prompt_file: Name of the prompt file (with or without .txt extension)
        variables: Optional dictionary of variables to substitute in the prompt

    Returns:
        The loaded prompt text
    """
    return _prompt_loader.load(prompt_file, variables)


def reload_prompts():
    """
    Clear the prompt cache
    """
    _prompt_loader.reload()


def list_available_prompts() -> list:
    """
    List all available prompt files
    """
    return _prompt_loader.list_prompts()