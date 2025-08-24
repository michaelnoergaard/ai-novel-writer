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

# Unified AI Story Writer - Single Application
from src.ai_story_writer.agents.story_agent import generate_story
from src.ai_story_writer.models.story_models import (
    AdaptiveGenerationConfig, AdaptiveGenerationResult, UserProfile, SystemContext, 
    AdaptationStrategy, PersonalizationIntensity, QualityConfig, GenerationStrategy, WorkflowConfiguration
)


def load_config(config_path: str = "config.toml") -> dict:
    """Load configuration from TOML file - must succeed"""
    with open(config_path, "rb") as f:
        return tomllib.load(f)


@click.command()
@click.argument('prompt', required=False)
@click.option('--config', '-c', default='config.toml', help='Config file path')
@click.option('--theme', '-t', help='Story theme (overrides config)')
@click.option('--words', '-w', type=int, help='Word count (overrides config)')
@click.option('--genre', '-g', help='Story genre - accepts any genre (sci-fi, cyberpunk, steampunk, etc.)')
@click.option('--output', '-o', help='Output file (overrides config)')
# Adaptive Intelligence Options
@click.option('--quality-mode', is_flag=True, help='Enable enhanced quality feedback')
@click.option('--target-quality', type=float, help='Set target quality threshold (0-10)')
@click.option('--max-passes', type=int, help='Maximum enhancement passes')
@click.option('--show-trends', is_flag=True, help='Display quality improvement trends')
@click.option('--no-enhancement', is_flag=True, help='Disable quality enhancement')
@click.option('--adaptive-mode', type=click.Choice(['conservative', 'moderate', 'aggressive']), default='moderate', help='Adaptive intelligence mode')
@click.option('--personalization', type=click.Choice(['minimal', 'moderate', 'comprehensive']), default='moderate', help='Personalization level')
@click.option('--user-id', type=str, help='User ID for personalization')
@click.option('--show-predictions', is_flag=True, help='Display predictive analytics')
@click.option('--show-intelligence', is_flag=True, help='Display intelligence insights')
def generate(prompt: Optional[str], config: str, theme: Optional[str], 
            words: Optional[int], genre: Optional[str], output: Optional[str],
            quality_mode: bool, target_quality: Optional[float], max_passes: Optional[int],
            show_trends: bool, no_enhancement: bool, adaptive_mode: str,
            personalization: str, user_id: Optional[str], show_predictions: bool, 
            show_intelligence: bool):
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
    
    # Generate the story using unified AI Story Writer
    try:
        if cfg.get('output', {}).get('verbose', True):
            click.echo(f"Generating story using unified AI Story Writer...")
            if quality_mode:
                click.echo("Enhanced quality feedback mode enabled")
            if show_predictions:
                click.echo("Predictive analytics enabled")
            if show_intelligence:
                click.echo("Intelligence insights enabled")
        
        gen_cfg = cfg.get('generation', {})
        workflow_cfg = cfg.get('workflow', {})
        quality_enhancement_cfg = cfg.get('quality_enhancement', {})
        adaptive_cfg = cfg.get('adaptive_intelligence', {})
        
        strategy = GenerationStrategy(gen_cfg.get('method', 'adaptive'))
        
        # Create workflow configuration
        workflow_config = WorkflowConfiguration(
            default_strategy=GenerationStrategy(workflow_cfg.get('default_strategy', 'adaptive')),
            max_workflow_time=workflow_cfg.get('max_workflow_time', 300),
            enable_quality_enhancement=workflow_cfg.get('enable_quality_enhancement', True),
            quality_threshold=workflow_cfg.get('quality_threshold', 7.0),
            max_enhancement_iterations=workflow_cfg.get('max_enhancement_iterations', 2)
        )
        
        # Create quality configuration with CLI overrides
        quality_config = QualityConfig(
            enable_multi_pass=not no_enhancement and quality_enhancement_cfg.get('enable_multi_pass', True),
            target_quality_score=target_quality or quality_enhancement_cfg.get('target_quality_score', 8.0),
            max_enhancement_passes=max_passes or quality_enhancement_cfg.get('max_enhancement_passes', 3),
            quality_convergence_threshold=quality_enhancement_cfg.get('quality_convergence_threshold', 0.1),
            enable_quality_prediction=quality_enhancement_cfg.get('enable_quality_prediction', True),
            
            # Enhancement strategies from config
            enhancement_strategy_weights=cfg.get('enhancement_strategies', {}),
            
            # User experience settings
            enable_progress_tracking=cfg.get('user_experience', {}).get('enable_progress_tracking', True),
            show_quality_trends=show_trends or cfg.get('user_experience', {}).get('show_quality_trends', True),
            display_enhancement_suggestions=quality_mode or cfg.get('user_experience', {}).get('display_enhancement_suggestions', True),
            interactive_enhancement=cfg.get('user_experience', {}).get('interactive_enhancement', False),
            quality_feedback_detail=cfg.get('user_experience', {}).get('quality_feedback_detail', 'comprehensive'),
            
            # Performance optimization
            enable_generation_caching=cfg.get('performance_optimization', {}).get('enable_generation_caching', True),
            cache_retention_hours=cfg.get('performance_optimization', {}).get('cache_retention_hours', 24),
            enable_parallel_assessment=cfg.get('performance_optimization', {}).get('enable_parallel_assessment', True),
            optimize_token_usage=cfg.get('performance_optimization', {}).get('optimize_token_usage', True),
            enable_resource_profiling=cfg.get('performance_optimization', {}).get('enable_resource_profiling', True),
            
            # Advanced metrics - ALL REQUIRED, NO OPTIONAL ASSESSMENTS
            enable_dialogue_assessment=True,
            enable_setting_assessment=True,
            enable_emotional_assessment=True,
            enable_originality_assessment=True,
            enable_technical_assessment=True,
            assessment_detail_level='comprehensive'
        )
        
        # Create V1.5 adaptive configuration
        adaptive_config = AdaptiveGenerationConfig(
            quality_config=quality_config,
            workflow_config=workflow_config,
            
            # V1.5 adaptive intelligence settings
            adaptation_strategy=AdaptationStrategy(adaptive_mode),
            personalization_intensity=PersonalizationIntensity(personalization),
            enable_predictive_analytics=True,
            enable_adaptive_learning=adaptive_cfg.get('enable_adaptive_learning', True),
            enable_resource_optimization=True,
            
            # Learning configuration
            learning_rate=adaptive_cfg.get('learning_rate', 0.1),
            prediction_confidence_threshold=adaptive_cfg.get('prediction_confidence_threshold', 0.7),
            adaptation_aggressiveness=adaptive_cfg.get('adaptation_aggressiveness', 0.5),
            
            # Performance settings
            max_adaptation_overhead=adaptive_cfg.get('max_adaptation_overhead', 0.2),
            enable_parallel_prediction=True,
            cache_learning_data=True,
            learning_history_window=adaptive_cfg.get('learning_history_window', 100)
        )
        
        # Create user profile if user_id provided
        user_profile = None
        if user_id:
            from datetime import datetime
            from src.ai_story_writer.models.story_models import UserPreferences
            
            # Create basic user profile (would be loaded from storage in real implementation)
            user_profile = UserProfile(
                user_id=user_id,
                preferences=UserPreferences(),
                generation_history=[],
                learning_data={},
                profile_created=datetime.now(),
                profile_updated=datetime.now(),
                interaction_count=0,
                satisfaction_history=[],
                adaptation_effectiveness=0.0
            )
        
        # Create system context
        system_context = SystemContext(
            current_load=0.3,  # Simulated system load
            available_resources={"cpu": 0.8, "memory": 0.9},
            active_learning_sessions=0,
            cache_status={"enabled": True, "hit_rate": 0.4},
            system_performance_trend="stable"
        )
        
        story = asyncio.run(generate_story(
            requirements=requirements,
            strategy=strategy,
            workflow_config=workflow_config,
            quality_config=quality_config,
            user_profile=user_profile,
            system_context=system_context,
            adaptive_config=adaptive_config
        ))
        
        # Display generation results
        if cfg.get('output', {}).get('verbose', True):
            # Adaptive intelligence output
            quality_summary = story.get_quality_summary()
            intelligence_summary = story.get_intelligence_summary()
            
            click.echo(f"✓ Story generated: '{story.title}' ({story.word_count} words)")
            click.echo(f"  Quality: {quality_summary['overall_score']:.1f}/10 ({quality_summary['quality_tier']})")
            
            if quality_summary['enhancement_passes'] > 0:
                click.echo(f"  Enhancement: {quality_summary['enhancement_passes']} passes, +{quality_summary['total_improvement']:.1f} improvement")
                click.echo(f"  Performance: {quality_summary['generation_time']:.1f}s, {quality_summary['tokens_used']} tokens")
            
            # Show adaptive intelligence insights
            if story.adaptation_applied:
                click.echo(f"  Adaptation: {intelligence_summary['adaptations']['effectiveness']:.2f} effectiveness, {intelligence_summary['adaptations']['strategy_adaptations']} adaptations")
            
            if show_predictions:
                pred_summary = intelligence_summary['predictions']
                click.echo(f"\n🔮 Predictions:")
                click.echo(f"  Quality range: {pred_summary['quality_range'][0]:.1f}-{pred_summary['quality_range'][1]:.1f} (confidence: {pred_summary['confidence']:.2f})")
                click.echo(f"  Accuracy score: {pred_summary['accuracy']:.1f}/10")
            
            if show_intelligence:
                eff_summary = intelligence_summary['efficiency']
                learn_summary = intelligence_summary['learning']
                click.echo(f"\n🧠 Intelligence:")
                click.echo(f"  Token efficiency: {eff_summary['token_efficiency']:.2f}, Time efficiency: {eff_summary['time_efficiency']:.2f}")
                click.echo(f"  Cache hit rate: {eff_summary['cache_hit_rate']:.1%}")
                click.echo(f"  Learning contributions: {learn_summary['contributions']}, Updates: {learn_summary['user_updates']}")
            
            # Show quality feedback if requested
            if quality_mode or show_trends:
                click.echo(f"\n📊 Quality Assessment:")
                click.echo(f"  Target achieved: {'✓' if quality_summary['target_achieved'] else '✗'}")
                
                if story.quality_feedback.strengths:
                    click.echo(f"  Strengths: {', '.join(story.quality_feedback.strengths[:2])}")
                
                if story.quality_feedback.areas_for_improvement:
                    click.echo(f"  Areas for improvement: {', '.join(story.quality_feedback.areas_for_improvement[:2])}")
                
                # Show optimization opportunities
                if story.optimization_opportunities:
                    click.echo(f"\n{story.get_optimization_report()}")
            
            # Show satisfaction prediction
            if user_profile:
                click.echo(f"  Predicted satisfaction: {story.user_satisfaction_prediction:.1f}/10")
        
        # Format output
        story_text = format_story_output(story, cfg.get('output', {}).get('verbose', True))
        
        # Handle output
        output_cfg = cfg.get('output', {})
        final_output = output or output_cfg.get('output_file')
        
        # Always save to file, use default if none specified
        if not final_output:
            final_output = "generated_story.txt"
            
        Path(final_output).write_text(story_text, encoding='utf-8')
        click.echo(f"Story saved to: {final_output}")
        
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