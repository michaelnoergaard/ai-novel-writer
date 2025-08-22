"""
Enhanced Pydantic models for AI Short Story Writer - Version 1.2
Extended data structures for enhanced story generation with structured output
"""

from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

# Import existing models to maintain compatibility
from basic_models import StoryGenre, StoryLength, StoryRequirements, GeneratedStory


class GenerationMethod(str, Enum):
    """Generation methods available in V1.2"""
    DIRECT = "direct"           # V1.1 compatible single-pass generation
    OUTLINE_BASED = "outline"   # V1.2 outline-first generation
    AUTO = "auto"              # Let the system choose best method


class ValidationLevel(str, Enum):
    """Validation strictness levels"""
    BASIC = "basic"           # Essential validation only
    STANDARD = "standard"     # Balanced validation (default)
    STRICT = "strict"         # Comprehensive validation


class StoryOutline(BaseModel):
    """Structured story outline for enhanced generation"""
    opening: str = Field(description="Story opening/hook description")
    rising_action: str = Field(description="Rising action and conflict development")
    climax: str = Field(description="Climactic moment description")
    resolution: str = Field(description="Resolution and conclusion")
    
    # Character and theme elements
    main_characters: List[str] = Field(default_factory=list, description="Main character descriptions")
    themes: List[str] = Field(default_factory=list, description="Key themes to explore")
    
    # Metadata
    estimated_word_count: Optional[int] = Field(None, description="Estimated words for this outline")
    
    model_config = {
        "str_strip_whitespace": True,
        "validate_assignment": True
    }


class ValidationResult(BaseModel):
    """Detailed validation result for story requirements"""
    is_valid: bool = Field(description="Overall validation status")
    
    # Specific validation checks
    word_count_valid: bool = Field(description="Word count within acceptable range")
    genre_length_compatible: bool = Field(description="Genre and length are compatible")
    theme_feasible: bool = Field(description="Theme is feasible for genre/length")
    
    # Detailed feedback
    warnings: List[str] = Field(default_factory=list, description="Non-critical warnings")
    suggestions: List[str] = Field(default_factory=list, description="Improvement suggestions")
    errors: List[str] = Field(default_factory=list, description="Critical errors to fix")
    
    # Technical details
    word_count_analysis: Dict[str, Any] = Field(default_factory=dict, description="Word count analysis details")
    
    model_config = {
        "str_strip_whitespace": True
    }


class GenerationMetadata(BaseModel):
    """Metadata about the story generation process"""
    generation_method: GenerationMethod = Field(description="Method used for generation")
    tools_used: List[str] = Field(default_factory=list, description="Tools called during generation")
    generation_time: float = Field(description="Total generation time in seconds")
    
    # Process details
    outline_generated: bool = Field(default=False, description="Whether an outline was generated")
    retry_count: int = Field(default=0, description="Number of retries needed")
    validation_level: ValidationLevel = Field(default=ValidationLevel.STANDARD)
    
    # Timestamps
    started_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    
    # Performance metrics
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    
    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }


class EnhancedGeneratedStory(BaseModel):
    """Enhanced container for V1.2 story generation output with structured metadata"""
    
    # Core story content (maintains V1.1 compatibility)
    title: str
    content: str
    word_count: int
    genre: StoryGenre
    requirements: StoryRequirements
    
    # V1.2 enhancements
    generation_method: GenerationMethod = Field(description="Method used for generation")
    outline_used: Optional[StoryOutline] = Field(None, description="Outline used (if outline-based)")
    validation_results: ValidationResult = Field(description="Comprehensive validation results")
    metadata: GenerationMetadata = Field(description="Generation process metadata")
    
    # Quality indicators
    structure_quality: Optional[float] = Field(None, ge=0.0, le=10.0, description="Structure quality score (0-10)")
    character_development: Optional[float] = Field(None, ge=0.0, le=10.0, description="Character development score (0-10)")
    theme_integration: Optional[float] = Field(None, ge=0.0, le=10.0, description="Theme integration score (0-10)")
    
    model_config = {
        "str_strip_whitespace": True,
        "validate_assignment": True
    }
    
    def to_basic_story(self) -> GeneratedStory:
        """Convert to basic GeneratedStory for V1.1 compatibility"""
        return GeneratedStory(
            title=self.title,
            content=self.content,
            word_count=self.word_count,
            genre=self.genre,
            requirements=self.requirements
        )
    
    @classmethod
    def from_basic_story(
        cls, 
        basic_story: GeneratedStory, 
        generation_method: GenerationMethod = GenerationMethod.DIRECT,
        outline: Optional[StoryOutline] = None,
        validation_results: Optional[ValidationResult] = None,
        metadata: Optional[GenerationMetadata] = None
    ) -> "EnhancedGeneratedStory":
        """Create enhanced story from basic story for easy migration"""
        
        # Default validation results
        if validation_results is None:
            validation_results = ValidationResult(
                is_valid=True,
                word_count_valid=True,
                genre_length_compatible=True,
                theme_feasible=True
            )
        
        # Default metadata
        if metadata is None:
            metadata = GenerationMetadata(
                generation_method=generation_method,
                generation_time=0.0,
                tools_used=[]
            )
        
        return cls(
            title=basic_story.title,
            content=basic_story.content,
            word_count=basic_story.word_count,
            genre=basic_story.genre,
            requirements=basic_story.requirements,
            generation_method=generation_method,
            outline_used=outline,
            validation_results=validation_results,
            metadata=metadata
        )


# Enhanced configuration models
class EnhancedAgentConfig(BaseModel):
    """Enhanced configuration for V1.2 agent features"""
    
    # Generation settings
    default_generation_method: GenerationMethod = GenerationMethod.AUTO
    outline_detail_level: str = Field(default="medium", pattern="^(basic|medium|detailed)$")
    validation_level: ValidationLevel = ValidationLevel.STANDARD
    
    # Tool settings
    enable_outline_generation: bool = True
    enable_character_guidelines: bool = True
    enable_theme_integration: bool = True
    show_tool_usage: bool = False
    
    # Quality settings
    enable_quality_scoring: bool = False  # Reserved for V1.5
    min_quality_threshold: float = Field(default=0.0, ge=0.0, le=10.0)
    
    # Performance settings
    max_outline_attempts: int = Field(default=2, ge=1, le=5)
    max_generation_attempts: int = Field(default=3, ge=1, le=5)
    
    model_config = {
        "str_strip_whitespace": True,
        "validate_assignment": True
    }


# Utility functions for model conversion
def convert_to_enhanced(basic_story: GeneratedStory, **kwargs) -> EnhancedGeneratedStory:
    """Utility function to convert basic story to enhanced story"""
    return EnhancedGeneratedStory.from_basic_story(basic_story, **kwargs)


def convert_to_basic(enhanced_story: EnhancedGeneratedStory) -> GeneratedStory:
    """Utility function to convert enhanced story to basic story"""
    return enhanced_story.to_basic_story()