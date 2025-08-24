"""
AI Story Writer V1.5 - Learning and Personalization Systems
Strategy learning and user personalization engines for adaptive intelligence.
"""

import logging
import math
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, deque

from ..models.story_models import (
    AdaptiveGenerationConfig, UserProfile, UserPreferences, GenerationPredictions,
    QualityConfig, AdaptationStrategy, PersonalizationIntensity, QualityEnhancedResult,
    GenerationStrategy
)
from ..models.basic_models import StoryRequirements, StoryGenre
from ..utils import StoryGenerationError

logger = logging.getLogger(__name__)


class StrategyLearningEngine:
    """Learns optimal generation strategies from historical performance"""
    
    def __init__(self, config: AdaptiveGenerationConfig):
        """Initialize strategy learning engine - must succeed"""
        self.config = config
        self.strategy_performance: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.genre_strategy_effectiveness: Dict[StoryGenre, Dict[GenerationStrategy, float]] = {}
        self.complexity_strategy_map: Dict[str, GenerationStrategy] = {}
        
        # Initialize base effectiveness scores
        self._initialize_strategy_patterns()
        
        logger.info("StrategyLearningEngine initialized with adaptive learning")
    
    def _initialize_strategy_patterns(self):
        """Initialize base strategy effectiveness patterns"""
        
        # Base effectiveness by genre (0-1 scale)
        base_patterns = {
            StoryGenre.SCIENCE_FICTION: {
                GenerationStrategy.ITERATIVE: 0.85,
                GenerationStrategy.ADAPTIVE: 0.90,
                GenerationStrategy.DIRECT: 0.70
            },
            StoryGenre.FANTASY: {
                GenerationStrategy.ITERATIVE: 0.88,
                GenerationStrategy.ADAPTIVE: 0.85,
                GenerationStrategy.DIRECT: 0.72
            },
            StoryGenre.MYSTERY: {
                GenerationStrategy.ITERATIVE: 0.90,
                GenerationStrategy.ADAPTIVE: 0.82,
                GenerationStrategy.DIRECT: 0.75
            },
            StoryGenre.ROMANCE: {
                GenerationStrategy.ITERATIVE: 0.75,
                GenerationStrategy.ADAPTIVE: 0.80,
                GenerationStrategy.DIRECT: 0.78
            },
            StoryGenre.LITERARY: {
                GenerationStrategy.ITERATIVE: 0.92,
                GenerationStrategy.ADAPTIVE: 0.88,
                GenerationStrategy.DIRECT: 0.65
            }
        }
        
        # Apply base patterns
        for genre, strategies in base_patterns.items():
            self.genre_strategy_effectiveness[genre] = strategies.copy()
        
        # Initialize complexity mapping
        self.complexity_strategy_map = {
            "low": GenerationStrategy.DIRECT,
            "medium": GenerationStrategy.ADAPTIVE,
            "high": GenerationStrategy.ITERATIVE
        }
    
    async def select_optimal_strategy(
        self,
        requirements: StoryRequirements,
        predictions: GenerationPredictions,
        user_profile: Optional[UserProfile] = None
    ) -> GenerationStrategy:
        """Select optimal generation strategy based on learning and predictions"""
        
        try:
            # Get genre-specific strategy effectiveness
            genre_effectiveness = self.genre_strategy_effectiveness.get(
                requirements.genre, 
                self.genre_strategy_effectiveness[StoryGenre.LITERARY]
            )
            
            # Factor in complexity
            complexity_level = self._assess_complexity_level(requirements, predictions)
            
            # User preference factor
            user_speed_preference = "balanced"
            if user_profile:
                user_speed_preference = user_profile.preferences.preferred_generation_speed
            
            # Calculate strategy scores
            strategy_scores = {}
            for strategy in GenerationStrategy:
                if strategy.value in ["direct", "adaptive", "iterative"]:  # Valid V1.5 strategies
                    base_score = genre_effectiveness.get(strategy, 0.7)
                    
                    # Complexity adjustment
                    complexity_bonus = self._get_complexity_bonus(strategy, complexity_level)
                    
                    # User preference adjustment
                    speed_bonus = self._get_speed_preference_bonus(strategy, user_speed_preference)
                    
                    # Quality prediction adjustment
                    quality_bonus = self._get_quality_prediction_bonus(strategy, predictions)
                    
                    # Historical performance boost
                    history_bonus = self._get_historical_performance_bonus(
                        strategy, requirements.genre, user_profile
                    )
                    
                    final_score = base_score + complexity_bonus + speed_bonus + quality_bonus + history_bonus
                    strategy_scores[strategy] = max(0.0, min(1.0, final_score))
            
            # Select best strategy
            optimal_strategy = max(strategy_scores.items(), key=lambda x: x[1])[0]
            
            logger.info(f"Selected optimal strategy: {optimal_strategy} "
                       f"(score: {strategy_scores[optimal_strategy]:.3f}) for {requirements.genre}")
            
            return optimal_strategy
            
        except Exception as e:
            logger.warning(f"Strategy selection failed, using adaptive: {e}")
            return GenerationStrategy.ADAPTIVE
    
    async def learn_from_generation(
        self,
        requirements: StoryRequirements,
        result: QualityEnhancedResult,
        predictions: GenerationPredictions
    ) -> List[str]:
        """Learn from generation results to improve strategy selection"""
        
        if not self.config.enable_adaptive_learning:
            return []
        
        updates = []
        
        try:
            # Extract performance data
            strategy_used = result.strategy_used if hasattr(result, 'strategy_used') else "adaptive"
            actual_quality = result.quality_metrics.overall_score
            generation_time = result.performance_metrics.total_generation_time
            enhancement_passes = len(result.enhancement_history)
            
            # Calculate effectiveness score (quality per resource unit)
            time_efficiency = actual_quality / max(generation_time, 1.0)
            pass_efficiency = actual_quality / max(enhancement_passes, 1)
            overall_effectiveness = (time_efficiency + pass_efficiency) / 2
            
            # Store performance data
            performance_data = {
                "timestamp": datetime.now(),
                "strategy": strategy_used,
                "genre": requirements.genre,
                "requirements": requirements.dict(),
                "quality": actual_quality,
                "time": generation_time,
                "passes": enhancement_passes,
                "effectiveness": overall_effectiveness,
                "predictions_accuracy": predictions.prediction_confidence
            }
            
            # Store in performance history
            key = f"{requirements.genre}_{strategy_used}"
            self.strategy_performance[key].append(performance_data)
            
            # Update strategy effectiveness for genre
            if requirements.genre in self.genre_strategy_effectiveness:
                strategy_enum = self._string_to_strategy(strategy_used)
                if strategy_enum in self.genre_strategy_effectiveness[requirements.genre]:
                    current_effectiveness = self.genre_strategy_effectiveness[requirements.genre][strategy_enum]
                    
                    # Normalize effectiveness score (0-1)
                    normalized_effectiveness = min(1.0, overall_effectiveness / 10.0)
                    
                    # Update with learning rate
                    learning_rate = self.config.learning_rate
                    updated_effectiveness = (current_effectiveness * (1 - learning_rate) + 
                                           normalized_effectiveness * learning_rate)
                    
                    self.genre_strategy_effectiveness[requirements.genre][strategy_enum] = updated_effectiveness
                    
                    updates.append(f"Updated {strategy_used} effectiveness for {requirements.genre}: "
                                 f"{current_effectiveness:.3f} -> {updated_effectiveness:.3f}")
            
            # Update complexity mapping if significant deviation
            predicted_complexity = self._assess_complexity_level(requirements, predictions)
            if actual_quality > 8.5 and strategy_used != "iterative":
                # High quality achieved without iterative - update complexity mapping
                if predicted_complexity == "high" and strategy_used in ["adaptive", "direct"]:
                    self.complexity_strategy_map[predicted_complexity] = self._string_to_strategy(strategy_used)
                    updates.append(f"Updated complexity mapping: high -> {strategy_used}")
            
            # Prune old performance data
            max_history = self.config.learning_history_window
            for key in self.strategy_performance:
                if len(self.strategy_performance[key]) > max_history:
                    self.strategy_performance[key] = self.strategy_performance[key][-max_history:]
            
            logger.debug(f"Strategy learning updated: {len(updates)} changes")
            return updates
            
        except Exception as e:
            logger.warning(f"Failed to learn from generation: {e}")
            return []
    
    def _assess_complexity_level(self, requirements: StoryRequirements, predictions: GenerationPredictions) -> str:
        """Assess complexity level (low/medium/high)"""
        
        # Word count factor
        word_complexity = 0.0
        if requirements.target_word_count < 1000:
            word_complexity = 0.2
        elif requirements.target_word_count < 3000:
            word_complexity = 0.5
        else:
            word_complexity = 0.8
        
        # Quality prediction complexity
        quality_range = predictions.predicted_quality_range
        quality_complexity = 1.0 - (sum(quality_range) / 2) / 10.0  # Inverse of predicted quality
        
        # Genre complexity
        genre_complexity_map = {
            StoryGenre.LITERARY: 0.9,
            StoryGenre.SCIENCE_FICTION: 0.8,
            StoryGenre.FANTASY: 0.8,
            StoryGenre.MYSTERY: 0.7,
            StoryGenre.ROMANCE: 0.4
        }
        genre_complexity = genre_complexity_map.get(requirements.genre, 0.6)
        
        # Combined complexity
        overall_complexity = (word_complexity + quality_complexity + genre_complexity) / 3
        
        if overall_complexity < 0.4:
            return "low"
        elif overall_complexity < 0.7:
            return "medium"
        else:
            return "high"
    
    def _get_complexity_bonus(self, strategy: GenerationStrategy, complexity_level: str) -> float:
        """Get bonus score for strategy based on complexity"""
        complexity_bonuses = {
            "low": {
                GenerationStrategy.DIRECT: 0.1,
                GenerationStrategy.ADAPTIVE: 0.0,
                GenerationStrategy.ITERATIVE: -0.1
            },
            "medium": {
                GenerationStrategy.DIRECT: -0.05,
                GenerationStrategy.ADAPTIVE: 0.1,
                GenerationStrategy.ITERATIVE: 0.0
            },
            "high": {
                GenerationStrategy.DIRECT: -0.2,
                GenerationStrategy.ADAPTIVE: 0.0,
                GenerationStrategy.ITERATIVE: 0.15
            }
        }
        
        return complexity_bonuses.get(complexity_level, {}).get(strategy, 0.0)
    
    def _get_speed_preference_bonus(self, strategy: GenerationStrategy, preference: str) -> float:
        """Get bonus score for strategy based on user speed preference"""
        speed_bonuses = {
            "fast": {
                GenerationStrategy.DIRECT: 0.15,
                GenerationStrategy.ADAPTIVE: 0.0,
                GenerationStrategy.ITERATIVE: -0.15
            },
            "balanced": {
                GenerationStrategy.DIRECT: 0.0,
                GenerationStrategy.ADAPTIVE: 0.1,
                GenerationStrategy.ITERATIVE: 0.0
            },
            "thorough": {
                GenerationStrategy.DIRECT: -0.1,
                GenerationStrategy.ADAPTIVE: 0.0,
                GenerationStrategy.ITERATIVE: 0.1
            }
        }
        
        return speed_bonuses.get(preference, {}).get(strategy, 0.0)
    
    def _get_quality_prediction_bonus(self, strategy: GenerationStrategy, predictions: GenerationPredictions) -> float:
        """Get bonus score based on quality predictions"""
        predicted_quality = sum(predictions.predicted_quality_range) / 2
        
        if predicted_quality < 7.0:
            # Low predicted quality - favor iterative
            return 0.1 if strategy == GenerationStrategy.ITERATIVE else 0.0
        elif predicted_quality > 8.5:
            # High predicted quality - can use faster methods
            return 0.05 if strategy == GenerationStrategy.DIRECT else 0.0
        
        return 0.0
    
    def _get_historical_performance_bonus(
        self,
        strategy: GenerationStrategy,
        genre: StoryGenre,
        user_profile: Optional[UserProfile]
    ) -> float:
        """Get bonus based on historical performance"""
        
        key = f"{genre}_{strategy.value}"
        if key in self.strategy_performance and len(self.strategy_performance[key]) >= 3:
            # Calculate recent average effectiveness
            recent_data = self.strategy_performance[key][-5:]  # Last 5 generations
            avg_effectiveness = sum(d["effectiveness"] for d in recent_data) / len(recent_data)
            
            # Convert to bonus (-0.1 to +0.1)
            normalized_bonus = (avg_effectiveness / 5.0) - 0.1
            return max(-0.1, min(0.1, normalized_bonus))
        
        return 0.0
    
    def _string_to_strategy(self, strategy_string: str) -> GenerationStrategy:
        """Convert strategy string to enum"""
        strategy_map = {
            "direct": GenerationStrategy.DIRECT,
            "adaptive": GenerationStrategy.ADAPTIVE,
            "iterative": GenerationStrategy.ITERATIVE
        }
        return strategy_map.get(strategy_string, GenerationStrategy.ADAPTIVE)


