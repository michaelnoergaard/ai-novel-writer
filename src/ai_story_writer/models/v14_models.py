"""
V1.4 Enhanced Data Models - Quality Enhancement Infrastructure
Advanced quality metrics, multi-pass generation tracking, and enhanced user experience models
"""

import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict

from .basic_models import StoryGenre, StoryLength, StoryRequirements
from .v13_models import QualityMetrics, WorkflowConfiguration


class EnhancementStrategy(str, Enum):
    """Targeted enhancement strategies for quality improvement"""
    STRUCTURE_FOCUS = "structure_focus"      # Improve narrative structure
    CHARACTER_FOCUS = "character_focus"      # Enhance character development  
    PACING_FOCUS = "pacing_focus"           # Optimize story pacing
    COHERENCE_FOCUS = "coherence_focus"     # Improve logical flow
    GENRE_FOCUS = "genre_focus"             # Strengthen genre conventions
    DIALOGUE_FOCUS = "dialogue_focus"       # Enhance dialogue quality
    SETTING_FOCUS = "setting_focus"         # Improve setting immersion
    EMOTIONAL_FOCUS = "emotional_focus"     # Enhance emotional impact
    TECHNICAL_FOCUS = "technical_focus"     # Improve prose quality
    COMPREHENSIVE = "comprehensive"          # Balanced improvement across all dimensions


class QualityDimension(str, Enum):
    """Individual quality assessment dimensions"""
    STRUCTURE = "structure"
    COHERENCE = "coherence"
    CHARACTER_DEVELOPMENT = "character_development"
    GENRE_COMPLIANCE = "genre_compliance"
    PACING_QUALITY = "pacing_quality"
    THEME_INTEGRATION = "theme_integration"
    DIALOGUE_QUALITY = "dialogue_quality"
    SETTING_IMMERSION = "setting_immersion"
    EMOTIONAL_IMPACT = "emotional_impact"
    ORIGINALITY_SCORE = "originality_score"
    TECHNICAL_QUALITY = "technical_quality"
    OVERALL = "overall"


