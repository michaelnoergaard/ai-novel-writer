"""
V1.3 Story Agent - Advanced Workflow Orchestration
Production-ready PydanticAI agent with workflow orchestration, quality assessment, and performance monitoring
"""

import asyncio
import logging
import time
from typing import Dict, Any, Optional
from datetime import datetime
from pydantic_ai import Agent, RunContext

# Import models and dependencies
from ..models.basic_models import StoryRequirements, StoryGenre, StoryLength
from ..models.v13_models import (
    AdvancedGeneratedStory, WorkflowState, WorkflowStage, QualityMetrics,
    GenerationStrategy, PerformanceMetrics, RequirementAnalysis,
    StrategyRecommendation, WorkflowConfiguration
)
from .v13_dependencies import V13StoryDependencies
from ..workflow import WorkflowEngine, WorkflowStep
from ..utils.config import StoryGenerationError, AgentError, ValidationError, WorkflowError

# Setup logging
logger = logging.getLogger(__name__)

# Enhanced system prompt for V1.3
V13_SYSTEM_PROMPT = """You are a professional short story writer with expertise in crafting compelling narratives using advanced workflow orchestration.

Your task is to generate complete, publishable short stories based on the given requirements using intelligent workflow management.

**Key Capabilities:**
- Advanced workflow orchestration with multi-step generation processes
- Intelligent strategy selection based on requirement analysis
- Real-time quality assessment and enhancement
- Performance monitoring and optimization
- Adaptive generation approaches

**Workflow Principles:**
- Analyze requirements thoroughly before generation
- Select optimal generation strategy based on complexity
- Use structured workflow steps for consistent quality
- Monitor progress and adjust approach as needed
- Validate quality at each stage
- Provide comprehensive feedback and insights

**Quality Standards:**
- Maintain high narrative quality through structured processes
- Ensure genre compliance and thematic integration
- Optimize for both quality and generation efficiency
- Provide transparent process insights and recommendations

**Tool Usage Guidelines:**
- Always start with requirement analysis and strategy selection
- Use workflow orchestration for complex or high-quality requirements
- Apply quality assessment throughout the generation process
- Monitor performance metrics for continuous improvement
- Provide detailed feedback on generation process and outcomes

Generate stories that are engaging, well-structured, and professionally crafted while maintaining transparency about the generation process and quality metrics."""


