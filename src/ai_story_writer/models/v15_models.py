"""
AI Story Writer V1.5 Models - Adaptive Intelligence Engine
Enhanced models with learning, prediction, and personalization capabilities.
"""

from typing import Dict, List, Optional, Tuple, Any, Union
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field

from .v14_models import QualityEnhancedResult, AdvancedQualityMetrics, EnhancementStrategy, QualityConfig
from .v13_models import GenerationStrategy, WorkflowConfiguration
from .basic_models import StoryRequirements


class AdaptationStrategy(str, Enum):
    """V1.5 adaptive strategy types"""
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


class QualityTrajectory(BaseModel):
    """Predicted quality improvement trajectory"""
    initial_quality_prediction: float
    quality_by_pass: List[float] = Field(description="Predicted quality after each enhancement pass")
    convergence_point: Optional[int] = Field(description="Pass where quality converges")
    optimal_stopping_point: int = Field(description="Recommended stopping point")
    efficiency_curve: List[float] = Field(description="Efficiency score by pass")
    diminishing_returns_threshold: float = Field(description="Quality improvement threshold for diminishing returns")


class AdaptiveGenerationConfig(BaseModel):
    """V1.5 adaptive generation configuration"""
    # Base V1.4 configuration
    quality_config: QualityConfig
    workflow_config: WorkflowConfiguration
    
    # V1.5 adaptive intelligence settings
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


class AdaptiveGenerationResult(QualityEnhancedResult):
    """Enhanced V1.4 result with V1.5 adaptive intelligence insights"""
    
    # V1.5 adaptive enhancements
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


class SystemContext(BaseModel):
    """Current system context for adaptive decision making"""
    current_load: float = Field(ge=0.0, le=1.0, description="Current system load (0-1)")
    available_resources: Dict[str, float] = Field(default_factory=dict)
    active_learning_sessions: int = Field(default=0)
    cache_status: Dict[str, Any] = Field(default_factory=dict)
    system_performance_trend: str = Field(default="stable", description="Recent performance trend")


# Configuration validation
def validate_adaptive_config(config: AdaptiveGenerationConfig) -> AdaptiveGenerationConfig:
    """Validate and optimize adaptive configuration - must succeed"""
    # V1.5 requires no fallbacks - all validation must pass
    if config.learning_rate <= 0 or config.learning_rate > 1:
        raise ValueError(f"Invalid learning rate: {config.learning_rate}")
        
    if config.prediction_confidence_threshold < 0.5:
        raise ValueError("Prediction confidence threshold must be >= 0.5 for reliable operation")
        
    if config.max_adaptation_overhead > 0.5:
        raise ValueError("Adaptation overhead cannot exceed 50% of generation time")
        
    return config