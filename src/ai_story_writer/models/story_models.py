"""
AI Story Writer - Unified Data Models
Consolidated models combining all story generation, quality enhancement, and adaptive intelligence capabilities.
"""

import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any, Union
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict

from .basic_models import StoryGenre, StoryLength, StoryRequirements
from .enhanced_models import EnhancedGeneratedStory, GenerationMethod, ValidationResult, GenerationMetadata


# === Generation and Workflow Models ===

class WorkflowStage(str, Enum):
    """Stages in the story generation workflow"""
    ANALYSIS = "analysis"
    STRATEGY_SELECTION = "strategy_selection"
    OUTLINE_GENERATION = "outline_generation"
    CONTENT_GENERATION = "content_generation"
    QUALITY_ASSESSMENT = "quality_assessment"
    ENHANCEMENT = "enhancement"
    FINALIZATION = "finalization"


class GenerationStrategy(str, Enum):
    """Available generation strategies"""
    DIRECT = "direct"           # Single-pass generation
    OUTLINE = "outline"         # Multi-step with outline
    ITERATIVE = "iterative"     # Multiple passes with improvement
    ADAPTIVE = "adaptive"       # Dynamic approach based on requirements


class WorkflowState(BaseModel):
    """Tracks the state of a workflow execution"""
    workflow_id: str
    stage: WorkflowStage
    progress: float = Field(ge=0.0, le=1.0, description="Completion percentage")
    current_step: str
    steps_completed: List[str] = Field(default_factory=list)
    steps_remaining: List[str] = Field(default_factory=list)
    estimated_completion_time: Optional[datetime] = None
    error_count: int = Field(default=0, ge=0)
    last_error: Optional[str] = None
    
    # Performance tracking
    start_time: Optional[datetime] = Field(default_factory=datetime.now)
    stage_times: Dict[str, float] = Field(default_factory=dict)
    
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }


class WorkflowConfiguration(BaseModel):
    """Configuration for workflow execution"""
    default_strategy: GenerationStrategy = GenerationStrategy.ADAPTIVE
    max_workflow_time: int = Field(default=300, ge=60, description="Maximum workflow time in seconds")
    enable_quality_enhancement: bool = Field(default=True)
    quality_threshold: float = Field(default=7.0, ge=0.0, le=10.0)
    max_enhancement_iterations: int = Field(default=2, ge=0, le=5)
    
    # Strategy-specific settings
    direct_timeout: int = Field(default=120, ge=30)
    outline_timeout: int = Field(default=180, ge=60)
    iterative_timeout: int = Field(default=300, ge=120)
    adaptive_timeout: int = Field(default=240, ge=90)
    
    # Quality settings
    enable_real_time_monitoring: bool = Field(default=True)
    quality_check_interval: int = Field(default=30, ge=10)
    minimum_quality_score: float = Field(default=6.0, ge=0.0, le=10.0)
    enable_improvement_suggestions: bool = Field(default=True)


# === Quality Assessment Models ===

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


class QualityMetrics(BaseModel):
    """Comprehensive quality assessment metrics"""
    overall_score: float = Field(default=0.0, ge=0.0, le=10.0, description="Overall quality score")
    structure_score: float = Field(default=0.0, ge=0.0, le=10.0, description="Narrative structure quality")
    coherence_score: float = Field(default=0.0, ge=0.0, le=10.0, description="Story coherence and flow")
    genre_compliance: float = Field(default=0.0, ge=0.0, le=10.0, description="Genre convention adherence")
    character_development: float = Field(default=0.0, ge=0.0, le=10.0, description="Character depth and consistency")
    pacing_quality: float = Field(default=0.0, ge=0.0, le=10.0, description="Story pacing assessment")
    theme_integration: float = Field(default=0.0, ge=0.0, le=10.0, description="Theme incorporation quality")
    
    # Detailed assessments
    word_count_accuracy: float = Field(default=0.0, ge=0.0, le=1.0, description="Word count precision")
    grammar_quality: float = Field(default=0.0, ge=0.0, le=10.0, description="Grammar and style quality")
    originality_score: float = Field(default=0.0, ge=0.0, le=10.0, description="Story originality")
    
    # Assessment metadata
    assessment_time: Optional[datetime] = Field(default_factory=datetime.now)
    assessment_method: str = Field(default="automated", description="Method used for assessment")
    confidence_level: float = Field(default=0.0, ge=0.0, le=1.0, description="Assessment confidence")


