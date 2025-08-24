"""
AI Story Writer V1.5 - Adaptive Intelligence Engine
Core adaptive intelligence coordination and orchestration.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any
from datetime import datetime

from ..models.story_models import (
    AdaptiveGenerationResult, AdaptiveGenerationConfig, GenerationPredictions,
    AdaptationInsights, PersonalizationRecord, LearningContributions, 
    EfficiencyMetrics, PredictionAccuracy, OptimizationOpportunity,
    UserProfile, SystemContext, QualityTrajectory, validate_adaptive_config,
    QualityEnhancedResult, QualityConfig, GenerationStrategy, WorkflowConfiguration
)
from ..models.basic_models import StoryRequirements
from ..utils import StoryGenerationError

from .prediction import QualityPredictionEngine, ResourcePredictionEngine
from .learning import StrategyLearningEngine, PersonalizationEngine
from .optimization import ResourceOptimizationEngine, EfficiencyAnalyzer

logger = logging.getLogger(__name__)


class AdaptiveIntelligenceEngine:
    """Core adaptive intelligence coordination for V1.5"""
    
    def __init__(self, config: AdaptiveGenerationConfig):
        """Initialize adaptive intelligence engine - must succeed"""
        try:
            self.config = validate_adaptive_config(config)
            
            # Initialize intelligence components
            self.quality_predictor = QualityPredictionEngine(config)
            self.resource_predictor = ResourcePredictionEngine(config)
            self.strategy_learner = StrategyLearningEngine(config)
            self.personalization_engine = PersonalizationEngine(config)
            self.resource_optimizer = ResourceOptimizationEngine(config)
            self.efficiency_analyzer = EfficiencyAnalyzer(config)
            
            # Intelligence state
            self.generation_history: List[str] = []
            self.learning_enabled = config.enable_adaptive_learning
            self.prediction_cache: Dict[str, Any] = {}
            
            logger.info("AdaptiveIntelligenceEngine initialized with V1.5 capabilities")
            
        except Exception as e:
            raise StoryGenerationError(f"Failed to initialize adaptive intelligence engine: {e}")
    
    async def generate_adaptive_story(
        self,
        requirements: StoryRequirements,
        user_profile: Optional[UserProfile] = None,
        system_context: Optional[SystemContext] = None
    ) -> AdaptiveGenerationResult:
        """Generate story with full adaptive intelligence - must succeed"""
        generation_id = f"adaptive_{int(time.time())}"
        start_time = time.time()
        
        try:
            logger.info(f"Starting V1.5 adaptive generation {generation_id}")
            
            # Phase 1: Predict and analyze
            predictions = await self._predict_generation_outcome(
                requirements, user_profile, system_context
            )
            
            # Phase 2: Adapt strategy and configuration  
            adapted_strategy, adaptation_insights = await self._adapt_generation_strategy(
                requirements, predictions, user_profile
            )
            
            # Phase 3: Personalize configuration
            personalized_config, personalization_record = await self._personalize_configuration(
                requirements, adapted_strategy, user_profile, predictions
            )
            
            # Phase 4: Execute optimized generation with V1.4 engine
            v14_result = await self._execute_optimized_generation(
                requirements, adapted_strategy, personalized_config, generation_id
            )
            
            # Phase 5: Analyze results and learn
            efficiency_metrics = await self._analyze_generation_efficiency(
                v14_result, predictions, start_time
            )
            
            prediction_accuracy = await self._evaluate_prediction_accuracy(
                predictions, v14_result
            )
            
            # Phase 6: Update learning systems
            learning_contributions = await self._update_learning_systems(
                requirements, v14_result, predictions, user_profile, generation_id
            )
            
            # Phase 7: Generate optimization opportunities
            optimization_opportunities = await self._identify_optimization_opportunities(
                v14_result, predictions, efficiency_metrics
            )
            
            # Phase 8: Create adaptive result
            adaptive_result = self._create_adaptive_result(
                v14_result, predictions, adaptation_insights, personalization_record,
                learning_contributions, efficiency_metrics, prediction_accuracy,
                optimization_opportunities, generation_id
            )
            
            total_time = time.time() - start_time
            logger.info(f"V1.5 adaptive generation {generation_id} completed in {total_time:.1f}s")
            
            return adaptive_result
            
        except Exception as e:
            logger.error(f"Adaptive generation {generation_id} failed: {e}")
            raise StoryGenerationError(f"V1.5 adaptive generation failed: {e}")
    
    async def _predict_generation_outcome(
        self,
        requirements: StoryRequirements,
        user_profile: Optional[UserProfile],
        system_context: Optional[SystemContext]
    ) -> GenerationPredictions:
        """Predict generation outcome and requirements"""
        cache_key = f"pred_{hash(str(requirements))}"
        
        if cache_key in self.prediction_cache:
            logger.debug("Using cached predictions")
            return self.prediction_cache[cache_key]
        
        # Quality prediction
        quality_prediction = await self.quality_predictor.predict_quality_range(
            requirements, user_profile
        )
        
        # Resource prediction
        resource_prediction = await self.resource_predictor.predict_resource_usage(
            requirements, quality_prediction, system_context
        )
        
        # Enhancement prediction
        enhancement_prediction = await self.quality_predictor.predict_enhancement_passes(
            requirements, quality_prediction
        )
        
        # Generate optimization recommendations
        optimization_recs = await self._generate_optimization_recommendations(
            requirements, quality_prediction, resource_prediction
        )
        
        predictions = GenerationPredictions(
            predicted_quality_range=quality_prediction.expected_range,
            predicted_generation_time=resource_prediction.estimated_time,
            predicted_enhancement_passes=enhancement_prediction.expected_passes,
            predicted_token_usage=resource_prediction.estimated_tokens,
            prediction_confidence=min(
                quality_prediction.confidence,
                resource_prediction.confidence,
                enhancement_prediction.confidence
            ),
            optimization_recommendations=optimization_recs,
            resource_efficiency_score=resource_prediction.efficiency_score
        )
        
        # Cache predictions
        self.prediction_cache[cache_key] = predictions
        
        return predictions
    
    async def _adapt_generation_strategy(
        self,
        requirements: StoryRequirements,
        predictions: GenerationPredictions,
        user_profile: Optional[UserProfile]
    ) -> tuple[GenerationStrategy, AdaptationInsights]:
        """Adapt generation strategy based on predictions and learning"""
        
        # Select base strategy using learning engine
        base_strategy = await self.strategy_learner.select_optimal_strategy(
            requirements, predictions, user_profile
        )
        
        # Apply adaptations based on predictions
        adaptations = []
        adapted_strategy = base_strategy
        
        # Complexity-based adaptation
        if predictions.predicted_quality_range[0] < 7.0:
            adapted_strategy = GenerationStrategy.ITERATIVE
            adaptations.append({
                "reason": "Low predicted quality - switching to iterative strategy",
                "impact": 0.3,
                "confidence": 0.8
            })
        
        # Resource-based adaptation
        if predictions.predicted_token_usage > 8000:
            if adapted_strategy == GenerationStrategy.ITERATIVE:
                adapted_strategy = GenerationStrategy.ADAPTIVE
                adaptations.append({
                    "reason": "High resource usage - optimizing with adaptive strategy",
                    "impact": 0.2,
                    "confidence": 0.7
                })
        
        # User preference adaptation
        if user_profile and user_profile.preferences.preferred_generation_speed == "fast":
            if adapted_strategy == GenerationStrategy.ITERATIVE:
                adapted_strategy = GenerationStrategy.DIRECT
                adaptations.append({
                    "reason": "User prefers fast generation - using direct strategy",
                    "impact": 0.4,
                    "confidence": 0.9
                })
        
        # Calculate adaptation effectiveness
        adaptation_effectiveness = sum(a["impact"] * a["confidence"] for a in adaptations) / max(len(adaptations), 1)
        
        adaptation_insights = AdaptationInsights(
            strategy_adaptations=[],  # Will be populated with actual adaptations
            personalization_impact=0.0,  # Will be calculated later
            learning_applied=[a["reason"] for a in adaptations],
            adaptation_effectiveness=adaptation_effectiveness,
            intelligence_contributions={
                "strategy_learning": 0.3,
                "prediction_based": 0.4,
                "user_preferences": 0.3 if user_profile else 0.0
            }
        )
        
        logger.info(f"Strategy adapted from {base_strategy} to {adapted_strategy} "
                   f"(effectiveness: {adaptation_effectiveness:.2f})")
        
        return adapted_strategy, adaptation_insights
    
    async def _personalize_configuration(
        self,
        requirements: StoryRequirements,
        strategy: GenerationStrategy,
        user_profile: Optional[UserProfile],
        predictions: GenerationPredictions
    ) -> tuple[QualityConfig, PersonalizationRecord]:
        """Personalize configuration based on user profile and predictions"""
        
        if not user_profile:
            # No personalization - use default config
            return self.config.quality_config, PersonalizationRecord(
                user_profile_applied=False,
                personalization_intensity=self.config.personalization_intensity,
                satisfaction_prediction=7.0  # Default expectation
            )
        
        # Apply personalization
        personalized_config = await self.personalization_engine.personalize_quality_config(
            self.config.quality_config, user_profile, requirements, predictions
        )
        
        # Calculate personalization impact
        personalization_impact = await self.personalization_engine.calculate_personalization_impact(
            user_profile, requirements
        )
        
        # Predict satisfaction
        satisfaction_prediction = await self.personalization_engine.predict_user_satisfaction(
            user_profile, requirements, predictions, personalized_config
        )
        
        personalization_record = PersonalizationRecord(
            user_profile_applied=True,
            preference_adaptations=await self.personalization_engine.get_applied_adaptations(),
            personalization_intensity=self.config.personalization_intensity,
            quality_preferences=user_profile.preferences.preferred_quality_dimensions,
            style_adaptations=[],  # Will be populated by personalization engine
            satisfaction_prediction=satisfaction_prediction
        )
        
        logger.info(f"Configuration personalized for user {user_profile.user_id} "
                   f"(impact: {personalization_impact:.2f})")
        
        return personalized_config, personalization_record
    
    async def _execute_optimized_generation(
        self,
        requirements: StoryRequirements,
        strategy: GenerationStrategy,
        quality_config: QualityConfig,
        generation_id: str
    ) -> QualityEnhancedResult:
        """Execute story generation with V1.4 engine using optimized configuration"""
        
        try:
            # Optimize workflow configuration for V1.5
            optimized_workflow_config = WorkflowConfiguration(
                default_strategy=strategy,
                max_workflow_time=self.config.workflow_config.max_workflow_time,
                enable_quality_enhancement=self.config.workflow_config.enable_quality_enhancement,
                quality_threshold=quality_config.target_quality_score,
                max_enhancement_iterations=quality_config.max_enhancement_passes
            )
            
            # Execute quality-enhanced generation with optimized parameters
            # Generate story using direct PydanticAI agent
            from pydantic_ai import Agent
            
            story_agent = Agent(
                'openai:gpt-4',
                system_prompt=f"""Generate a {requirements.target_word_count}-word {requirements.genre.value} story.
