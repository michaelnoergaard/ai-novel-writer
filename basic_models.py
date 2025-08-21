"""
Basic Pydantic models for the AI Short Story Writer - Version 1
Simple data structures for story generation
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class StoryGenre(str, Enum):
    """Supported story genres for Version 1"""
    LITERARY = "literary"
    MYSTERY = "mystery" 
    SCIENCE_FICTION = "science_fiction"
    FANTASY = "fantasy"
    ROMANCE = "romance"


class StoryLength(str, Enum):
    """Story length categories"""
    FLASH = "flash"  # 100-1000 words
    SHORT = "short"  # 1000-7500 words


class StoryRequirements(BaseModel):
    """Basic story generation requirements"""
    genre: StoryGenre
    length: StoryLength
    target_word_count: int = Field(ge=100, le=7500)
    theme: Optional[str] = None
    setting: Optional[str] = None
    
    model_config = {
        "str_strip_whitespace": True,
        "validate_assignment": True
    }


class GeneratedStory(BaseModel):
    """Container for generated story output"""
    title: str
    content: str
    word_count: int
    genre: StoryGenre
    requirements: StoryRequirements
    
    model_config = {
        "str_strip_whitespace": True
    }