class AdvancedQualityMetrics(BaseModel):
    """Enhanced quality metrics with 12-dimensional assessment"""
    
    # Core metrics (enhanced)
    overall_score: float = Field(ge=0.0, le=10.0, description="Overall quality score")
    structure_score: float = Field(ge=0.0, le=10.0, description="Narrative arc assessment")
    coherence_score: float = Field(ge=0.0, le=10.0, description="Logical consistency")
    genre_compliance: float = Field(ge=0.0, le=10.0, description="Genre convention adherence")
    character_development: float = Field(ge=0.0, le=10.0, description="Character depth and consistency")
    pacing_quality: float = Field(ge=0.0, le=10.0, description="Story rhythm and tension")
    theme_integration: float = Field(ge=0.0, le=10.0, description="Theme incorporation")
    
    # Enhanced quality dimensions
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


# === Enhancement Models ===

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


class QualityImprovement(BaseModel):
    """Specific quality improvement suggestion"""
    dimension: QualityDimension = Field(description="Quality dimension to improve")
    current_score: float = Field(ge=0.0, le=10.0, description="Current score for this dimension")
    target_score: float = Field(ge=0.0, le=10.0, description="Target score for this dimension")
    improvement_potential: float = Field(ge=0.0, description="Potential improvement points")
    suggestion: str = Field(description="Specific improvement suggestion")
    priority: int = Field(ge=1, le=5, description="Priority level (1=highest, 5=lowest)")
    estimated_effort: str = Field(description="Estimated effort level (low/medium/high)")


class ImprovementSuggestion(BaseModel):
    """Specific suggestions for story improvement"""
    category: str = Field(description="Category of improvement (structure, character, etc.)")
    priority: str = Field(description="Priority level (high, medium, low)")
    suggestion: str = Field(description="Specific improvement suggestion")
    reasoning: str = Field(description="Why this improvement is suggested")
    estimated_impact: float = Field(ge=0.0, le=1.0, description="Expected quality improvement")


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


class ConvergenceMetrics(BaseModel):
    """Quality improvement convergence analysis"""
    convergence_detected: bool = Field(default=False, description="Whether quality convergence was detected")
    convergence_pass: Optional[int] = Field(default=None, description="Pass number where convergence occurred")
    quality_plateau_threshold: float = Field(default=0.1, description="Threshold for detecting quality plateau")
    improvement_velocity: List[float] = Field(default_factory=list, description="Quality improvement rate per pass")
    diminishing_returns_detected: bool = Field(default=False, description="Whether diminishing returns were detected")
    optimal_pass_prediction: Optional[int] = Field(default=None, description="Predicted optimal number of passes")


# === Adaptive Intelligence Models ===

class AdaptationStrategy(str, Enum):
    """Adaptive strategy types"""
    CONSERVATIVE = "conservative"  # Minimal adaptation, high reliability
    MODERATE = "moderate"         # Balanced adaptation
    AGGRESSIVE = "aggressive"     # Maximum adaptation, learning-focused
    PREDICTIVE = "predictive"     # Prediction-driven adaptation
    PERSONALIZED = "personalized" # User-specific adaptation


class PersonalizationIntensity(str, Enum):
    """Level of personalization to apply"""
    MINIMAL = "minimal"
    MODERATE = "moderate" 
    COMPREHENSIVE = "comprehensive"


class PredictionConfidence(str, Enum):
    """Confidence levels for predictions"""
    LOW = "low"        # < 0.6 confidence
    MEDIUM = "medium"  # 0.6-0.8 confidence  
    HIGH = "high"      # > 0.8 confidence


class GenerationPredictions(BaseModel):
    """Predictive analytics for story generation"""
    predicted_quality_range: Tuple[float, float] = Field(description="Expected quality score range (min, max)")
    predicted_generation_time: float = Field(description="Estimated generation time in seconds")
    predicted_enhancement_passes: int = Field(description="Expected number of enhancement passes needed")
    predicted_token_usage: int = Field(description="Estimated token consumption")
    prediction_confidence: float = Field(ge=0.0, le=1.0, description="Confidence in predictions (0-1)")
    optimization_recommendations: List[str] = Field(default_factory=list, description="Recommended optimizations")
    resource_efficiency_score: float = Field(ge=0.0, le=10.0, description="Expected resource efficiency (0-10)")


