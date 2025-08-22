"""
Enhanced Story Agent - Version 1.2 Implementation
Production-ready PydanticAI agent with enhanced tools and structured output
"""

import asyncio
import logging
import time
from typing import Dict, Any, Optional
from datetime import datetime
from pydantic_ai import Agent, RunContext

# Import models and dependencies
from basic_models import StoryRequirements, StoryGenre, StoryLength
from enhanced_models import (
    EnhancedGeneratedStory, StoryOutline, ValidationResult, GenerationMetadata,
    GenerationMethod, ValidationLevel, EnhancedAgentConfig
)
from enhanced_dependencies import EnhancedStoryDependencies
from config import StoryGenerationError, AgentError, ValidationError

# Setup logging
logger = logging.getLogger(__name__)

# Enhanced system prompt for V1.2
ENHANCED_V12_SYSTEM_PROMPT = """You are a professional short story writer with expertise in crafting compelling narratives.

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

IMPORTANT: Always use the available tools to get guidelines before writing. For outline-based generation, create a detailed outline first, then write the story based on that outline."""

# Create the enhanced story agent
enhanced_story_agent = Agent(
    'openai:gpt-4o',
    deps_type=EnhancedStoryDependencies,
    system_prompt=ENHANCED_V12_SYSTEM_PROMPT,
    retries=3
)


# Enhanced Tools for V1.2

@enhanced_story_agent.tool
async def get_genre_guidelines(ctx: RunContext[EnhancedStoryDependencies], genre: StoryGenre) -> str:
    """Get comprehensive writing guidelines for the specified genre"""
    logger.debug(f"Tool called: get_genre_guidelines for {genre.value}")
    ctx.deps.log_tool_usage("get_genre_guidelines", genre.value)
    guidelines = ctx.deps.genre_guidelines.get(genre, "Follow general storytelling principles")
    logger.debug(f"Returning enhanced guidelines for {genre.value}: {len(guidelines)} characters")
    return guidelines


@enhanced_story_agent.tool
async def get_length_guidelines(ctx: RunContext[EnhancedStoryDependencies], length: StoryLength) -> str:
    """Get comprehensive guidelines for the specified story length"""
    logger.debug(f"Tool called: get_length_guidelines for {length.value}")
    ctx.deps.log_tool_usage("get_length_guidelines", length.value)
    guidelines = ctx.deps.length_guidelines.get(length, "Follow general short story structure")
    logger.debug(f"Returning enhanced length guidelines for {length.value}: {len(guidelines)} characters")
    return guidelines


