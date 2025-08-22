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

# Import latest version - V1.3 Workflow Orchestration
try:
    from src.ai_story_writer.agents.v13_story_agent import generate_story_v13
    from src.ai_story_writer.models.v13_models import GenerationStrategy, WorkflowConfiguration
    V13_AVAILABLE = True
except ImportError:
    # Fallback to V1.2
    from src.ai_story_writer.agents import generate_story_enhanced
    from src.ai_story_writer.models import GenerationMethod, ValidationLevel, EnhancedAgentConfig
    V13_AVAILABLE = False


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
@click.option('--genre', '-g', help='Story genre - accepts any genre (sci-fi, cyberpunk, steampunk, etc.)')
@click.option('--output', '-o', help='Output file (overrides config)')
def generate(prompt: Optional[str], config: str, theme: Optional[str], 
            words: Optional[int], genre: Optional[str], output: Optional[str]):
    """Generate a story using configuration file settings.
    
    PROMPT: Optional story prompt or theme
    
    Examples:
        uv run main.py
        uv run main.py "A tale of courage"
        uv run main.py -g "sci-fi" -w 500 "Robot rebellion"
        uv run main.py -g "cyberpunk" -t "neon dreams"
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
            setting=story_cfg.get('setting') if story_cfg.get('setting') else None,
            original_genre=final_genre  # Preserve the original user input
        )
    except Exception as e:
        click.echo(f"Error creating story requirements: {e}", err=True)
        sys.exit(1)
    
    # Generate the story using latest available version
    try:
        if cfg.get('output', {}).get('verbose', True):
            version_info = "V1.3 workflow orchestration" if V13_AVAILABLE else "V1.2 enhanced"
            click.echo(f"Generating story using {version_info}...")
        
        if V13_AVAILABLE:
            # Use V1.3 workflow orchestration
            gen_cfg = cfg.get('generation', {})
            workflow_cfg = cfg.get('workflow', {})
            
            strategy = GenerationStrategy(gen_cfg.get('method', 'adaptive'))
            config_obj = WorkflowConfiguration(
                default_strategy=GenerationStrategy(workflow_cfg.get('default_strategy', 'adaptive')),
                max_workflow_time=workflow_cfg.get('max_workflow_time', 300),
                enable_quality_enhancement=workflow_cfg.get('enable_quality_enhancement', True),
                quality_threshold=workflow_cfg.get('quality_threshold', 7.0),
                max_enhancement_iterations=workflow_cfg.get('max_enhancement_iterations', 2)
            )
            
            story = asyncio.run(generate_story_v13(requirements, strategy, config_obj))
        else:
            # Fallback to V1.2
            gen_cfg = cfg.get('generation', {})
            gen_method = GenerationMethod(gen_cfg.get('method', 'auto'))
            validation_level = ValidationLevel(gen_cfg.get('validation_level', 'standard'))
            config_obj = EnhancedAgentConfig(default_generation_method=gen_method)
            
            story = asyncio.run(generate_story_enhanced(requirements, gen_method, validation_level, config_obj))
        
        if cfg.get('output', {}).get('verbose', True):
            if V13_AVAILABLE and hasattr(story, 'quality_metrics'):
                click.echo(f"✓ Story generated: '{story.title}' ({story.word_count} words, quality: {story.quality_metrics.overall_score:.1f})")
            else:
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
        
        # V1.3 enhanced metadata
        if hasattr(story, 'quality_metrics') and story.quality_metrics:
            lines.append(f"**Quality Score:** {story.quality_metrics.overall_score:.1f}/10")
            lines.append(f"**Generation Strategy:** {story.strategy_used}")
            lines.append(f"**Generation Time:** {story.generation_time:.2f} seconds")
            if hasattr(story, 'workflow_id'):
                lines.append(f"**Workflow ID:** {story.workflow_id}")
        # V1.2 metadata fallback
        elif hasattr(story, 'generation_method'):
            lines.append(f"**Generation Method:** {story.generation_method}")
            if hasattr(story, 'metadata') and 'generation_time' in story.metadata:
                lines.append(f"**Generation Time:** {story.metadata['generation_time']:.2f} seconds")
        
        if hasattr(story, 'requirements') and story.requirements and story.requirements.theme:
            lines.append(f"**Theme:** {story.requirements.theme}")
        
        lines.append("")
        lines.append("---")
        lines.append("")
    
    # Story content
    lines.append(story.content)
    
    return "\n".join(lines)


if __name__ == '__main__':
    generate()