class V13StoryAgent:
    """
    Version 1.3 Story Agent with advanced workflow orchestration, quality assessment,
    and performance monitoring capabilities.
    """
    
    def __init__(self, config: Optional[WorkflowConfiguration] = None):
        self.config = config or WorkflowConfiguration()
        self.dependencies = V13StoryDependencies(self.config)
        
        # Initialize workflow engine
        self.workflow_engine = WorkflowEngine({
            'max_workflow_time': self.config.max_workflow_time,
            'enable_quality_enhancement': self.config.enable_quality_enhancement,
            'quality_threshold': self.config.quality_threshold,
            'max_enhancement_iterations': self.config.max_enhancement_iterations
        })
        
        # Register workflow steps
        self._register_workflow_steps()
        
        # Create PydanticAI agent
        self.agent = Agent(
            'openai:gpt-4o',
            deps_type=V13StoryDependencies,
            system_prompt=V13_SYSTEM_PROMPT,
            retries=3
        )
        
        # Note: Tools removed - using direct prompts instead
        
        logger.info("V13StoryAgent initialized with workflow orchestration")
    
    def _register_workflow_steps(self) -> None:
        """Register workflow steps with the engine"""
        
        # Step 1: Requirements Analysis
        self.workflow_engine.register_step(
            name="requirements_analysis",
            stage=WorkflowStage.ANALYSIS,
            handler=self._analyze_requirements_step,
            timeout=30,
            retry_count=2,
            required=True
        )
        
        # Step 2: Strategy Selection
        self.workflow_engine.register_step(
            name="strategy_selection",
            stage=WorkflowStage.STRATEGY_SELECTION,
            handler=self._select_strategy_step,
            timeout=30,
            retry_count=2,
            required=True
        )
        
        # Step 3: Outline Generation (conditional)
        self.workflow_engine.register_step(
            name="outline_generation",
            stage=WorkflowStage.OUTLINE_GENERATION,
            handler=self._generate_outline_step,
            timeout=60,
            retry_count=2,
            required=False
        )
        
        # Step 4: Content Generation
        self.workflow_engine.register_step(
            name="content_generation",
            stage=WorkflowStage.CONTENT_GENERATION,
            handler=self._generate_content_step,
            timeout=120,
            retry_count=2,
            required=True
        )
        
        # Step 5: Quality Assessment
        self.workflow_engine.register_step(
            name="quality_assessment",
            stage=WorkflowStage.QUALITY_ASSESSMENT,
            handler=self._assess_quality_step,
            timeout=60,
            retry_count=2,
            required=True
        )
        
        # Step 6: Enhancement (conditional)
        self.workflow_engine.register_step(
            name="enhancement",
            stage=WorkflowStage.ENHANCEMENT,
            handler=self._enhance_story_step,
            timeout=90,
            retry_count=1,
            required=False
        )
    
    def _register_tools(self) -> None:
        """Register tools with the PydanticAI agent - DISABLED"""
        # Tools disabled - using direct prompts instead to avoid infinite loops
        return
        
        @self.agent.tool
        async def analyze_story_requirements(
            ctx: RunContext[V13StoryDependencies], 
            requirements: StoryRequirements
        ) -> RequirementAnalysis:
            """Analyze story requirements for complexity and feasibility"""
            logger.debug("Tool: analyze_story_requirements")
            return ctx.deps.analyze_requirements(requirements)
        
        @self.agent.tool
        async def select_generation_strategy(
            ctx: RunContext[V13StoryDependencies],
            requirements: StoryRequirements
        ) -> StrategyRecommendation:
            """Select optimal generation strategy based on requirements"""
            logger.debug("Tool: select_generation_strategy")
            return ctx.deps.get_strategy_recommendation(requirements)
        
        @self.agent.tool
        async def generate_story_outline(
            ctx: RunContext[V13StoryDependencies],
            requirements: StoryRequirements
        ) -> Dict[str, Any]:
            """Generate structured story outline"""
            logger.debug("Tool: generate_story_outline")
            
            # Get genre guidelines
            genre_guidelines = ctx.deps.genre_guidelines.get(requirements.genre, "")
            
            outline_prompt = f"""Create a detailed story outline for a {requirements.genre.value} story.

Requirements:
- Genre: {requirements.genre.value}
- Target word count: {requirements.target_word_count}
- Theme: {requirements.theme or 'Not specified'}
- Setting: {requirements.setting or 'Not specified'}

Guidelines:
{genre_guidelines}

Create an outline with:
1. Opening: Character introduction and situation setup
2. Rising Action: Conflict development and complications
3. Climax: Peak moment of tension or revelation
4. Resolution: Conclusion and character growth

Format as a structured outline with clear sections."""
            
            result = await self.agent.run(outline_prompt, deps=ctx.deps)
            
            return {
                'outline_content': result.data if hasattr(result, 'data') else str(result),
                'structure': 'four_act',
                'estimated_sections': 4
            }
        
        @self.agent.tool
        async def generate_story_content(
            ctx: RunContext[V13StoryDependencies],
            requirements: StoryRequirements,
            outline: Optional[Dict[str, Any]] = None
        ) -> Dict[str, str]:
            """Generate the main story content"""
            logger.debug("Tool: generate_story_content")
            
            # Build generation prompt
            genre_guidelines = ctx.deps.genre_guidelines.get(requirements.genre, "")
            length_guidelines = ctx.deps.length_guidelines.get(requirements.length, "")
            
            content_prompt = f"""Write a complete {requirements.genre.value} short story.

Requirements:
- Genre: {requirements.genre.value}
- Length: {requirements.length.value}
- Target word count: {requirements.target_word_count} words
- Theme: {requirements.theme or 'Not specified'}
- Setting: {requirements.setting or 'Not specified'}

Guidelines:
{genre_guidelines}

{length_guidelines}"""
            
            if outline:
                content_prompt += f"\n\nBased on this outline:\n{outline.get('outline_content', '')}"
            
            content_prompt += "\n\nWrite the complete story with a compelling title."
            
            # Generate content
            result = await self.agent.run(content_prompt, deps=ctx.deps)
            content = result.data if hasattr(result, 'data') else str(result)
            
            # Extract title and content
            lines = content.strip().split('\n')
            title = lines[0].strip('# ').strip() if lines else "Untitled Story"
            story_content = '\n'.join(lines[1:]).strip() if len(lines) > 1 else content
            
            return {
                'title': title,
                'content': story_content
            }
        
        @self.agent.tool
        async def assess_story_quality(
            ctx: RunContext[V13StoryDependencies],
            story_content: str,
            story_title: str,
            requirements: StoryRequirements
        ) -> QualityMetrics:
            """Assess the quality of generated story"""
            logger.debug("Tool: assess_story_quality")
            return await ctx.deps.quality_assessor.assess_quality(
                story_content, story_title, requirements
            )
        
        @self.agent.tool
        async def enhance_story_quality(
            ctx: RunContext[V13StoryDependencies],
            story_content: str,
            story_title: str,
            quality_metrics: QualityMetrics,
            requirements: StoryRequirements
        ) -> Dict[str, str]:
            """Enhance story quality based on assessment"""
            logger.debug("Tool: enhance_story_quality")
            
            # Get improvement suggestions
            suggestions = ctx.deps.get_enhancement_suggestions(
                quality_metrics, story_content, requirements
            )
            
            if not suggestions:
                return {'title': story_title, 'content': story_content}
            
            # Create enhancement prompt
            suggestion_text = '\n'.join([f"- {s.suggestion}" for s in suggestions[:3]])
            
            enhancement_prompt = f"""Enhance this {requirements.genre.value} story based on the following suggestions:

{suggestion_text}

Original Story:
Title: {story_title}

{story_content}

Improve the story while maintaining its core narrative and staying within approximately {requirements.target_word_count} words."""
            
            result = await self.agent.run(enhancement_prompt, deps=ctx.deps)
            enhanced_content = result.data if hasattr(result, 'data') else str(result)
            
            # Extract enhanced title and content
            lines = enhanced_content.strip().split('\n')
            enhanced_title = lines[0].strip('# ').strip() if lines else story_title
            enhanced_story = '\n'.join(lines[1:]).strip() if len(lines) > 1 else enhanced_content
            
            return {
                'title': enhanced_title,
                'content': enhanced_story
            }
    
    async def _analyze_requirements_step(self, context: Dict[str, Any]) -> RequirementAnalysis:
        """Workflow step: Analyze requirements"""
        requirements = context['requirements']
        analysis = self.dependencies.analyze_requirements(requirements)
        
        logger.info(f"Requirements analysis: complexity={analysis.complexity_score:.2f}, "
                   f"difficulty={analysis.estimated_difficulty}")
        
        return analysis
    
    async def _select_strategy_step(self, context: Dict[str, Any]) -> StrategyRecommendation:
        """Workflow step: Select generation strategy"""
        requirements = context['requirements']
        strategy_rec = self.dependencies.get_strategy_recommendation(requirements)
        
        # Update context with selected strategy
        context['selected_strategy'] = strategy_rec.recommended_strategy
        
        logger.info(f"Selected strategy: {strategy_rec.recommended_strategy.value} "
                   f"(confidence: {strategy_rec.confidence:.2f})")
        
        return strategy_rec
    
    async def _generate_outline_step(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Workflow step: Generate story outline (conditional)"""
        strategy = context.get('selected_strategy', GenerationStrategy.DIRECT)
        requirements = context['requirements']
        
        # Skip outline for direct strategy
        if strategy == GenerationStrategy.DIRECT:
            logger.debug("Skipping outline generation for direct strategy")
            return None
        
        # Build outline generation prompt
        genre_guidelines = self.dependencies.genre_guidelines.get(requirements.genre, "")
        
        outline_prompt = f"""Create a detailed story outline for a {requirements.genre.value} story.

Requirements:
- Genre: {requirements.genre.value}
- Target word count: {requirements.target_word_count}
- Theme: {requirements.theme or 'Not specified'}
- Setting: {requirements.setting or 'Not specified'}

Guidelines:
{genre_guidelines}

Create an outline with:
1. Opening: Character introduction and situation setup
2. Rising Action: Conflict development and complications
3. Climax: Peak moment of tension or revelation
4. Resolution: Conclusion and character growth

Format as a structured outline with clear sections."""
        
        # Generate outline using agent
        result = await self.agent.run(outline_prompt, deps=self.dependencies)
        
        outline = {
            'outline_content': result.data if hasattr(result, 'data') else str(result),
            'structure': 'four_act',
            'estimated_sections': 4
        }
        
        logger.debug("Generated story outline")
        return outline
    
    async def _generate_content_step(self, context: Dict[str, Any]) -> Dict[str, str]:
        """Workflow step: Generate story content"""
        requirements = context['requirements']
        outline = context['results'].get('outline_generation')
        
        # Build generation prompt
        genre_guidelines = self.dependencies.genre_guidelines.get(requirements.genre, "")
        length_guidelines = self.dependencies.length_guidelines.get(requirements.length, "")
        
        content_prompt = f"""Write a complete {requirements.genre.value} short story.

Requirements:
- Genre: {requirements.genre.value}
- Length: {requirements.length.value}
- Target word count: {requirements.target_word_count} words
- Theme: {requirements.theme or 'Not specified'}
- Setting: {requirements.setting or 'Not specified'}

Guidelines:
{genre_guidelines}

{length_guidelines}

"""
        
        # Add outline if available
        if outline and outline.get('outline_content'):
            content_prompt += f"""\nOutline to follow:
{outline['outline_content']}

Use this outline as a guide but feel free to expand and develop the story naturally.
"""
        
        content_prompt += """\n\nWrite a compelling, well-structured story that meets all requirements. Include a compelling title.

Provide the story in this format:
**Title:** [Your compelling title here]

[Your complete story here]"""
        
        # Generate content using agent
        result = await self.agent.run(content_prompt, deps=self.dependencies)
        
        # Parse the result to extract title and content
        story_text = result.data if hasattr(result, 'data') else str(result)
        
        # Extract title and content
        lines = story_text.strip().split('\n')
        title = "Untitled Story"
        content_start_idx = 0
        
        # Look for title in first few lines
        for i, line in enumerate(lines[:5]):
            if line.strip().startswith('**Title:**'):
                title = line.replace('**Title:**', '').strip()
                content_start_idx = i + 1
                break
            elif line.strip().startswith('Title:'):
                title = line.replace('Title:', '').strip()
                content_start_idx = i + 1
                break
        
        # Get content (skip empty lines after title)
        content_lines = lines[content_start_idx:]
        while content_lines and not content_lines[0].strip():
            content_lines = content_lines[1:]
        
        content = '\n'.join(content_lines) if content_lines else story_text
        
        content_result = {
            'title': title,
            'content': content
        }
        
        # Update context with generated content
        context['story_title'] = content_result['title']
        context['story_content'] = content_result['content']
        
        logger.info(f"Generated story: '{content_result['title']}' "
                   f"({len(content_result['content'].split())} words)")
        
        return content_result
    
    async def _assess_quality_step(self, context: Dict[str, Any]) -> QualityMetrics:
        """Workflow step: Assess story quality"""
        story_content = context['story_content']
        story_title = context['story_title']
        requirements = context['requirements']
        
        # Assess quality using tool
        quality_metrics = await self.dependencies.quality_assessor.assess_quality(
            story_content, story_title, requirements
        )
        
        # Update context with quality metrics
        context['quality_metrics'] = quality_metrics
        
        logger.info(f"Quality assessment: overall={quality_metrics.overall_score:.1f}, "
                   f"structure={quality_metrics.structure_score:.1f}, "
                   f"coherence={quality_metrics.coherence_score:.1f}")
        
        return quality_metrics
    
    async def _enhance_story_step(self, context: Dict[str, Any]) -> Optional[Dict[str, str]]:
        """Workflow step: Enhance story quality (conditional)"""
        quality_metrics = context.get('quality_metrics')
        if not quality_metrics:
            return None
        
        requirements = context['requirements']
        
        # Check if enhancement is needed
        if not self.dependencies.should_use_enhancement(quality_metrics, requirements):
            logger.debug("Skipping enhancement - quality meets threshold")
            return None
        
        story_content = context['story_content']
        story_title = context['story_title']
        
        # Build enhancement prompt
        enhancement_prompt = f"""Enhance the quality of this {requirements.genre.value} story based on the quality assessment.

Original Title: {story_title}

Original Story:
{story_content}

Quality Assessment:
- Overall Score: {quality_metrics.overall_score}/10
- Structure Score: {quality_metrics.structure_score}/10
- Coherence Score: {quality_metrics.coherence_score}/10
- Character Development: {quality_metrics.character_development}/10
- Pacing Quality: {quality_metrics.pacing_quality}/10
- Genre Compliance: {quality_metrics.genre_compliance}/10
- Theme Integration: {quality_metrics.theme_integration}/10

Focus on improving the areas with lower scores while maintaining the story's core strengths.

Provide the enhanced story in this format:
**Title:** [Enhanced title if needed]

[Enhanced story content]"""
        
        # Generate enhanced content using agent
        result = await self.agent.run(enhancement_prompt, deps=self.dependencies)
        
        # Parse the result to extract title and content
        enhanced_text = result.data if hasattr(result, 'data') else str(result)
        
        # Extract title and content
        lines = enhanced_text.strip().split('\n')
        enhanced_title = story_title  # Default to original title
        content_start_idx = 0
        
        # Look for title in first few lines
        for i, line in enumerate(lines[:5]):
            if line.strip().startswith('**Title:**'):
                enhanced_title = line.replace('**Title:**', '').strip()
                content_start_idx = i + 1
                break
            elif line.strip().startswith('Title:'):
                enhanced_title = line.replace('Title:', '').strip()
                content_start_idx = i + 1
                break
        
        # Get content (skip empty lines after title)
        content_lines = lines[content_start_idx:]
        while content_lines and not content_lines[0].strip():
            content_lines = content_lines[1:]
        
        enhanced_content = '\n'.join(content_lines) if content_lines else enhanced_text
        
        enhanced_result = {
            'title': enhanced_title,
            'content': enhanced_content
        }
        
        # Update context with enhanced content
        context['story_title'] = enhanced_result['title']
        context['story_content'] = enhanced_result['content']
        
        logger.info(f"Enhanced story quality for: '{enhanced_result['title']}'")
        return enhanced_result


async def generate_story_v13(
    requirements: StoryRequirements,
    strategy: Optional[GenerationStrategy] = None,
    config: Optional[WorkflowConfiguration] = None,
    progress_callback: Optional[callable] = None
) -> AdvancedGeneratedStory:
    """
    Generate a story using V1.3 workflow orchestration
    
    Args:
        requirements: Story generation requirements
        strategy: Optional strategy override
        config: Optional workflow configuration
        progress_callback: Optional progress callback function
        
    Returns:
        AdvancedGeneratedStory with comprehensive results
    """
    try:
        # Initialize agent
        agent = V13StoryAgent(config)
        
        # Auto-select strategy if not provided
        if strategy is None:
            strategy_rec = agent.dependencies.get_strategy_recommendation(requirements)
            strategy = strategy_rec.recommended_strategy
            logger.info(f"Auto-selected strategy: {strategy.value}")
        
        # Start performance monitoring
        workflow_id = f"v13_{int(time.time())}"
        agent.dependencies.performance_monitor.start_workflow_monitoring(
            workflow_id, strategy, {
                'genre': requirements.genre.value,
                'target_word_count': requirements.target_word_count,
                'theme': requirements.theme,
                'setting': requirements.setting
            }
        )
        
        # Execute workflow
        result = await agent.workflow_engine.execute_workflow(
            requirements, strategy, progress_callback
        )
        
        # Record performance
        agent.dependencies.log_performance_data(
            strategy, requirements, True, 
            result.quality_metrics.overall_score,
            result.generation_time
        )
        
        # Finish monitoring
        performance_metrics = agent.dependencies.performance_monitor.finish_workflow_monitoring(
            workflow_id, True, result.quality_metrics.overall_score, result.word_count
        )
        
        # Update result with performance metrics
        result.performance_metrics = performance_metrics
        
        logger.info(f"V1.3 generation completed successfully: '{result.title}' "
                   f"({result.word_count} words, quality: {result.quality_metrics.overall_score:.1f})")
        
        return result
        
    except Exception as e:
        logger.error(f"V1.3 story generation failed: {e}")
        raise StoryGenerationError(f"V1.3 generation failed: {e}") from e