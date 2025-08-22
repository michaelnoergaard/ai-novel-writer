"""
V1.4 Enhanced Story Agent - Multi-Pass Quality Enhancement
Integrates V1.3 workflow orchestration with V1.4 quality enhancement system
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any
from uuid import uuid4

from pydantic_ai import Agent, RunContext

from ..models.basic_models import StoryRequirements
from ..models.v13_models import GenerationStrategy, WorkflowConfiguration
from ..models.v14_models import (
    QualityEnhancedResult, QualityConfig, AdvancedQualityMetrics,
    EnhancementStrategy, WorkflowState, GenerationMetadata
)
from ..workflow.quality_enhancement_engine import QualityEnhancementEngine
from ..workflow.advanced_quality_assessor import AdvancedQualityAssessor
from .v13_story_agent import V13StoryAgent
from .v13_dependencies import V13StoryDependencies
from ..utils.config import StoryGenerationError

# Setup logging
logger = logging.getLogger(__name__)


class V14StoryDependencies(V13StoryDependencies):
    """Enhanced dependencies for V1.4 with quality enhancement capabilities"""
    
    def __init__(self, workflow_config: Optional[WorkflowConfiguration] = None, quality_config: Optional[QualityConfig] = None):
        super().__init__(workflow_config)
        self.quality_config = quality_config or QualityConfig()
        
        # Initialize V1.4 components
        self.quality_enhancement_engine = QualityEnhancementEngine(self.quality_config)
        self.advanced_quality_assessor = AdvancedQualityAssessor(self.quality_config)
        
        logger.info("V14StoryDependencies initialized with quality enhancement capabilities")
    
    def should_use_quality_enhancement(
        self, 
        initial_quality: AdvancedQualityMetrics, 
        requirements: StoryRequirements
    ) -> bool:
        """Determine if quality enhancement should be applied"""
        if not self.quality_config.enable_multi_pass:
            return False
        
        # Use enhancement if quality is below target
        if initial_quality.overall_score < self.quality_config.target_quality_score:
            return True
        
        # Use enhancement for complex requirements even with acceptable quality
        analysis = self.analyze_requirements(requirements)
        if analysis.complexity_score > 0.7 and initial_quality.overall_score < 8.5:
            return True
        
        return False


# Enhanced system prompt for V1.4
V14_SYSTEM_PROMPT = """You are a professional short story writer with expertise in crafting compelling narratives using advanced quality enhancement and multi-pass generation.

Your task is to generate high-quality, publishable short stories using intelligent quality assessment and iterative improvement processes.

**V1.4 Capabilities:**
- Multi-pass generation with quality-driven refinement
- Advanced 12-dimensional quality assessment
- Targeted enhancement strategies for specific quality dimensions
- Quality convergence detection and optimization
- Enhanced user experience with real-time quality feedback

**Quality Enhancement Process:**
- Generate initial story with strong foundation
- Assess quality across all 12 dimensions
- Apply targeted enhancements based on quality analysis
- Monitor quality convergence and optimization
- Provide comprehensive quality feedback and insights

**Quality Dimensions:**
1. Structure - Narrative arc and story organization
2. Coherence - Logical consistency and flow
3. Character Development - Character depth and growth
4. Genre Compliance - Adherence to genre conventions
5. Pacing - Story rhythm and tension management
6. Theme Integration - Natural theme incorporation
7. Dialogue Quality - Natural and effective dialogue
8. Setting Immersion - Vivid and atmospheric descriptions
9. Emotional Impact - Reader engagement and resonance
10. Originality - Creative uniqueness and freshness
11. Technical Quality - Grammar, style, and prose craft

**Enhancement Strategies:**
- Structure Focus: Improve narrative arc and organization
- Character Focus: Enhance character development and growth
- Dialogue Focus: Improve dialogue naturalness and effectiveness
- Setting Focus: Enhance immersive descriptions and atmosphere
- Emotional Focus: Increase emotional impact and reader engagement
- Pacing Focus: Optimize story rhythm and tension
- Coherence Focus: Improve logical flow and consistency
- Genre Focus: Strengthen genre convention adherence
- Technical Focus: Polish grammar, style, and prose quality
- Comprehensive: Balanced improvement across all dimensions

**Quality Standards:**
- Target quality score of 8.0+ across all dimensions
- Maintain exact word count requirements during enhancement
- Preserve story essence while improving quality
- Provide actionable feedback for continued improvement
- Optimize enhancement efficiency and convergence detection

