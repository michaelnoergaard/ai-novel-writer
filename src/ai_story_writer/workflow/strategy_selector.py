"""
Strategy Selector - Version 1.3 Implementation
Intelligent selection of optimal generation strategies based on requirements analysis
"""

import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from ..models.basic_models import StoryRequirements, StoryGenre, StoryLength
from ..models.v13_models import (
    GenerationStrategy, StrategyRecommendation, RequirementAnalysis
)
from ..utils.config import StoryGenerationError

# Setup logging
logger = logging.getLogger(__name__)


class StrategySelector:
    """
    Analyzes story requirements and selects the optimal generation strategy
    based on complexity, historical performance, and resource constraints.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Strategy performance history (would be persisted in production)
        self.strategy_performance: Dict[str, List[Dict[str, Any]]] = {
            strategy.value: [] for strategy in GenerationStrategy
        }
        
        # Configuration settings
        self.adaptive_threshold = self.config.get('adaptive_threshold', 0.8)
        self.simple_story_max_words = self.config.get('simple_story_max_words', 1000)
        self.complex_story_min_words = self.config.get('complex_story_min_words', 1500)
        self.enable_strategy_learning = self.config.get('enable_strategy_learning', True)
        
        # Genre complexity mapping
        self.genre_complexity = {
            StoryGenre.LITERARY: 0.8,      # High complexity - character and theme focus
            StoryGenre.MYSTERY: 0.7,       # Medium-high - structure and plot critical
            StoryGenre.SCIENCE_FICTION: 0.9,  # High complexity - world-building
            StoryGenre.FANTASY: 0.9,       # High complexity - world-building
            StoryGenre.ROMANCE: 0.6        # Medium complexity - relationship focus
        }
        
        logger.info("StrategySelector initialized")
    
    def select_strategy(self, requirements: StoryRequirements) -> StrategyRecommendation:
        """
        Select the optimal generation strategy based on requirements analysis
        
        Args:
            requirements: Story generation requirements
            
        Returns:
            StrategyRecommendation with selected strategy and alternatives
        """
        try:
            logger.debug(f"Selecting strategy for {requirements.genre.value} story ({requirements.target_word_count} words)")
            
            # Analyze requirements complexity
            analysis = self.analyze_requirements(requirements)
            
            # Get strategy recommendations
            strategy_scores = self._score_strategies(requirements, analysis)
            
            # Select best strategy
            best_strategy = max(strategy_scores.items(), key=lambda x: x[1]['score'])
            strategy_name, strategy_data = best_strategy
            
            # Build recommendation
            recommendation = StrategyRecommendation(
                recommended_strategy=GenerationStrategy(strategy_name),
                confidence=strategy_data['confidence'],
                reasoning=strategy_data['reasoning'],
                estimated_time=strategy_data['estimated_time'],
                estimated_quality=strategy_data['estimated_quality']
            )
            
            # Add alternatives
            sorted_strategies = sorted(
                strategy_scores.items(), 
                key=lambda x: x[1]['score'], 
                reverse=True
            )[1:3]  # Top 2 alternatives
            
            for alt_name, alt_data in sorted_strategies:
                recommendation.alternatives.append({
                    'strategy': GenerationStrategy(alt_name),
                    'confidence': alt_data['confidence'],
                    'reasoning': alt_data['reasoning'],
                    'estimated_time': alt_data['estimated_time']
                })
            
            logger.info(f"Selected strategy: {strategy_name} (confidence: {strategy_data['confidence']:.2f})")
            return recommendation
            
        except Exception as e:
            logger.error(f"Strategy selection failed: {e}")
            # Fallback to adaptive strategy
            return StrategyRecommendation(
                recommended_strategy=GenerationStrategy.ADAPTIVE,
                confidence=0.5,
                reasoning=f"Fallback strategy due to selection error: {e}",
                estimated_time=180.0,
                estimated_quality=7.0
            )
    
    def analyze_requirements(self, requirements: StoryRequirements) -> RequirementAnalysis:
        """
        Analyze story requirements to determine complexity and feasibility
        
        Args:
            requirements: Story generation requirements
            
        Returns:
            RequirementAnalysis with detailed assessment
        """
        try:
            # Word count complexity
            word_count_factor = self._analyze_word_count_complexity(requirements.target_word_count)
            
            # Genre complexity
            genre_complexity = self.genre_complexity.get(requirements.genre, 0.7)
            
            # Theme complexity
            theme_complexity = self._analyze_theme_complexity(requirements.theme)
            
            # Setting specificity
            setting_complexity = self._analyze_setting_complexity(requirements.setting)
            
            # Overall complexity score
            complexity_factors = [word_count_factor, genre_complexity, theme_complexity, setting_complexity]
            complexity_score = sum(complexity_factors) / len(complexity_factors)
            
            # Feasibility assessment
            feasibility_score = self._assess_feasibility(requirements, complexity_score)
            
            # Determine difficulty level
            if complexity_score < 0.4:
                difficulty = "easy"
            elif complexity_score < 0.7:
                difficulty = "medium"
            else:
                difficulty = "hard"
            
            analysis = RequirementAnalysis(
                complexity_score=complexity_score,
                feasibility_score=feasibility_score,
                estimated_difficulty=difficulty,
                word_count_feasibility=word_count_factor,
                genre_familiarity=1.0 - genre_complexity,  # Inverse of complexity
                theme_complexity=theme_complexity,
                setting_specificity=setting_complexity
            )
            
            # Add recommendations
            analysis.recommended_tools = self._recommend_tools(requirements, analysis)
            analysis.potential_challenges = self._identify_challenges(requirements, analysis)
            analysis.success_predictors = self._identify_success_predictors(requirements, analysis)
            
            logger.debug(f"Requirements analysis: complexity={complexity_score:.2f}, feasibility={feasibility_score:.2f}")
            return analysis
            
        except Exception as e:
            logger.error(f"Requirements analysis failed: {e}")
            # Return default analysis
            return RequirementAnalysis(
                complexity_score=0.5,
                feasibility_score=0.8,
                estimated_difficulty="medium",
                word_count_feasibility=0.8,
                genre_familiarity=0.7,
                theme_complexity=0.5,
                setting_specificity=0.5
            )
    
    def record_strategy_performance(
        self,
        strategy: GenerationStrategy,
        requirements: StoryRequirements,
        success: bool,
        quality_score: float,
        generation_time: float,
        error_count: int = 0
    ) -> None:
        """
        Record strategy performance for learning and optimization
        
        Args:
            strategy: Strategy that was used
            requirements: Requirements that were processed
            success: Whether generation was successful
            quality_score: Quality score achieved
            generation_time: Time taken for generation
            error_count: Number of errors encountered
        """
        if not self.enable_strategy_learning:
            return
        
        try:
            performance_record = {
                'timestamp': datetime.now().isoformat(),
                'genre': requirements.genre.value,
                'word_count': requirements.target_word_count,
                'theme_provided': bool(requirements.theme),
                'setting_provided': bool(requirements.setting),
                'success': success,
                'quality_score': quality_score,
                'generation_time': generation_time,
                'error_count': error_count
            }
            
            self.strategy_performance[strategy.value].append(performance_record)
            
            # Keep only recent performance data (last 100 records)
            if len(self.strategy_performance[strategy.value]) > 100:
                self.strategy_performance[strategy.value] = self.strategy_performance[strategy.value][-100:]
            
            logger.debug(f"Recorded performance for {strategy.value}: success={success}, quality={quality_score:.1f}")
            
        except Exception as e:
            logger.warning(f"Failed to record strategy performance: {e}")
    
    def get_strategy_statistics(self) -> Dict[str, Dict[str, Any]]:
        """Get performance statistics for all strategies"""
        stats = {}
        
        for strategy_name, records in self.strategy_performance.items():
            if not records:
                stats[strategy_name] = {
                    'total_uses': 0,
                    'success_rate': 0.0,
                    'avg_quality': 0.0,
                    'avg_time': 0.0
                }
                continue
            
            successful_records = [r for r in records if r['success']]
            
            stats[strategy_name] = {
                'total_uses': len(records),
                'success_rate': len(successful_records) / len(records),
                'avg_quality': sum(r['quality_score'] for r in successful_records) / max(len(successful_records), 1),
                'avg_time': sum(r['generation_time'] for r in records) / len(records),
                'avg_errors': sum(r['error_count'] for r in records) / len(records)
            }
        
        return stats
    
    def _score_strategies(
        self,
        requirements: StoryRequirements,
        analysis: RequirementAnalysis
    ) -> Dict[str, Dict[str, Any]]:
        """Score all available strategies for the given requirements"""
        
        scores = {}
        
        # Score DIRECT strategy
        scores['direct'] = self._score_direct_strategy(requirements, analysis)
        
        # Score OUTLINE strategy
        scores['outline'] = self._score_outline_strategy(requirements, analysis)
        
        # Score ITERATIVE strategy
        scores['iterative'] = self._score_iterative_strategy(requirements, analysis)
        
        # Score ADAPTIVE strategy
        scores['adaptive'] = self._score_adaptive_strategy(requirements, analysis)
        
        return scores
    
    def _score_direct_strategy(self, requirements: StoryRequirements, analysis: RequirementAnalysis) -> Dict[str, Any]:
        """Score the direct generation strategy"""
        
        # Direct works best for simple, short stories
        complexity_penalty = analysis.complexity_score * 0.3
        word_count_bonus = 0.2 if requirements.target_word_count <= self.simple_story_max_words else 0.0
        
        base_score = 0.7
        score = base_score - complexity_penalty + word_count_bonus
        
        # Historical performance adjustment
        historical_bonus = self._get_historical_performance_bonus('direct', requirements)
        score += historical_bonus
        
        confidence = min(max(score, 0.3), 0.9)
        
        return {
            'score': score,
            'confidence': confidence,
            'reasoning': f"Direct strategy suitable for {'simple' if analysis.complexity_score < 0.5 else 'moderately complex'} requirements",
            'estimated_time': 60.0 + requirements.target_word_count * 0.02,
            'estimated_quality': 7.0 - analysis.complexity_score * 2.0
        }
    
    def _score_outline_strategy(self, requirements: StoryRequirements, analysis: RequirementAnalysis) -> Dict[str, Any]:
        """Score the outline-based strategy"""
        
        # Outline works well for structured stories and medium complexity
        complexity_bonus = min(analysis.complexity_score * 0.4, 0.3)
        structure_bonus = 0.2 if requirements.genre in [StoryGenre.MYSTERY, StoryGenre.LITERARY] else 0.1
        
        base_score = 0.8
        score = base_score + complexity_bonus + structure_bonus
        
        # Historical performance adjustment
        historical_bonus = self._get_historical_performance_bonus('outline', requirements)
        score += historical_bonus
        
        confidence = min(max(score, 0.4), 0.95)
        
        return {
            'score': score,
            'confidence': confidence,
            'reasoning': "Outline strategy provides structure for well-planned narratives",
            'estimated_time': 120.0 + requirements.target_word_count * 0.03,
            'estimated_quality': 7.5 + analysis.complexity_score * 1.0
        }
    
    def _score_iterative_strategy(self, requirements: StoryRequirements, analysis: RequirementAnalysis) -> Dict[str, Any]:
        """Score the iterative improvement strategy"""
        
        # Iterative works best for high complexity and quality requirements
        complexity_bonus = analysis.complexity_score * 0.7  # Increased from 0.5
        quality_bonus = 0.5 if requirements.target_word_count >= self.complex_story_min_words else 0.1  # Increased from 0.3
        
        # Additional bonus for word counts above 1800 to ensure longer stories use iterative
        length_bonus = 0.3 if requirements.target_word_count >= 1800 else 0.0
        
        base_score = 0.7  # Increased from 0.6
        score = base_score + complexity_bonus + quality_bonus + length_bonus
        
        # Reduced time penalty
        time_penalty = 0.05  # Reduced from 0.1
        score -= time_penalty
        
        # Historical performance adjustment
        historical_bonus = self._get_historical_performance_bonus('iterative', requirements)
        score += historical_bonus
        
        confidence = min(max(score, 0.3), 0.95)  # Increased max confidence
        
        return {
            'score': score,
            'confidence': confidence,
            'reasoning': "Iterative strategy provides highest quality through multiple refinement passes, especially for longer stories",
            'estimated_time': 240.0 + requirements.target_word_count * 0.05,
            'estimated_quality': 8.0 + analysis.complexity_score * 0.5
        }
    
    def _score_adaptive_strategy(self, requirements: StoryRequirements, analysis: RequirementAnalysis) -> Dict[str, Any]:
        """Score the adaptive strategy"""
        
        # Adaptive is generally good but not specialized
        base_score = 0.75
        
        # Bonus for uncertain or mixed complexity
        uncertainty_bonus = 0.1 if 0.4 <= analysis.complexity_score <= 0.7 else 0.0
        
        score = base_score + uncertainty_bonus
        
        # Historical performance adjustment
        historical_bonus = self._get_historical_performance_bonus('adaptive', requirements)
        score += historical_bonus
        
        confidence = min(max(score, 0.5), 0.85)
        
        return {
            'score': score,
            'confidence': confidence,
            'reasoning': "Adaptive strategy dynamically adjusts approach based on content development",
            'estimated_time': 150.0 + requirements.target_word_count * 0.035,
            'estimated_quality': 7.2 + analysis.complexity_score * 0.8
        }
    
    def _get_historical_performance_bonus(self, strategy: str, requirements: StoryRequirements) -> float:
        """Get performance bonus based on historical data"""
        if not self.enable_strategy_learning:
            return 0.0
        
        records = self.strategy_performance.get(strategy, [])
        if not records:
            return 0.0
        
        # Filter records for similar requirements
        similar_records = [
            r for r in records
            if (r['genre'] == requirements.genre.value and
                abs(r['word_count'] - requirements.target_word_count) < requirements.target_word_count * 0.3)
        ]
        
        if not similar_records:
            return 0.0
        
        # Calculate performance bonus
        avg_success = sum(r['success'] for r in similar_records) / len(similar_records)
        avg_quality = sum(r['quality_score'] for r in similar_records if r['success']) / max(1, sum(r['success'] for r in similar_records))
        
        performance_bonus = (avg_success - 0.8) * 0.2 + (avg_quality - 7.0) * 0.05
        
        return max(min(performance_bonus, 0.2), -0.1)  # Cap bonus/penalty
    
    def _analyze_word_count_complexity(self, word_count: int) -> float:
        """Analyze complexity based on target word count"""
        if word_count <= 500:
            return 0.2  # Very simple
        elif word_count <= 1000:
            return 0.4  # Simple
        elif word_count <= 1500:
            return 0.6  # Medium
        elif word_count <= 3000:
            return 0.8  # Complex - includes 2000 word stories
        elif word_count <= 5000:
            return 0.9  # Very complex
        else:
            return 1.0  # Extremely complex
    
    def _analyze_theme_complexity(self, theme: Optional[str]) -> float:
        """Analyze complexity based on theme specificity"""
        if not theme:
            return 0.1  # No theme constraint
        
        theme_words = theme.lower().split()
        
        # Simple heuristics for theme complexity
        if len(theme_words) == 1:
            return 0.3  # Simple theme
        elif len(theme_words) <= 3:
            return 0.5  # Medium theme
        else:
            return 0.7  # Complex theme
    
    def _analyze_setting_complexity(self, setting: Optional[str]) -> float:
        """Analyze complexity based on setting specificity"""
        if not setting:
            return 0.1  # No setting constraint
        
        setting_words = setting.lower().split()
        
        # Simple heuristics for setting complexity
        if len(setting_words) <= 2:
            return 0.3  # Simple setting
        elif len(setting_words) <= 5:
            return 0.5  # Medium setting
        else:
            return 0.7  # Complex setting
    
    def _assess_feasibility(self, requirements: StoryRequirements, complexity_score: float) -> float:
        """Assess overall feasibility of the requirements"""
        
        # Base feasibility
        base_feasibility = 0.9
        
        # Complexity penalty
        complexity_penalty = complexity_score * 0.2
        
        # Word count feasibility
        word_count_penalty = 0.0
        if requirements.target_word_count > 7000:
            word_count_penalty = 0.1
        elif requirements.target_word_count < 100:
            word_count_penalty = 0.2
        
        feasibility = base_feasibility - complexity_penalty - word_count_penalty
        
        return max(min(feasibility, 1.0), 0.3)
    
    def _recommend_tools(self, requirements: StoryRequirements, analysis: RequirementAnalysis) -> List[str]:
        """Recommend tools based on requirements analysis"""
        tools = ['get_genre_guidelines', 'validate_story_requirements']
        
        if analysis.complexity_score > 0.5:
            tools.append('generate_story_outline')
        
        if requirements.theme:
            tools.append('get_theme_integration_guidance')
        
        if analysis.complexity_score > 0.7:
            tools.extend(['get_character_guidelines', 'validate_word_count_precise'])
        
        return tools
    
    def _identify_challenges(self, requirements: StoryRequirements, analysis: RequirementAnalysis) -> List[str]:
        """Identify potential challenges based on analysis"""
        challenges = []
        
        if analysis.complexity_score > 0.8:
            challenges.append("High complexity requirements may require multiple iterations")
        
        if requirements.target_word_count > 5000:
            challenges.append("Long story length may impact coherence and pacing")
        
        if requirements.genre in [StoryGenre.SCIENCE_FICTION, StoryGenre.FANTASY]:
            challenges.append("World-building requirements may increase generation complexity")
        
        if analysis.theme_complexity > 0.6:
            challenges.append("Complex theme integration may require careful handling")
        
        return challenges
    
    def _identify_success_predictors(self, requirements: StoryRequirements, analysis: RequirementAnalysis) -> List[str]:
        """Identify factors that predict successful generation"""
        predictors = []
        
        if analysis.feasibility_score > 0.8:
            predictors.append("High feasibility score indicates good success potential")
        
        if requirements.target_word_count in range(1000, 3000):
            predictors.append("Target word count is in optimal range for quality generation")
        
        if requirements.theme and analysis.theme_complexity < 0.5:
            predictors.append("Clear, simple theme provides good guidance")
        
        if requirements.genre in [StoryGenre.LITERARY, StoryGenre.ROMANCE]:
            predictors.append("Genre has well-established conventions for reliable generation")
        
        return predictors