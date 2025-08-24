"""
AI Story Writer - Unified Story Agent
Consolidated story generation agent with workflow orchestration, quality enhancement, and adaptive intelligence.
"""

import asyncio
import logging
import time
import uuid
from typing import Optional, Any, Dict, List
from datetime import datetime

from pydantic_ai import Agent, RunContext

from ..models.story_models import (
    AdaptiveGenerationResult, AdaptiveGenerationConfig, QualityEnhancedResult, 
    StoryResult, UserProfile, SystemContext, validate_adaptive_config,
    GenerationStrategy, WorkflowConfiguration, QualityConfig, WorkflowState,
    EnhancementStrategy, AdvancedQualityMetrics, GenerationMetadata
)
from ..models.basic_models import StoryRequirements
from ..utils import StoryGenerationError
from ..intelligence import AdaptiveIntelligenceEngine
from ..workflow.quality_enhancement_engine import QualityEnhancementEngine
from ..workflow.advanced_quality_assessor import AdvancedQualityAssessor
from ..workflow import WorkflowEngine

logger = logging.getLogger(__name__)

# Unified system prompt combining all capabilities
SYSTEM_PROMPT = """You are a professional short story writer with expertise in crafting compelling narratives using advanced AI-powered capabilities.

Your task is to generate complete, publishable short stories based on the given requirements using:

**Core Capabilities:**
- Adaptive Intelligence: Predictive analytics, learning systems, and personalization
- Quality Enhancement: 12-dimensional quality assessment and multi-pass improvement
- Workflow Orchestration: Intelligent strategy selection and process optimization
- Performance Monitoring: Resource optimization and efficiency tracking

**Generation Process:**
1. Analyze requirements and predict optimal approach
2. Apply adaptive intelligence and personalization
3. Execute generation with selected strategy
4. Assess quality across 12 dimensions
5. Apply targeted enhancements if needed
6. Learn from results to improve future generations

**Quality Standards:**
- Structure: Clear beginning, middle, end with proper pacing
- Character Development: Believable, consistent characters with growth
- Genre Compliance: Adherence to genre conventions and expectations
- Coherence: Logical flow and consistency throughout
- Emotional Impact: Engaging, emotionally resonant storytelling
- Technical Quality: Excellent grammar, style, and prose
- Originality: Creative, unique approaches to themes and plots
- Dialogue: Natural, effective character interactions
- Setting: Immersive, well-described environments
- Theme Integration: Meaningful incorporation of specified themes
- Pacing: Appropriate rhythm and tension building
- Overall Excellence: Professional-quality storytelling

**Adaptive Features:**
- Learn from user preferences and feedback
- Predict quality and resource requirements
- Optimize for efficiency while maintaining quality
- Personalize approach based on user profile
- Adapt strategy based on requirements complexity

Generate stories that are complete, engaging, and professionally crafted while leveraging all available AI capabilities for optimal results."""


