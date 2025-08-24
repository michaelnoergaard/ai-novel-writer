"""
Quality Enhancement Engine - V1.6 Unified
Multi-pass story enhancement with quality-driven refinement and convergence detection
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from uuid import uuid4

from ..models.basic_models import StoryRequirements
from ..models.story_models import (
    AdvancedQualityMetrics, EnhancementStrategy, QualityDimension,
    EnhancementPass, QualityFeedback, GenerationInsights, ConvergenceMetrics,
    QualityImprovement, QualityEnhancedResult, QualityConfig,
    EnhancedPerformanceMetrics, WorkflowState, WorkflowStage
)
from ..models.enhanced_models import GenerationMetadata, GenerationMethod
from .advanced_quality_assessor import AdvancedQualityAssessor
from ..utils.config import StoryGenerationError

# Setup logging
logger = logging.getLogger(__name__)


class QualityEnhancementEngine:
    """
    Advanced quality enhancement system with multi-pass refinement.
    
    Features:
    - Multi-pass story enhancement with targeted improvements
    - Quality convergence detection to optimize enhancement cycles
    - Strategy selection based on quality dimension analysis
    - Performance optimization and resource tracking
    - Comprehensive quality feedback and insights
    """
    
    def __init__(self, config: QualityConfig):
        """Initialize the quality enhancement engine"""
        self.config = config
        self.quality_assessor = AdvancedQualityAssessor()
        self.enhancement_strategies = self._load_enhancement_strategies()
        self.performance_tracker = EnhancementPerformanceTracker()
        
        logger.info("QualityEnhancementEngine initialized with V1.4 capabilities")
    
    async def enhance_story(
        self,
        initial_story: str,
        initial_title: str,
        requirements: StoryRequirements,
        target_quality: Optional[float] = None,
        max_passes: Optional[int] = None
    ) -> QualityEnhancedResult:
        """
        Perform multi-pass story enhancement with quality convergence detection.
        
        Args:
            initial_story: Initial story content to enhance
            initial_title: Initial story title
            requirements: Story generation requirements
            target_quality: Target quality score (uses config default if None)
            max_passes: Maximum enhancement passes (uses config default if None)
            
        Returns:
            QualityEnhancedResult with enhanced story and comprehensive metrics
        """
        # Use config defaults if not specified
        target_quality = target_quality or self.config.target_quality_score
        max_passes = max_passes or self.config.max_enhancement_passes
        
        # Initialize tracking
        generation_id = str(uuid4())
        start_time = time.time()
        
        logger.info(f"Starting quality enhancement for generation {generation_id}")
        logger.info(f"Target quality: {target_quality}, Max passes: {max_passes}")
        
        # Assess initial quality
        initial_quality = await self.quality_assessor.assess_comprehensive(
            initial_story, requirements
        )
        
        logger.info(f"Initial quality score: {initial_quality.overall_score:.2f}")
        
        # Initialize workflow state with unified model fields
        workflow_state = WorkflowState(
            workflow_id=generation_id,
            stage=WorkflowStage.QUALITY_ASSESSMENT,
            progress=0.0,
            current_step="quality_enhancement_initial",
            steps_completed=["initial_generation", "initial_assessment"],
            steps_remaining=["enhancement_passes", "final_assessment"]
        )
        
        # Check if already meets target
        if initial_quality.overall_score >= target_quality:
            logger.info("Initial story already meets target quality - skipping enhancement")
            return await self._build_final_result(
                content=initial_story,
                title=initial_title,
                requirements=requirements,
                enhancement_passes=[],
                final_quality=initial_quality,
                workflow_state=workflow_state,
                generation_id=generation_id,
                start_time=start_time
            )
        
        # Perform enhancement passes
        enhancement_passes = []
        current_content = initial_story
        current_title = initial_title
        convergence_metrics = ConvergenceMetrics()
        
        for pass_num in range(1, max_passes + 1):
            logger.info(f"Starting enhancement pass {pass_num}/{max_passes}")
            
            # Update workflow state
            workflow_state.progress = pass_num / max_passes
            workflow_state.current_step = f"enhancement_pass_{pass_num}"
            
            # Assess current quality
            current_quality = await self.quality_assessor.assess_comprehensive(
                current_content, requirements
            )
            
            # Check if target quality achieved
            if current_quality.overall_score >= target_quality:
                logger.info(f"Target quality achieved in pass {pass_num}")
                break
            
            # Determine enhancement strategy
            strategy = self._select_enhancement_strategy(current_quality, requirements)
            logger.info(f"Selected enhancement strategy: {strategy}")
            
            # Apply enhancement
            pass_start_time = time.time()
            enhanced_content, enhanced_title, improvements = await self._apply_enhancement(
                current_content, current_title, requirements, strategy, current_quality
            )
            pass_duration = time.time() - pass_start_time
            
            # Assess enhanced quality
            enhanced_quality = await self.quality_assessor.assess_comprehensive(
                enhanced_content, requirements
            )
            
            # Record enhancement pass
            enhancement_pass = EnhancementPass(
                pass_number=pass_num,
                strategy_used=strategy,
                quality_before=current_quality,
                quality_after=enhanced_quality,
                improvements_made=improvements,
                focus_dimensions=self._get_focus_dimensions(strategy),
                time_taken=pass_duration,
                token_usage=self._estimate_token_usage(current_content, enhanced_content),
                quality_improvement=enhanced_quality.overall_score - current_quality.overall_score,
                dimension_improvements=self._calculate_dimension_improvements(
                    current_quality, enhanced_quality
                )
            )
            
            enhancement_passes.append(enhancement_pass)
            
            # Update convergence tracking
            convergence_metrics = self._update_convergence_metrics(
                convergence_metrics, enhancement_passes
            )
            
            # Check for convergence
            if self._detect_quality_convergence(enhancement_passes, convergence_metrics):
                logger.info(f"Quality convergence detected at pass {pass_num}")
                convergence_metrics.convergence_detected = True
                convergence_metrics.convergence_pass = pass_num
                break
            
            # Update for next iteration
            current_content = enhanced_content
            current_title = enhanced_title
            
            logger.info(f"Pass {pass_num} completed. Quality: {current_quality.overall_score:.2f} → {enhanced_quality.overall_score:.2f}")
        
        # Final quality assessment
        final_quality = await self.quality_assessor.assess_comprehensive(
            current_content, requirements
        )
        
        # Build comprehensive result
        return await self._build_final_result(
            content=current_content,
            title=current_title,
            requirements=requirements,
            enhancement_passes=enhancement_passes,
            final_quality=final_quality,
            workflow_state=workflow_state,
            generation_id=generation_id,
            start_time=start_time,
            convergence_metrics=convergence_metrics
        )
    
    def _select_enhancement_strategy(
        self,
        quality_metrics: AdvancedQualityMetrics,
        requirements: StoryRequirements
    ) -> EnhancementStrategy:
        """
        Select the most appropriate enhancement strategy based on quality analysis.
        
        Args:
            quality_metrics: Current quality metrics
            requirements: Story requirements for context
            
        Returns:
            Selected enhancement strategy
        """
        # Get weakest dimensions
        weak_dimensions = quality_metrics.get_weakest_dimensions(threshold=7.0)
        
        if not weak_dimensions:
            return EnhancementStrategy.COMPREHENSIVE
        
        # Strategy selection logic based on weakest dimensions
        strategy_priorities = {
            QualityDimension.STRUCTURE: EnhancementStrategy.STRUCTURE_FOCUS,
            QualityDimension.CHARACTER_DEVELOPMENT: EnhancementStrategy.CHARACTER_FOCUS,
            QualityDimension.PACING_QUALITY: EnhancementStrategy.PACING_FOCUS,
            QualityDimension.COHERENCE: EnhancementStrategy.COHERENCE_FOCUS,
            QualityDimension.GENRE_COMPLIANCE: EnhancementStrategy.GENRE_FOCUS,
            QualityDimension.DIALOGUE_QUALITY: EnhancementStrategy.DIALOGUE_FOCUS,
            QualityDimension.SETTING_IMMERSION: EnhancementStrategy.SETTING_FOCUS,
            QualityDimension.EMOTIONAL_IMPACT: EnhancementStrategy.EMOTIONAL_FOCUS,
            QualityDimension.TECHNICAL_QUALITY: EnhancementStrategy.TECHNICAL_FOCUS,
        }
        
        # Find the weakest dimension with highest priority
        dimension_scores = {
            QualityDimension.STRUCTURE: quality_metrics.structure_score,
            QualityDimension.CHARACTER_DEVELOPMENT: quality_metrics.character_development,
            QualityDimension.PACING_QUALITY: quality_metrics.pacing_quality,
            QualityDimension.COHERENCE: quality_metrics.coherence_score,
            QualityDimension.GENRE_COMPLIANCE: quality_metrics.genre_compliance,
            QualityDimension.DIALOGUE_QUALITY: quality_metrics.dialogue_quality,
            QualityDimension.SETTING_IMMERSION: quality_metrics.setting_immersion,
            QualityDimension.EMOTIONAL_IMPACT: quality_metrics.emotional_impact,
            QualityDimension.TECHNICAL_QUALITY: quality_metrics.technical_quality,
        }
        
        # Get strategy weights from config
        weights = self.config.enhancement_strategy_weights
        
        # Calculate weighted priority for each weak dimension
        weighted_priorities = {}
        for dimension in weak_dimensions:
            if dimension in strategy_priorities:
                strategy = strategy_priorities[dimension]
                weight_key = f"{strategy.replace('_focus', '_weight')}"
                weight = weights.get(weight_key, 1.0)
                score = dimension_scores[dimension]
                # Lower score and higher weight = higher priority
                weighted_priorities[dimension] = (10.0 - score) * weight
        
        if weighted_priorities:
            # Select dimension with highest weighted priority
            target_dimension = max(weighted_priorities.items(), key=lambda x: x[1])[0]
            return strategy_priorities[target_dimension]
        
        return EnhancementStrategy.COMPREHENSIVE
    
    async def _apply_enhancement(
        self,
        content: str,
        title: str,
        requirements: StoryRequirements,
        strategy: EnhancementStrategy,
        quality_metrics: AdvancedQualityMetrics
    ) -> Tuple[str, str, List[str]]:
        """
        Apply the selected enhancement strategy to improve the story.
        
        Args:
            content: Current story content
            title: Current story title
            requirements: Story requirements
            strategy: Enhancement strategy to apply
            quality_metrics: Current quality metrics
            
        Returns:
            Tuple of (enhanced_content, enhanced_title, improvements_made)
        """
        # Build enhancement prompt based on strategy
        enhancement_prompt = self._build_enhancement_prompt(
            content, title, requirements, strategy, quality_metrics
        )
        
        # Apply enhancement using the quality assessor's enhancement capabilities
        enhanced_result = await self.quality_assessor.apply_targeted_enhancement(
            content, title, requirements, strategy, enhancement_prompt
        )
        
        # Extract improvements made
        improvements = self._extract_improvements_made(
            content, enhanced_result['content'], strategy
        )
        
        return enhanced_result['content'], enhanced_result['title'], improvements
    
    def _build_enhancement_prompt(
        self,
        content: str,
        title: str,
        requirements: StoryRequirements,
        strategy: EnhancementStrategy,
        quality_metrics: AdvancedQualityMetrics
    ) -> str:
        """Build targeted enhancement prompt based on strategy and quality analysis"""
        
        base_prompt = f"""Enhance this {requirements.get_display_genre()} story based on the specified strategy.