@enhanced_story_agent.tool
async def validate_story_requirements(
    ctx: RunContext[EnhancedStoryDependencies], 
    requirements: StoryRequirements,
    validation_level: ValidationLevel = ValidationLevel.STANDARD
) -> ValidationResult:
    """Comprehensive validation of story requirements with detailed feedback"""
    logger.debug(f"Tool called: validate_story_requirements with {validation_level.value} level")
    ctx.deps.log_tool_usage("validate_story_requirements", f"{validation_level.value}")
    ctx.deps.metrics["validation_runs"] += 1
    
    # Get validation rules for this level
    rules = ctx.deps.get_validation_rules_for(validation_level)
    
    # Initialize validation result
    result = ValidationResult(is_valid=True)
    
    # Word count validation
    word_count_valid = True
    if requirements.target_word_count < 100:
        result.errors.append("Target word count must be at least 100 words")
        word_count_valid = False
    elif requirements.target_word_count > 7500:
        result.errors.append("Target word count must not exceed 7500 words")
        word_count_valid = False
    
    result.word_count_valid = word_count_valid
    
    # Genre-length compatibility check
    genre_length_compatible = True
    if requirements.length == StoryLength.FLASH and requirements.target_word_count > 1000:
        result.warnings.append("Flash fiction typically under 1000 words for best results")
    elif requirements.length == StoryLength.SHORT and requirements.target_word_count < 1000:
        result.warnings.append("Short stories typically 1000+ words for full development")
    
    result.genre_length_compatible = genre_length_compatible
    
    # Theme feasibility check
    theme_feasible = True
    if requirements.theme and rules["require_theme_check"]:
        # Basic theme validation - could be enhanced in future versions
        if len(requirements.theme.strip()) < 3:
            result.warnings.append("Theme is very short - consider more specific themes")
        elif len(requirements.theme.strip()) > 100:
            result.warnings.append("Theme is very long - consider more focused themes")
    
    result.theme_feasible = theme_feasible
    
    # Overall validation
    result.is_valid = word_count_valid and genre_length_compatible and theme_feasible and len(result.errors) == 0
    
    # Add suggestions based on requirements
    if requirements.genre == StoryGenre.LITERARY and requirements.target_word_count < 1500:
        result.suggestions.append("Literary stories often benefit from longer word counts for character development")
    
    if requirements.genre == StoryGenre.MYSTERY and not requirements.theme:
        result.suggestions.append("Consider adding a theme like 'justice', 'truth', or 'deception' for mystery stories")
    
    # Store analysis details
    result.word_count_analysis = {
        "target": requirements.target_word_count,
        "min_recommended": 100 if requirements.length == StoryLength.FLASH else 1000,
        "max_recommended": 1000 if requirements.length == StoryLength.FLASH else 7500,
        "tolerance": rules["word_count_tolerance"]
    }
    
    logger.debug(f"Validation complete: valid={result.is_valid}, warnings={len(result.warnings)}, suggestions={len(result.suggestions)}")
    return result


@enhanced_story_agent.tool
async def generate_story_outline(
    ctx: RunContext[EnhancedStoryDependencies],
    requirements: StoryRequirements
) -> StoryOutline:
    """Generate a structured story outline based on requirements"""
    logger.debug(f"Tool called: generate_story_outline for {requirements.genre.value}/{requirements.length.value}")
    ctx.deps.log_tool_usage("generate_story_outline", f"{requirements.genre.value}-{requirements.length.value}")
    
    # Get outline pattern for this genre/length combination
    pattern = ctx.deps.get_outline_pattern_for(requirements.genre, requirements.length)
    
    # Create outline based on pattern and requirements
    outline = StoryOutline(
        opening=f"Opening focused on {pattern['character_emphasis']} - establish protagonist and initial situation",
        rising_action=f"Development following {pattern['structure']} - build conflict and tension",
        climax=f"Climactic moment that resolves main conflict - {pattern['focus']}",
        resolution=f"Satisfying conclusion with {pattern['theme_approach']} approach to theme",
        estimated_word_count=requirements.target_word_count
    )
    
    # Add character suggestions based on genre/length
    char_guidelines = ctx.deps.get_character_guidelines_for(requirements.genre, requirements.length)
    if "protagonist" in char_guidelines.lower():
        outline.main_characters.append("Protagonist with clear motivation and internal conflict")
    
    if requirements.genre == StoryGenre.MYSTERY:
        outline.main_characters.append("Detective/investigator character")
        outline.main_characters.append("Suspect(s) with believable motives")
    elif requirements.genre == StoryGenre.ROMANCE:
        outline.main_characters.append("Romantic lead with individual character arc")
        outline.main_characters.append("Love interest with complementary qualities")
    
    # Add theme suggestions
    if requirements.theme:
        outline.themes.append(requirements.theme)
    
    # Add genre-appropriate themes
    if requirements.genre == StoryGenre.LITERARY:
        outline.themes.extend(["human nature", "personal growth", "relationships"])
    elif requirements.genre == StoryGenre.MYSTERY:
        outline.themes.extend(["justice", "truth", "deception"])
    elif requirements.genre == StoryGenre.SCIENCE_FICTION:
        outline.themes.extend(["progress vs tradition", "humanity vs technology"])
    elif requirements.genre == StoryGenre.FANTASY:
        outline.themes.extend(["good vs evil", "power and responsibility"])
    elif requirements.genre == StoryGenre.ROMANCE:
        outline.themes.extend(["love conquers all", "personal growth", "trust"])
    
    logger.debug(f"Generated outline with {len(outline.main_characters)} characters and {len(outline.themes)} themes")
    return outline