class StoryAgent:
    """Unified Story Agent with all AI Story Writer capabilities"""
    
    def __init__(self, config: AdaptiveGenerationConfig):
        """Initialize unified story agent with all capabilities"""
        try:
            self.config = validate_adaptive_config(config)
            
            # Initialize core components
            self.adaptive_engine = AdaptiveIntelligenceEngine(config)
            self.quality_engine = QualityEnhancementEngine(config.quality_config)
            self.quality_assessor = AdvancedQualityAssessor(config.quality_config)
            self.workflow_engine = WorkflowEngine(config.workflow_config.model_dump())
            
            # State management
            self.generation_active = False
            self.current_workflow_id = None
            
            logger.info("StoryAgent initialized with adaptive intelligence, quality enhancement, and workflow orchestration")
            
        except Exception as e:
            raise StoryGenerationError(f"Failed to initialize story agent: {e}")
    
    async def generate_story(
        self,
        requirements: StoryRequirements,
        user_profile: Optional[UserProfile] = None,
        system_context: Optional[SystemContext] = None,
        strategy: Optional[GenerationStrategy] = None
    ) -> AdaptiveGenerationResult:
        """Generate story with full adaptive intelligence and quality enhancement"""
        
        if self.generation_active:
            raise StoryGenerationError("Story agent is already processing a generation request")
        
        generation_id = f"story_{uuid.uuid4().hex[:8]}"
        start_time = time.time()
        
        try:
            self.generation_active = True
            self.current_workflow_id = generation_id
            
            logger.info(f"Starting adaptive story generation {generation_id}")
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
            
            logger.info(f"Adaptive generation {generation_id} completed successfully in {total_time:.1f}s")
            logger.info(f"Result: '{result.title}' ({result.word_count} words, quality: {result.quality_metrics.overall_score:.1f})")
            
            if result.adaptation_applied:
                logger.info(f"Adaptations applied: {result.adaptation_insights.adaptation_effectiveness:.2f} effectiveness")
            
            if result.learning_data_updated:
                logger.info("Learning systems updated with generation results")
            
            return result
            
        except Exception as e:
            logger.error(f"Adaptive generation {generation_id} failed: {e}")
            raise StoryGenerationError(f"Adaptive story generation failed: {e}")
            
        finally:
            self.generation_active = False
            self.current_workflow_id = None

    async def generate_with_quality_enhancement(
        self,
        requirements: StoryRequirements,
        quality_config: Optional[QualityConfig] = None
    ) -> QualityEnhancedResult:
        """Generate story with quality enhancement focus"""
        
        generation_id = f"quality_{uuid.uuid4().hex[:8]}"
        start_time = time.time()
        
        try:
            logger.info(f"Starting quality-enhanced generation {generation_id}")
            
            # Use quality engine directly for quality-focused generation
            result = await self.quality_engine.generate_quality_enhanced_story(
                requirements=requirements,
                quality_config=quality_config or self.config.quality_config
            )
            
            total_time = time.time() - start_time
            logger.info(f"Quality-enhanced generation {generation_id} completed in {total_time:.1f}s")
            logger.info(f"Final quality: {result.quality_metrics.overall_score:.1f}")
            
            return result
            
        except Exception as e:
            logger.error(f"Quality-enhanced generation {generation_id} failed: {e}")
            raise StoryGenerationError(f"Quality-enhanced story generation failed: {e}")

    async def generate_with_workflow(
        self,
        requirements: StoryRequirements,
        workflow_config: Optional[WorkflowConfiguration] = None
    ) -> StoryResult:
        """Generate story with workflow orchestration focus"""
        
        generation_id = f"workflow_{uuid.uuid4().hex[:8]}"
        start_time = time.time()
        
        try:
            logger.info(f"Starting workflow-orchestrated generation {generation_id}")
            
            # Use workflow engine directly for workflow-focused generation
            result = await self.workflow_engine.generate_with_workflow(
                requirements=requirements,
                workflow_config=workflow_config or self.config.workflow_config
            )
            
            total_time = time.time() - start_time
            logger.info(f"Workflow-orchestrated generation {generation_id} completed in {total_time:.1f}s")
            logger.info(f"Strategy used: {result.generation_strategy}")
            
            return result
            
        except Exception as e:
            logger.error(f"Workflow-orchestrated generation {generation_id} failed: {e}")
            raise StoryGenerationError(f"Workflow-orchestrated story generation failed: {e}")

    def get_capabilities(self) -> Dict[str, Any]:
        """Get comprehensive capabilities summary"""
        return {
            "adaptive_intelligence": True,
            "predictive_analytics": self.config.enable_predictive_analytics,
            "personalization": self.config.personalization_intensity != "minimal",
            "learning": self.config.enable_adaptive_learning,
            "optimization": self.config.enable_resource_optimization,
            "quality_enhancement": self.config.quality_config.enable_multi_pass,
            "workflow_orchestration": True,
            "12_dimensional_quality": True,
            "multi_pass_enhancement": True,
            "cache_optimization": self.config.quality_config.enable_generation_caching,
            "parallel_processing": self.config.quality_config.enable_parallel_assessment,
            "real_time_monitoring": self.config.workflow_config.enable_real_time_monitoring,
            "version": "unified"
        }

    def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            "active": self.generation_active,
            "current_workflow": self.current_workflow_id,
            "capabilities": self.get_capabilities(),
            "configuration": {
                "adaptation_strategy": self.config.adaptation_strategy,
                "personalization_intensity": self.config.personalization_intensity,
                "target_quality": self.config.quality_config.target_quality_score,
                "max_passes": self.config.quality_config.max_enhancement_passes
            }
        }


