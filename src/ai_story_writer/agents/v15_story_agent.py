"""
AI Story Writer V1.5 - Adaptive Intelligence Story Agent
Main story generation agent with adaptive intelligence capabilities.
"""

import asyncio
import logging
import time
import uuid
from typing import Optional, Any

from ..models.v15_models import (
    AdaptiveGenerationResult, AdaptiveGenerationConfig, UserProfile, SystemContext,
    validate_adaptive_config
)
from ..models.v13_models import GenerationStrategy, WorkflowConfiguration
from ..models.basic_models import StoryRequirements
from ..utils import StoryGenerationError

from ..intelligence import AdaptiveIntelligenceEngine

logger = logging.getLogger(__name__)


class V15StoryAgent:
    """V1.5 Story Agent with Adaptive Intelligence Engine"""
    
    def __init__(self, config: AdaptiveGenerationConfig):
        """Initialize V1.5 story agent - must succeed"""
        try:
            self.config = validate_adaptive_config(config)
            self.adaptive_engine = AdaptiveIntelligenceEngine(config)
            self.generation_active = False
            
            logger.info("V15StoryAgent initialized with adaptive intelligence capabilities")
            
        except Exception as e:
            raise StoryGenerationError(f"Failed to initialize V1.5 story agent: {e}")
    
    async def generate_adaptive_story(
        self,
        requirements: StoryRequirements,
        user_profile: Optional[UserProfile] = None,
        system_context: Optional[SystemContext] = None
    ) -> AdaptiveGenerationResult:
        """Generate story with full V1.5 adaptive intelligence"""
        
        if self.generation_active:
            raise StoryGenerationError("V1.5 agent is already processing a generation request")
        
        generation_id = f"v15_{uuid.uuid4().hex[:8]}"
        start_time = time.time()
        
        try:
            self.generation_active = True
            
            logger.info(f"Starting V1.5 adaptive story generation {generation_id}")
            logger.info(f"Requirements: {requirements.genre}, {requirements.target_word_count} words")
            
            if user_profile:
                logger.info(f"User profile: {user_profile.user_id} ({user_profile.interaction_count} interactions)")
            
            if system_context:
                logger.info(f"System context: load={system_context.current_load:.2f}")
            
            # Execute adaptive intelligence generation
            result = await self.adaptive_engine.generate_adaptive_story(
                requirements=requirements,
                user_profile=user_profile,
                system_context=system_context
            )
            
            total_time = time.time() - start_time
            
            logger.info(f"V1.5 adaptive generation {generation_id} completed successfully in {total_time:.1f}s")
            logger.info(f"Result: '{result.title}' ({result.word_count} words, quality: {result.quality_metrics.overall_score:.1f})")
            
            if result.adaptation_applied:
                logger.info(f"Adaptations applied: {result.adaptation_insights.adaptation_effectiveness:.2f} effectiveness")
            
            if result.learning_data_updated:
                logger.info("Learning systems updated with generation results")
            
            return result
            
        except Exception as e:
            logger.error(f"V1.5 adaptive generation {generation_id} failed: {e}")
            raise StoryGenerationError(f"V1.5 adaptive story generation failed: {e}")
            
        finally:
            self.generation_active = False


# Main V1.5 generation function
async def generate_story_v15(
    requirements: StoryRequirements,
    strategy: GenerationStrategy = GenerationStrategy.ADAPTIVE,
    workflow_config: Optional[WorkflowConfiguration] = None,
    quality_config: Optional[Any] = None,
    user_profile: Optional[UserProfile] = None,
    system_context: Optional[SystemContext] = None,
    adaptive_config: Optional[AdaptiveGenerationConfig] = None
) -> AdaptiveGenerationResult:
    """
    Generate story using V1.5 Adaptive Intelligence Engine
    
    This is the main entry point for V1.5 story generation with adaptive intelligence.
    NO FALLBACKS - V1.5 only, must succeed or fail explicitly.
    """
    
    try:
        logger.info("Starting V1.5 adaptive story generation")
        
        # Create adaptive configuration if not provided
        if adaptive_config is None:
            from ..models.v14_models import QualityConfig
            
            # Create default quality config if not provided
            if quality_config is None:
                quality_config = QualityConfig()
            
            # Create default workflow config if not provided
            if workflow_config is None:
                workflow_config = WorkflowConfiguration(
                    default_strategy=strategy,
                    max_workflow_time=300,
                    enable_quality_enhancement=True,
                    quality_threshold=8.0,
                    max_enhancement_iterations=3
                )
            
            # Create adaptive configuration
            from ..models.v15_models import AdaptationStrategy, PersonalizationIntensity
            adaptive_config = AdaptiveGenerationConfig(
                quality_config=quality_config,
                workflow_config=workflow_config,
                adaptation_strategy=AdaptationStrategy.MODERATE,
                personalization_intensity=PersonalizationIntensity.MODERATE,
                enable_predictive_analytics=True,
                enable_adaptive_learning=True,
                enable_resource_optimization=True
            )
        
        # Initialize and execute V1.5 agent
        v15_agent = V15StoryAgent(adaptive_config)
        
        result = await v15_agent.generate_adaptive_story(
            requirements=requirements,
            user_profile=user_profile,
            system_context=system_context
        )
        
        logger.info("V1.5 adaptive story generation completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"V1.5 story generation failed: {e}")
        raise StoryGenerationError(f"V1.5 adaptive story generation failed: {e}")


# V1.5 Dependencies for agent initialization
class V15StoryDependencies:
    """V1.5 Story generation dependencies with adaptive intelligence"""
    
    def __init__(self, config: Optional[AdaptiveGenerationConfig] = None):
        """Initialize V1.5 dependencies - must succeed"""
        try:
            # Default configuration
            if config is None:
                from ..models.v14_models import QualityConfig
                from ..models.v15_models import AdaptationStrategy, PersonalizationIntensity
                
                config = AdaptiveGenerationConfig(
                    quality_config=QualityConfig(),
                    workflow_config=WorkflowConfiguration(),
                    adaptation_strategy=AdaptationStrategy.MODERATE,
                    personalization_intensity=PersonalizationIntensity.MODERATE,
                    enable_predictive_analytics=True,
                    enable_adaptive_learning=True,
                    enable_resource_optimization=True
                )
            
            self.config = validate_adaptive_config(config)
            self.adaptive_engine = AdaptiveIntelligenceEngine(config)
            
            # V1.5 capabilities
            self.capabilities = {
                "adaptive_intelligence": True,
                "predictive_analytics": config.enable_predictive_analytics,
                "personalization": config.personalization_intensity != PersonalizationIntensity.MINIMAL,
                "learning": config.enable_adaptive_learning,
                "optimization": config.enable_resource_optimization,
                "quality_enhancement": config.quality_config.enable_multi_pass,
                "version": "1.5"
            }
            
            logger.info("V15StoryDependencies initialized with adaptive intelligence capabilities")
            
        except Exception as e:
            raise StoryGenerationError(f"Failed to initialize V1.5 dependencies: {e}")
    
    def get_capabilities_summary(self) -> str:
        """Get summary of V1.5 capabilities"""
        enabled_features = [feature for feature, enabled in self.capabilities.items() if enabled and feature != "version"]
        return f"V1.5 Features: {', '.join(enabled_features)}"