Theme: {requirements.theme or 'Open theme'}
Requirements: Complete story with clear beginning, middle, and end."""
            )
            
            # Generate basic story
            basic_story_result = await story_agent.run(
                f"Write a {requirements.target_word_count}-word {requirements.genre.value} story" +
                (f" about {requirements.theme}" if requirements.theme else "")
            )
            
            # Then enhance the story with quality engine
            from ..workflow.quality_enhancement_engine import QualityEnhancementEngine
            quality_engine = QualityEnhancementEngine(quality_config)
            # PydanticAI result might have different attribute names
            story_text = basic_story_result.data if hasattr(basic_story_result, 'data') else str(basic_story_result)
            
            v14_result = await quality_engine.enhance_story(
                initial_story=story_text,
                initial_title="Generated Story",  # Simple title for now
                requirements=requirements,
                target_quality=quality_config.target_quality_score,
                max_passes=quality_config.max_enhancement_passes
            )
            
            logger.info(f"Quality engine execution completed for {generation_id}")
            return v14_result
            
        except Exception as e:
            raise StoryGenerationError(f"Optimized generation execution failed: {e}")
    
    async def _analyze_generation_efficiency(
        self,
        result: QualityEnhancedResult,
        predictions: GenerationPredictions,
        start_time: float
    ) -> EfficiencyMetrics:
        """Analyze generation efficiency and performance"""
        
        actual_time = time.time() - start_time
        
        # Calculate efficiency metrics
        efficiency_metrics = await self.efficiency_analyzer.analyze_efficiency(
            result, predictions, actual_time
        )
        
        return efficiency_metrics
    
    async def _evaluate_prediction_accuracy(
        self,
        predictions: GenerationPredictions,
        result: QualityEnhancedResult
    ) -> PredictionAccuracy:
        """Evaluate accuracy of predictions against actual results"""
        
        # Quality prediction accuracy
        actual_quality = result.quality_metrics.overall_score
        predicted_range = predictions.predicted_quality_range
        quality_accuracy = 1.0 if predicted_range[0] <= actual_quality <= predicted_range[1] else \
                         max(0.0, 1.0 - abs(actual_quality - sum(predicted_range) / 2) / 5.0)
        
        # Time prediction accuracy  
        actual_time = result.performance_metrics.total_generation_time
        predicted_time = predictions.predicted_generation_time
        time_accuracy = max(0.0, 1.0 - abs(actual_time - predicted_time) / max(predicted_time, 1.0))
        
        # Enhancement passes accuracy
        actual_passes = len(result.enhancement_history)
        predicted_passes = predictions.predicted_enhancement_passes
        passes_accuracy = 1.0 if actual_passes == predicted_passes else \
                         max(0.0, 1.0 - abs(actual_passes - predicted_passes) / max(predicted_passes, 1))
        
        # Overall prediction score
        overall_score = (quality_accuracy + time_accuracy + passes_accuracy) / 3.0 * 10.0
        
        return PredictionAccuracy(
            quality_prediction_accuracy=quality_accuracy,
            time_prediction_accuracy=time_accuracy,
            resource_prediction_accuracy=0.8,  # Placeholder - would track token usage
            enhancement_passes_accuracy=passes_accuracy,
            overall_prediction_score=overall_score
        )
    
    async def _update_learning_systems(
        self,
        requirements: StoryRequirements,
        result: QualityEnhancedResult,
        predictions: GenerationPredictions,
        user_profile: Optional[UserProfile],
        generation_id: str
    ) -> LearningContributions:
        """Update learning systems with generation results"""
        
        if not self.learning_enabled:
            return LearningContributions()
        
        # Update strategy learning
        strategy_updates = await self.strategy_learner.learn_from_generation(
            requirements, result, predictions
        )
        
        # Update personalization if user profile exists
        user_updates = {}
        if user_profile:
            user_updates = await self.personalization_engine.update_user_profile(
                user_profile, result, predictions
            )
        
        # Update quality prediction models
        quality_updates = await self.quality_predictor.update_prediction_models(
            requirements, result, predictions
        )
        
        learning_contributions = LearningContributions(
            strategy_learning_points=strategy_updates,
            quality_pattern_discoveries=quality_updates,
            user_preference_updates=user_updates,
            prediction_accuracy_data={
                "quality_accuracy": (result.quality_metrics.overall_score - predictions.predicted_quality_range[0]) / (predictions.predicted_quality_range[1] - predictions.predicted_quality_range[0])
            },
            optimization_insights=[]  # Will be populated by optimization analysis
        )
        
        logger.info(f"Learning systems updated for generation {generation_id}")
        return learning_contributions
    
    async def _identify_optimization_opportunities(
        self,
        result: QualityEnhancedResult,
        predictions: GenerationPredictions,
        efficiency_metrics: EfficiencyMetrics
    ) -> List[OptimizationOpportunity]:
        """Identify optimization opportunities for future generations"""
        
        opportunities = []
        
        # Token efficiency opportunity
        if efficiency_metrics.token_efficiency < 0.5:  # Less than 0.5 quality points per token
            opportunities.append(OptimizationOpportunity(
                opportunity_type="token_efficiency",
                description="Token usage could be optimized for better quality-to-token ratio",
                potential_impact=6.0,
                implementation_complexity="moderate",
                recommendation="Consider more targeted enhancement strategies or improved prompt optimization"
            ))
        
        # Time efficiency opportunity
        if efficiency_metrics.time_efficiency < 2.0:  # Less than 2 quality points per second
            opportunities.append(OptimizationOpportunity(
                opportunity_type="time_efficiency", 
                description="Generation time could be reduced while maintaining quality",
                potential_impact=5.0,
                implementation_complexity="low",
                recommendation="Implement parallel processing or caching for similar requests"
            ))
        
        # Cache utilization opportunity
        if efficiency_metrics.cache_hit_rate < 0.3:
            opportunities.append(OptimizationOpportunity(
                opportunity_type="cache_optimization",
                description="Cache utilization is low - similar requests could benefit from caching",
                potential_impact=4.0,
                implementation_complexity="low", 
                recommendation="Implement smarter caching strategies for outlines and partial generations"
            ))
        
        # Prediction accuracy opportunity
        if predictions.prediction_confidence < 0.7:
            opportunities.append(OptimizationOpportunity(
                opportunity_type="prediction_accuracy",
                description="Prediction confidence is low - models could be improved",
                potential_impact=7.0,
                implementation_complexity="high",
                recommendation="Gather more training data and refine prediction algorithms"
            ))
        
        return opportunities
    
    async def _generate_optimization_recommendations(
        self,
        requirements: StoryRequirements,
        quality_prediction: Any,
        resource_prediction: Any
    ) -> List[str]:
        """Generate optimization recommendations based on predictions"""
        recommendations = []
        
        if quality_prediction.expected_range[1] > 8.5:
            recommendations.append("High quality predicted - consider reducing enhancement passes")
        
        if resource_prediction.estimated_tokens > 10000:
            recommendations.append("High token usage predicted - consider outline-based generation")
            
        if resource_prediction.estimated_time > 120:
            recommendations.append("Long generation time predicted - consider parallel processing")
        
        return recommendations
    
    def _create_adaptive_result(
        self,
        v14_result: QualityEnhancedResult,
        predictions: GenerationPredictions,
        adaptation_insights: AdaptationInsights,
        personalization_record: PersonalizationRecord,
        learning_contributions: LearningContributions,
        efficiency_metrics: EfficiencyMetrics,
        prediction_accuracy: PredictionAccuracy,
        optimization_opportunities: List[OptimizationOpportunity],
        generation_id: str
    ) -> AdaptiveGenerationResult:
        """Create comprehensive adaptive generation result"""
        
        # Create V1.5 adaptive result by extending V1.4 result
        adaptive_result = AdaptiveGenerationResult(
            # Inherit all V1.4 fields
            **v14_result.dict(),
            
            # V1.5 adaptive enhancements
            generation_predictions=predictions,
            adaptation_insights=adaptation_insights,
            personalization_applied=personalization_record,
            learning_contributions=learning_contributions,
            efficiency_metrics=efficiency_metrics,
            predicted_vs_actual=prediction_accuracy,
            optimization_opportunities=optimization_opportunities,
            user_satisfaction_prediction=personalization_record.satisfaction_prediction,
            adaptation_applied=True,
            learning_data_updated=self.learning_enabled
        )
        
        return adaptive_result