@enhanced_story_agent.tool
async def get_character_guidelines(
    ctx: RunContext[EnhancedStoryDependencies],
    genre: StoryGenre,
    length: StoryLength
) -> str:
    """Get character development guidelines for specific genre and length combination"""
    logger.debug(f"Tool called: get_character_guidelines for {genre.value}/{length.value}")
    ctx.deps.log_tool_usage("get_character_guidelines", f"{genre.value}-{length.value}")
    
    guidelines = ctx.deps.get_character_guidelines_for(genre, length)
    logger.debug(f"Returning character guidelines: {len(guidelines)} characters")
    return guidelines


@enhanced_story_agent.tool
async def get_theme_integration_guidance(
    ctx: RunContext[EnhancedStoryDependencies],
    genre: StoryGenre,
    theme: Optional[str] = None
) -> str:
    """Get guidance on integrating themes into the specified genre"""
    logger.debug(f"Tool called: get_theme_integration_guidance for {genre.value}")
    ctx.deps.log_tool_usage("get_theme_integration_guidance", f"{genre.value}")
    
    base_guidance = ctx.deps.get_theme_integration_for(genre)
    
    if theme:
        enhanced_guidance = f"{base_guidance}\n\nFor the theme '{theme}': Consider how this theme can be explored through character actions, conflicts, and the resolution specific to {genre.value} stories."
        return enhanced_guidance
    
    return base_guidance


@enhanced_story_agent.tool
async def validate_word_count_precise(
    ctx: RunContext[EnhancedStoryDependencies], 
    content: str, 
    target: int,
    tolerance: float = 0.15
) -> Dict[str, Any]:
    """Precise word count validation with configurable tolerance"""
    logger.debug(f"Tool called: validate_word_count_precise with target {target}, tolerance {tolerance}")
    ctx.deps.log_tool_usage("validate_word_count_precise", f"target-{target}")
    
    if not content or not content.strip():
        logger.warning("validate_word_count_precise called with empty content")
        return {
            "is_valid": False,
            "actual_count": 0,
            "target_count": target,
            "min_acceptable": int(target * (1 - tolerance)),
            "max_acceptable": int(target * (1 + tolerance)),
            "error": "Empty content provided",
            "variance_percentage": 100.0
        }
    
    actual_count = len(content.split())
    min_words = int(target * (1 - tolerance))
    max_words = int(target * (1 + tolerance))
    
    is_valid = min_words <= actual_count <= max_words
    variance_percentage = abs(actual_count - target) / target * 100
    
    result = {
        "is_valid": is_valid,
        "actual_count": actual_count,
        "target_count": target,
        "min_acceptable": min_words,
        "max_acceptable": max_words,
        "variance_percentage": round(variance_percentage, 1),
        "tolerance_used": tolerance
    }
    
    if not is_valid:
        if actual_count < min_words:
            result["feedback"] = f"Story is {min_words - actual_count} words too short ({variance_percentage:.1}% under target)"
        else:
            result["feedback"] = f"Story is {actual_count - max_words} words too long ({variance_percentage:.1}% over target)"
    else:
        result["feedback"] = f"Word count within acceptable range ({variance_percentage:.1}% variance)"
    
    logger.debug(f"Word count validation: {actual_count}/{target} (valid: {is_valid}, variance: {variance_percentage:.1}%)")
    return result


# Enhanced Story Generator Class