class AdvancedQualityMetrics(BaseModel):
    """Enhanced quality metrics with 12-dimensional assessment"""
    
    # Core V1.3 metrics (enhanced)
    overall_score: float = Field(ge=0.0, le=10.0, description="Overall quality score")
    structure_score: float = Field(ge=0.0, le=10.0, description="Narrative arc assessment")
    coherence_score: float = Field(ge=0.0, le=10.0, description="Logical consistency")
    genre_compliance: float = Field(ge=0.0, le=10.0, description="Genre convention adherence")
    character_development: float = Field(ge=0.0, le=10.0, description="Character depth and consistency")
    pacing_quality: float = Field(ge=0.0, le=10.0, description="Story rhythm and tension")
    theme_integration: float = Field(ge=0.0, le=10.0, description="Theme incorporation")
    
    # V1.4 enhancements - new quality dimensions
    dialogue_quality: float = Field(ge=0.0, le=10.0, description="Dialogue naturalness and effectiveness")
    setting_immersion: float = Field(ge=0.0, le=10.0, description="Setting description and atmosphere")
    emotional_impact: float = Field(ge=0.0, le=10.0, description="Emotional resonance and engagement")
    originality_score: float = Field(ge=0.0, le=10.0, description="Creative uniqueness and freshness")
    technical_quality: float = Field(ge=0.0, le=10.0, description="Grammar, style, and prose quality")
    
    # Quality trend analysis
    improvement_trend: List[float] = Field(default_factory=list, description="Quality scores across iterations")
    enhancement_effectiveness: Dict[str, float] = Field(default_factory=dict, description="Effectiveness of each enhancement type")
    
    # Metadata
    assessment_timestamp: datetime = Field(default_factory=datetime.now)
    assessment_duration: float = Field(default=0.0, description="Time taken for assessment in seconds")
    
    model_config = ConfigDict(use_enum_values=True)
    
    def get_weakest_dimensions(self, threshold: float = 7.0) -> List[QualityDimension]:
        """Get quality dimensions that fall below the threshold"""
        weak_dimensions = []
        dimension_scores = {
            QualityDimension.STRUCTURE: self.structure_score,
            QualityDimension.COHERENCE: self.coherence_score,
            QualityDimension.CHARACTER_DEVELOPMENT: self.character_development,
            QualityDimension.GENRE_COMPLIANCE: self.genre_compliance,
            QualityDimension.PACING_QUALITY: self.pacing_quality,
            QualityDimension.THEME_INTEGRATION: self.theme_integration,
            QualityDimension.DIALOGUE_QUALITY: self.dialogue_quality,
            QualityDimension.SETTING_IMMERSION: self.setting_immersion,
            QualityDimension.EMOTIONAL_IMPACT: self.emotional_impact,
            QualityDimension.ORIGINALITY_SCORE: self.originality_score,
            QualityDimension.TECHNICAL_QUALITY: self.technical_quality,
        }
        
        for dimension, score in dimension_scores.items():
            if score < threshold:
                weak_dimensions.append(dimension)
        
        return weak_dimensions
    
    def calculate_improvement_potential(self, target_score: float = 8.0) -> Dict[QualityDimension, float]:
        """Calculate improvement potential for each dimension"""
        potential = {}
        dimension_scores = {
            QualityDimension.STRUCTURE: self.structure_score,
            QualityDimension.COHERENCE: self.coherence_score,
            QualityDimension.CHARACTER_DEVELOPMENT: self.character_development,
            QualityDimension.GENRE_COMPLIANCE: self.genre_compliance,
            QualityDimension.PACING_QUALITY: self.pacing_quality,
            QualityDimension.THEME_INTEGRATION: self.theme_integration,
            QualityDimension.DIALOGUE_QUALITY: self.dialogue_quality,
            QualityDimension.SETTING_IMMERSION: self.setting_immersion,
            QualityDimension.EMOTIONAL_IMPACT: self.emotional_impact,
            QualityDimension.ORIGINALITY_SCORE: self.originality_score,
            QualityDimension.TECHNICAL_QUALITY: self.technical_quality,
        }
        
        for dimension, score in dimension_scores.items():
            if score < target_score:
                potential[dimension] = target_score - score
            else:
                potential[dimension] = 0.0
                
        return potential


class ConvergenceMetrics(BaseModel):
    """Quality improvement convergence analysis"""
    convergence_detected: bool = Field(default=False, description="Whether quality convergence was detected")
    convergence_pass: Optional[int] = Field(default=None, description="Pass number where convergence occurred")
    quality_plateau_threshold: float = Field(default=0.1, description="Threshold for detecting quality plateau")
    improvement_velocity: List[float] = Field(default_factory=list, description="Quality improvement rate per pass")
    diminishing_returns_detected: bool = Field(default=False, description="Whether diminishing returns were detected")
    optimal_pass_prediction: Optional[int] = Field(default=None, description="Predicted optimal number of passes")


class QualityImprovement(BaseModel):
    """Specific quality improvement suggestion"""
    dimension: QualityDimension = Field(description="Quality dimension to improve")
    current_score: float = Field(ge=0.0, le=10.0, description="Current score for this dimension")
    target_score: float = Field(ge=0.0, le=10.0, description="Target score for this dimension")
    improvement_potential: float = Field(ge=0.0, description="Potential improvement points")
    suggestion: str = Field(description="Specific improvement suggestion")
    priority: int = Field(ge=1, le=5, description="Priority level (1=highest, 5=lowest)")
    estimated_effort: str = Field(description="Estimated effort level (low/medium/high)")


