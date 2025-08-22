"""
AI Short Story Writer - Simplified CLI Interface
Configuration-driven story generation with minimal command-line options
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional
import tomllib

import click
from src.ai_story_writer.models import StoryRequirements, StoryGenre, StoryLength
from src.ai_story_writer.utils import setup_logging, validate_environment, ConfigurationError, StoryGenerationError, export_story_to_pdf

# Import latest version - V1.2 Enhanced
from src.ai_story_writer.agents import generate_story_enhanced
from src.ai_story_writer.models import GenerationMethod, ValidationLevel, EnhancedAgentConfig


def load_config(config_path: str = "config.toml") -> dict:
    """Load configuration from TOML file"""
    try:
        with open(config_path, "rb") as f:
            return tomllib.load(f)
    except FileNotFoundError:
        click.echo(f"Config file '{config_path}' not found. Using defaults.", err=True)
        return {}
    except Exception as e:
        click.echo(f"Error loading config: {e}", err=True)
        return {}


@click.command()
@click.argument('prompt', required=False)
@click.option('--config', '-c', default='config.toml', help='Config file path')
@click.option('--theme', '-t', help='Story theme (overrides config)')
@click.option('--words', '-w', type=int, help='Word count (overrides config)')
@click.option('--genre', '-g', help='Story genre (overrides config)')
@click.option('--output', '-o', help='Output file (overrides config)')
def generate(prompt: Optional[str], config: str, theme: Optional[str], 
            words: Optional[int], genre: Optional[str], output: Optional[str]):
    """Generate a story using configuration file settings.
    
    PROMPT: Optional story prompt or theme
    
    Examples:
        uv run main_simple.py
        uv run main_simple.py "A tale of courage"
        uv run main_simple.py -t "mystery" -w 500
    """
    
    # Load configuration
    cfg = load_config(config)
    
    # Set up logging
    try:
        setup_logging()
    except Exception as e:
        click.echo(f"Logging setup failed: {e}", err=True)
    
    # Validate environment
    try:
        env_status = validate_environment()
        if cfg.get('output', {}).get('verbose', True):
            click.echo(f"Environment validated: {env_status}")
    except ConfigurationError as e:
        click.echo(f"Configuration error: {e}", err=True)
        sys.exit(1)
    
    # Build story requirements from config + overrides
    story_cfg = cfg.get('story', {})
    
    # Use prompt as theme if provided
    final_theme = prompt or theme or story_cfg.get('theme', '')
    final_words = words or story_cfg.get('words', 1000)
    final_genre = genre or story_cfg.get('genre', 'literary')
    final_length = 'flash' if final_words <= 1000 else 'short'
    
    if cfg.get('output', {}).get('verbose', True):
        click.echo(f"Generating {final_genre} story ({final_words} words)")
        if final_theme:
            click.echo(f"Theme: {final_theme}")
    
    try:
        # Create story requirements
        requirements = StoryRequirements(
            genre=StoryGenre(final_genre),
            length=StoryLength(final_length),
            target_word_count=final_words,
            theme=final_theme if final_theme else None,
            setting=story_cfg.get('setting') if story_cfg.get('setting') else None
        )
    except Exception as e:
        click.echo(f"Error creating story requirements: {e}", err=True)
        sys.exit(1)
    
    # Generate the story using V1.2 enhanced
    try:
        if cfg.get('output', {}).get('verbose', True):
            click.echo("Generating story...")
        
        gen_cfg = cfg.get('generation', {})
        gen_method = GenerationMethod(gen_cfg.get('method', 'auto'))
        validation_level = ValidationLevel(gen_cfg.get('validation_level', 'standard'))
        config_obj = EnhancedAgentConfig(default_generation_method=gen_method)
        
        story = asyncio.run(generate_story_enhanced(requirements, gen_method, validation_level, config_obj))
        
        if cfg.get('output', {}).get('verbose', True):
            click.echo(f"✓ Story generated: '{story.title}' ({story.word_count} words)")
        
        # Format output
        story_text = format_story_output(story, cfg.get('output', {}).get('verbose', True))
        
        # Handle output
        output_cfg = cfg.get('output', {})
        final_output = output or output_cfg.get('output_file')
        
        if final_output:
            Path(final_output).write_text(story_text, encoding='utf-8')
            click.echo(f"Story saved to: {final_output}")
        else:
            click.echo(story_text)
        
        # Handle PDF export
        pdf_file = output_cfg.get('pdf_file')
        if pdf_file:
            try:
                export_story_to_pdf(story, pdf_file)
                click.echo(f"PDF exported to: {pdf_file}")
            except Exception as e:
                click.echo(f"PDF export failed: {e}", err=True)
        
    except KeyboardInterrupt:
        click.echo("\nGeneration interrupted by user", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        if cfg.get('output', {}).get('verbose', True):
            import traceback
            click.echo(traceback.format_exc(), err=True)
        sys.exit(1)


def format_story_output(story, include_metadata: bool = False) -> str:
    """Format the story for output"""
    lines = []
    
    # Title
    lines.append(f"# {story.title}")
    lines.append("")
    
    if include_metadata:
        lines.append(f"**Genre:** {story.genre.value.title()}")
        lines.append(f"**Word Count:** {story.word_count}")
        lines.append(f"**Generation Method:** {story.generation_method.value}")
        lines.append(f"**Generation Time:** {story.metadata.generation_time:.2f} seconds")
        if story.requirements.theme:
            lines.append(f"**Theme:** {story.requirements.theme}")
        lines.append("")
        lines.append("---")
        lines.append("")
    
    # Story content
    lines.append(story.content)
    
    return "\n".join(lines)


if __name__ == '__main__':
    generate()