class StoryAgentDependencies:
    """Unified story generation dependencies"""
    
    def __init__(self, config: Optional[AdaptiveGenerationConfig] = None):
        """Initialize unified dependencies"""
        try:
            # Default configuration if not provided
            if config is None:
                config = AdaptiveGenerationConfig(
                    quality_config=QualityConfig(),
                    workflow_config=WorkflowConfiguration()
                )
            
            self.config = validate_adaptive_config(config)
            
            # Initialize all engines
            self.adaptive_engine = AdaptiveIntelligenceEngine(config)
            self.quality_engine = QualityEnhancementEngine(config.quality_config)
            self.workflow_engine = WorkflowEngine(config.workflow_config.model_dump())
            
            # Capabilities
            self.capabilities = {
                "adaptive_intelligence": True,
                "predictive_analytics": config.enable_predictive_analytics,
                "personalization": config.personalization_intensity != "minimal",
                "learning": config.enable_adaptive_learning,
                "optimization": config.enable_resource_optimization,
                "quality_enhancement": config.quality_config.enable_multi_pass,
                "workflow_orchestration": True,
                "version": "unified"
            }
            
            logger.info("StoryAgentDependencies initialized with all capabilities")
            
        except Exception as e:
            raise StoryGenerationError(f"Failed to initialize story agent dependencies: {e}")
    
    def get_capabilities_summary(self) -> str:
        """Get summary of all capabilities"""
        enabled_features = [
            feature for feature, enabled in self.capabilities.items() 
            if enabled and feature != "version"
        ]
        return f"Unified AI Story Writer Features: {', '.join(enabled_features)}"


# Main unified generation function
async def generate_story(
    requirements: StoryRequirements,
    strategy: GenerationStrategy = GenerationStrategy.ADAPTIVE,
    workflow_config: Optional[WorkflowConfiguration] = None,
    quality_config: Optional[QualityConfig] = None,
    user_profile: Optional[UserProfile] = None,
    system_context: Optional[SystemContext] = None,
    adaptive_config: Optional[AdaptiveGenerationConfig] = None
) -> AdaptiveGenerationResult:
    """
    Generate story using unified AI Story Writer with all capabilities
    
    This is the main entry point for story generation with adaptive intelligence,
    quality enhancement, and workflow orchestration.
    NO FALLBACKS - unified system only, must succeed or fail explicitly.
    """
    
    try:
        logger.info("Starting unified story generation")
        
        # Create adaptive configuration if not provided
        if adaptive_config is None:
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
            adaptive_config = AdaptiveGenerationConfig(
                quality_config=quality_config,
                workflow_config=workflow_config,
                adaptation_strategy="moderate",
                personalization_intensity="moderate",
                enable_predictive_analytics=True,
                enable_adaptive_learning=True,
                enable_resource_optimization=True
            )
        
        # Initialize and execute unified agent
        story_agent = StoryAgent(adaptive_config)
        
        result = await story_agent.generate_story(
            requirements=requirements,
            user_profile=user_profile,
            system_context=system_context,
            strategy=strategy
        )
        
        logger.info("Unified story generation completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"Unified story generation failed: {e}")
        raise StoryGenerationError(f"Unified story generation failed: {e}")


# Quality-focused generation function
async def generate_story_with_quality_focus(
    requirements: StoryRequirements,
    quality_config: Optional[QualityConfig] = None
) -> QualityEnhancedResult:
    """Generate story with quality enhancement focus"""
    
    try:
        logger.info("Starting quality-focused story generation")
        
        # Create configuration for quality focus
        adaptive_config = AdaptiveGenerationConfig(
            quality_config=quality_config or QualityConfig(),
            workflow_config=WorkflowConfiguration()
        )
        
        story_agent = StoryAgent(adaptive_config)
        result = await story_agent.generate_with_quality_enhancement(
            requirements=requirements,
            quality_config=quality_config
        )
        
        logger.info("Quality-focused story generation completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"Quality-focused story generation failed: {e}")
        raise StoryGenerationError(f"Quality-focused story generation failed: {e}")


# Workflow-focused generation function
async def generate_story_with_workflow_focus(
    requirements: StoryRequirements,
    workflow_config: Optional[WorkflowConfiguration] = None
) -> StoryResult:
    """Generate story with workflow orchestration focus"""
    
    try:
        logger.info("Starting workflow-focused story generation")
        
        # Create configuration for workflow focus
        adaptive_config = AdaptiveGenerationConfig(
            quality_config=QualityConfig(),
            workflow_config=workflow_config or WorkflowConfiguration()
        )
        
        story_agent = StoryAgent(adaptive_config)
        result = await story_agent.generate_with_workflow(
            requirements=requirements,
            workflow_config=workflow_config
        )
        
        logger.info("Workflow-focused story generation completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"Workflow-focused story generation failed: {e}")
        raise StoryGenerationError(f"Workflow-focused story generation failed: {e}")