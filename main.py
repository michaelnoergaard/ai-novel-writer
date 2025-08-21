"""
AI Short Story Writer - Version 1 CLI Interface
Command-line interface for generating short stories using PydanticAI
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional

import click
from basic_models import StoryRequirements, StoryGenre, StoryLength
from simple_agent_v1 import generate_story
from config import setup_logging, validate_environment, ConfigurationError, StoryGenerationError
from pdf_formatter import export_story_to_pdf


@click.command()
@click.option(
    '--genre', '-g',
    type=click.Choice(['literary', 'mystery', 'science_fiction', 'fantasy', 'romance']),
    default='literary',
    help='Genre of the story to generate'
)
@click.option(
    '--length', '-l',
    type=click.Choice(['flash', 'short']),
    default='short',
    help='Length category of the story'
)
@click.option(
    '--words', '-w',
    type=int,
    default=2000,
    help='Target word count (100-7500)'
)
@click.option(
    '--theme', '-t',
    type=str,
    help='Optional theme for the story'
)
@click.option(
    '--setting', '-s',
    type=str,
    help='Optional setting for the story'
)
@click.option(
    '--output', '-o',
    type=click.Path(),
    help='Output file path (optional, defaults to stdout)'
)
@click.option(
    '--pdf', '-p',
    type=click.Path(),
    help='Export to PDF file path (e.g., story.pdf)'
)
@click.option(
    '--verbose', '-v',
    is_flag=True,
    help='Verbose output with generation details'
)
def generate(
    genre: str,
    length: str,
    words: int,
    theme: Optional[str],
    setting: Optional[str],
    output: Optional[str],
    pdf: Optional[str],
    verbose: bool
):
    """Generate a short story using AI agents.
    
    This tool generates complete short stories with professional
    formatting options including themed PDF export.
    
    Examples:
    
        # Generate a basic literary short story
        uv run main.py generate
        
        # Generate and export to themed PDF
        uv run main.py generate -g mystery -w 2000 -p mystery_story.pdf
        
        # Generate with theme and save both text and PDF
        uv run main.py generate -g fantasy -t "courage" -o story.txt -p story.pdf
        
        # Generate flash fiction with verbose output
        uv run main.py generate -l flash -w 750 -v -p flash.pdf
    """
    
    # Setup logging
    log_level = "DEBUG" if verbose else "INFO"
    setup_logging(log_level)
    
    # Validate environment
    try:
        env_status = validate_environment()
        if verbose:
            click.echo(f"Environment validated: {env_status}")
    except ConfigurationError as e:
        click.echo(f"Configuration error: {e}", err=True)
        click.echo("Please set required environment variables.", err=True)
        sys.exit(1)
    
    # Validate word count
    if words < 100 or words > 7500:
        click.echo("Error: Word count must be between 100 and 7500", err=True)
        sys.exit(1)
    
    # Validate word count against length category
    if length == 'flash' and words > 1000:
        click.echo("Warning: Flash fiction typically under 1000 words", err=True)
    elif length == 'short' and words < 1000:
        click.echo("Warning: Short stories typically 1000+ words", err=True)
    
    if verbose:
        click.echo(f"Generating {genre} {length} story...")
        click.echo(f"Target word count: {words}")
        if theme:
            click.echo(f"Theme: {theme}")
        if setting:
            click.echo(f"Setting: {setting}")
        click.echo()
    
    # Create requirements
    try:
        requirements = StoryRequirements(
            genre=StoryGenre(genre),
            length=StoryLength(length),
            target_word_count=words,
            theme=theme,
            setting=setting
        )
    except Exception as e:
        click.echo(f"Error creating story requirements: {e}", err=True)
        sys.exit(1)
    
    # Generate the story
    try:
        if verbose:
            click.echo("Generating story... (this may take a minute)")
        
        story = asyncio.run(generate_story(requirements))
        
        if verbose:
            click.echo(f"Generation complete!")
            click.echo(f"Title: {story.title}")
            click.echo(f"Word count: {story.word_count}")
            click.echo(f"Genre: {story.genre}")
            click.echo("-" * 50)
        
        # Prepare output
        story_text = format_story_output(story, verbose)
        
        # Handle PDF export
        if pdf:
            pdf_path = Path(pdf)
            try:
                pdf_path.parent.mkdir(parents=True, exist_ok=True)
                exported_path = export_story_to_pdf(story, pdf_path)
                click.echo(f"PDF exported to: {exported_path}")
                if verbose:
                    click.echo(f"PDF features theme-based styling for {story.genre.value} genre")
            except Exception as e:
                click.echo(f"Error exporting PDF: {e}", err=True)
                if verbose:
                    import traceback
                    click.echo(traceback.format_exc(), err=True)
                sys.exit(1)
        
        # Write to text file or stdout
        if output:
            output_path = Path(output)
            try:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_text(story_text, encoding='utf-8')
                click.echo(f"Story saved to: {output_path}")
            except Exception as e:
                click.echo(f"Error saving to file: {e}", err=True)
                sys.exit(1)
        elif not pdf:  # Only show on stdout if no PDF was generated
            click.echo(story_text)
            
    except StoryGenerationError as e:
        click.echo(f"Story generation error: {e}", err=True)
        sys.exit(1)
    except KeyboardInterrupt:
        click.echo("\nGeneration interrupted by user", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        if verbose:
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
        if story.requirements.theme:
            lines.append(f"**Theme:** {story.requirements.theme}")
        if story.requirements.setting:
            lines.append(f"**Setting:** {story.requirements.setting}")
        lines.append("")
        lines.append("---")
        lines.append("")
    
    # Story content
    lines.append(story.content)
    
    return "\n".join(lines)


@click.group()
@click.version_option(version="1.0.0", prog_name="AI Short Story Writer")
def cli():
    """AI Short Story Writer - Autonomous story generation with professional formatting
    
    This tool generates complete short stories using AI agents with
    professional PDF export featuring theme-based styling.
    Each story is crafted to be publication-ready with proper
    structure, character development, and narrative flow.
    """
    pass


@cli.command()
def info():
    """Display information about the story generator"""
    click.echo("AI Short Story Writer - Version 1.0")
    click.echo("=====================================")
    click.echo()
    click.echo("Supported Genres:")
    for genre in StoryGenre:
        click.echo(f"  - {genre.value}")
    click.echo()
    click.echo("Length Categories:")
    click.echo("  - flash: 100-1000 words")
    click.echo("  - short: 1000-7500 words")
    click.echo()
    click.echo("Example Usage:")
    click.echo("  python main.py generate -g mystery -w 2500 -t 'betrayal'")


@cli.command()
def examples():
    """Show example commands"""
    examples_text = """
Example Commands:

Basic generation to console:
  uv run main.py generate

Generate mystery story as themed PDF:
  uv run main.py generate -g mystery -w 2000 -p mystery_story.pdf

Literary fiction with theme (PDF + text):
  uv run main.py generate -g literary -t "redemption" -w 3000 -o story.txt -p story.pdf

Flash fiction with verbose output:
  uv run main.py generate -l flash -w 750 -v -p flash.pdf

Fantasy with setting and theme:
  uv run main.py generate -g fantasy -s "enchanted forest" -t "courage" -w 4000 -p fantasy.pdf

Romance with professional PDF styling:
  uv run main.py generate -g romance -w 2000 -p romance_story.pdf -v
"""
    click.echo(examples_text)


# Add the generate command to the CLI group
cli.add_command(generate)


if __name__ == '__main__':
    cli()