class EnhancementPass(BaseModel):
    """Detailed tracking of each enhancement pass"""
    pass_number: int = Field(ge=1, description="Enhancement pass number")
    strategy_used: EnhancementStrategy = Field(description="Enhancement strategy applied")
    
    # Quality metrics before and after
    quality_before: AdvancedQualityMetrics = Field(description="Quality metrics before enhancement")
    quality_after: AdvancedQualityMetrics = Field(description="Quality metrics after enhancement")
    
    # Enhancement details
    improvements_made: List[str] = Field(default_factory=list, description="Specific improvements made")
    focus_dimensions: List[QualityDimension] = Field(default_factory=list, description="Dimensions targeted for improvement")
    
    # Performance metrics
    time_taken: float = Field(ge=0.0, description="Time taken for this pass in seconds")
    token_usage: int = Field(ge=0, description="Tokens used for this enhancement pass")
    
    # Effectiveness metrics
    quality_improvement: float = Field(description="Overall quality improvement achieved")
    dimension_improvements: Dict[str, float] = Field(default_factory=dict, description="Improvement per dimension")
    
    # Metadata
    timestamp: datetime = Field(default_factory=datetime.now)
    enhancement_prompt_used: Optional[str] = Field(default=None, description="Enhancement prompt used")
    
    model_config = ConfigDict(use_enum_values=True)


class QualityFeedback(BaseModel):
    """Comprehensive quality feedback for users"""
    overall_assessment: str = Field(description="Overall quality assessment summary")
    overall_score: float = Field(ge=0.0, le=10.0, description="Overall quality score")
    
    # Strengths and weaknesses
    strengths: List[str] = Field(default_factory=list, description="Story strengths identified")
    areas_for_improvement: List[str] = Field(default_factory=list, description="Areas needing improvement")
    
    # Specific suggestions
    specific_suggestions: List[QualityImprovement] = Field(default_factory=list, description="Actionable improvement suggestions")
    
    # Trend analysis
    quality_trend_analysis: str = Field(description="Analysis of quality trends across passes")
    improvement_trajectory: str = Field(description="Trajectory of quality improvements")
    
    # Achievement indicators
    target_achieved: bool = Field(default=False, description="Whether target quality was achieved")
    quality_tier: str = Field(description="Quality tier (excellent/good/acceptable/needs_work)")
    
    # Enhancement insights
    enhancement_summary: str = Field(description="Summary of enhancement process")
    most_effective_strategy: Optional[EnhancementStrategy] = Field(default=None, description="Most effective enhancement strategy used")
    
    model_config = ConfigDict(use_enum_values=True)


class GenerationInsights(BaseModel):
    """Insights about the generation and enhancement process"""
    
    # Strategy effectiveness
    strategy_effectiveness: Dict[str, float] = Field(default_factory=dict, description="Effectiveness of each strategy used")
    optimal_strategy_sequence: List[EnhancementStrategy] = Field(default_factory=list, description="Optimal sequence of strategies")
    
    # Convergence analysis
    quality_convergence_point: Optional[int] = Field(default=None, description="Pass where quality converged")
    optimal_pass_count: int = Field(ge=0, description="Optimal number of enhancement passes")
    diminishing_returns_point: Optional[int] = Field(default=None, description="Pass where diminishing returns began")
    
    # Resource efficiency
    resource_efficiency: float = Field(ge=0.0, le=1.0, description="Resource usage efficiency score")
    time_efficiency: float = Field(ge=0.0, description="Time per quality point improvement")
    token_efficiency: float = Field(ge=0.0, description="Tokens per quality point improvement")
    
    # Caching and optimization
    cache_hit_rate: float = Field(ge=0.0, le=1.0, description="Cache utilization rate")
    optimization_opportunities: List[str] = Field(default_factory=list, description="Identified optimization opportunities")
    
    # Prediction accuracy
    quality_prediction_accuracy: Optional[float] = Field(default=None, description="Accuracy of initial quality prediction")
    enhancement_prediction_accuracy: Optional[float] = Field(default=None, description="Accuracy of enhancement outcome prediction")
    
    model_config = ConfigDict(use_enum_values=True)


