"""
Simple Story Agent - Version 1.1 Implementation
Production-ready PydanticAI agent for generating complete short stories
"""

import asyncio
import logging
from typing import Dict, Any
from pydantic_ai import Agent, RunContext
from ..models.basic_models import StoryRequirements, GeneratedStory, StoryGenre, StoryLength
from ..utils.config import AgentConfig, StoryGenerationError, AgentError, ValidationError

# Setup logging
logger = logging.getLogger(__name__)


class StoryDependencies:
    """Dependencies for the story agent"""
    def __init__(self):
        self.genre_guidelines = {
            StoryGenre.LITERARY: "Focus on character development, internal conflict, and meaningful themes. Use subtle, elegant prose with deep psychological insight.",
            StoryGenre.MYSTERY: "Include a central puzzle or crime to solve. Build suspense through clues and red herrings. Provide a satisfying resolution.",
            StoryGenre.SCIENCE_FICTION: "Incorporate speculative technology or scientific concepts. Explore how these elements impact characters and society.",
            StoryGenre.FANTASY: "Include magical or supernatural elements. Create an immersive world with its own rules and mythology.",
            StoryGenre.ROMANCE: "Focus on emotional connection between characters. Build tension through relationship conflicts and resolutions."
        }
        
        self.length_guidelines = {
            StoryLength.FLASH: "Tell a complete story in under 1000 words. Focus on a single moment or revelation. Every word must count.",
            StoryLength.SHORT: "Develop a full narrative arc in 1000-7500 words. Include character development, plot progression, and satisfying resolution."
        }


# Enhanced system prompt for V1.1
ENHANCED_SYSTEM_PROMPT = """You are a professional short story writer with expertise in crafting compelling narratives.

Your task is to generate complete, publishable short stories based on the given requirements.

Key principles:
- Create engaging characters with clear motivations and distinct voices
- Develop a focused plot with a clear beginning, middle, and end
- Use vivid, economical prose that serves the story
- Ensure every element contributes to the overall effect
- Follow genre conventions while maintaining originality
- Stay within the specified word count range with precision
- Integrate themes and settings naturally into the narrative

Structure your stories with:
1. An engaging opening that establishes character and situation
2. Rising action that develops conflict and tension
3. A climactic moment that resolves the main conflict
4. A satisfying conclusion that provides closure

Write in third person unless the genre specifically benefits from first person.
Use present tense for immediacy unless past tense better serves the narrative.
Ensure consistency in character voice, plot logic, and world-building throughout.

Always use the available tools to get genre and length guidelines before writing."""

# Create the enhanced story agent with retry configuration
simple_story_agent = Agent(
    'openai:gpt-4o',
    deps_type=StoryDependencies,
    system_prompt=ENHANCED_SYSTEM_PROMPT,
    retries=3
)


@simple_story_agent.tool
async def get_genre_guidelines(ctx: RunContext[StoryDependencies], genre: StoryGenre) -> str:
    """Get comprehensive writing guidelines for the specified genre"""
    logger.debug(f"Tool called: get_genre_guidelines for {genre.value}")
    guidelines = ctx.deps.genre_guidelines.get(genre, "Follow general storytelling principles")
    logger.debug(f"Returning guidelines for {genre.value}: {len(guidelines)} characters")
    return guidelines


@simple_story_agent.tool
async def get_length_guidelines(ctx: RunContext[StoryDependencies], length: StoryLength) -> str:
    """Get comprehensive guidelines for the specified story length"""
    logger.debug(f"Tool called: get_length_guidelines for {length.value}")
    guidelines = ctx.deps.length_guidelines.get(length, "Follow general short story structure")
    logger.debug(f"Returning length guidelines for {length.value}: {len(guidelines)} characters")
    return guidelines


@simple_story_agent.tool
async def validate_word_count(ctx: RunContext[StoryDependencies], content: str, target: int) -> Dict[str, Any]:
    """Validate that the story meets word count requirements with detailed feedback"""
    logger.debug(f"Tool called: validate_word_count with target {target}")
    
    if not content or not content.strip():
        logger.warning("validate_word_count called with empty content")
        return {
            "is_valid": False,
            "actual_count": 0,
            "target_count": target,
            "min_acceptable": int(target * 0.9),
            "max_acceptable": int(target * 1.1),
            "error": "Empty content provided"
        }
    
    word_count = len(content.split())
    tolerance = 0.1  # Allow 10% variance
    min_words = int(target * (1 - tolerance))
    max_words = int(target * (1 + tolerance))
    
    is_valid = min_words <= word_count <= max_words
    
    result = {
        "is_valid": is_valid,
        "actual_count": word_count,
        "target_count": target,
        "min_acceptable": min_words,
        "max_acceptable": max_words
    }
    
    if not is_valid:
        if word_count < min_words:
            result["feedback"] = f"Story is {min_words - word_count} words too short"
        else:
            result["feedback"] = f"Story is {word_count - max_words} words too long"
    
    logger.debug(f"Word count validation: {word_count}/{target} (valid: {is_valid})")
    return result