CRITICAL WORD COUNT REQUIREMENT: You MUST maintain exactly {requirements.target_word_count} words. This is a firm requirement.

Original Title: {title}

Original Story:
{content}

Enhancement Strategy: {strategy.replace('_', ' ').title()}
Current Overall Quality Score: {quality_metrics.overall_score:.1f}/10"""
        
        # Add strategy-specific guidance
        strategy_guidance = {
            EnhancementStrategy.STRUCTURE_FOCUS: f"""
Focus on improving narrative structure:
- Current structure score: {quality_metrics.structure_score:.1f}/10
- Strengthen the story arc and pacing
- Improve transitions between scenes
- Enhance opening, climax, and resolution
- Ensure clear cause-and-effect progression""",
            
            EnhancementStrategy.CHARACTER_FOCUS: f"""
Focus on enhancing character development:
- Current character score: {quality_metrics.character_development:.1f}/10
- Deepen character motivations and personalities
- Add character growth and development arcs
- Improve character dialogue and voice
- Strengthen character relationships and interactions""",
            
            EnhancementStrategy.DIALOGUE_FOCUS: f"""
Focus on improving dialogue quality:
- Current dialogue score: {quality_metrics.dialogue_quality:.1f}/10
- Make dialogue more natural and authentic
- Ensure each character has a distinct voice
- Use dialogue to advance plot and reveal character
- Balance dialogue with narrative description""",
            
            EnhancementStrategy.SETTING_FOCUS: f"""