class StrategyAdaptation(BaseModel):
    """Record of strategy adaptation applied"""
    original_strategy: GenerationStrategy
    adapted_strategy: GenerationStrategy
    adaptation_reason: str
    adaptation_impact: float = Field(ge=0.0, le=1.0, description="Impact of adaptation (0-1)")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence in adaptation")


class AdaptationInsights(BaseModel):
    """Insights from adaptive intelligence application"""
    strategy_adaptations: List[StrategyAdaptation] = Field(default_factory=list)
    personalization_impact: float = Field(ge=0.0, le=10.0, description="Impact of personalization on quality")
    learning_applied: List[str] = Field(default_factory=list, description="Learning patterns applied")
    adaptation_effectiveness: float = Field(ge=0.0, le=1.0, description="Overall adaptation effectiveness")
    intelligence_contributions: Dict[str, float] = Field(default_factory=dict, description="Contribution by intelligence component")


class UserPreferences(BaseModel):
    """User-specific preferences learned from interaction history"""
    preferred_quality_dimensions: Dict[str, float] = Field(default_factory=dict, description="Weights for quality dimensions")
    preferred_generation_speed: str = Field(default="balanced", description="Speed preference: fast|balanced|thorough")
    preferred_enhancement_level: str = Field(default="moderate", description="Enhancement preference: minimal|moderate|comprehensive")
    feedback_detail_preference: str = Field(default="standard", description="Feedback detail: minimal|standard|comprehensive")
    genre_expertise: Dict[str, float] = Field(default_factory=dict, description="User expertise by genre (0-1)")
    satisfaction_patterns: Dict[str, float] = Field(default_factory=dict, description="What leads to user satisfaction")


class UserProfile(BaseModel):
    """Comprehensive user profile for personalization"""
    user_id: str
    preferences: UserPreferences
    generation_history: List[str] = Field(default_factory=list, description="Recent generation IDs")
    learning_data: Dict[str, Any] = Field(default_factory=dict, description="Learning data for this user")
    profile_created: datetime = Field(default_factory=datetime.now)
    profile_updated: datetime = Field(default_factory=datetime.now)
    interaction_count: int = Field(default=0, description="Number of interactions")
    satisfaction_history: List[float] = Field(default_factory=list, description="Historical satisfaction scores")
    adaptation_effectiveness: float = Field(default=0.0, description="How well adaptations work for this user")


class PersonalizationRecord(BaseModel):
    """Record of personalization applied to generation"""
    user_profile_applied: bool
    preference_adaptations: Dict[str, Any] = Field(default_factory=dict, description="Specific preference adaptations")
    personalization_intensity: PersonalizationIntensity
    quality_preferences: Dict[str, float] = Field(default_factory=dict, description="User's quality dimension preferences")
    style_adaptations: List[str] = Field(default_factory=list, description="Style adaptations applied")
    satisfaction_prediction: float = Field(ge=0.0, le=10.0, description="Predicted user satisfaction")


class LearningContributions(BaseModel):
    """Contributions to system learning from this generation"""
    strategy_learning_points: List[str] = Field(default_factory=list)
    quality_pattern_discoveries: List[str] = Field(default_factory=list)
    user_preference_updates: Dict[str, Any] = Field(default_factory=dict)
    prediction_accuracy_data: Dict[str, float] = Field(default_factory=dict)
    optimization_insights: List[str] = Field(default_factory=list)


class SystemContext(BaseModel):
    """Current system context for adaptive decision making"""
    current_load: float = Field(ge=0.0, le=1.0, description="Current system load (0-1)")
    available_resources: Dict[str, float] = Field(default_factory=dict)
    active_learning_sessions: int = Field(default=0)
    cache_status: Dict[str, Any] = Field(default_factory=dict)
    system_performance_trend: str = Field(default="stable", description="Recent performance trend")


# === Performance and Metrics Models ===

