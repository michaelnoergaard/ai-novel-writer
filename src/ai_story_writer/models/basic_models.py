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
    
    @classmethod
    def _missing_(cls, value):
        """Handle flexible genre input with intelligent mapping"""
        if not isinstance(value, str):
            return None
            
        # Normalize input
        normalized = value.lower().strip().replace('-', '_').replace(' ', '_')
        
        # Common aliases and mappings
        genre_mappings = {
            'sci_fi': cls.SCIENCE_FICTION,
            'scifi': cls.SCIENCE_FICTION,
            'sf': cls.SCIENCE_FICTION,
            'science': cls.SCIENCE_FICTION,
            'detective': cls.MYSTERY,
            'crime': cls.MYSTERY,
            'thriller': cls.MYSTERY,
            'whodunit': cls.MYSTERY,
            'love': cls.ROMANCE,
            'romantic': cls.ROMANCE,
            'drama': cls.LITERARY,
            'fiction': cls.LITERARY,
            'contemporary': cls.LITERARY,
            'magical': cls.FANTASY,
            'epic': cls.FANTASY,
            'urban_fantasy': cls.FANTASY,
        }
        
        # Try direct mapping first
        if normalized in genre_mappings:
            return genre_mappings[normalized]
            
        # Try partial matches
        for alias, genre in genre_mappings.items():
            if alias in normalized or normalized in alias:
                return genre
                
        # Try to match with existing enum values
        for genre in cls:
            if normalized == genre.value or normalized in genre.value:
                return genre
                
        # If no mapping found, default to literary for any unrecognized genre
        # This allows the AI to handle any genre while providing a fallback
        return cls.LITERARY


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
    original_genre: Optional[str] = Field(default=None, description="Original user-specified genre")
    
    model_config = {
        "str_strip_whitespace": True,
        "validate_assignment": True
    }
    
    def get_display_genre(self) -> str:
        """Get the genre name for display and AI prompts"""
        return self.original_genre or self.genre.value


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