Focus on enhancing setting immersion:
- Current setting score: {quality_metrics.setting_immersion:.1f}/10
- Create more vivid and immersive descriptions
- Integrate setting with mood and atmosphere
- Use setting to support theme and genre
- Balance description with action and dialogue""",
            
            EnhancementStrategy.EMOTIONAL_FOCUS: f"""
Focus on increasing emotional impact:
- Current emotional score: {quality_metrics.emotional_impact:.1f}/10
- Heighten emotional resonance and engagement
- Develop emotional stakes for characters
- Use sensory details to evoke emotions
- Create moments of genuine emotional connection""",
            
            EnhancementStrategy.PACING_FOCUS: f"""
Focus on optimizing story pacing:
- Current pacing score: {quality_metrics.pacing_quality:.1f}/10
- Improve rhythm and tension management
- Balance action with reflection
- Optimize scene length and transitions
- Build tension effectively toward climax""",
            
            EnhancementStrategy.COHERENCE_FOCUS: f"""
Focus on improving logical coherence:
- Current coherence score: {quality_metrics.coherence_score:.1f}/10
- Eliminate plot holes and inconsistencies
- Improve logical flow between events
- Strengthen cause-and-effect relationships
- Ensure character actions are well-motivated""",
            
            EnhancementStrategy.GENRE_FOCUS: f"""