class SimpleStoryGenerator:
    """Main class for generating stories using the simple agent"""
    
    def __init__(self):
        self.dependencies = StoryDependencies()
    
    async def generate_story(self, requirements: StoryRequirements) -> GeneratedStory:
        """Generate a complete story based on requirements"""
        
        # Validate requirements
        self._validate_requirements(requirements)
        
        logger.info(f"Generating {requirements.genre} story of {requirements.target_word_count} words")
        
        # Prepare the prompt for story generation
        prompt = self._create_generation_prompt(requirements)
        
        try:
            # Generate the story using the agent
            logger.info(f"Starting story generation with PydanticAI agent")
            logger.debug(f"Prompt length: {len(prompt)} characters")
            
            result = await simple_story_agent.run(
                prompt,
                deps=self.dependencies
            )
            
            story_content = result.output
            if not story_content or len(story_content.strip()) < 50:
                raise AgentError("Agent returned insufficient content (less than 50 characters)")
            
            logger.debug(f"Generated story content: {len(story_content)} characters")
            
            # Generate a title
            logger.debug("Generating story title using agent")
            title = await self._generate_title(story_content, requirements)
            logger.debug(f"Generated title: '{title}'")
            
            # Count words and validate
            word_count = len(story_content.split())
            self._validate_word_count(word_count, requirements.target_word_count)
            
            logger.info(f"Story generation successful - Title: '{title}', Words: {word_count}, Genre: {requirements.genre.value}")
            
            return GeneratedStory(
                title=title,
                content=story_content,
                word_count=word_count,
                genre=requirements.genre,
                requirements=requirements
            )
            
        except StoryGenerationError:
            # Re-raise our custom exceptions as-is
            raise
        except AgentError:
            # Re-raise agent errors as-is
            raise
        except ValidationError:
            # Re-raise validation errors as-is
            raise
        except Exception as e:
            logger.error(f"Unexpected error during story generation: {type(e).__name__}: {str(e)}")
            raise AgentError(f"Unexpected error during story generation: {str(e)}")
    
    def _validate_requirements(self, requirements: StoryRequirements) -> None:
        """Validate story requirements"""
        if requirements.target_word_count < 100:
            raise ValidationError("Target word count must be at least 100")
        if requirements.target_word_count > 7500:
            raise ValidationError("Target word count must not exceed 7500")
        
        # Validate length category alignment
        if requirements.length == StoryLength.FLASH and requirements.target_word_count > 1000:
            logger.warning("Flash fiction typically under 1000 words")
        elif requirements.length == StoryLength.SHORT and requirements.target_word_count < 1000:
            logger.warning("Short stories typically 1000+ words")
    
    def _validate_word_count(self, actual: int, target: int) -> None:
        """Validate generated story word count"""
        tolerance = 0.2  # Allow 20% variance
        min_words = int(target * (1 - tolerance))
        max_words = int(target * (1 + tolerance))
        
        if actual < min_words:
            logger.warning(f"Story too short: {actual} words (target: {target})")
        elif actual > max_words:
            logger.warning(f"Story too long: {actual} words (target: {target})")
        else:
            logger.debug(f"Word count within acceptable range: {actual}/{target}")
    
    def _create_generation_prompt(self, requirements: StoryRequirements) -> str:
        """Create a detailed prompt for story generation"""
        
        prompt_parts = [
            f"Write a {requirements.genre.value} short story of approximately {requirements.target_word_count} words.",
            f"This should be a {requirements.length.value} fiction piece."
        ]
        
        if requirements.theme:
            prompt_parts.append(f"Theme: {requirements.theme}")
        
        if requirements.setting:
            prompt_parts.append(f"Setting: {requirements.setting}")
        
        prompt_parts.extend([
            "",
            "Requirements:",
            f"- Genre: {requirements.genre.value}",
            f"- Target word count: {requirements.target_word_count}",
            "- Complete story with beginning, middle, and end",
            "- Engaging characters and compelling plot",
            "- Professional quality prose",
            "",
            "Generate the story now:"
        ])
        
        return "\n".join(prompt_parts)
    
    async def _generate_title(self, story_content: str, requirements: StoryRequirements) -> str:
        """Generate an appropriate title for the story"""
        title_prompt = f"""Based on this {requirements.genre.value} story, generate a compelling, appropriate title:

{story_content[:500]}...

Generate only the title, nothing else."""

        try:
            logger.debug("Generating title with agent")
            result = await simple_story_agent.run(
                title_prompt,
                deps=self.dependencies
            )
            title = result.output.strip().strip('"').strip("'")
            if not title:
                raise AgentError("Agent returned empty title")
            return title
        except Exception as e:
            logger.warning(f"Title generation failed: {e}. Using fallback title.")
            # Fallback title if generation fails
            return f"A {requirements.genre.value.title()} Story"


# Convenience function for direct usage
async def generate_story(requirements: StoryRequirements) -> GeneratedStory:
    """Generate a story using the simple story generator"""
    generator = SimpleStoryGenerator()
    return await generator.generate_story(requirements)