class EnhancedPerformanceMetrics(BaseModel):
    """Enhanced performance tracking for V1.4"""
    
    # Core timing metrics
    total_generation_time: float = Field(ge=0.0, description="Total time for complete generation process")
    initial_generation_time: float = Field(ge=0.0, description="Time for initial story generation")
    enhancement_time: float = Field(ge=0.0, description="Total time for all enhancement passes")
    quality_assessment_time: float = Field(ge=0.0, description="Total time for quality assessments")
    
    # Token usage tracking
    total_tokens_used: int = Field(ge=0, description="Total tokens used across all operations")
    initial_generation_tokens: int = Field(ge=0, description="Tokens used for initial generation")
    enhancement_tokens: int = Field(ge=0, description="Tokens used for enhancements")
    assessment_tokens: int = Field(ge=0, description="Tokens used for quality assessments")
    
    # Pass-by-pass metrics
    pass_timings: List[float] = Field(default_factory=list, description="Time taken for each enhancement pass")
    pass_token_usage: List[int] = Field(default_factory=list, description="Tokens used for each enhancement pass")
    
    # Efficiency metrics
    quality_per_second: float = Field(ge=0.0, description="Quality improvement per second")
    quality_per_token: float = Field(ge=0.0, description="Quality improvement per token")
    
    # Resource utilization
    memory_usage_mb: Optional[float] = Field(default=None, description="Peak memory usage in MB")
    cpu_usage_percent: Optional[float] = Field(default=None, description="Average CPU usage percentage")
    
    # Cache metrics
    cache_hits: int = Field(ge=0, description="Number of cache hits")
    cache_misses: int = Field(ge=0, description="Number of cache misses")
    cache_hit_rate: float = Field(ge=0.0, le=1.0, description="Cache hit rate")


class CacheUtilizationReport(BaseModel):
    """Cache utilization and performance report"""
    cache_enabled: bool = Field(description="Whether caching was enabled")
    cache_hits: int = Field(ge=0, description="Number of cache hits")
    cache_misses: int = Field(ge=0, description="Number of cache misses")
    cache_hit_rate: float = Field(ge=0.0, le=1.0, description="Overall cache hit rate")
    
    # Component-specific caching
    outline_cache_hits: int = Field(ge=0, description="Outline cache hits")
    content_cache_hits: int = Field(ge=0, description="Content cache hits")
    assessment_cache_hits: int = Field(ge=0, description="Assessment cache hits")
    
    # Performance impact
    time_saved_seconds: float = Field(ge=0.0, description="Time saved through caching")
    tokens_saved: int = Field(ge=0, description="Tokens saved through caching")
    
    # Cache efficiency
    cache_efficiency_score: float = Field(ge=0.0, le=1.0, description="Overall cache efficiency")
    cache_recommendations: List[str] = Field(default_factory=list, description="Recommendations for improving cache utilization")


class WorkflowState(BaseModel):
    """Enhanced workflow state tracking for V1.4"""
    current_phase: str = Field(description="Current workflow phase")
    completed_phases: List[str] = Field(default_factory=list, description="Completed workflow phases")
    remaining_phases: List[str] = Field(default_factory=list, description="Remaining workflow phases")
    
    # Enhancement-specific state
    current_pass: int = Field(ge=0, description="Current enhancement pass number")
    total_passes_planned: int = Field(ge=1, description="Total enhancement passes planned")
    enhancement_strategy_sequence: List[EnhancementStrategy] = Field(default_factory=list, description="Sequence of enhancement strategies")
    
    # Quality tracking
    target_quality: float = Field(ge=0.0, le=10.0, description="Target quality score")
    current_quality: float = Field(ge=0.0, le=10.0, description="Current quality score")
    quality_achieved: bool = Field(default=False, description="Whether target quality was achieved")
    
    # Progress indicators
    overall_progress: float = Field(ge=0.0, le=1.0, description="Overall progress percentage")
    phase_progress: float = Field(ge=0.0, le=1.0, description="Current phase progress percentage")
    
    # Timestamps
    workflow_start_time: datetime = Field(default_factory=datetime.now)
    current_phase_start_time: datetime = Field(default_factory=datetime.now)
    estimated_completion_time: Optional[datetime] = Field(default=None)
    
    model_config = ConfigDict(use_enum_values=True)