Focus on strengthening genre conventions:
- Current genre compliance: {quality_metrics.genre_compliance:.1f}/10
- Better adhere to {requirements.get_display_genre()} conventions
- Enhance genre-specific elements and tropes
- Meet reader expectations for the genre
- Balance innovation with genre requirements""",
            
            EnhancementStrategy.TECHNICAL_FOCUS: f"""
Focus on improving technical quality:
- Current technical score: {quality_metrics.technical_quality:.1f}/10
- Enhance prose style and word choice
- Improve sentence structure and variety
- Eliminate grammatical errors and awkward phrasing
- Polish overall writing quality""",
            
            EnhancementStrategy.COMPREHENSIVE: f"""
Comprehensive enhancement across all quality dimensions:
- Focus on the weakest areas while maintaining strengths
- Balance improvements across structure, character, dialogue, and setting
- Enhance overall storytelling effectiveness
- Maintain genre conventions and thematic coherence"""
        }
        
        guidance = strategy_guidance.get(strategy, strategy_guidance[EnhancementStrategy.COMPREHENSIVE])
        
        return base_prompt + guidance + f"""

Provide the enhanced story in this format:
**Title:** [Enhanced title if needed, otherwise keep original]

[Enhanced story content - exactly {requirements.target_word_count} words]"""
    
    def _get_focus_dimensions(self, strategy: EnhancementStrategy) -> List[QualityDimension]:
        """Get the quality dimensions that a strategy focuses on"""
        focus_map = {
            EnhancementStrategy.STRUCTURE_FOCUS: [QualityDimension.STRUCTURE],
            EnhancementStrategy.CHARACTER_FOCUS: [QualityDimension.CHARACTER_DEVELOPMENT],
            EnhancementStrategy.DIALOGUE_FOCUS: [QualityDimension.DIALOGUE_QUALITY],
            EnhancementStrategy.SETTING_FOCUS: [QualityDimension.SETTING_IMMERSION],
            EnhancementStrategy.EMOTIONAL_FOCUS: [QualityDimension.EMOTIONAL_IMPACT],
            EnhancementStrategy.PACING_FOCUS: [QualityDimension.PACING_QUALITY],
            EnhancementStrategy.COHERENCE_FOCUS: [QualityDimension.COHERENCE],
            EnhancementStrategy.GENRE_FOCUS: [QualityDimension.GENRE_COMPLIANCE],
            EnhancementStrategy.TECHNICAL_FOCUS: [QualityDimension.TECHNICAL_QUALITY],
            EnhancementStrategy.COMPREHENSIVE: [
                QualityDimension.STRUCTURE, QualityDimension.CHARACTER_DEVELOPMENT,
                QualityDimension.COHERENCE, QualityDimension.PACING_QUALITY
            ]
        }
        return focus_map.get(strategy, [])
    
    def _calculate_dimension_improvements(
        self,
        before: AdvancedQualityMetrics,
        after: AdvancedQualityMetrics
    ) -> Dict[str, float]:
        """Calculate improvement in each quality dimension"""
        improvements = {}
        
        dimension_pairs = [
            ("structure", before.structure_score, after.structure_score),
            ("coherence", before.coherence_score, after.coherence_score),
            ("character_development", before.character_development, after.character_development),
            ("genre_compliance", before.genre_compliance, after.genre_compliance),
            ("pacing_quality", before.pacing_quality, after.pacing_quality),
            ("theme_integration", before.theme_integration, after.theme_integration),
            ("dialogue_quality", before.dialogue_quality, after.dialogue_quality),
            ("setting_immersion", before.setting_immersion, after.setting_immersion),
            ("emotional_impact", before.emotional_impact, after.emotional_impact),
            ("originality_score", before.originality_score, after.originality_score),
            ("technical_quality", before.technical_quality, after.technical_quality),
        ]
        
        for dimension, before_score, after_score in dimension_pairs:
            improvements[dimension] = after_score - before_score
            
        return improvements
    
    def _extract_improvements_made(
        self,
        original_content: str,
        enhanced_content: str,
        strategy: EnhancementStrategy
    ) -> List[str]:
        """Extract specific improvements made during enhancement"""
        improvements = []
        
        # Basic comparison metrics
        original_words = len(original_content.split())
        enhanced_words = len(enhanced_content.split())
        
        # Strategy-specific improvement detection
        if strategy == EnhancementStrategy.DIALOGUE_FOCUS:
            original_quotes = original_content.count('"')
            enhanced_quotes = enhanced_content.count('"')
            if enhanced_quotes > original_quotes:
                improvements.append("Added dialogue to improve character interaction")
        
        elif strategy == EnhancementStrategy.SETTING_FOCUS:
            # Look for descriptive improvements (rough heuristic)
            descriptive_words = ['vivid', 'atmospheric', 'immersive', 'detailed']
            for word in descriptive_words:
                if word in enhanced_content.lower() and word not in original_content.lower():
                    improvements.append(f"Enhanced setting description with {word} details")
        
        elif strategy == EnhancementStrategy.CHARACTER_FOCUS:
            # Character-related improvements
            improvements.append("Enhanced character development and motivations")
        
        elif strategy == EnhancementStrategy.STRUCTURE_FOCUS:
            improvements.append("Improved narrative structure and flow")
        
        # General improvements
        if abs(enhanced_words - original_words) < 50:  # Word count maintained
            improvements.append("Maintained target word count while enhancing quality")
        
        if not improvements:
            improvements.append(f"Applied {strategy.replace('_', ' ')} enhancement")
        
        return improvements
    
    def _estimate_token_usage(self, original: str, enhanced: str) -> int:
        """Estimate token usage for enhancement (rough approximation)"""
        # Rough estimate: 1 token per 4 characters
        original_tokens = len(original) // 4
        enhanced_tokens = len(enhanced) // 4
        # Enhancement typically requires input + output + processing overhead
        return original_tokens + enhanced_tokens + 500  # Processing overhead
    
    def _update_convergence_metrics(
        self,
        convergence: ConvergenceMetrics,
        enhancement_passes: List[EnhancementPass]
    ) -> ConvergenceMetrics:
        """Update convergence tracking metrics"""
        if len(enhancement_passes) < 2:
            return convergence
        
        # Calculate improvement velocity
        recent_improvements = [
            pass_obj.quality_improvement for pass_obj in enhancement_passes[-2:]
        ]
        convergence.improvement_velocity.extend(recent_improvements)
        
        # Check for diminishing returns
        if len(recent_improvements) >= 2:
            latest_improvement = recent_improvements[-1]
            previous_improvement = recent_improvements[-2]
            
            if latest_improvement < previous_improvement * 0.5:  # 50% reduction
                convergence.diminishing_returns_detected = True
        
        return convergence
    
    def _detect_quality_convergence(
        self,
        enhancement_passes: List[EnhancementPass],
        convergence_metrics: ConvergenceMetrics
    ) -> bool:
        """Detect if quality improvement has converged"""
        if len(enhancement_passes) < 2:
            return False
        
        # Check if improvement is below threshold
        latest_improvement = enhancement_passes[-1].quality_improvement
        if latest_improvement < self.config.quality_convergence_threshold:
            return True
        
        # Check for diminishing returns
        if convergence_metrics.diminishing_returns_detected:
            return True
        
        # Check for quality plateau (last 2 passes show minimal improvement)
        if len(enhancement_passes) >= 2:
            last_two_improvements = [
                pass_obj.quality_improvement for pass_obj in enhancement_passes[-2:]
            ]
            if all(improvement < self.config.quality_convergence_threshold for improvement in last_two_improvements):
                return True
        
        return False
    
    async def _build_final_result(
        self,
        content: str,
        title: str,
        requirements: StoryRequirements,
        enhancement_passes: List[EnhancementPass],
        final_quality: AdvancedQualityMetrics,
        workflow_state: WorkflowState,
        generation_id: str,
        start_time: float,
        convergence_metrics: Optional[ConvergenceMetrics] = None
    ) -> QualityEnhancedResult:
        """Build the comprehensive final result"""
        
        total_time = time.time() - start_time
        
        # Calculate performance metrics
        total_enhancement_tokens = sum(pass_obj.token_usage for pass_obj in enhancement_passes)
        total_assessment_time = sum(pass_obj.quality_after.assessment_duration for pass_obj in enhancement_passes)
        
        performance_metrics = EnhancedPerformanceMetrics(
            total_generation_time=total_time,
            initial_generation_time=0.0,  # Would need to track from caller
            enhancement_time=sum(pass_obj.time_taken for pass_obj in enhancement_passes),
            quality_assessment_time=total_assessment_time,
            total_tokens_used=3000 + total_enhancement_tokens,  # Estimate initial + enhancement
            initial_generation_tokens=3000,  # Estimate for initial generation
            enhancement_tokens=total_enhancement_tokens,
            assessment_tokens=500,  # Estimate for assessments
            pass_timings=[pass_obj.time_taken for pass_obj in enhancement_passes],
            pass_token_usage=[pass_obj.token_usage for pass_obj in enhancement_passes],
            quality_per_second=final_quality.overall_score / total_time if total_time > 0 else 0.0,
            quality_per_token=final_quality.overall_score / max(1, 3000 + total_enhancement_tokens),
            cache_hits=0,  # Would be tracked by cache system
            cache_misses=0,
            cache_hit_rate=0.0
        )
        
        # Generate quality feedback
        quality_feedback = await self._generate_quality_feedback(
            final_quality, enhancement_passes, requirements
        )
        
        # Generate insights
        generation_insights = self._generate_generation_insights(
            enhancement_passes, final_quality, performance_metrics
        )
        
        # Create generation metadata with required fields
        generation_metadata = GenerationMetadata(
            generation_method=GenerationMethod.AUTO,  # Using AUTO for quality enhancement 
            generation_time=total_time,
            tools_used=["quality_assessor", "story_enhancer"],
            outline_generated=False,  # Quality enhancement doesn't generate outlines
            retry_count=0
        )
        
        # Determine quality tier
        quality_tier = self._determine_quality_tier(final_quality.overall_score)
        
        # Create cache utilization report (placeholder)
        cache_utilization = self._create_cache_report()
        
        return QualityEnhancedResult(
            title=title,
            content=content,
            word_count=len(content.split()),
            genre=requirements.genre,
            quality_metrics=final_quality,
            enhancement_history=enhancement_passes,
            quality_feedback=quality_feedback,
            generation_insights=generation_insights,
            convergence_metrics=convergence_metrics or ConvergenceMetrics(),
            workflow_state=workflow_state,
            performance_metrics=performance_metrics,
            cache_utilization=cache_utilization,
            requirements=requirements,
            generation_metadata=generation_metadata,
            target_quality_achieved=final_quality.overall_score >= (target_quality or self.config.target_quality_score),
            enhancement_successful=len(enhancement_passes) > 0,
            quality_tier=quality_tier
        )
    
    async def _generate_quality_feedback(
        self,
        quality_metrics: AdvancedQualityMetrics,
        enhancement_passes: List[EnhancementPass],
        requirements: StoryRequirements
    ) -> QualityFeedback:
        """Generate comprehensive quality feedback for the user"""
        
        # Determine overall assessment
        if quality_metrics.overall_score >= 9.0:
            overall_assessment = "Exceptional quality story with outstanding execution across all dimensions."
        elif quality_metrics.overall_score >= 8.0:
            overall_assessment = "High quality story with strong execution and engaging narrative."
        elif quality_metrics.overall_score >= 7.0:
            overall_assessment = "Good quality story with solid fundamentals and room for minor improvements."
        elif quality_metrics.overall_score >= 6.0:
            overall_assessment = "Acceptable quality story with decent execution but noticeable areas for improvement."
        else:
            overall_assessment = "Story shows potential but needs significant improvement in multiple areas."
        
        # Identify strengths
        strengths = []
        dimension_scores = {
            "Structure": quality_metrics.structure_score,
            "Character Development": quality_metrics.character_development,
            "Dialogue": quality_metrics.dialogue_quality,
            "Setting": quality_metrics.setting_immersion,
            "Emotional Impact": quality_metrics.emotional_impact,
            "Technical Quality": quality_metrics.technical_quality,
            "Genre Compliance": quality_metrics.genre_compliance,
            "Coherence": quality_metrics.coherence_score,
            "Pacing": quality_metrics.pacing_quality,
            "Theme Integration": quality_metrics.theme_integration,
            "Originality": quality_metrics.originality_score
        }
        
        for dimension, score in dimension_scores.items():
            if score >= 8.5:
                strengths.append(f"Excellent {dimension.lower()} ({score:.1f}/10)")
            elif score >= 8.0:
                strengths.append(f"Strong {dimension.lower()} ({score:.1f}/10)")
        
        # Identify areas for improvement
        areas_for_improvement = []
        specific_suggestions = []
        
        for dimension, score in dimension_scores.items():
            if score < 7.0:
                areas_for_improvement.append(f"{dimension} needs enhancement ({score:.1f}/10)")
                
                # Create specific suggestions
                suggestion = QualityImprovement(
                    dimension=getattr(QualityDimension, dimension.upper().replace(" ", "_"), QualityDimension.OVERALL),
                    current_score=score,
                    target_score=8.0,
                    improvement_potential=8.0 - score,
                    suggestion=self._get_improvement_suggestion(dimension, score),
                    priority=self._calculate_priority(score),
                    estimated_effort="medium" if score > 5.0 else "high"
                )
                specific_suggestions.append(suggestion)
        
        # Analyze quality trends
        if enhancement_passes:
            initial_score = enhancement_passes[0].quality_before.overall_score
            final_score = quality_metrics.overall_score
            improvement = final_score - initial_score
            
            if improvement > 1.0:
                trend_analysis = f"Excellent improvement trajectory with {improvement:.1f} point gain across {len(enhancement_passes)} passes."
            elif improvement > 0.5:
                trend_analysis = f"Good improvement with {improvement:.1f} point quality gain through enhancement."
            elif improvement > 0.0:
                trend_analysis = f"Modest improvement of {improvement:.1f} points achieved through enhancement."
            else:
                trend_analysis = "Quality remained stable through enhancement process."
        else:
            trend_analysis = "No enhancement passes performed - initial generation quality maintained."
        
        # Determine most effective strategy
        most_effective_strategy = None
        if enhancement_passes:
            strategy_effectiveness = {}
            for pass_obj in enhancement_passes:
                strategy = pass_obj.strategy_used
                improvement = pass_obj.quality_improvement
                if strategy in strategy_effectiveness:
                    strategy_effectiveness[strategy] = max(strategy_effectiveness[strategy], improvement)
                else:
                    strategy_effectiveness[strategy] = improvement
            
            if strategy_effectiveness:
                # Get the strategy with highest improvement
                best_strategy, _ = max(strategy_effectiveness.items(), key=lambda x: x[1])
                most_effective_strategy = best_strategy
        
        return QualityFeedback(
            overall_assessment=overall_assessment,
            overall_score=quality_metrics.overall_score,
            strengths=strengths,
            areas_for_improvement=areas_for_improvement,
            specific_suggestions=specific_suggestions,
            quality_trend_analysis=trend_analysis,
            improvement_trajectory="Positive" if enhancement_passes and enhancement_passes[-1].quality_improvement > 0 else "Stable",
            target_achieved=quality_metrics.overall_score >= self.config.target_quality_score,
            quality_tier=self._determine_quality_tier(quality_metrics.overall_score),
            enhancement_summary=f"Completed {len(enhancement_passes)} enhancement passes with {quality_metrics.overall_score:.1f}/10 final score",
            most_effective_strategy=most_effective_strategy
        )
    
    def _get_improvement_suggestion(self, dimension: str, score: float) -> str:
        """Get specific improvement suggestion for a dimension"""
        suggestions = {
            "Structure": "Focus on strengthening the story arc with clearer beginning, middle, and end",
            "Character Development": "Develop character motivations and growth arcs more deeply",
            "Dialogue": "Make dialogue more natural and character-specific",
            "Setting": "Add more immersive sensory details and atmospheric descriptions",
            "Emotional Impact": "Enhance emotional stakes and reader connection to characters",
            "Technical Quality": "Improve prose style, word choice, and sentence variety",
            "Genre Compliance": f"Better incorporate {self.config} genre conventions and expectations",
            "Coherence": "Strengthen logical flow and eliminate plot inconsistencies",
            "Pacing": "Optimize story rhythm and tension building",
            "Theme Integration": "Weave themes more naturally into the narrative",
            "Originality": "Add more unique and creative elements to stand out"
        }
        
        return suggestions.get(dimension, "Focus on improving this aspect of the story")
    
    def _calculate_priority(self, score: float) -> int:
        """Calculate improvement priority based on score"""
        if score < 5.0:
            return 1  # Highest priority
        elif score < 6.5:
            return 2  # High priority
        elif score < 7.5:
            return 3  # Medium priority
        elif score < 8.5:
            return 4  # Low priority
        else:
            return 5  # Lowest priority
    
    def _generate_generation_insights(
        self,
        enhancement_passes: List[EnhancementPass],
        final_quality: AdvancedQualityMetrics,
        performance_metrics: EnhancedPerformanceMetrics
    ) -> GenerationInsights:
        """Generate insights about the generation process"""
        
        # Calculate strategy effectiveness
        strategy_effectiveness = {}
        if enhancement_passes:
            for pass_obj in enhancement_passes:
                strategy = pass_obj.strategy_used
                improvement = pass_obj.quality_improvement
                if strategy in strategy_effectiveness:
                    strategy_effectiveness[strategy] = max(strategy_effectiveness[strategy], improvement)
                else:
                    strategy_effectiveness[strategy] = improvement
        
        # Determine optimal strategy sequence
        optimal_sequence = [pass_obj.strategy_used for pass_obj in enhancement_passes] if enhancement_passes else []
        
        # Calculate convergence point
        quality_convergence_point = None
        diminishing_returns_point = None
        
        if len(enhancement_passes) >= 2:
            for i, pass_obj in enumerate(enhancement_passes[1:], 1):
                if pass_obj.quality_improvement < self.config.quality_convergence_threshold:
                    quality_convergence_point = i
                    break
                    
                if i > 1 and pass_obj.quality_improvement < enhancement_passes[i-2].quality_improvement * 0.5:
                    diminishing_returns_point = i
        
        # Calculate efficiency metrics
        total_time = performance_metrics.total_generation_time
        total_tokens = performance_metrics.total_tokens_used
        
        resource_efficiency = final_quality.overall_score / (total_time + total_tokens / 1000) if (total_time + total_tokens / 1000) > 0 else 0.0
        time_efficiency = final_quality.overall_score / total_time if total_time > 0 else 0.0
        token_efficiency = final_quality.overall_score / max(1, total_tokens)
        
        return GenerationInsights(
            strategy_effectiveness=strategy_effectiveness,
            optimal_strategy_sequence=optimal_sequence,
            quality_convergence_point=quality_convergence_point,
            optimal_pass_count=len(enhancement_passes),
            diminishing_returns_point=diminishing_returns_point,
            resource_efficiency=min(1.0, resource_efficiency),  # Cap at 1.0
            time_efficiency=time_efficiency,
            token_efficiency=token_efficiency,
            cache_hit_rate=performance_metrics.cache_hit_rate,
            optimization_opportunities=self._identify_optimization_opportunities(enhancement_passes, performance_metrics),
            quality_prediction_accuracy=None,  # Would need prediction baseline
            enhancement_prediction_accuracy=None
        )
    
    def _identify_optimization_opportunities(
        self,
        enhancement_passes: List[EnhancementPass],
        performance_metrics: EnhancedPerformanceMetrics
    ) -> List[str]:
        """Identify opportunities for optimization"""
        opportunities = []
        
        if len(enhancement_passes) > 3:
            opportunities.append("Consider reducing maximum passes - diminishing returns detected")
        
        if performance_metrics.total_tokens_used > 10000:
            opportunities.append("High token usage - consider more targeted enhancement strategies")
        
        if performance_metrics.cache_hit_rate < 0.3:
            opportunities.append("Low cache utilization - enable caching for similar requests")
        
        if performance_metrics.total_generation_time > 300:  # 5 minutes
            opportunities.append("Long generation time - consider parallel processing optimization")
        
        return opportunities
    
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
    
    def _create_cache_report(self) -> "CacheUtilizationReport":
        """Create cache utilization report (placeholder for now)"""
        from ..models.story_models import CacheUtilizationReport
        
        return CacheUtilizationReport(
            cache_enabled=self.config.enable_generation_caching,
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
    
    def _load_enhancement_strategies(self) -> Dict[EnhancementStrategy, Dict[str, Any]]:
        """Load enhancement strategy configurations"""
        # This would typically load from configuration files
        # For now, return basic configuration
        return {
            strategy: {"weight": 1.0, "enabled": True} 
            for strategy in EnhancementStrategy
        }


class EnhancementPerformanceTracker:
    """Track performance metrics during enhancement process"""
    
    def __init__(self):
        self.start_time = None
        self.metrics = {}
    
    def start_tracking(self):
        """Start performance tracking"""
        self.start_time = time.time()
        self.metrics = {
            "passes": [],
            "total_tokens": 0,
            "cache_hits": 0,
            "cache_misses": 0
        }
    
    def record_pass(self, pass_time: float, tokens: int, quality_improvement: float):
        """Record metrics for an enhancement pass"""
        self.metrics["passes"].append({
            "time": pass_time,
            "tokens": tokens,
            "improvement": quality_improvement
        })
        self.metrics["total_tokens"] += tokens
    
    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        total_time = time.time() - self.start_time if self.start_time else 0
        
        return {
            "total_time": total_time,
            "total_passes": len(self.metrics["passes"]),
            "total_tokens": self.metrics["total_tokens"],
            "cache_hit_rate": self.metrics["cache_hits"] / max(1, self.metrics["cache_hits"] + self.metrics["cache_misses"]),
            "avg_pass_time": sum(p["time"] for p in self.metrics["passes"]) / max(1, len(self.metrics["passes"])),
            "avg_tokens_per_pass": self.metrics["total_tokens"] / max(1, len(self.metrics["passes"]))
        }