class PerformanceMetrics(BaseModel):
    """Performance and execution metrics for generation process"""
    total_generation_time: float = Field(ge=0.0, description="Total generation time in seconds")
    workflow_execution_time: float = Field(ge=0.0, description="Workflow orchestration time")
    ai_generation_time: float = Field(ge=0.0, description="AI model generation time")
    quality_assessment_time: float = Field(ge=0.0, description="Quality assessment time")
    
    # Stage-specific timing
    stage_times: Dict[str, float] = Field(default_factory=dict)
    
    # Resource utilization
    memory_usage_mb: Optional[float] = Field(default=None, ge=0.0)
    cpu_usage_percent: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    
    # API usage
    api_calls_made: int = Field(default=0, ge=0)
    tokens_used: int = Field(default=0, ge=0)
    
    # Success metrics
    retry_count: int = Field(default=0, ge=0)
    error_count: int = Field(default=0, ge=0)
    success_rate: float = Field(default=1.0, ge=0.0, le=1.0)


class EnhancedPerformanceMetrics(BaseModel):
    """Enhanced performance tracking"""
    
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


class EfficiencyMetrics(BaseModel):
    """Advanced efficiency tracking for adaptive systems"""
    token_efficiency: float = Field(description="Tokens per quality point achieved")
    time_efficiency: float = Field(description="Quality points per second")
    adaptation_overhead: float = Field(description="Time spent on adaptive processing")
    prediction_overhead: float = Field(description="Time spent on predictions")
    learning_overhead: float = Field(description="Time spent on learning updates")
    cache_hit_rate: float = Field(ge=0.0, le=1.0, description="Adaptive cache utilization rate")
    resource_optimization_impact: float = Field(description="Resource savings from optimization")


class PredictionAccuracy(BaseModel):
    """Tracking accuracy of predictions vs actual outcomes"""
    quality_prediction_accuracy: float = Field(ge=0.0, le=1.0, description="Quality prediction accuracy")
    time_prediction_accuracy: float = Field(ge=0.0, le=1.0, description="Time prediction accuracy")
    resource_prediction_accuracy: float = Field(ge=0.0, le=1.0, description="Resource prediction accuracy")
    enhancement_passes_accuracy: float = Field(ge=0.0, le=1.0, description="Enhancement passes prediction accuracy")
    overall_prediction_score: float = Field(ge=0.0, le=10.0, description="Overall prediction accuracy score")


class OptimizationOpportunity(BaseModel):
    """Identified optimization opportunity"""
    opportunity_type: str = Field(description="Type of optimization opportunity")
    description: str = Field(description="Description of the opportunity")
    potential_impact: float = Field(ge=0.0, le=10.0, description="Potential impact score")
    implementation_complexity: str = Field(description="Implementation complexity estimate")
    recommendation: str = Field(description="Specific recommendation")


# === Tool and Reporting Models ===

class ToolUsageReport(BaseModel):
    """Report on tool usage during generation"""
    tools_used: List[str] = Field(default_factory=list)
    tool_execution_times: Dict[str, float] = Field(default_factory=dict)
    tool_success_rates: Dict[str, float] = Field(default_factory=dict)
    tool_effectiveness_scores: Dict[str, float] = Field(default_factory=dict)
    
    # Tool recommendations
    recommended_tools: List[str] = Field(default_factory=list)
    unused_beneficial_tools: List[str] = Field(default_factory=list)


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


# === Analysis and Recommendation Models ===

class StrategyRecommendation(BaseModel):
    """Recommendation for generation strategy selection"""
    recommended_strategy: GenerationStrategy
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence in recommendation")
    reasoning: str = Field(description="Why this strategy is recommended")
    estimated_time: float = Field(ge=0.0, description="Estimated generation time")
    estimated_quality: float = Field(ge=0.0, le=10.0, description="Expected quality score")
    
    # Alternative strategies
    alternatives: List[Dict[str, Union[GenerationStrategy, float, str]]] = Field(default_factory=list)


class RequirementAnalysis(BaseModel):
    """Analysis of story requirements for strategy selection"""
    complexity_score: float = Field(ge=0.0, le=1.0, description="Requirement complexity")
    feasibility_score: float = Field(ge=0.0, le=1.0, description="Generation feasibility")
    estimated_difficulty: str = Field(description="Difficulty level (easy, medium, hard)")
    
    # Requirement assessment
    word_count_feasibility: float = Field(ge=0.0, le=1.0)
    genre_familiarity: float = Field(ge=0.0, le=1.0)
    theme_complexity: float = Field(ge=0.0, le=1.0)
    setting_specificity: float = Field(ge=0.0, le=1.0)
    
    # Recommendations
    recommended_tools: List[str] = Field(default_factory=list)
    potential_challenges: List[str] = Field(default_factory=list)
    success_predictors: List[str] = Field(default_factory=list)


