"""
AI Short Story Writer

A production-ready tool for generating professional-quality short stories using AI agents.
"""

__version__ = "1.2.0"
__author__ = "AI Story Writer Team"

from .agents.enhanced_story_agent import generate_story_enhanced
from .models.enhanced_models import EnhancedGeneratedStory, StoryRequirements, StoryGenre, StoryLength

__all__ = [
    "generate_story_enhanced",
    "EnhancedGeneratedStory", 
    "StoryRequirements",
    "StoryGenre",
    "StoryLength"
]