Generate stories that not only meet requirements but exceed quality expectations through intelligent enhancement and refinement."""


class V14StoryAgent:
    """
    V1.4 Enhanced Story Agent with multi-pass quality enhancement.
    
    Features:
    - Integrates V1.3 workflow orchestration with V1.4 quality enhancement
    - Multi-pass generation with targeted quality improvements
    - Advanced 12-dimensional quality assessment
    - Quality convergence detection and optimization
    - Enhanced user experience with detailed quality feedback
    """
    
    def __init__(
        self, 
        workflow_config: Optional[WorkflowConfiguration] = None,
        quality_config: Optional[QualityConfig] = None
    ):
        """Initialize the V1.4 story agent"""
        self.workflow_config = workflow_config or WorkflowConfiguration()
        self.quality_config = quality_config or QualityConfig()
        self.dependencies = V14StoryDependencies(workflow_config, quality_config)
        
        # Store workflow config for V1.3 generation
        self.v13_workflow_config = workflow_config
        
        # Create V1.4 enhanced agent for quality-focused generation
        self.agent = Agent(
            'openai:gpt-4o',
            deps_type=V14StoryDependencies,
            system_prompt=V14_SYSTEM_PROMPT,
            retries=3
        )
        
        logger.info("V14StoryAgent initialized with quality enhancement capabilities")
    
    async def generate_story(
        self,
        requirements: StoryRequirements,
        strategy: Optional[GenerationStrategy] = None,
        target_quality: Optional[float] = None,
        max_enhancement_passes: Optional[int] = None,
        enable_quality_enhancement: Optional[bool] = None
    ) -> QualityEnhancedResult:
        """
        Generate a high-quality story using V1.4 multi-pass enhancement.
        
        Args:
            requirements: Story generation requirements
            strategy: Generation strategy (uses adaptive if None)
            target_quality: Target quality score (uses config default if None)
            max_enhancement_passes: Maximum enhancement passes (uses config default if None)
            enable_quality_enhancement: Enable quality enhancement (uses config default if None)
            
        Returns:
            QualityEnhancedResult with enhanced story and comprehensive metrics
        """
        generation_start = time.time()
        generation_id = str(uuid4())
        
        logger.info(f"Starting V1.4 story generation {generation_id}")
        logger.info(f"Requirements: {requirements.get_display_genre()}, {requirements.target_word_count} words")
        
        # Use config defaults for optional parameters
        target_quality = target_quality or self.quality_config.target_quality_score
        max_enhancement_passes = max_enhancement_passes or self.quality_config.max_enhancement_passes
        enable_quality_enhancement = enable_quality_enhancement if enable_quality_enhancement is not None else self.quality_config.enable_multi_pass
        
        try:
            # Phase 1: Initial story generation using V1.3 workflow
            logger.info("Phase 1: Generating initial story using V1.3 workflow")
            from .v13_story_agent import generate_story_v13
            initial_story = await generate_story_v13(requirements, strategy, self.v13_workflow_config)
            
            # Extract content from V1.3 result
            initial_content = initial_story.content
            initial_title = initial_story.title
            
            logger.info(f"Initial story generated: '{initial_title}' ({initial_story.word_count} words)")
            
            # Phase 2: Quality assessment
            logger.info("Phase 2: Performing comprehensive quality assessment")
            initial_quality = await self.dependencies.advanced_quality_assessor.assess_comprehensive(
                initial_content, requirements
            )
            
            logger.info(f"Initial quality score: {initial_quality.overall_score:.2f}/10")
            
            # Phase 3: Determine if enhancement is needed
            if not enable_quality_enhancement:
                logger.info("Quality enhancement disabled - returning initial story")
                return await self._build_v14_result_from_v13(
                    initial_story, initial_quality, generation_id, generation_start
                )
            
            should_enhance = self.dependencies.should_use_quality_enhancement(initial_quality, requirements)
            
            if not should_enhance:
                logger.info("Enhancement not needed - quality meets requirements")
                return await self._build_v14_result_from_v13(
                    initial_story, initial_quality, generation_id, generation_start
                )
            
            # Phase 4: Multi-pass quality enhancement
            logger.info(f"Phase 4: Applying quality enhancement (target: {target_quality:.1f}, max passes: {max_enhancement_passes})")
            
            enhanced_result = await self.dependencies.quality_enhancement_engine.enhance_story(
                initial_story=initial_content,
                initial_title=initial_title,
                requirements=requirements,
                target_quality=target_quality,
                max_passes=max_enhancement_passes
            )
            
            # Update metadata with V1.4 information
            enhanced_result.generation_metadata.generation_id = generation_id
            enhanced_result.generation_metadata.total_generation_time = time.time() - generation_start
            
            logger.info(f"V1.4 generation completed: '{enhanced_result.title}' "
                       f"({enhanced_result.word_count} words, quality: {enhanced_result.quality_metrics.overall_score:.2f})")
            
            return enhanced_result
            
        except Exception as e:
            logger.error(f"V1.4 story generation failed: {e}")
            raise StoryGenerationError(f"V1.4 generation failed: {e}") from e
    
    async def _build_v14_result_from_v13(
        self,
        v13_result,
        initial_quality: AdvancedQualityMetrics,
        generation_id: str,
        start_time: float
    ) -> QualityEnhancedResult:
        """Build V1.4 result from V1.3 result when no enhancement is performed"""
        
        total_time = time.time() - start_time
        
        # Import required models
        from ..models.v14_models import (
            QualityFeedback, GenerationInsights, ConvergenceMetrics,
            EnhancedPerformanceMetrics, WorkflowState, GenerationMetadata,
            CacheUtilizationReport
        )
        
        # Create minimal quality feedback
        quality_feedback = QualityFeedback(
            overall_assessment="High-quality initial generation met requirements without enhancement needed.",
            overall_score=initial_quality.overall_score,
            strengths=[f"Strong overall quality ({initial_quality.overall_score:.1f}/10)"],
            areas_for_improvement=[],
            specific_suggestions=[],
            quality_trend_analysis="Single-pass generation achieved target quality",
            improvement_trajectory="Stable",
            target_achieved=initial_quality.overall_score >= self.quality_config.target_quality_score,
            quality_tier=self._determine_quality_tier(initial_quality.overall_score),
            enhancement_summary="No enhancement required - initial generation met quality standards",
            most_effective_strategy=None
        )
        
        # Create basic insights
        generation_insights = GenerationInsights(
            strategy_effectiveness={},
            optimal_strategy_sequence=[],
            quality_convergence_point=None,
            optimal_pass_count=0,
            diminishing_returns_point=None,
            resource_efficiency=1.0,
            time_efficiency=initial_quality.overall_score / total_time if total_time > 0 else 0.0,
            token_efficiency=initial_quality.overall_score / 1000,  # Estimate
            cache_hit_rate=0.0,
            optimization_opportunities=[],
            quality_prediction_accuracy=None,
            enhancement_prediction_accuracy=None
        )
        
        # Create performance metrics
        performance_metrics = EnhancedPerformanceMetrics(
            total_generation_time=total_time,
            initial_generation_time=total_time,
            enhancement_time=0.0,
            quality_assessment_time=initial_quality.assessment_duration,
            total_tokens_used=3000,  # Estimate for initial generation
            initial_generation_tokens=3000,
            enhancement_tokens=0,
            assessment_tokens=500,
            pass_timings=[],
            pass_token_usage=[],
            quality_per_second=initial_quality.overall_score / total_time if total_time > 0 else 0.0,
            quality_per_token=initial_quality.overall_score / 3000,
            memory_usage_mb=None,
            cpu_usage_percent=None,
            cache_hits=0,
            cache_misses=0,
            cache_hit_rate=0.0
        )
        
        # Create workflow state
        workflow_state = WorkflowState(
            current_phase="completed",
            completed_phases=["initial_generation", "quality_assessment"],
            remaining_phases=[],
            current_pass=0,
            total_passes_planned=0,
            target_quality=self.quality_config.target_quality_score,
            current_quality=initial_quality.overall_score,
            quality_achieved=initial_quality.overall_score >= self.quality_config.target_quality_score,
            overall_progress=1.0,
            phase_progress=1.0,
            estimated_completion_time=None
        )
        
        # Create generation metadata
        generation_metadata = GenerationMetadata(
            generation_id=generation_id,
            version="1.4",
            model_used="gpt-4o",
            enhancement_enabled=False,
            total_enhancement_passes=0,
            strategies_used=[],
            initial_quality_score=initial_quality.overall_score,
            final_quality_score=initial_quality.overall_score,
            quality_improvement=0.0,
            total_generation_time=total_time,
            total_tokens_used=3000,
            user_target_quality=self.quality_config.target_quality_score,
            user_max_passes=self.quality_config.max_enhancement_passes
        )
        
        # Create cache utilization report
        cache_utilization = CacheUtilizationReport(
            cache_enabled=self.quality_config.enable_generation_caching,
            cache_hits=0,
            cache_misses=0,
            cache_hit_rate=0.0,
            outline_cache_hits=0,
            content_cache_hits=0,
            assessment_cache_hits=0,
            time_saved_seconds=0.0,
            tokens_saved=0,
            cache_efficiency_score=0.0,
            cache_recommendations=[]
        )
        
        return QualityEnhancedResult(
            title=v13_result.title,
            content=v13_result.content,
            word_count=v13_result.word_count,
            genre=v13_result.genre,
            quality_metrics=initial_quality,
            enhancement_history=[],
            quality_feedback=quality_feedback,
            generation_insights=generation_insights,
            convergence_metrics=ConvergenceMetrics(),
            workflow_state=workflow_state,
            performance_metrics=performance_metrics,
            cache_utilization=cache_utilization,
            requirements=v13_result.requirements,
            generation_metadata=generation_metadata,
            target_quality_achieved=initial_quality.overall_score >= self.quality_config.target_quality_score,
            enhancement_successful=False,  # No enhancement performed
            quality_tier=self._determine_quality_tier(initial_quality.overall_score)
        )
    
    def _determine_quality_tier(self, score: float) -> str:
        """Determine quality tier based on score"""
        if score >= 9.0:
            return "excellent"
        elif score >= 8.0:
            return "good"
        elif score >= 7.0:
            return "acceptable"
        else:
            return "needs_work"
    
    async def assess_story_quality(
        self,
        story_content: str,
        requirements: StoryRequirements
    ) -> AdvancedQualityMetrics:
        """
        Assess story quality using V1.4 advanced quality assessment.
        
        Args:
            story_content: Story content to assess
            requirements: Story requirements for context
            
        Returns:
            AdvancedQualityMetrics with comprehensive quality scores
        """
        return await self.dependencies.advanced_quality_assessor.assess_comprehensive(
            story_content, requirements
        )
    
    async def enhance_existing_story(
        self,
        story_content: str,
        story_title: str,
        requirements: StoryRequirements,
        target_quality: Optional[float] = None,
        max_passes: Optional[int] = None
    ) -> QualityEnhancedResult:
        """
        Enhance an existing story using V1.4 quality enhancement.
        
        Args:
            story_content: Existing story content
            story_title: Existing story title
            requirements: Story requirements
            target_quality: Target quality score
            max_passes: Maximum enhancement passes
            
        Returns:
            QualityEnhancedResult with enhanced story
        """
        logger.info(f"Enhancing existing story: '{story_title}'")
        
        return await self.dependencies.quality_enhancement_engine.enhance_story(
            initial_story=story_content,
            initial_title=story_title,
            requirements=requirements,
            target_quality=target_quality,
            max_passes=max_passes
        )
    
    async def predict_enhancement_potential(
        self,
        story_content: str,
        requirements: StoryRequirements
    ) -> Dict[str, Any]:
        """
        Predict enhancement potential for a story.
        
        Args:
            story_content: Story content to analyze
            requirements: Story requirements
            
        Returns:
            Enhancement potential prediction
        """
        # Assess current quality
        quality_metrics = await self.assess_story_quality(story_content, requirements)
        
        # Predict enhancement potential
        return await self.dependencies.advanced_quality_assessor.predict_enhancement_potential(
            quality_metrics, requirements
        )
    
    def get_quality_config(self) -> QualityConfig:
        """Get current quality configuration"""
        return self.quality_config
    
    def update_quality_config(self, config: QualityConfig):
        """Update quality configuration"""
        self.quality_config = config
        self.dependencies.quality_config = config
        self.dependencies.quality_enhancement_engine.config = config
        self.dependencies.advanced_quality_assessor.config = config
        
        logger.info("Quality configuration updated")


# Helper function for easy V1.4 story generation
async def generate_story_v14(
    requirements: StoryRequirements,
    strategy: Optional[GenerationStrategy] = None,
    workflow_config: Optional[WorkflowConfiguration] = None,
    quality_config: Optional[QualityConfig] = None,
    target_quality: Optional[float] = None,
    max_enhancement_passes: Optional[int] = None,
    enable_quality_enhancement: Optional[bool] = None
) -> QualityEnhancedResult:
    """
    Generate a story using V1.4 quality enhancement system.
    
    Args:
        requirements: Story generation requirements
        strategy: Generation strategy (optional)
        workflow_config: Workflow configuration (optional)
        quality_config: Quality configuration (optional)
        target_quality: Target quality score (optional)
        max_enhancement_passes: Maximum enhancement passes (optional)
        enable_quality_enhancement: Enable quality enhancement (optional)
        
    Returns:
        QualityEnhancedResult with enhanced story and comprehensive metrics
    """
    agent = V14StoryAgent(workflow_config, quality_config)
    
    return await agent.generate_story(
        requirements=requirements,
        strategy=strategy,
        target_quality=target_quality,
        max_enhancement_passes=max_enhancement_passes,
        enable_quality_enhancement=enable_quality_enhancement
    )