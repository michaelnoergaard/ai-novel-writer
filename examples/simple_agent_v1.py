"""
Simplified Story Agent - Version 1 (No PydanticAI dependency)
Direct OpenAI API integration for story generation
"""

import asyncio
import logging
from typing import Dict, Any
from openai import AsyncOpenAI
from basic_models import StoryRequirements, GeneratedStory, StoryGenre, StoryLength
from config import StoryGenerationError, AgentError, ValidationError

logger = logging.getLogger(__name__)


class SimpleStoryAgent:
    """Simplified story agent using direct OpenAI API calls"""
    
    def __init__(self, client: AsyncOpenAI = None):
        self.client = client or AsyncOpenAI()
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

    async def generate_story(self, requirements: StoryRequirements) -> GeneratedStory:
        """Generate a complete story based on requirements"""
        
        # Validate requirements
        self._validate_requirements(requirements)
        
        logger.info(f"Generating {requirements.genre} story of {requirements.target_word_count} words")
        
        try:
            # Generate the story
            story_content = await self._generate_story_content(requirements)
            
            if not story_content or len(story_content.strip()) < 50:
                raise AgentError("Generated content is too short or empty")
            
            # Generate a title
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

    async def _generate_story_content(self, requirements: StoryRequirements) -> str:
        """Generate the main story content"""
        system_prompt = self._create_system_prompt()
        user_prompt = self._create_user_prompt(requirements)
        
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=4000
        )
        
        return response.choices[0].message.content.strip()

    async def _generate_title(self, story_content: str, requirements: StoryRequirements) -> str:
        """Generate an appropriate title for the story"""
        title_prompt = f"""Based on this {requirements.genre.value} story, generate a compelling, appropriate title.

Story excerpt:
{story_content[:500]}...

Generate only the title, nothing else."""

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a professional editor who creates compelling titles for short stories."},
                    {"role": "user", "content": title_prompt}
                ],
                temperature=0.8,
                max_tokens=50
            )
            
            title = response.choices[0].message.content.strip().strip('"').strip("'")
            return title if title else f"A {requirements.genre.value.title()} Story"
            
        except Exception as e:
            logger.warning(f"Title generation failed: {e}")
            return f"A {requirements.genre.value.title()} Story"

    def _create_system_prompt(self) -> str:
        """Create the system prompt for story generation"""
        return """You are a professional short story writer with expertise in crafting compelling narratives.

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
Use present tense for immediacy unless past tense better serves the narrative.

Generate ONLY the story content, no titles or metadata."""

    def _create_user_prompt(self, requirements: StoryRequirements) -> str:
        """Create the user prompt for story generation"""
        
        prompt_parts = [
            f"Write a {requirements.genre.value} short story of approximately {requirements.target_word_count} words.",
            f"This should be a {requirements.length.value} fiction piece.",
            "",
            f"Genre guidelines: {self.genre_guidelines.get(requirements.genre, 'Follow general storytelling principles')}",
            f"Length guidelines: {self.length_guidelines.get(requirements.length, 'Follow general short story structure')}",
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


# Convenience function for direct usage
async def generate_story(requirements: StoryRequirements) -> GeneratedStory:
    """Generate a story using the simple story agent"""
    agent = SimpleStoryAgent()
    return await agent.generate_story(requirements)