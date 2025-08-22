"""
AI Short Story Writer - Version 1.2 CLI Interface
Enhanced command-line interface with dual generation modes and structured output
"""

import asyncio
import sys
import json
from pathlib import Path
from typing import Optional

import click
from basic_models import StoryRequirements, StoryGenre, StoryLength
from enhanced_models import GenerationMethod, ValidationLevel, EnhancedAgentConfig
from enhanced_story_agent import generate_story_enhanced
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
# V1.2 Enhanced Options
@click.option(
    '--generation-method', '-m',
    type=click.Choice(['auto', 'direct', 'outline']),
    default='auto',
    help='Generation method: auto (smart selection), direct (V1.1 compatible), outline (V1.2 enhanced)'
)
@click.option(
    '--validation-level',
    type=click.Choice(['basic', 'standard', 'strict']),
    default='standard',
    help='Validation strictness level'
)
@click.option(
    '--show-outline',
    is_flag=True,
    help='Display the generated outline (for outline-based generation)'
)
@click.option(
    '--validation-details',
    is_flag=True,
    help='Show detailed validation results'
)
@click.option(
    '--metadata',
    is_flag=True,
    help='Include generation metadata in output'
)
@click.option(
    '--json-output',
    is_flag=True,
    help='Output results in JSON format'
)
def generate(
    genre: str,
    length: str,
    words: int,
    theme: Optional[str],
    setting: Optional[str],
    output: Optional[str],
    pdf: Optional[str],
    verbose: bool,
    generation_method: str,
    validation_level: str,
    show_outline: bool,
    validation_details: bool,
    metadata: bool,
    json_output: bool
):
    """Generate a short story using enhanced AI agents.
    
    Version 1.2 features dual generation modes with enhanced tools and structured output.
    
    Examples:
    
        # Generate using auto-selected method (V1.2 smart selection)
        uv run main_v12.py generate
        
        # Generate with outline-based method
        uv run main_v12.py generate -m outline --show-outline
        
        # Generate with strict validation and metadata
        uv run main_v12.py generate --validation-level strict --metadata
        
        # Generate mystery with theme and export structured data
        uv run main_v12.py generate -g mystery -t "justice" --json-output -o story.json
        
        # V1.1 compatible mode (direct generation)
        uv run main_v12.py generate -m direct -v
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
        sys.exit(1)
    
    # Create story requirements
    try:
        story_genre = StoryGenre(genre)
        story_length = StoryLength(length)
        requirements = StoryRequirements(
            genre=story_genre,
            length=story_length,
            target_word_count=words,
            theme=theme,
            setting=setting
        )
    except ValueError as e:
        click.echo(f"Invalid requirements: {e}", err=True)
        sys.exit(1)
    
    # Convert string enums to model enums
    gen_method = GenerationMethod(generation_method)
    val_level = ValidationLevel(validation_level)
    
    # Create configuration
    config = EnhancedAgentConfig(
        default_generation_method=gen_method,
        validation_level=val_level,
        show_tool_usage=verbose
    )
    
    # Display generation info
    if not json_output:
        click.echo(f"Generating {story_genre.value} {story_length.value} story...")
        click.echo(f"Target word count: {words}")
        click.echo(f"Generation method: {gen_method.value}")
        click.echo(f"Validation level: {val_level.value}")
        if theme:
            click.echo(f"Theme: {theme}")
        if setting:
            click.echo(f"Setting: {setting}")
        click.echo("")
        click.echo("Generating story... (this may take a minute)")
    
    # Generate story
    try:
        story = asyncio.run(
            generate_story_enhanced(
                requirements, 
                gen_method, 
                val_level, 
                config
            )
        )
        
        if not json_output:
            click.echo("Generation complete!")
        
        # Display results based on options
        if json_output:
            output_data = {
                "title": story.title,
                "content": story.content,
                "word_count": story.word_count,
                "genre": story.genre.value,
                "generation_method": story.generation_method.value,
                "requirements": {
                    "genre": story.requirements.genre.value,
                    "length": story.requirements.length.value,
                    "target_word_count": story.requirements.target_word_count,
                    "theme": story.requirements.theme,
                    "setting": story.requirements.setting
                }
            }
            
            if metadata:
                output_data["metadata"] = {
                    "tools_used": story.metadata.tools_used,
                    "generation_time": story.metadata.generation_time,
                    "outline_generated": story.metadata.outline_generated,
                    "validation_level": story.metadata.validation_level.value
                }
            
            if show_outline and story.outline_used:
                output_data["outline"] = {
                    "opening": story.outline_used.opening,
                    "rising_action": story.outline_used.rising_action,
                    "climax": story.outline_used.climax,
                    "resolution": story.outline_used.resolution,
                    "characters": story.outline_used.main_characters,
                    "themes": story.outline_used.themes
                }
            
            if validation_details:
                output_data["validation"] = {
                    "is_valid": story.validation_results.is_valid,
                    "word_count_valid": story.validation_results.word_count_valid,
                    "warnings": story.validation_results.warnings,
                    "suggestions": story.validation_results.suggestions,
                    "word_count_analysis": story.validation_results.word_count_analysis
                }
            
            # Output JSON
            if output:
                with open(output, 'w', encoding='utf-8') as f:
                    json.dump(output_data, f, indent=2, ensure_ascii=False)
                click.echo(f"JSON output saved to: {output}")
            else:
                click.echo(json.dumps(output_data, indent=2, ensure_ascii=False))
        
        else:
            # Standard text output
            display_story_text(
                story, 
                show_outline=show_outline, 
                validation_details=validation_details,
                metadata_info=metadata,
                verbose=verbose
            )
            
            # Save text output if requested
            if output:
                save_text_output(story, output)
        
        # Generate PDF if requested
        if pdf:
            generate_pdf_output(story, pdf, verbose)
    
    except StoryGenerationError as e:
        click.echo(f"Story generation error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def display_story_text(story, show_outline=False, validation_details=False, metadata_info=False, verbose=False):
    """Display story in formatted text output"""
    
    # Display outline if requested and available
    if show_outline and story.outline_used:
        click.echo("=" * 50)
        click.echo("STORY OUTLINE")
        click.echo("=" * 50)
        click.echo(f"Opening: {story.outline_used.opening}")
        click.echo(f"Rising Action: {story.outline_used.rising_action}")
        click.echo(f"Climax: {story.outline_used.climax}")
        click.echo(f"Resolution: {story.outline_used.resolution}")
        if story.outline_used.main_characters:
            click.echo(f"Characters: {', '.join(story.outline_used.main_characters)}")
        if story.outline_used.themes:
            click.echo(f"Themes: {', '.join(story.outline_used.themes)}")
        click.echo("")
    
    # Display validation details if requested
    if validation_details:
        click.echo("=" * 50)
        click.echo("VALIDATION RESULTS")
        click.echo("=" * 50)
        click.echo(f"Overall Valid: {'✓' if story.validation_results.is_valid else '✗'}")
        click.echo(f"Word Count Valid: {'✓' if story.validation_results.word_count_valid else '✗'}")
        
        if story.validation_results.warnings:
            click.echo("Warnings:")
            for warning in story.validation_results.warnings:
                click.echo(f"  - {warning}")
        
        if story.validation_results.suggestions:
            click.echo("Suggestions:")
            for suggestion in story.validation_results.suggestions:
                click.echo(f"  - {suggestion}")
        
        if story.validation_results.word_count_analysis:
            analysis = story.validation_results.word_count_analysis
            click.echo(f"Word Count Analysis: {analysis.get('actual', 'N/A')}/{analysis.get('target', 'N/A')} words")
        
        click.echo("")
    
    # Display metadata if requested
    if metadata_info:
        click.echo("=" * 50)
        click.echo("GENERATION METADATA")
        click.echo("=" * 50)
        click.echo(f"Method: {story.generation_method.value}")
        click.echo(f"Generation Time: {story.metadata.generation_time:.2f} seconds")
        click.echo(f"Outline Generated: {'Yes' if story.metadata.outline_generated else 'No'}")
        click.echo(f"Tools Used: {', '.join(story.metadata.tools_used) if story.metadata.tools_used else 'None'}")
        click.echo(f"Validation Level: {story.metadata.validation_level.value}")
        click.echo("")
    
    # Main story output
    click.echo(f"Title: {story.title}")
    click.echo(f"Word count: {story.word_count}")
    click.echo(f"Genre: {story.genre.value}")
    click.echo("-" * 50)
    click.echo(f"# {story.title}")
    click.echo("")
    click.echo(f"**Genre:** {story.genre.value.title()}")
    click.echo(f"**Word Count:** {story.word_count}")
    if story.generation_method == GenerationMethod.OUTLINE_BASED:
        click.echo(f"**Generation Method:** Outline-based (V1.2)")
    else:
        click.echo(f"**Generation Method:** Direct (V1.1 compatible)")
    click.echo("")
    click.echo("---")
    click.echo("")
    click.echo(story.content)


def save_text_output(story, output_path):
    """Save story to text file"""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"# {story.title}\n\n")
        f.write(f"**Genre:** {story.genre.value.title()}\n")
        f.write(f"**Word Count:** {story.word_count}\n")
        f.write(f"**Generation Method:** {story.generation_method.value}\n\n")
        f.write("---\n\n")
        f.write(story.content)
    
    click.echo(f"Story saved to: {output_path}")


def generate_pdf_output(story, pdf_path, verbose):
    """Generate PDF output using existing formatter"""
    try:
        # Convert enhanced story to basic story for PDF compatibility
        basic_story = story.to_basic_story()
        export_story_to_pdf(basic_story, pdf_path)
        click.echo(f"PDF saved to: {pdf_path}")
    except Exception as e:
        click.echo(f"PDF generation failed: {e}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()


@click.command()
def info():
    """Display information about the V1.2 enhanced story generator"""
    click.echo("AI Short Story Writer - Version 1.2")
    click.echo("Enhanced story generation with dual modes and structured output")
    click.echo("")
    click.echo("Generation Methods:")
    click.echo("  • auto    - Smart method selection based on requirements")
    click.echo("  • direct  - V1.1 compatible single-pass generation")
    click.echo("  • outline - V1.2 enhanced outline-first generation")
    click.echo("")
    click.echo("Validation Levels:")
    click.echo("  • basic    - Essential validation only")
    click.echo("  • standard - Balanced validation (default)")
    click.echo("  • strict   - Comprehensive validation")
    click.echo("")
    click.echo("Enhanced Features:")
    click.echo("  • Structured story outlines")
    click.echo("  • Detailed validation feedback")
    click.echo("  • Generation metadata tracking")
    click.echo("  • JSON output support")
    click.echo("  • Enhanced tool ecosystem (7 tools)")
    click.echo("")
    click.echo("Tools Available:")
    click.echo("  • Genre guidelines")
    click.echo("  • Length guidelines") 
    click.echo("  • Story outline generation")
    click.echo("  • Requirement validation")
    click.echo("  • Character development guidelines")
    click.echo("  • Theme integration guidance")
    click.echo("  • Precise word count validation")


@click.command()
def examples():
    """Show example commands for V1.2 features"""
    click.echo("AI Short Story Writer V1.2 - Example Commands")
    click.echo("")
    click.echo("Basic Usage (Auto Method Selection):")
    click.echo("  uv run main_v12.py generate")
    click.echo("  uv run main_v12.py generate -g mystery -w 2500")
    click.echo("")
    click.echo("Outline-Based Generation:")
    click.echo("  uv run main_v12.py generate -m outline --show-outline")
    click.echo("  uv run main_v12.py generate -g fantasy -m outline -t 'courage' --show-outline")
    click.echo("")
    click.echo("Enhanced Validation:")
    click.echo("  uv run main_v12.py generate --validation-level strict --validation-details")
    click.echo("  uv run main_v12.py generate -g literary --validation-level basic")
    click.echo("")
    click.echo("Structured Output:")
    click.echo("  uv run main_v12.py generate --json-output --metadata")
    click.echo("  uv run main_v12.py generate --json-output --show-outline -o story.json")
    click.echo("")
    click.echo("V1.1 Compatibility:")
    click.echo("  uv run main_v12.py generate -m direct -v")
    click.echo("  uv run main_v12.py generate -m direct -g mystery -w 2000 -p story.pdf")
    click.echo("")
    click.echo("Advanced Usage:")
    click.echo("  uv run main_v12.py generate -g romance -t 'second chances' \\")
    click.echo("    -s 'small coastal town' -m outline --show-outline \\")
    click.echo("    --validation-details --metadata -p romance.pdf")


@click.group()
def cli():
    """AI Short Story Writer - Version 1.2
    
    Enhanced story generation with dual modes and structured output.
    """
    pass


# Add commands to the CLI group
cli.add_command(generate)
cli.add_command(info)
cli.add_command(examples)


if __name__ == '__main__':
    cli()