class GenerationMetadata(BaseModel):
    """Enhanced generation metadata for V1.4"""
    
    # Basic metadata
    generation_id: str = Field(description="Unique generation identifier")
    version: str = Field(default="1.4", description="AI Story Writer version")
    generation_timestamp: datetime = Field(default_factory=datetime.now)
    
    # Model and configuration
    model_used: str = Field(description="AI model used for generation")
    configuration_snapshot: Dict[str, Any] = Field(default_factory=dict, description="Configuration used for generation")
    
    # Enhancement metadata
    enhancement_enabled: bool = Field(description="Whether quality enhancement was enabled")
    total_enhancement_passes: int = Field(ge=0, description="Total number of enhancement passes performed")
    strategies_used: List[EnhancementStrategy] = Field(default_factory=list, description="Enhancement strategies used")
    
    # Quality metadata
    initial_quality_score: float = Field(ge=0.0, le=10.0, description="Initial quality score before enhancement")
    final_quality_score: float = Field(ge=0.0, le=10.0, description="Final quality score after enhancement")
    quality_improvement: float = Field(description="Total quality improvement achieved")
    
    # Performance metadata
    total_generation_time: float = Field(ge=0.0, description="Total generation time")
    total_tokens_used: int = Field(ge=0, description="Total tokens used")
    
    # User context
    user_target_quality: Optional[float] = Field(default=None, description="User-specified target quality")
    user_max_passes: Optional[int] = Field(default=None, description="User-specified maximum passes")
    
    model_config = ConfigDict(use_enum_values=True)


class QualityEnhancedResult(BaseModel):
    """Comprehensive result model for V1.4 quality-enhanced generation"""
    
    # Core story content
    title: str = Field(description="Story title")
    content: str = Field(description="Story content")
    word_count: int = Field(ge=0, description="Story word count")
    genre: StoryGenre = Field(description="Story genre")
    
    # V1.4 quality enhancements
    quality_metrics: AdvancedQualityMetrics = Field(description="Comprehensive quality metrics")
    enhancement_history: List[EnhancementPass] = Field(default_factory=list, description="History of enhancement passes")
    quality_feedback: QualityFeedback = Field(description="User-facing quality feedback")
    generation_insights: GenerationInsights = Field(description="Generation process insights")
    convergence_metrics: ConvergenceMetrics = Field(description="Quality convergence analysis")
    
    # Workflow and performance data
    workflow_state: WorkflowState = Field(description="Workflow execution state")
    performance_metrics: EnhancedPerformanceMetrics = Field(description="Performance and resource metrics")
    cache_utilization: CacheUtilizationReport = Field(description="Cache utilization report")
    
    # Original requirements and metadata
    requirements: StoryRequirements = Field(description="Original story requirements")
    generation_metadata: GenerationMetadata = Field(description="Generation metadata and context")
    
    # Success indicators
    target_quality_achieved: bool = Field(description="Whether target quality was achieved")
    enhancement_successful: bool = Field(description="Whether enhancement process was successful")
    quality_tier: str = Field(description="Final quality tier achieved")
    
    model_config = ConfigDict(use_enum_values=True)
    
    def get_quality_summary(self) -> Dict[str, Any]:
        """Get a summary of quality metrics for display"""
        return {
            "overall_score": self.quality_metrics.overall_score,
            "quality_tier": self.quality_tier,
            "enhancement_passes": len(self.enhancement_history),
            "total_improvement": self.quality_metrics.overall_score - self.generation_metadata.initial_quality_score,
            "target_achieved": self.target_quality_achieved,
            "generation_time": self.performance_metrics.total_generation_time,
            "tokens_used": self.performance_metrics.total_tokens_used
        }
    
    def get_top_improvements(self, limit: int = 3) -> List[QualityImprovement]:
        """Get top quality improvements achieved"""
        return sorted(
            self.quality_feedback.specific_suggestions, 
            key=lambda x: x.improvement_potential, 
            reverse=True
        )[:limit]


