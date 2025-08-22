"""
V1.3 Enhanced Dependencies - Workflow-Aware Story Generation
Extended dependencies with workflow orchestration, quality assessment, and performance monitoring
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from ..models.basic_models import StoryGenre, StoryLength, StoryRequirements
from ..models.v13_models import (
    GenerationStrategy, WorkflowConfiguration, QualityMetrics,
    RequirementAnalysis, StrategyRecommendation
)
from ..workflow import QualityAssessor, StrategySelector, PerformanceMonitor

# Setup logging
logger = logging.getLogger(__name__)


class V13StoryDependencies:
    """
    Enhanced dependencies for V1.3 story agent with workflow orchestration,
    quality assessment, and intelligent strategy selection capabilities.
    """
    
    def __init__(self, config: Optional[WorkflowConfiguration] = None):
        self.config = config or WorkflowConfiguration()
        
        # Initialize workflow components
        self.quality_assessor = QualityAssessor()
        self.strategy_selector = StrategySelector()
        self.performance_monitor = PerformanceMonitor()
        
        # Enhanced genre guidelines with workflow considerations
        self.genre_guidelines = {
            StoryGenre.LITERARY: """
            Focus on character development, internal conflict, and meaningful themes. 
            Use subtle, elegant prose with deep psychological insight. Emphasize emotional truth over plot mechanics.
            Explore human nature, relationships, and universal experiences.
            
            **Workflow Recommendations:**
            - Use outline strategy for complex character arcs
            - Employ iterative strategy for thematic depth
            - Apply enhanced validation for literary quality
            """,
            
            StoryGenre.MYSTERY: """
            Include a central puzzle or crime to solve. Build suspense through clues and red herrings. 
            Provide a satisfying resolution that feels both surprising and inevitable. Focus on investigation, deduction, 
            and revelation. Maintain logical consistency throughout.
            
            **Workflow Recommendations:**
            - Outline strategy essential for plot consistency
            - Use quality assessment for logical coherence
            - Monitor pacing throughout generation
            """,
            
            StoryGenre.SCIENCE_FICTION: """
            Explore technological, scientific, or futuristic concepts. Build coherent world-building that supports the narrative.
            Balance scientific plausibility with engaging storytelling. Consider social, ethical, or philosophical implications
            of technological advancement.
            
            **Workflow Recommendations:**
            - Iterative strategy for world-building consistency
            - Enhanced validation for scientific coherence
            - Quality assessment for originality
            """,
            
            StoryGenre.FANTASY: """
            Create immersive magical or supernatural worlds with consistent rules and systems.
            Develop rich world-building, mythology, and magical elements. Focus on heroic journeys, 
            moral conflicts, and the struggle between good and evil.
            
            **Workflow Recommendations:**
            - Outline strategy for world-building structure
            - Iterative refinement for fantasy elements
            - Quality assessment for internal consistency
            """,
            
            StoryGenre.ROMANCE: """
            Center the narrative on developing romantic relationships between characters.
            Build emotional tension, character chemistry, and satisfying romantic resolution.
            Focus on emotional authenticity and relationship dynamics.
            
            **Workflow Recommendations:**
            - Direct or outline strategy based on complexity
            - Quality assessment for emotional authenticity
            - Character development validation
            """
        }
        
        # Enhanced length guidelines with workflow strategies
        self.length_guidelines = {
            StoryLength.FLASH: """
            Tell a complete story meeting the EXACT target word count specified in requirements. 
            Focus on a single moment, revelation, or emotional truth. Every word must count. 
            Create immediate impact with efficient storytelling. Often works best with a twist, 
            epiphany, or powerful emotional moment.
            
            **IMPORTANT:** Always write to meet the precise target word count specified in requirements.
            
            **Workflow Strategy:** Direct generation is typically most effective for flash fiction.
            Focus on precision and economy of language. Use quality assessment for impact measurement.
            """,
            
            StoryLength.SHORT: """
            Develop a full narrative arc meeting the EXACT target word count specified in requirements. 
            Include character development, plot progression, and satisfying resolution. Allow for subplot 
            development and richer world-building. Can explore complex themes and character relationships.
            
            **IMPORTANT:** Always write to meet the precise target word count - do not default to 1000 words.
            
            **Workflow Strategy:** Outline or iterative strategies recommended for longer pieces.
            Use comprehensive quality assessment and performance monitoring.
            """
        }
        
        # Workflow-specific guidelines
        self.workflow_strategies = {
            GenerationStrategy.DIRECT: """
            Single-pass generation suitable for simple, straightforward stories.
            Best for flash fiction, clear requirements, and time-sensitive generation.
            Minimal overhead with basic quality validation.
            """,
            
            GenerationStrategy.OUTLINE: """
            Two-phase generation: outline creation followed by story writing.
            Excellent for structured narratives, complex plots, and ensuring coherence.
            Provides foundation for consistent story development.
            """,
            
            GenerationStrategy.ITERATIVE: """
            Multiple-pass generation with quality improvement between iterations.
            Best for high-quality requirements, complex themes, and detailed character development.
            Highest quality output with increased generation time.
            """,
            
            GenerationStrategy.ADAPTIVE: """
            Dynamic strategy selection based on requirements analysis and real-time assessment.
            Balances quality and efficiency by choosing optimal approach for specific requirements.
            Recommended for varied or uncertain requirements.
            """
        }
        
        # Quality assessment criteria
        self.quality_criteria = {
            'structure': {
                'weight': 0.20,
                'description': 'Clear beginning, middle, end with proper narrative flow',
                'assessment_method': 'automated_structure_analysis'
            },
            'coherence': {
                'weight': 0.20,
                'description': 'Logical consistency and smooth transitions',
                'assessment_method': 'coherence_scoring'
            },
            'character_development': {
                'weight': 0.15,
                'description': 'Character depth, motivation, and growth',
                'assessment_method': 'character_analysis'
            },
            'genre_compliance': {
                'weight': 0.15,
                'description': 'Adherence to genre conventions and expectations',
                'assessment_method': 'genre_validation'
            },
            'theme_integration': {
                'weight': 0.10,
                'description': 'Natural incorporation of specified themes',
                'assessment_method': 'theme_analysis'
            },
            'pacing': {
                'weight': 0.10,
                'description': 'Appropriate rhythm and tension management',
                'assessment_method': 'pacing_analysis'
            },
            'originality': {
                'weight': 0.10,
                'description': 'Creative and unique storytelling elements',
                'assessment_method': 'originality_scoring'
            }
        }
        
        # Performance optimization guidelines
        self.performance_guidelines = {
            'time_thresholds': {
                'flash_fiction': 60,      # seconds
                'short_story': 180,       # seconds
                'complex_story': 300      # seconds
            },
            'quality_thresholds': {
                'minimum_acceptable': 6.0,
                'target_quality': 7.5,
                'excellence_threshold': 8.5
            },
            'optimization_strategies': {
                'high_latency': 'Consider simpler generation strategies',
                'low_quality': 'Use iterative strategy with quality enhancement',
                'high_error_rate': 'Improve requirement validation and fallback handling'
            }
        }
        
        logger.info("V13StoryDependencies initialized with workflow capabilities")
    
    def get_strategy_recommendation(self, requirements: StoryRequirements) -> StrategyRecommendation:
        """Get recommended generation strategy for the given requirements"""
        return self.strategy_selector.select_strategy(requirements)
    
    def analyze_requirements(self, requirements: StoryRequirements) -> RequirementAnalysis:
        """Perform comprehensive requirements analysis"""
        return self.strategy_selector.analyze_requirements(requirements)
    
    def get_quality_criteria_for_genre(self, genre: StoryGenre) -> Dict[str, Any]:
        """Get quality assessment criteria specific to the genre"""
        base_criteria = self.quality_criteria.copy()
        
        # Adjust weights based on genre
        if genre == StoryGenre.LITERARY:
            base_criteria['character_development']['weight'] = 0.25
            base_criteria['theme_integration']['weight'] = 0.20
            base_criteria['structure']['weight'] = 0.15
        elif genre == StoryGenre.MYSTERY:
            base_criteria['structure']['weight'] = 0.30
            base_criteria['coherence']['weight'] = 0.25
            base_criteria['pacing']['weight'] = 0.15
        elif genre in [StoryGenre.SCIENCE_FICTION, StoryGenre.FANTASY]:
            base_criteria['originality']['weight'] = 0.25
            base_criteria['coherence']['weight'] = 0.25
            base_criteria['genre_compliance']['weight'] = 0.20
        
        return base_criteria
    
    def get_workflow_configuration(self, strategy: GenerationStrategy) -> Dict[str, Any]:
        """Get configuration parameters for the specified workflow strategy"""
        base_config = {
            'timeout': self.config.adaptive_timeout,
            'quality_threshold': self.config.quality_threshold,
            'enable_enhancement': self.config.enable_quality_enhancement,
            'max_iterations': self.config.max_enhancement_iterations
        }
        
        if strategy == GenerationStrategy.DIRECT:
            base_config.update({
                'timeout': self.config.direct_timeout,
                'enable_outline': False,
                'enable_enhancement': False,
                'quality_checks': ['basic']
            })
        elif strategy == GenerationStrategy.OUTLINE:
            base_config.update({
                'timeout': self.config.outline_timeout,
                'enable_outline': True,
                'outline_timeout': 30,
                'quality_checks': ['basic', 'structure']
            })
        elif strategy == GenerationStrategy.ITERATIVE:
            base_config.update({
                'timeout': self.config.iterative_timeout,
                'enable_outline': True,
                'enable_enhancement': True,
                'max_iterations': 3,
                'quality_checks': ['comprehensive']
            })
        elif strategy == GenerationStrategy.ADAPTIVE:
            base_config.update({
                'timeout': self.config.adaptive_timeout,
                'enable_dynamic_adjustment': True,
                'quality_checks': ['adaptive']
            })
        
        return base_config
    
    def get_performance_targets(self, requirements: StoryRequirements) -> Dict[str, float]:
        """Get performance targets for the given requirements"""
        word_count = requirements.target_word_count
        
        if word_count <= 500:
            target_time = self.performance_guidelines['time_thresholds']['flash_fiction']
        elif word_count <= 3000:
            target_time = self.performance_guidelines['time_thresholds']['short_story']
        else:
            target_time = self.performance_guidelines['time_thresholds']['complex_story']
        
        return {
            'target_generation_time': target_time,
            'maximum_generation_time': target_time * 2,
            'target_quality_score': self.performance_guidelines['quality_thresholds']['target_quality'],
            'minimum_quality_score': self.performance_guidelines['quality_thresholds']['minimum_acceptable']
        }
    
    def should_use_enhancement(self, quality_metrics: QualityMetrics, requirements: StoryRequirements) -> bool:
        """Determine if quality enhancement should be applied"""
        if not self.config.enable_quality_enhancement:
            return False
        
        # Use enhancement if quality is below threshold
        if quality_metrics.overall_score < self.config.quality_threshold:
            return True
        
        # Use enhancement for complex requirements even with acceptable quality
        analysis = self.analyze_requirements(requirements)
        if analysis.complexity_score > 0.7 and quality_metrics.overall_score < 8.0:
            return True
        
        return False
    
    def get_enhancement_suggestions(
        self,
        quality_metrics: QualityMetrics,
        story_content: str,
        requirements: StoryRequirements
    ) -> List[str]:
        """Get specific enhancement suggestions based on quality assessment"""
        return self.quality_assessor.generate_improvement_suggestions(
            quality_metrics, story_content, requirements
        )
    
    def log_performance_data(
        self,
        strategy: GenerationStrategy,
        requirements: StoryRequirements,
        success: bool,
        quality_score: float,
        generation_time: float,
        error_count: int = 0
    ) -> None:
        """Log performance data for strategy optimization"""
        self.strategy_selector.record_strategy_performance(
            strategy, requirements, success, quality_score, generation_time, error_count
        )
        
    def get_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """Get recommendations for improving generation performance"""
        return self.performance_monitor.get_optimization_recommendations()
    
    def cleanup_old_data(self) -> None:
        """Clean up old performance and metrics data"""
        self.performance_monitor.cleanup_old_metrics()
        
    def get_performance_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get performance summary for the specified period"""
        return self.performance_monitor.get_performance_summary(days)
    
    def stop_monitoring(self) -> None:
        """Stop performance monitoring"""
        self.performance_monitor.stop()