class PersonalizationEngine:
    """Manages user personalization and preference learning"""
    
    def __init__(self, config: AdaptiveGenerationConfig):
        """Initialize personalization engine - must succeed"""
        self.config = config
        self.user_profiles: Dict[str, UserProfile] = {}
        self.global_patterns: Dict[str, Any] = {}
        self.applied_adaptations: Dict[str, Any] = {}
        
        logger.info("PersonalizationEngine initialized")
    
    async def personalize_quality_config(
        self,
        base_config: QualityConfig,
        user_profile: UserProfile,
        requirements: StoryRequirements,
        predictions: GenerationPredictions
    ) -> QualityConfig:
        """Personalize quality configuration based on user profile"""
        
        try:
            # Start with base configuration
            personalized_config = QualityConfig(**base_config.dict())
            
            # Clear applied adaptations for this session
            self.applied_adaptations.clear()
            
            # Adjust target quality based on user preferences
            if user_profile.preferences.preferred_enhancement_level == "minimal":
                personalized_config.target_quality_score = max(7.0, base_config.target_quality_score - 0.5)
                self.applied_adaptations["target_quality"] = "reduced for minimal enhancement preference"
            elif user_profile.preferences.preferred_enhancement_level == "comprehensive":
                personalized_config.target_quality_score = min(9.5, base_config.target_quality_score + 0.3)
                self.applied_adaptations["target_quality"] = "increased for comprehensive enhancement preference"
            
            # Adjust max passes based on user speed preference
            if user_profile.preferences.preferred_generation_speed == "fast":
                personalized_config.max_enhancement_passes = max(1, base_config.max_enhancement_passes - 1)
                self.applied_adaptations["max_passes"] = "reduced for speed preference"
            elif user_profile.preferences.preferred_generation_speed == "thorough":
                personalized_config.max_enhancement_passes = min(5, base_config.max_enhancement_passes + 1)
                self.applied_adaptations["max_passes"] = "increased for thorough preference"
            
            # Adjust quality dimension weights based on user preferences
            if user_profile.preferences.preferred_quality_dimensions:
                # Apply user's quality dimension preferences
                personalized_weights = base_config.enhancement_strategy_weights.copy()
                
                for dimension, weight in user_profile.preferences.preferred_quality_dimensions.items():
                    if dimension in personalized_weights:
                        # Adjust weight based on user preference (0.5-1.5 multiplier)
                        multiplier = 0.5 + (weight * 1.0)  # weight is 0-1, so multiplier is 0.5-1.5
                        personalized_weights[dimension] *= multiplier
                
                personalized_config.enhancement_strategy_weights = personalized_weights
                self.applied_adaptations["quality_dimensions"] = f"adjusted {len(user_profile.preferences.preferred_quality_dimensions)} dimensions"
            
            # Genre expertise adjustment
            user_expertise = user_profile.preferences.genre_expertise.get(requirements.genre.value, 0.5)
            if user_expertise < 0.3:
                # Low expertise - be more conservative
                personalized_config.quality_convergence_threshold *= 0.8
                self.applied_adaptations["convergence_threshold"] = "reduced for low genre expertise"
            elif user_expertise > 0.8:
                # High expertise - can be more aggressive
                personalized_config.quality_convergence_threshold *= 1.2
                self.applied_adaptations["convergence_threshold"] = "increased for high genre expertise"
            
            # Satisfaction pattern adjustment
            if user_profile.satisfaction_history:
                avg_satisfaction = sum(user_profile.satisfaction_history) / len(user_profile.satisfaction_history)
                if avg_satisfaction < 7.0:
                    # User typically not satisfied - increase quality targets
                    personalized_config.target_quality_score = min(9.5, personalized_config.target_quality_score + 0.5)
                    self.applied_adaptations["satisfaction_adjustment"] = f"increased target for low avg satisfaction ({avg_satisfaction:.1f})"
            
            logger.info(f"Quality config personalized for user {user_profile.user_id}: "
                       f"{len(self.applied_adaptations)} adaptations")
            
            return personalized_config
            
        except Exception as e:
            logger.warning(f"Quality config personalization failed: {e}")
            return base_config
    
    async def calculate_personalization_impact(
        self,
        user_profile: UserProfile,
        requirements: StoryRequirements
    ) -> float:
        """Calculate expected impact of personalization (0-10 scale)"""
        
        impact_factors = []
        
        # User interaction history impact
        if user_profile.interaction_count > 10:
            impact_factors.append(min(2.0, user_profile.interaction_count * 0.1))
        
        # Preference specificity impact
        pref_specificity = len(user_profile.preferences.preferred_quality_dimensions) * 0.3
        impact_factors.append(min(2.0, pref_specificity))
        
        # Genre expertise impact
        user_expertise = user_profile.preferences.genre_expertise.get(requirements.genre.value, 0.5)
        expertise_impact = abs(user_expertise - 0.5) * 4.0  # Max 2.0 impact
        impact_factors.append(expertise_impact)
        
        # Adaptation effectiveness history
        if user_profile.adaptation_effectiveness > 0:
            impact_factors.append(user_profile.adaptation_effectiveness * 3.0)
        
        # Calculate weighted impact
        total_impact = sum(impact_factors)
        normalized_impact = min(10.0, total_impact)
        
        return normalized_impact
    
    async def predict_user_satisfaction(
        self,
        user_profile: UserProfile,
        requirements: StoryRequirements,
        predictions: GenerationPredictions,
        personalized_config: QualityConfig
    ) -> float:
        """Predict user satisfaction with personalized generation (0-10 scale)"""
        
        # Base satisfaction from quality prediction
        predicted_quality = sum(predictions.predicted_quality_range) / 2
        base_satisfaction = predicted_quality
        
        # User preference alignment bonus
        preference_bonus = 0.0
        
        # Speed preference alignment
        if user_profile.preferences.preferred_generation_speed == "fast":
            if predictions.predicted_generation_time < 60:
                preference_bonus += 0.5
        elif user_profile.preferences.preferred_generation_speed == "thorough":
            if predictions.predicted_enhancement_passes >= 2:
                preference_bonus += 0.5
        
        # Quality level alignment
        if user_profile.preferences.preferred_enhancement_level == "comprehensive":
            if personalized_config.target_quality_score >= 8.5:
                preference_bonus += 0.3
        elif user_profile.preferences.preferred_enhancement_level == "minimal":
            if personalized_config.max_enhancement_passes <= 2:
                preference_bonus += 0.3
        
        # Genre expertise factor
        user_expertise = user_profile.preferences.genre_expertise.get(requirements.genre.value, 0.5)
        expertise_bonus = (user_expertise - 0.5) * 0.4  # ±0.2 adjustment
        
        # Historical satisfaction trend
        history_bonus = 0.0
        if user_profile.satisfaction_history:
            recent_trend = user_profile.satisfaction_history[-3:]  # Last 3 interactions
            if len(recent_trend) >= 2:
                trend = (recent_trend[-1] - recent_trend[0]) / len(recent_trend)
                history_bonus = trend * 0.1  # Small trend adjustment
        
        # Calculate final prediction
        final_satisfaction = base_satisfaction + preference_bonus + expertise_bonus + history_bonus
        return max(0.0, min(10.0, final_satisfaction))
    
    async def update_user_profile(
        self,
        user_profile: UserProfile,
        result: QualityEnhancedResult,
        predictions: GenerationPredictions
    ) -> Dict[str, Any]:
        """Update user profile based on generation results"""
        
        if not self.config.enable_adaptive_learning:
            return {}
        
        updates = {}
        
        try:
            # Update interaction count
            user_profile.interaction_count += 1
            updates["interaction_count"] = user_profile.interaction_count
            
            # Infer satisfaction from quality and user behavior
            # (In a real system, this would come from explicit user feedback)
            inferred_satisfaction = self._infer_satisfaction(result, predictions)
            user_profile.satisfaction_history.append(inferred_satisfaction)
            
            # Keep satisfaction history manageable
            if len(user_profile.satisfaction_history) > 20:
                user_profile.satisfaction_history = user_profile.satisfaction_history[-20:]
            
            updates["satisfaction_history"] = len(user_profile.satisfaction_history)
            
            # Update genre expertise based on results
            genre = result.requirements.genre.value
            if genre not in user_profile.preferences.genre_expertise:
                user_profile.preferences.genre_expertise[genre] = 0.5
            
            # Adjust expertise based on quality achievement
            quality_score = result.quality_metrics.overall_score
            if quality_score >= 8.0:
                user_profile.preferences.genre_expertise[genre] = min(1.0, 
                    user_profile.preferences.genre_expertise[genre] + 0.05)
                updates[f"{genre}_expertise"] = "increased"
            elif quality_score < 6.0:
                user_profile.preferences.genre_expertise[genre] = max(0.0,
                    user_profile.preferences.genre_expertise[genre] - 0.05)
                updates[f"{genre}_expertise"] = "decreased"
            
            # Update adaptation effectiveness
            if hasattr(result, 'adaptation_insights'):
                adaptation_effectiveness = getattr(result.adaptation_insights, 'adaptation_effectiveness', 0.0)
                if user_profile.adaptation_effectiveness == 0.0:
                    user_profile.adaptation_effectiveness = adaptation_effectiveness
                else:
                    # Running average
                    user_profile.adaptation_effectiveness = (user_profile.adaptation_effectiveness * 0.8 + 
                                                           adaptation_effectiveness * 0.2)
                updates["adaptation_effectiveness"] = user_profile.adaptation_effectiveness
            
            # Update profile timestamp
            user_profile.profile_updated = datetime.now()
            
            logger.debug(f"User profile updated for {user_profile.user_id}: {len(updates)} changes")
            return updates
            
        except Exception as e:
            logger.warning(f"Failed to update user profile: {e}")
            return {}
    
    async def get_applied_adaptations(self) -> Dict[str, Any]:
        """Get record of adaptations applied in current session"""
        return self.applied_adaptations.copy()
    
    def _infer_satisfaction(self, result: QualityEnhancedResult, predictions: GenerationPredictions) -> float:
        """Infer user satisfaction from generation results (0-10 scale)"""
        
        # Base satisfaction from quality
        quality_score = result.quality_metrics.overall_score
        base_satisfaction = quality_score
        
        # Prediction accuracy bonus (users like predictable results)
        if hasattr(result, 'predicted_vs_actual'):
            prediction_accuracy = result.predicted_vs_actual.overall_prediction_score / 10.0
            accuracy_bonus = prediction_accuracy * 0.5
        else:
            accuracy_bonus = 0.0
        
        # Efficiency bonus (reasonable time/resources)
        if hasattr(result, 'efficiency_metrics'):
            efficiency = result.efficiency_metrics.time_efficiency
            if efficiency > 2.0:  # Good efficiency
                efficiency_bonus = 0.3
            elif efficiency < 1.0:  # Poor efficiency  
                efficiency_bonus = -0.3
            else:
                efficiency_bonus = 0.0
        else:
            efficiency_bonus = 0.0
        
        final_satisfaction = base_satisfaction + accuracy_bonus + efficiency_bonus
        return max(0.0, min(10.0, final_satisfaction))