class EnhancedStoryGenerator:
    """Enhanced story generator with dual generation modes for V1.2"""
    
    def __init__(self, config: Optional[EnhancedAgentConfig] = None):
        self.dependencies = EnhancedStoryDependencies()
        self.config = config or EnhancedAgentConfig()
    
    async def generate_story(
        self, 
        requirements: StoryRequirements,
        generation_method: Optional[GenerationMethod] = None,
        validation_level: Optional[ValidationLevel] = None
    ) -> EnhancedGeneratedStory:
        """Generate a story using enhanced V1.2 capabilities"""
        
        start_time = time.time()
        self.dependencies.reset_metrics()
        
        # Determine generation method
        if generation_method is None:
            generation_method = self.config.default_generation_method
        
        if generation_method == GenerationMethod.AUTO:
            # Auto-select based on requirements
            if requirements.target_word_count >= 2000 or requirements.theme or requirements.setting:
                generation_method = GenerationMethod.OUTLINE_BASED
            else:
                generation_method = GenerationMethod.DIRECT
        
        # Determine validation level
        if validation_level is None:
            validation_level = self.config.validation_level
        
        logger.info(f"Starting enhanced story generation: {generation_method.value} method, {validation_level.value} validation")
        
        try:
            if generation_method == GenerationMethod.OUTLINE_BASED:
                return await self._generate_with_outline(requirements, validation_level, start_time)
            else:
                return await self._generate_direct(requirements, validation_level, start_time)
                
        except Exception as e:
            logger.error(f"Enhanced story generation failed: {str(e)}")
            if isinstance(e, (StoryGenerationError, AgentError, ValidationError)):
                raise
            raise AgentError(f"Unexpected error during enhanced story generation: {str(e)}")
    
    async def _generate_direct(
        self, 
        requirements: StoryRequirements, 
        validation_level: ValidationLevel,
        start_time: float
    ) -> EnhancedGeneratedStory:
        """Direct generation method (V1.1 compatible)"""
        
        logger.debug("Using direct generation method (V1.1 compatible)")
        
        # Validate requirements
        validation_result = await self._validate_requirements(requirements, validation_level)
        if not validation_result.is_valid:
            raise ValidationError(f"Requirements validation failed: {', '.join(validation_result.errors)}")
        
        # Generate story using existing method
        prompt = self._create_generation_prompt(requirements)
        
        logger.debug("Calling enhanced story generation agent (direct method)")
        result = await enhanced_story_agent.run(prompt, deps=self.dependencies)
        
        story_content = result.output
        if not story_content or len(story_content.strip()) < 50:
            raise AgentError("Agent returned insufficient content (less than 50 characters)")
        
        # Generate title
        title = await self._generate_title(story_content, requirements)
        
        # Final validation
        word_count = len(story_content.split())
        final_validation = await self._final_validation(story_content, requirements, validation_level)
        
        # Create metadata
        generation_time = time.time() - start_time
        metadata = GenerationMetadata(
            generation_method=GenerationMethod.DIRECT,
            tools_used=self.dependencies.tool_usage_log.copy(),
            generation_time=generation_time,
            validation_level=validation_level,
            completed_at=datetime.now()
        )
        
        logger.info(f"Direct generation complete - Title: '{title}', Words: {word_count}")
        
        return EnhancedGeneratedStory(
            title=title,
            content=story_content,
            word_count=word_count,
            genre=requirements.genre,
            requirements=requirements,
            generation_method=GenerationMethod.DIRECT,
            outline_used=None,
            validation_results=final_validation,
            metadata=metadata
        )
    
    async def _generate_with_outline(
        self, 
        requirements: StoryRequirements, 
        validation_level: ValidationLevel,
        start_time: float
    ) -> EnhancedGeneratedStory:
        """Outline-based generation method (V1.2 enhancement)"""
        
        logger.debug("Using outline-based generation method (V1.2 enhancement)")
        
        # Validate requirements
        validation_result = await self._validate_requirements(requirements, validation_level)
        if not validation_result.is_valid:
            raise ValidationError(f"Requirements validation failed: {', '.join(validation_result.errors)}")
        
        # Generate outline first
        logger.debug("Generating story outline")
        outline = await self._generate_outline(requirements)
        
        # Generate story based on outline
        story_content = await self._generate_from_outline(outline, requirements)
        
        if not story_content or len(story_content.strip()) < 50:
            raise AgentError("Agent returned insufficient content (less than 50 characters)")
        
        # Generate title
        title = await self._generate_title(story_content, requirements)
        
        # Final validation
        word_count = len(story_content.split())
        final_validation = await self._final_validation(story_content, requirements, validation_level)
        
        # Create metadata
        generation_time = time.time() - start_time
        metadata = GenerationMetadata(
            generation_method=GenerationMethod.OUTLINE_BASED,
            tools_used=self.dependencies.tool_usage_log.copy(),
            generation_time=generation_time,
            outline_generated=True,
            validation_level=validation_level,
            completed_at=datetime.now()
        )
        
        logger.info(f"Outline-based generation complete - Title: '{title}', Words: {word_count}")
        
        return EnhancedGeneratedStory(
            title=title,
            content=story_content,
            word_count=word_count,
            genre=requirements.genre,
            requirements=requirements,
            generation_method=GenerationMethod.OUTLINE_BASED,
            outline_used=outline,
            validation_results=final_validation,
            metadata=metadata
        )
    
    async def _validate_requirements(
        self, 
        requirements: StoryRequirements, 
        validation_level: ValidationLevel
    ) -> ValidationResult:
        """Validate story requirements using enhanced validation"""
        # Create a simple validation result for now - in future versions this could use the tool
        # For V1.2, we'll implement basic validation logic directly
        
        # Initialize all required fields
        word_count_valid = True
        genre_length_compatible = True
        theme_feasible = True
        errors = []
        warnings = []
        
        # Basic validation checks
        if requirements.target_word_count < 100:
            errors.append("Target word count must be at least 100")
            word_count_valid = False
        elif requirements.target_word_count > 7500:
            errors.append("Target word count must not exceed 7500")
            word_count_valid = False
        
        # Add warnings for common issues
        if requirements.length == StoryLength.FLASH and requirements.target_word_count > 1000:
            warnings.append("Flash fiction typically under 1000 words for best results")
        elif requirements.length == StoryLength.SHORT and requirements.target_word_count < 1000:
            warnings.append("Short stories typically 1000+ words for full development")
        
        # Overall validation
        is_valid = word_count_valid and genre_length_compatible and theme_feasible and len(errors) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            word_count_valid=word_count_valid,
            genre_length_compatible=genre_length_compatible,
            theme_feasible=theme_feasible,
            warnings=warnings,
            errors=errors
        )
    
    async def _generate_outline(self, requirements: StoryRequirements) -> StoryOutline:
        """Generate story outline using the agent"""
        outline_prompt = f"""Generate a detailed story outline for a {requirements.genre.value} {requirements.length.value} story of {requirements.target_word_count} words.

Requirements:
- Genre: {requirements.genre.value}
- Length: {requirements.length.value}
- Target word count: {requirements.target_word_count}
"""
        
        if requirements.theme:
            outline_prompt += f"- Theme: {requirements.theme}\n"
        
        if requirements.setting:
            outline_prompt += f"- Setting: {requirements.setting}\n"
        
        outline_prompt += "\nUse the generate_story_outline tool to create a structured outline."
        
        # This will trigger the generate_story_outline tool
        result = await enhanced_story_agent.run(outline_prompt, deps=self.dependencies)
        
        # For now, return a basic outline - in practice, the tool would return the StoryOutline
        # This is a simplified implementation for demonstration
        return StoryOutline(
            opening="Engaging opening that establishes character and situation",
            rising_action="Development of conflict and tension",
            climax="Climactic moment that resolves main conflict",
            resolution="Satisfying conclusion with thematic resolution",
            main_characters=["Protagonist with clear motivation"],
            themes=[requirements.theme] if requirements.theme else ["character growth"],
            estimated_word_count=requirements.target_word_count
        )
    
    async def _generate_from_outline(self, outline: StoryOutline, requirements: StoryRequirements) -> str:
        """Generate story content based on the outline"""
        
        outline_prompt = f"""Write a {requirements.genre.value} short story based on this detailed outline:

Opening: {outline.opening}
Rising Action: {outline.rising_action}
Climax: {outline.climax}
Resolution: {outline.resolution}

Characters: {', '.join(outline.main_characters)}
Themes: {', '.join(outline.themes)}

Target word count: {requirements.target_word_count} words

Generate the complete story following this outline structure."""
        
        result = await enhanced_story_agent.run(outline_prompt, deps=self.dependencies)
        return result.output
    
    async def _generate_title(self, story_content: str, requirements: StoryRequirements) -> str:
        """Generate an appropriate title for the story"""
        title_prompt = f"""Based on this {requirements.genre.value} story, generate a compelling, appropriate title:

{story_content[:500]}...

Generate only the title, nothing else."""

        try:
            logger.debug("Generating title with enhanced agent")
            result = await enhanced_story_agent.run(title_prompt, deps=self.dependencies)
            title = result.output.strip().strip('"').strip("'")
            if not title:
                raise AgentError("Agent returned empty title")
            return title
        except Exception as e:
            logger.warning(f"Title generation failed: {e}. Using fallback title.")
            return f"A {requirements.genre.value.title()} Story"
    
    async def _final_validation(
        self, 
        content: str, 
        requirements: StoryRequirements, 
        validation_level: ValidationLevel
    ) -> ValidationResult:
        """Perform final validation on generated content"""
        
        # Use the validation tool for final check
        word_count_result = await enhanced_story_agent.run(
            f"Validate word count for story with target {requirements.target_word_count}",
            deps=self.dependencies
        )
        
        # Create comprehensive validation result
        word_count = len(content.split())
        tolerance = 0.2 if validation_level == ValidationLevel.STANDARD else 0.1
        min_words = int(requirements.target_word_count * (1 - tolerance))
        max_words = int(requirements.target_word_count * (1 + tolerance))
        
        validation_result = ValidationResult(
            is_valid=min_words <= word_count <= max_words,
            word_count_valid=min_words <= word_count <= max_words,
            genre_length_compatible=True,
            theme_feasible=True,
            word_count_analysis={
                "actual": word_count,
                "target": requirements.target_word_count,
                "min_acceptable": min_words,
                "max_acceptable": max_words,
                "variance_percentage": abs(word_count - requirements.target_word_count) / requirements.target_word_count * 100
            }
        )
        
        if not validation_result.word_count_valid:
            if word_count < min_words:
                validation_result.warnings.append(f"Story is {min_words - word_count} words shorter than target")
            else:
                validation_result.warnings.append(f"Story is {word_count - max_words} words longer than target")
        
        return validation_result
    
    def _create_generation_prompt(self, requirements: StoryRequirements) -> str:
        """Create a detailed prompt for direct story generation"""
        
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
            "First, get the genre and length guidelines using the available tools, then generate the story."
        ])
        
        return "\n".join(prompt_parts)


# Convenience functions for V1.2

async def generate_story_enhanced(
    requirements: StoryRequirements,
    generation_method: Optional[GenerationMethod] = None,
    validation_level: Optional[ValidationLevel] = None,
    config: Optional[EnhancedAgentConfig] = None
) -> EnhancedGeneratedStory:
    """Generate a story using the enhanced V1.2 generator"""
    generator = EnhancedStoryGenerator(config)
    return await generator.generate_story(requirements, generation_method, validation_level)


async def generate_story(requirements: StoryRequirements) -> EnhancedGeneratedStory:
    """Generate a story using V1.2 with auto-selected method (maintains V1.1 compatibility)"""
    return await generate_story_enhanced(requirements, GenerationMethod.AUTO)