class QualityTrajectory(BaseModel):
    """Predicted quality improvement trajectory"""
    initial_quality_prediction: float
    quality_by_pass: List[float] = Field(description="Predicted quality after each enhancement pass")
    convergence_point: Optional[int] = Field(description="Pass where quality converges")
    optimal_stopping_point: int = Field(description="Recommended stopping point")
    efficiency_curve: List[float] = Field(description="Efficiency score by pass")
    diminishing_returns_threshold: float = Field(description="Quality improvement threshold for diminishing returns")


# === Configuration Models ===

class QualityConfig(BaseModel):
    """Configuration for quality enhancement system"""
    
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


class AdaptiveGenerationConfig(BaseModel):
    """Adaptive generation configuration"""
    # Base configuration
    quality_config: QualityConfig
    workflow_config: WorkflowConfiguration
    
    # Adaptive intelligence settings
    adaptation_strategy: AdaptationStrategy = AdaptationStrategy.MODERATE
    personalization_intensity: PersonalizationIntensity = PersonalizationIntensity.MODERATE
    enable_predictive_analytics: bool = True
    enable_adaptive_learning: bool = True
    enable_resource_optimization: bool = True
    
    # Learning configuration
    learning_rate: float = Field(default=0.1, ge=0.0, le=1.0)
    prediction_confidence_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    adaptation_aggressiveness: float = Field(default=0.5, ge=0.0, le=1.0)
    
    # Performance settings
    max_adaptation_overhead: float = Field(default=0.2, description="Maximum overhead allowed for adaptation (fraction)")
    enable_parallel_prediction: bool = True
    cache_learning_data: bool = True
    learning_history_window: int = Field(default=100, description="Number of generations to consider for learning")


# === Result Models ===

class StoryResult(BaseModel):
    """Enhanced story result with comprehensive workflow and quality features"""
    
    # Core story content (inherited from V1.2)
    title: str
    content: str
    word_count: int
    genre: StoryGenre
    
    # Enhanced features
    workflow_state: WorkflowState
    quality_metrics: QualityMetrics
    generation_strategy: GenerationStrategy
    performance_metrics: PerformanceMetrics
    tool_usage_report: ToolUsageReport
    improvement_suggestions: List[ImprovementSuggestion] = Field(default_factory=list)
    
    # Metadata
    generation_time: float
    workflow_id: str
    strategy_used: str
    quality_passes: int = Field(default=1, ge=1)
    
    # Compatibility fields
    requirements: StoryRequirements
    generation_method: str  # For backward compatibility
    outline_used: Optional[Any] = None
    validation_results: Optional[Any] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }


class QualityEnhancedResult(BaseModel):
    """Comprehensive result model for quality-enhanced generation"""
    
    # Core story content
    title: str = Field(description="Story title")
    content: str = Field(description="Story content")
    word_count: int = Field(ge=0, description="Story word count")
    genre: StoryGenre = Field(description="Story genre")
    
    # Quality enhancements
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


