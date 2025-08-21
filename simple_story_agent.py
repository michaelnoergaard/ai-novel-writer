"""
Simple Story Agent - Version 1 Implementation
Single agent that generates complete short stories using PydanticAI
"""

import asyncio
import logging
from typing import Dict, Any
from pydantic_ai import Agent, RunContext
from basic_models import StoryRequirements, GeneratedStory, StoryGenre, StoryLength
from config import AgentConfig, StoryGenerationError, AgentError, ValidationError

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


# Create the simple story agent
simple_story_agent = Agent(
    'openai:gpt-4o',
    deps_type=StoryDependencies,
    result_type=str,
    system_prompt="""You are a professional short story writer with expertise in crafting compelling narratives.
    
    Your task is to generate complete, publishable short stories based on the given requirements.
    
    Key principles:
    - Create engaging characters with clear motivations
    - Develop a focused plot with a clear beginning, middle, and end
    - Use vivid, economical prose that serves the story
    - Ensure every element contributes to the overall effect
    - Follow genre conventions while maintaining originality
    - Stay within the specified word count range
    
    Structure your stories with:
    1. An engaging opening that establishes character and situation
    2. Rising action that develops conflict and tension
    3. A climactic moment that resolves the main conflict
    4. A satisfying conclusion that provides closure
    
    Write in third person unless the genre specifically benefits from first person.
    Use present tense for immediacy unless past tense better serves the narrative."""
)


@simple_story_agent.tool
async def get_genre_guidelines(ctx: RunContext[StoryDependencies], genre: StoryGenre) -> str:
    """Get writing guidelines for the specified genre"""
    return ctx.deps.genre_guidelines.get(genre, "Follow general storytelling principles")


@simple_story_agent.tool
async def get_length_guidelines(ctx: RunContext[StoryDependencies], length: StoryLength) -> str:
    """Get guidelines for the specified story length"""
    return ctx.deps.length_guidelines.get(length, "Follow general short story structure")


@simple_story_agent.tool
async def validate_word_count(ctx: RunContext[StoryDependencies], content: str, target: int) -> Dict[str, Any]:
    """Validate that the story meets word count requirements"""
    word_count = len(content.split())
    tolerance = 0.1  # Allow 10% variance
    min_words = int(target * (1 - tolerance))
    max_words = int(target * (1 + tolerance))
    
    is_valid = min_words <= word_count <= max_words
    
    return {
        "is_valid": is_valid,
        "actual_count": word_count,
        "target_count": target,
        "min_acceptable": min_words,
        "max_acceptable": max_words
    }


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
            logger.debug("Calling story generation agent")
            result = await simple_story_agent.run(
                prompt,
                deps=self.dependencies
            )
            
            story_content = result.data
            if not story_content or len(story_content.strip()) < 50:
                raise AgentError("Agent returned insufficient content")
            
            # Generate a title
            logger.debug("Generating story title")
            title = await self._generate_title(story_content, requirements)
            
            # Count words and validate
            word_count = len(story_content.split())
            self._validate_word_count(word_count, requirements.target_word_count)
            
            logger.info(f"Story generation complete. Word count: {word_count}")
            
            return GeneratedStory(
                title=title,
                content=story_content,
                word_count=word_count,
                genre=requirements.genre,
                requirements=requirements
            )
            
        except Exception as e:
            logger.error(f"Story generation failed: {str(e)}")
            if isinstance(e, (StoryGenerationError, AgentError, ValidationError)):
                raise
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
            result = await simple_story_agent.run(
                title_prompt,
                deps=self.dependencies
            )
            return result.data.strip().strip('"').strip("'")
        except:
            # Fallback title if generation fails
            return f"A {requirements.genre.value.title()} Story"


# Convenience function for direct usage
async def generate_story(requirements: StoryRequirements) -> GeneratedStory:
    """Generate a story using the simple story generator"""
    generator = SimpleStoryGenerator()
    return await generator.generate_story(requirements)