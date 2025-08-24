"""
AI Story Writer V1.5 - Prediction Engines
Quality and resource prediction systems for adaptive intelligence.
"""

import logging
import math
from typing import Dict, List, Optional, Tuple, Any, NamedTuple
from datetime import datetime, timedelta

from ..models.story_models import (
    AdaptiveGenerationConfig, GenerationPredictions, UserProfile, SystemContext,
    PredictionConfidence
)
from ..models.basic_models import StoryRequirements, StoryGenre, StoryLength
from ..utils import StoryGenerationError

logger = logging.getLogger(__name__)


class QualityPrediction(NamedTuple):
    """Quality prediction result"""
    expected_range: Tuple[float, float]
    confidence: float
    factors: Dict[str, float]


class ResourcePrediction(NamedTuple):
    """Resource prediction result"""
    estimated_time: float
    estimated_tokens: int
    efficiency_score: float
    confidence: float


class EnhancementPrediction(NamedTuple):
    """Enhancement prediction result"""
    expected_passes: int
    confidence: float
    reasoning: str


class QualityPredictionEngine:
    """Predicts story quality outcomes based on requirements and learning data"""
    
    def __init__(self, config: AdaptiveGenerationConfig):
        """Initialize quality prediction engine - must succeed"""
        self.config = config
        self.prediction_history: List[Dict[str, Any]] = []
        self.genre_patterns: Dict[StoryGenre, Dict[str, float]] = self._initialize_genre_patterns()
        self.length_patterns: Dict[StoryLength, Dict[str, float]] = self._initialize_length_patterns()
        
        logger.info("QualityPredictionEngine initialized")
    
    def _initialize_genre_patterns(self) -> Dict[StoryGenre, Dict[str, float]]:
        """Initialize base quality patterns by genre"""
        return {
            StoryGenre.SCIENCE_FICTION: {
                "base_quality": 7.2,
                "complexity_factor": 1.1,
                "enhancement_potential": 0.8,
                "variability": 0.6
            },
            StoryGenre.FANTASY: {
                "base_quality": 7.4,
                "complexity_factor": 1.2,
                "enhancement_potential": 0.9,
                "variability": 0.7
            },
            StoryGenre.MYSTERY: {
                "base_quality": 7.6,
                "complexity_factor": 0.9,
                "enhancement_potential": 0.7,
                "variability": 0.5
            },
            StoryGenre.ROMANCE: {
                "base_quality": 7.3,
                "complexity_factor": 0.8,
                "enhancement_potential": 0.6,
                "variability": 0.4
            },
            StoryGenre.LITERARY: {
                "base_quality": 7.8,
                "complexity_factor": 1.3,
                "enhancement_potential": 0.9,
                "variability": 0.8
            }
        }
    
    def _initialize_length_patterns(self) -> Dict[StoryLength, Dict[str, float]]:
        """Initialize base quality patterns by length"""
        return {
            StoryLength.FLASH: {
                "base_modifier": 0.9,
                "complexity_bonus": 0.2,
                "enhancement_efficiency": 1.2
            },
            StoryLength.SHORT: {
                "base_modifier": 1.0,
                "complexity_bonus": 0.0,
                "enhancement_efficiency": 1.0
            }
        }
    
    async def predict_quality_range(
        self,
        requirements: StoryRequirements,
        user_profile: Optional[UserProfile] = None
    ) -> QualityPrediction:
        """Predict expected quality range for story generation"""
        
        try:
            # Get base patterns
            genre_pattern = self.genre_patterns.get(requirements.genre, self.genre_patterns[StoryGenre.LITERARY])
            length_pattern = self.length_patterns.get(requirements.length, self.length_patterns[StoryLength.SHORT])
            
            # Calculate base quality prediction
            base_quality = genre_pattern["base_quality"] * length_pattern["base_modifier"]
            
            # Factor in complexity
            complexity_score = self._calculate_complexity_score(requirements)
            complexity_adjustment = complexity_score * genre_pattern["complexity_factor"] * 0.3
            
            # User expertise factor
            user_factor = 0.0
            if user_profile:
                user_expertise = user_profile.preferences.genre_expertise.get(requirements.genre.value, 0.5)
                user_factor = (user_expertise - 0.5) * 0.4  # ±0.2 adjustment
            
            # Theme complexity factor
            theme_complexity = self._assess_theme_complexity(requirements.theme or "")
            theme_adjustment = theme_complexity * 0.2
            
            # Calculate predicted quality
            predicted_quality = base_quality + complexity_adjustment + user_factor + theme_adjustment
            
            # Calculate variance based on factors
            variance = genre_pattern["variability"] * (1 + complexity_score * 0.5)
            quality_range = (
                max(0.0, predicted_quality - variance),
                min(10.0, predicted_quality + variance)
            )
            
            # Calculate confidence based on data availability and patterns
            confidence = self._calculate_prediction_confidence(
                requirements, user_profile, complexity_score
            )
            
            # Quality factors breakdown
            factors = {
                "genre_base": genre_pattern["base_quality"],
                "length_modifier": length_pattern["base_modifier"],
                "complexity": complexity_adjustment,
                "user_expertise": user_factor,
                "theme_complexity": theme_adjustment,
                "predicted_center": predicted_quality,
                "variance": variance
            }
            
            logger.debug(f"Quality prediction: {quality_range} (confidence: {confidence:.2f})")
            
            return QualityPrediction(
                expected_range=quality_range,
                confidence=confidence,
                factors=factors
            )
            
        except Exception as e:
            raise StoryGenerationError(f"Quality prediction failed: {e}")
    
    async def predict_enhancement_passes(
        self,
        requirements: StoryRequirements,
        quality_prediction: QualityPrediction
    ) -> EnhancementPrediction:
        """Predict number of enhancement passes needed"""
        
        try:
            # Get target quality from config
            target_quality = self.config.quality_config.target_quality_score
            predicted_initial = sum(quality_prediction.expected_range) / 2
            
            # Calculate quality gap
            quality_gap = max(0.0, target_quality - predicted_initial)
            
            # Estimate passes based on quality gap and enhancement potential
            genre_pattern = self.genre_patterns.get(requirements.genre, self.genre_patterns[StoryGenre.LITERARY])
            enhancement_potential = genre_pattern["enhancement_potential"]
            
            # Passes calculation
            if quality_gap <= 0.1:
                expected_passes = 0
                reasoning = "Initial quality already meets target"
            elif quality_gap <= 0.5:
                expected_passes = 1
                reasoning = "Minor enhancement needed"
            elif quality_gap <= 1.0:
                expected_passes = min(2, int(quality_gap / (enhancement_potential * 0.4)) + 1)
                reasoning = "Moderate enhancement required"
            else:
                expected_passes = min(self.config.quality_config.max_enhancement_passes, 
                                    int(quality_gap / (enhancement_potential * 0.3)) + 1)
                reasoning = "Significant enhancement needed"
            
            # Confidence based on prediction confidence and enhancement patterns
            confidence = quality_prediction.confidence * 0.9  # Slightly less confident about enhancement
            
            logger.debug(f"Enhancement prediction: {expected_passes} passes ({reasoning})")
            
            return EnhancementPrediction(
                expected_passes=expected_passes,
                confidence=confidence,
                reasoning=reasoning
            )
            
        except Exception as e:
            raise StoryGenerationError(f"Enhancement prediction failed: {e}")
    
    async def update_prediction_models(
        self,
        requirements: StoryRequirements,
        actual_result: Any,
        predictions: GenerationPredictions
    ) -> List[str]:
        """Update prediction models based on actual results"""
        
        if not self.config.enable_adaptive_learning:
            return []
        
        updates = []
        
        try:
            # Calculate prediction errors
            actual_quality = actual_result.quality_metrics.overall_score
            predicted_range = predictions.predicted_quality_range
            prediction_error = actual_quality - sum(predicted_range) / 2
            
            # Update genre patterns if significant error
            if abs(prediction_error) > 0.5:
                genre_pattern = self.genre_patterns[requirements.genre]
                learning_rate = self.config.learning_rate
                
                # Adjust base quality
                genre_pattern["base_quality"] += prediction_error * learning_rate * 0.1
                updates.append(f"Updated {requirements.genre} base quality by {prediction_error * learning_rate * 0.1:.3f}")
                
                # Adjust variability based on prediction accuracy
                if abs(prediction_error) > genre_pattern["variability"]:
                    genre_pattern["variability"] *= 1.05  # Increase variability
                    updates.append(f"Increased {requirements.genre} variability to {genre_pattern['variability']:.3f}")
            
            # Store prediction for analysis
            self.prediction_history.append({
                "timestamp": datetime.now(),
                "requirements": requirements.dict(),
                "predicted_range": predicted_range,
                "actual_quality": actual_quality,
                "error": prediction_error
            })
            
            # Keep history manageable
            if len(self.prediction_history) > self.config.learning_history_window:
                self.prediction_history = self.prediction_history[-self.config.learning_history_window:]
            
            logger.debug(f"Prediction models updated: {len(updates)} changes")
            return updates
            
        except Exception as e:
            logger.warning(f"Failed to update prediction models: {e}")
            return []
    
    def _calculate_complexity_score(self, requirements: StoryRequirements) -> float:
        """Calculate complexity score for requirements (0-1)"""
        complexity = 0.0
        
        # Length complexity
        length_complexity = {
            StoryLength.FLASH: 0.2,
            StoryLength.SHORT: 0.4
        }
        complexity += length_complexity.get(requirements.length, 0.4)
        
        # Word count complexity (normalized)
        word_ratio = requirements.target_word_count / 2000  # 2000 as baseline
        complexity += min(0.3, word_ratio * 0.3)
        
        # Theme complexity based on theme analysis
        theme_complexity = self._assess_theme_complexity(requirements.theme or "")
        complexity += theme_complexity * 0.3
        
        return min(1.0, complexity)
    
    def _assess_theme_complexity(self, prompt: str) -> float:
        """Assess thematic complexity of prompt (0-1)"""
        if not prompt:
            return 0.0
        
        complexity_indicators = [
            "philosophical", "existential", "metaphysical", "psychological",
            "complex", "intricate", "layered", "nuanced", "abstract",
            "paradox", "dilemma", "conflict", "tension", "ambiguous"
        ]
        
        prompt_lower = prompt.lower()
        indicator_count = sum(1 for indicator in complexity_indicators if indicator in prompt_lower)
        
        # Length factor
        length_factor = min(1.0, len(prompt.split()) / 50)  # 50 words as baseline
        
        return min(1.0, (indicator_count * 0.1) + length_factor)
    
    def _calculate_prediction_confidence(
        self,
        requirements: StoryRequirements,
        user_profile: Optional[UserProfile],
        complexity_score: float
    ) -> float:
        """Calculate confidence in prediction (0-1)"""
        
        base_confidence = 0.7  # Base confidence level
        
        # Reduce confidence for high complexity
        complexity_penalty = complexity_score * 0.2
        
        # Increase confidence if we have user history
        user_bonus = 0.0
        if user_profile and user_profile.interaction_count > 5:
            user_bonus = min(0.15, user_profile.interaction_count * 0.01)
        
        # Genre familiarity (from training data)
        genre_confidence = {
            StoryGenre.SCIENCE_FICTION: 0.85,
            StoryGenre.FANTASY: 0.80,
            StoryGenre.MYSTERY: 0.90,
            StoryGenre.ROMANCE: 0.88,
            StoryGenre.LITERARY: 0.75  # More variable
        }
        genre_bonus = (genre_confidence.get(requirements.genre, 0.8) - 0.8) * 0.2
        
        final_confidence = base_confidence - complexity_penalty + user_bonus + genre_bonus
        return max(0.3, min(0.95, final_confidence))