class AdaptiveGenerationResult(QualityEnhancedResult):
    """Enhanced result with adaptive intelligence insights"""
    
    # Adaptive enhancements
    generation_predictions: GenerationPredictions
    adaptation_insights: AdaptationInsights  
    personalization_applied: PersonalizationRecord
    learning_contributions: LearningContributions
    efficiency_metrics: EfficiencyMetrics
    
    # Predictive analytics results
    predicted_vs_actual: PredictionAccuracy
    optimization_opportunities: List[OptimizationOpportunity] = Field(default_factory=list)
    user_satisfaction_prediction: float = Field(ge=0.0, le=10.0, description="Predicted user satisfaction")
    
    # Intelligence metadata
    intelligence_version: str = Field(default="1.5", description="Adaptive intelligence version")
    adaptation_applied: bool = Field(description="Whether adaptive intelligence was applied")
    learning_data_updated: bool = Field(description="Whether learning systems were updated")
    
    def get_intelligence_summary(self) -> Dict[str, Any]:
        """Get comprehensive intelligence summary"""
        return {
            "predictions": {
                "quality_range": self.generation_predictions.predicted_quality_range,
                "confidence": self.generation_predictions.prediction_confidence,
                "accuracy": self.predicted_vs_actual.overall_prediction_score
            },
            "adaptations": {
                "strategy_adaptations": len(self.adaptation_insights.strategy_adaptations),
                "personalization_impact": self.adaptation_insights.personalization_impact,
                "effectiveness": self.adaptation_insights.adaptation_effectiveness
            },
            "efficiency": {
                "token_efficiency": self.efficiency_metrics.token_efficiency,
                "time_efficiency": self.efficiency_metrics.time_efficiency,
                "cache_hit_rate": self.efficiency_metrics.cache_hit_rate
            },
            "learning": {
                "contributions": len(self.learning_contributions.strategy_learning_points),
                "user_updates": bool(self.learning_contributions.user_preference_updates),
                "optimization_insights": len(self.learning_contributions.optimization_insights)
            },
            "satisfaction": {
                "predicted": self.user_satisfaction_prediction,
                "personalization_impact": self.personalization_applied.satisfaction_prediction
            }
        }
    
    def get_optimization_report(self) -> str:
        """Generate optimization recommendations report"""
        if not self.optimization_opportunities:
            return "No optimization opportunities identified."
            
        report = "🔧 Optimization Opportunities:\n"
        for i, opp in enumerate(self.optimization_opportunities[:3], 1):  # Top 3
            impact = "🔥" if opp.potential_impact >= 7.0 else "⚡" if opp.potential_impact >= 4.0 else "💡"
            report += f"{i}. {impact} {opp.description} (Impact: {opp.potential_impact:.1f}/10)\n"
            report += f"   Recommendation: {opp.recommendation}\n"
            
        return report


# === Enhanced Workflow State ===

class EnhancedWorkflowState(BaseModel):
    """Enhanced workflow state tracking"""
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


# === Enhanced Generation Metadata ===

class EnhancedGenerationMetadata(BaseModel):
    """Enhanced generation metadata"""
    
    # Basic metadata
    generation_id: str = Field(description="Unique generation identifier")
    version: str = Field(default="1.5", description="AI Story Writer version")
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


# === Configuration validation ===

def validate_adaptive_config(config: AdaptiveGenerationConfig) -> AdaptiveGenerationConfig:
    """Validate and optimize adaptive configuration - must succeed"""
    # Requires no fallbacks - all validation must pass
    if config.learning_rate <= 0 or config.learning_rate > 1:
        raise ValueError(f"Invalid learning rate: {config.learning_rate}")
        
    if config.prediction_confidence_threshold < 0.5:
        raise ValueError("Prediction confidence threshold must be >= 0.5 for reliable operation")
        
    if config.max_adaptation_overhead > 0.5:
        raise ValueError("Adaptation overhead cannot exceed 50% of generation time")
        
    return config


# Export all unified models
__all__ = [
    # Core models
    "WorkflowStage", "GenerationStrategy", "WorkflowState", "WorkflowConfiguration",
    
    # Quality models
    "QualityDimension", "QualityMetrics", "AdvancedQualityMetrics", 
    "QualityImprovement", "ImprovementSuggestion", "QualityFeedback",
    
    # Enhancement models
    "EnhancementStrategy", "EnhancementPass", "ConvergenceMetrics",
    
    # Adaptive intelligence models
    "AdaptationStrategy", "PersonalizationIntensity", "PredictionConfidence",
    "GenerationPredictions", "StrategyAdaptation", "AdaptationInsights",
    "UserPreferences", "UserProfile", "PersonalizationRecord", 
    "LearningContributions", "SystemContext",
    
    # Performance models
    "PerformanceMetrics", "EnhancedPerformanceMetrics", "EfficiencyMetrics",
    "PredictionAccuracy", "OptimizationOpportunity",
    
    # Tool and reporting models
    "ToolUsageReport", "CacheUtilizationReport", "GenerationInsights",
    
    # Analysis models
    "StrategyRecommendation", "RequirementAnalysis", "QualityTrajectory",
    
    # Configuration models
    "QualityConfig", "AdaptiveGenerationConfig",
    
    # Result models
    "StoryResult", "QualityEnhancedResult", "AdaptiveGenerationResult",
    
    # Enhanced models
    "EnhancedWorkflowState", "EnhancedGenerationMetadata",
    
    # Validation functions
    "validate_adaptive_config"
]