class QualityConfig(BaseModel):
    """Configuration for V1.4 quality enhancement system"""
    
    # Quality enhancement settings
    enable_multi_pass: bool = Field(default=True, description="Enable multi-pass enhancement")
    target_quality_score: float = Field(default=8.0, ge=0.0, le=10.0, description="Target quality score")
    max_enhancement_passes: int = Field(default=3, ge=1, le=10, description="Maximum enhancement passes")
    quality_convergence_threshold: float = Field(default=0.1, ge=0.01, le=1.0, description="Quality convergence threshold")
    enable_quality_prediction: bool = Field(default=True, description="Enable quality prediction")
    
    # Enhancement strategy settings
    enhancement_strategy_weights: Dict[str, float] = Field(
        default_factory=lambda: {
            "structure_weight": 1.0,
            "character_weight": 1.2,
            "pacing_weight": 1.1,
            "dialogue_weight": 0.9,
            "setting_weight": 0.8,
            "emotional_impact_weight": 1.3,
            "originality_weight": 0.7,
            "technical_weight": 1.0
        },
        description="Weights for different enhancement strategies"
    )
    
    # User experience settings
    enable_progress_tracking: bool = Field(default=True, description="Enable progress tracking")
    show_quality_trends: bool = Field(default=True, description="Show quality trends")
    display_enhancement_suggestions: bool = Field(default=True, description="Display enhancement suggestions")
    interactive_enhancement: bool = Field(default=False, description="Enable interactive enhancement")
    quality_feedback_detail: str = Field(default="comprehensive", description="Quality feedback detail level")
    
    # Performance optimization settings
    enable_generation_caching: bool = Field(default=True, description="Enable generation caching")
    cache_retention_hours: int = Field(default=24, ge=1, le=168, description="Cache retention in hours")
    enable_parallel_assessment: bool = Field(default=True, description="Enable parallel quality assessment")
    optimize_token_usage: bool = Field(default=True, description="Optimize token usage")
    enable_resource_profiling: bool = Field(default=True, description="Enable resource profiling")
    
    # Advanced metrics settings
    enable_dialogue_assessment: bool = Field(default=True, description="Enable dialogue quality assessment")
    enable_setting_assessment: bool = Field(default=True, description="Enable setting quality assessment")
    enable_emotional_assessment: bool = Field(default=True, description="Enable emotional impact assessment")
    enable_originality_assessment: bool = Field(default=True, description="Enable originality assessment")
    enable_technical_assessment: bool = Field(default=True, description="Enable technical quality assessment")
    assessment_detail_level: str = Field(default="comprehensive", description="Assessment detail level")
    
    model_config = ConfigDict(use_enum_values=True)


# Export all new V1.4 models
__all__ = [
    "EnhancementStrategy",
    "QualityDimension", 
    "AdvancedQualityMetrics",
    "ConvergenceMetrics",
    "QualityImprovement",
    "EnhancementPass",
    "QualityFeedback",
    "GenerationInsights",
    "EnhancedPerformanceMetrics",
    "CacheUtilizationReport",
    "WorkflowState",
    "GenerationMetadata",
    "QualityEnhancedResult",
    "QualityConfig"
]