class ResourcePredictionEngine:
    """Predicts computational resource usage for story generation"""
    
    def __init__(self, config: AdaptiveGenerationConfig):
        """Initialize resource prediction engine - must succeed"""
        self.config = config
        self.resource_history: List[Dict[str, Any]] = []
        
        # Base resource patterns
        self.base_patterns = {
            "tokens_per_word": 1.3,  # Average tokens per output word
            "time_per_token": 0.05,  # Seconds per token
            "enhancement_multiplier": 1.4,  # Resource multiplication per enhancement pass
            "complexity_multiplier": 1.2  # Resource multiplication for complex requests
        }
        
        logger.info("ResourcePredictionEngine initialized")
    
    async def predict_resource_usage(
        self,
        requirements: StoryRequirements,
        quality_prediction: QualityPrediction,
        system_context: Optional[SystemContext] = None
    ) -> ResourcePrediction:
        """Predict computational resource usage"""
        
        try:
            # Base token estimation
            target_words = requirements.target_word_count
            base_tokens = int(target_words * self.base_patterns["tokens_per_word"])
            
            # Enhancement overhead
            predicted_passes = max(1, int(quality_prediction.factors.get("predicted_center", 7.0) < self.config.quality_config.target_quality_score))
            enhancement_overhead = (predicted_passes - 1) * self.base_patterns["enhancement_multiplier"]
            
            # Complexity overhead
            complexity_factor = quality_prediction.factors.get("complexity", 0.0)
            complexity_overhead = complexity_factor * self.base_patterns["complexity_multiplier"]
            
            # Total token estimation
            total_multiplier = 1.0 + enhancement_overhead + complexity_overhead
            estimated_tokens = int(base_tokens * total_multiplier)
            
            # Time estimation
            base_time = estimated_tokens * self.base_patterns["time_per_token"]
            
            # System load adjustment
            load_factor = 1.0
            if system_context and system_context.current_load > 0.7:
                load_factor = 1.2 + (system_context.current_load - 0.7) * 2  # Exponential slowdown
            
            estimated_time = base_time * load_factor
            
            # Efficiency score (quality per resource unit)
            predicted_quality = sum(quality_prediction.expected_range) / 2
            efficiency_score = (predicted_quality / max(estimated_tokens / 1000, 1.0)) * 2  # Normalized
            
            # Confidence based on historical data and system state
            confidence = self._calculate_resource_confidence(requirements, system_context)
            
            logger.debug(f"Resource prediction: {estimated_tokens} tokens, {estimated_time:.1f}s "
                        f"(efficiency: {efficiency_score:.2f})")
            
            return ResourcePrediction(
                estimated_time=estimated_time,
                estimated_tokens=estimated_tokens,
                efficiency_score=min(10.0, efficiency_score),
                confidence=confidence
            )
            
        except Exception as e:
            raise StoryGenerationError(f"Resource prediction failed: {e}")
    
    def _calculate_resource_confidence(
        self,
        requirements: StoryRequirements,
        system_context: Optional[SystemContext]
    ) -> float:
        """Calculate confidence in resource predictions"""
        
        base_confidence = 0.8
        
        # Reduce confidence for unusual word counts
        typical_range = (500, 5000)
        if not (typical_range[0] <= requirements.target_word_count <= typical_range[1]):
            base_confidence -= 0.1
        
        # Reduce confidence if system under high load
        if system_context and system_context.current_load > 0.8:
            base_confidence -= 0.2
        
        # Historical data confidence boost
        if len(self.resource_history) > 10:
            base_confidence += 0.1
        
        return max(0.5, min(0.95, base_confidence))