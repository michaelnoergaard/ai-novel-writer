"""
V1.4 Advanced Quality Assessor
Enhanced quality assessment with comprehensive 12-dimensional analysis
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from pydantic_ai import Agent, RunContext

from ..models.basic_models import StoryRequirements
from ..models.v14_models import (
    AdvancedQualityMetrics, QualityDimension, EnhancementStrategy,
    QualityConfig
)
from .quality_assessor import QualityAssessor
from ..utils.config import StoryGenerationError

# Setup logging
logger = logging.getLogger(__name__)


class AdvancedQualityAssessor(QualityAssessor):
    """
    Enhanced quality assessment system with 12-dimensional analysis.
    
    Extends the V1.3 QualityAssessor with:
    - 5 additional quality dimensions (dialogue, setting, emotional impact, originality, technical)
    - Parallel assessment for improved performance
    - Enhancement potential prediction
    - Targeted enhancement capabilities
    """
    
    def __init__(self, config: Optional[QualityConfig] = None):
        """Initialize the advanced quality assessor"""
        super().__init__()
        self.config = config or QualityConfig()
        
        # Initialize base quality assessor for V1.3 metrics
        self.quality_assessor = QualityAssessor()
        
        # Create specialized assessment agents
        self.dialogue_agent = Agent(
            'openai:gpt-4o',
            system_prompt=self._get_dialogue_assessment_prompt()
        )
        
        self.setting_agent = Agent(
            'openai:gpt-4o',
            system_prompt=self._get_setting_assessment_prompt()
        )
        
        self.emotional_agent = Agent(
            'openai:gpt-4o',
            system_prompt=self._get_emotional_assessment_prompt()
        )
        
        self.originality_agent = Agent(
            'openai:gpt-4o',
            system_prompt=self._get_originality_assessment_prompt()
        )
        
        self.technical_agent = Agent(
            'openai:gpt-4o',
            system_prompt=self._get_technical_assessment_prompt()
        )
        
        # Enhancement agent for targeted improvements
        self.enhancement_agent = Agent(
            'openai:gpt-4o',
            system_prompt=self._get_enhancement_prompt()
        )
        
        logger.info("AdvancedQualityAssessor initialized with V1.4 capabilities")
    
    async def assess_comprehensive(
        self, 
        story: str, 
        requirements: StoryRequirements
    ) -> AdvancedQualityMetrics:
        """
        Perform comprehensive quality assessment across all 12 dimensions.
        
        Args:
            story: Story content to assess
            requirements: Story requirements for context
            
        Returns:
            AdvancedQualityMetrics with comprehensive quality scores
        """
        assessment_start = time.time()
        
        logger.debug(f"Starting comprehensive quality assessment for {len(story.split())} word story")
        
        # Get basic V1.3 metrics first using correct method
        basic_metrics = await self.quality_assessor.assess_quality(story, "Untitled", requirements)
        
        # Run V1.4 enhanced assessments in parallel if enabled
        if self.config.enable_parallel_assessment:
            enhanced_assessments = await self._assess_enhanced_dimensions_parallel(story, requirements)
        else:
            enhanced_assessments = await self._assess_enhanced_dimensions_sequential(story, requirements)
        
        # Combine all metrics
        assessment_duration = time.time() - assessment_start
        
        advanced_metrics = AdvancedQualityMetrics(
            # Core V1.3 metrics (enhanced)
            overall_score=basic_metrics.overall_score,
            structure_score=basic_metrics.structure_score,
            coherence_score=basic_metrics.coherence_score,
            genre_compliance=basic_metrics.genre_compliance,
            character_development=basic_metrics.character_development,
            pacing_quality=basic_metrics.pacing_quality,
            theme_integration=basic_metrics.theme_integration,
            
            # V1.4 new dimensions
            dialogue_quality=enhanced_assessments['dialogue_quality'],
            setting_immersion=enhanced_assessments['setting_immersion'],
            emotional_impact=enhanced_assessments['emotional_impact'],
            originality_score=enhanced_assessments['originality_score'],
            technical_quality=enhanced_assessments['technical_quality'],
            
            # Metadata
            assessment_timestamp=datetime.now(),
            assessment_duration=assessment_duration
        )
        
        # Recalculate overall score with new dimensions
        advanced_metrics.overall_score = self._calculate_comprehensive_overall_score(advanced_metrics)
        
        logger.debug(f"Quality assessment completed in {assessment_duration:.2f}s - Overall: {advanced_metrics.overall_score:.2f}")
        
        return advanced_metrics
    
    async def _assess_enhanced_dimensions_parallel(
        self, 
        story: str, 
        requirements: StoryRequirements
    ) -> Dict[str, float]:
        """Assess enhanced dimensions in parallel for better performance"""
        
        assessment_tasks = []
        
        if self.config.enable_dialogue_assessment:
            assessment_tasks.append(self._assess_dialogue_quality(story))
        
        if self.config.enable_setting_assessment:
            assessment_tasks.append(self._assess_setting_immersion(story))
        
        if self.config.enable_emotional_assessment:
            assessment_tasks.append(self._assess_emotional_impact(story))
        
        if self.config.enable_originality_assessment:
            assessment_tasks.append(self._assess_originality(story, requirements))
        
        if self.config.enable_technical_assessment:
            assessment_tasks.append(self._assess_technical_quality(story))
        
        # Run assessments in parallel
        results = await asyncio.gather(*assessment_tasks, return_exceptions=True)
        
        # Process results and handle any exceptions
        enhanced_scores = {}
        dimension_names = ['dialogue_quality', 'setting_immersion', 'emotional_impact', 'originality_score', 'technical_quality']
        enabled_dimensions = []
        
        if self.config.enable_dialogue_assessment:
            enabled_dimensions.append('dialogue_quality')
        if self.config.enable_setting_assessment:
            enabled_dimensions.append('setting_immersion')
        if self.config.enable_emotional_assessment:
            enabled_dimensions.append('emotional_impact')
        if self.config.enable_originality_assessment:
            enabled_dimensions.append('originality_score')
        if self.config.enable_technical_assessment:
            enabled_dimensions.append('technical_quality')
        
        for i, result in enumerate(results):
            dimension = enabled_dimensions[i]
            if isinstance(result, Exception):
                raise StoryGenerationError(f"Critical assessment failure for {dimension}: {result}")
            enhanced_scores[dimension] = result
        
        # Ensure all dimensions are present - fail if any are missing
        for dimension in dimension_names:
            if dimension not in enhanced_scores:
                raise StoryGenerationError(f"Missing assessment for dimension: {dimension}")
            if enhanced_scores[dimension] is None:
                raise StoryGenerationError(f"Null assessment result for dimension: {dimension}")
        
        return enhanced_scores
    
    async def _assess_enhanced_dimensions_sequential(
        self, 
        story: str, 
        requirements: StoryRequirements
    ) -> Dict[str, float]:
        """Assess enhanced dimensions sequentially"""
        enhanced_scores = {}
        
        # All assessments are required - no optional dimensions allowed
        enhanced_scores['dialogue_quality'] = await self._assess_dialogue_quality(story)
        enhanced_scores['setting_immersion'] = await self._assess_setting_immersion(story)
        enhanced_scores['emotional_impact'] = await self._assess_emotional_impact(story)
        enhanced_scores['originality_score'] = await self._assess_originality(story, requirements)
        enhanced_scores['technical_quality'] = await self._assess_technical_quality(story)
        
        return enhanced_scores
    
    async def _assess_dialogue_quality(self, story: str) -> float:
        """Assess dialogue quality and naturalness"""
        assessment_prompt = f"""Assess the dialogue quality in this story on a scale of 0-10.

Consider:
- Naturalness and authenticity of speech
- Character voice distinctiveness
- Dialogue's role in advancing plot and revealing character
- Balance between dialogue and narrative description
- Effective use of subtext and implication

Story to assess:
{story}

Provide only a numerical score from 0.0 to 10.0 (e.g., 8.5)"""

        result = await self.dialogue_agent.run(assessment_prompt)
        
        # Extract numerical score - must succeed
        score_text = result.output if hasattr(result, 'output') else str(result)
        score = self._extract_numerical_score(score_text)
        
        if not (0.0 <= score <= 10.0):
            raise StoryGenerationError(f"Invalid dialogue quality score: {score}")
            
        return score
    
    async def _assess_setting_immersion(self, story: str) -> float:
        """Assess setting description and immersion quality"""
        assessment_prompt = f"""Assess the setting immersion quality in this story on a scale of 0-10.

Consider:
- Vividness and detail of setting descriptions
- Integration of setting with mood and atmosphere
- Use of sensory details to create immersion
- Setting's contribution to story theme and genre
- Balance of description with action and dialogue

Story to assess:
{story}

Provide only a numerical score from 0.0 to 10.0 (e.g., 8.5)"""

        result = await self.setting_agent.run(assessment_prompt)
        
        score_text = result.output if hasattr(result, 'output') else str(result)
        score = self._extract_numerical_score(score_text)
        
        if not (0.0 <= score <= 10.0):
            raise StoryGenerationError(f"Invalid setting immersion score: {score}")
            
        return score
    
    async def _assess_emotional_impact(self, story: str) -> float:
        """Assess emotional resonance and reader engagement"""
        assessment_prompt = f"""Assess the emotional impact of this story on a scale of 0-10.

Consider:
- Emotional resonance and reader engagement
- Character emotional depth and development
- Evocation of feelings through narrative techniques
- Emotional stakes and investment in characters
- Use of emotional moments to enhance story impact

Story to assess:
{story}

Provide only a numerical score from 0.0 to 10.0 (e.g., 8.5)"""

        result = await self.emotional_agent.run(assessment_prompt)
        
        score_text = result.output if hasattr(result, 'output') else str(result)
        score = self._extract_numerical_score(score_text)
        
        if not (0.0 <= score <= 10.0):
            raise StoryGenerationError(f"Invalid emotional impact score: {score}")
            
        return score
    
    async def _assess_originality(self, story: str, requirements: StoryRequirements) -> float:
        """Assess creative uniqueness and freshness"""
        assessment_prompt = f"""Assess the originality and creative uniqueness of this {requirements.get_display_genre()} story on a scale of 0-10.

Consider:
- Unique plot elements and creative twists
- Fresh approach to common themes or tropes
- Original character types or relationships
- Creative use of genre conventions
- Avoidance of clichés and predictable elements

Story to assess:
{story}

Provide only a numerical score from 0.0 to 10.0 (e.g., 8.5)"""

        result = await self.originality_agent.run(assessment_prompt)
        
        score_text = result.output if hasattr(result, 'output') else str(result)
        score = self._extract_numerical_score(score_text)
        
        if not (0.0 <= score <= 10.0):
            raise StoryGenerationError(f"Invalid originality score: {score}")
            
        return score
    
    async def _assess_technical_quality(self, story: str) -> float:
        """Assess grammar, style, and prose quality"""
        assessment_prompt = f"""Assess the technical writing quality of this story on a scale of 0-10.

Consider:
- Grammar and syntax correctness
- Sentence structure variety and flow
- Word choice and vocabulary appropriateness
- Prose style and readability
- Overall writing craft and polish

Story to assess:
{story}

Provide only a numerical score from 0.0 to 10.0 (e.g., 8.5)"""

        result = await self.technical_agent.run(assessment_prompt)
        
        score_text = result.output if hasattr(result, 'output') else str(result)
        score = self._extract_numerical_score(score_text)
        
        if not (0.0 <= score <= 10.0):
            raise StoryGenerationError(f"Invalid technical quality score: {score}")
            
        return score
    
    def _calculate_comprehensive_overall_score(self, metrics: AdvancedQualityMetrics) -> float:
        """Calculate overall score incorporating all 12 dimensions"""
        
        # V1.4 weighting scheme for 12 dimensions
        weights = {
            'structure': 0.12,
            'coherence': 0.10,
            'character_development': 0.12,
            'genre_compliance': 0.08,
            'pacing_quality': 0.10,
            'theme_integration': 0.08,
            'dialogue_quality': 0.10,
            'setting_immersion': 0.08,
            'emotional_impact': 0.12,
            'originality_score': 0.06,
            'technical_quality': 0.04
        }
        
        # Calculate weighted average
        weighted_sum = (
            metrics.structure_score * weights['structure'] +
            metrics.coherence_score * weights['coherence'] +
            metrics.character_development * weights['character_development'] +
            metrics.genre_compliance * weights['genre_compliance'] +
            metrics.pacing_quality * weights['pacing_quality'] +
            metrics.theme_integration * weights['theme_integration'] +
            metrics.dialogue_quality * weights['dialogue_quality'] +
            metrics.setting_immersion * weights['setting_immersion'] +
            metrics.emotional_impact * weights['emotional_impact'] +
            metrics.originality_score * weights['originality_score'] +
            metrics.technical_quality * weights['technical_quality']
        )
        
        return round(weighted_sum, 2)
    
    def _extract_numerical_score(self, text: str) -> float:
        """Extract numerical score from assessment text - must succeed"""
        import re
        
        # Look for decimal numbers
        numbers = re.findall(r'\b\d+\.?\d*\b', text)
        
        for num_str in numbers:
            try:
                score = float(num_str)
                if 0.0 <= score <= 10.0:
                    return score
            except ValueError:
                continue
        
        raise StoryGenerationError(f"Could not extract valid numerical score from assessment: {text[:200]}")
    
    async def apply_targeted_enhancement(
        self,
        content: str,
        title: str,
        requirements: StoryRequirements,
        strategy: EnhancementStrategy,
        enhancement_prompt: str
    ) -> Dict[str, str]:
        """
        Apply targeted enhancement using the specified strategy.
        
        Args:
            content: Current story content
            title: Current story title
            requirements: Story requirements
            strategy: Enhancement strategy to apply
            enhancement_prompt: Pre-built enhancement prompt
            
        Returns:
            Dictionary with enhanced 'content' and 'title'
        """
        logger.debug(f"Applying {strategy} enhancement strategy")
        
        result = await self.enhancement_agent.run(enhancement_prompt)
        
        # Extract enhanced content
        enhanced_text = result.output if hasattr(result, 'output') else str(result)
        
        if not enhanced_text or not enhanced_text.strip():
            raise StoryGenerationError("Enhancement agent returned empty response")
        
        # Parse title and content
        enhanced_title, enhanced_content = self._parse_enhanced_result(enhanced_text, title)
        
        if not enhanced_content or not enhanced_content.strip():
            raise StoryGenerationError("Enhancement failed to produce valid content")
        
        return {
            'title': enhanced_title,
            'content': enhanced_content
        }
    
    def _parse_enhanced_result(self, enhanced_text: str, fallback_title: str) -> Tuple[str, str]:
        """Parse enhanced result to extract title and content"""
        lines = enhanced_text.strip().split('\n')
        enhanced_title = fallback_title
        content_start_idx = 0
        
        # Look for title in first few lines
        for i, line in enumerate(lines[:5]):
            if line.strip().startswith('**Title:**'):
                enhanced_title = line.replace('**Title:**', '').strip()
                content_start_idx = i + 1
                break
            elif line.strip().startswith('Title:'):
                enhanced_title = line.replace('Title:', '').strip()
                content_start_idx = i + 1
                break
        
        # Get content (skip empty lines after title)
        content_lines = lines[content_start_idx:]
        while content_lines and not content_lines[0].strip():
            content_lines = content_lines[1:]
        
        enhanced_content = '\n'.join(content_lines) if content_lines else enhanced_text
        
        return enhanced_title, enhanced_content
    
    async def predict_enhancement_potential(
        self, 
        quality_metrics: AdvancedQualityMetrics,
        requirements: StoryRequirements
    ) -> Dict[str, Any]:
        """
        Predict potential quality improvements and optimal strategies.
        
        Args:
            quality_metrics: Current quality metrics
            requirements: Story requirements for context
            
        Returns:
            Enhancement prediction data
        """
        # Calculate improvement potential for each dimension
        improvement_potential = quality_metrics.calculate_improvement_potential(
            target_score=self.config.target_quality_score
        )
        
        # Identify optimal enhancement strategies
        weak_dimensions = quality_metrics.get_weakest_dimensions(threshold=7.0)
        
        optimal_strategies = []
        for dimension in weak_dimensions:
            if dimension == QualityDimension.STRUCTURE:
                optimal_strategies.append(EnhancementStrategy.STRUCTURE_FOCUS)
            elif dimension == QualityDimension.CHARACTER_DEVELOPMENT:
                optimal_strategies.append(EnhancementStrategy.CHARACTER_FOCUS)
            elif dimension == QualityDimension.DIALOGUE_QUALITY:
                optimal_strategies.append(EnhancementStrategy.DIALOGUE_FOCUS)
            elif dimension == QualityDimension.SETTING_IMMERSION:
                optimal_strategies.append(EnhancementStrategy.SETTING_FOCUS)
            elif dimension == QualityDimension.EMOTIONAL_IMPACT:
                optimal_strategies.append(EnhancementStrategy.EMOTIONAL_FOCUS)
            elif dimension == QualityDimension.PACING_QUALITY:
                optimal_strategies.append(EnhancementStrategy.PACING_FOCUS)
            elif dimension == QualityDimension.COHERENCE:
                optimal_strategies.append(EnhancementStrategy.COHERENCE_FOCUS)
            elif dimension == QualityDimension.GENRE_COMPLIANCE:
                optimal_strategies.append(EnhancementStrategy.GENRE_FOCUS)
            elif dimension == QualityDimension.TECHNICAL_QUALITY:
                optimal_strategies.append(EnhancementStrategy.TECHNICAL_FOCUS)
        
        if not optimal_strategies:
            optimal_strategies = [EnhancementStrategy.COMPREHENSIVE]
        
        # Estimate enhancement likelihood
        total_potential = sum(improvement_potential.values())
        enhancement_likelihood = min(1.0, total_potential / 10.0)  # Scale to 0-1
        
        # Estimate resource requirements
        estimated_passes = max(1, min(self.config.max_enhancement_passes, len(weak_dimensions)))
        estimated_time = estimated_passes * 45  # 45 seconds per pass estimate
        estimated_tokens = estimated_passes * 3000  # 3000 tokens per pass estimate
        
        return {
            'improvement_potential': improvement_potential,
            'weak_dimensions': weak_dimensions,
            'optimal_strategies': optimal_strategies,
            'enhancement_likelihood': enhancement_likelihood,
            'estimated_passes': estimated_passes,
            'estimated_time_seconds': estimated_time,
            'estimated_token_usage': estimated_tokens,
            'target_achievable': quality_metrics.overall_score + total_potential >= self.config.target_quality_score
        }
    
    def _get_dialogue_assessment_prompt(self) -> str:
        """Get system prompt for dialogue assessment agent"""
        return """You are an expert dialogue assessor for creative writing.

Your task is to evaluate dialogue quality in stories based on:
- Naturalness and authenticity of speech patterns
- Character voice distinctiveness and consistency
- Dialogue's effectiveness in advancing plot and revealing character
- Appropriate balance between dialogue and narrative description
- Effective use of subtext, implication, and realistic conversation flow

Always provide precise numerical scores from 0.0 to 10.0 where:
- 9.0-10.0: Exceptional dialogue that feels completely natural and distinctive
- 8.0-8.9: Strong dialogue with clear character voices and effective story advancement
- 7.0-7.9: Good dialogue that serves the story well with minor areas for improvement
- 6.0-6.9: Adequate dialogue with some stilted or generic elements
- 5.0-5.9: Weak dialogue that feels artificial or doesn't serve the story effectively
- Below 5.0: Poor dialogue that detracts from the story experience

Focus on the quality and effectiveness of dialogue, not the overall story quality."""
    
    def _get_setting_assessment_prompt(self) -> str:
        """Get system prompt for setting assessment agent"""
        return """You are an expert setting and atmosphere assessor for creative writing.

Your task is to evaluate setting immersion quality based on:
- Vividness and detail of setting descriptions
- Integration of setting with mood, atmosphere, and story themes
- Effective use of sensory details to create immersion
- Setting's contribution to genre authenticity and reader experience
- Appropriate balance of description with action and dialogue

Always provide precise numerical scores from 0.0 to 10.0 where:
- 9.0-10.0: Exceptional setting that creates complete immersion and atmosphere
- 8.0-8.9: Strong setting descriptions that enhance mood and story experience
- 7.0-7.9: Good setting work that supports the story effectively
- 6.0-6.9: Adequate setting with some areas lacking detail or atmosphere
- 5.0-5.9: Weak setting that doesn't create sufficient immersion
- Below 5.0: Poor setting descriptions that fail to establish atmosphere

Focus on setting quality and immersion, not overall story quality."""
    
    def _get_emotional_assessment_prompt(self) -> str:
        """Get system prompt for emotional impact assessment agent"""
        return """You are an expert emotional impact assessor for creative writing.

Your task is to evaluate emotional resonance and reader engagement based on:
- Emotional depth and authenticity of character experiences
- Story's ability to evoke feelings and create emotional investment
- Effective use of emotional stakes and character development
- Emotional moments that enhance overall story impact
- Reader engagement and emotional connection to characters and events

Always provide precise numerical scores from 0.0 to 10.0 where:
- 9.0-10.0: Exceptional emotional impact that deeply engages and moves readers
- 8.0-8.9: Strong emotional resonance with genuine character emotions
- 7.0-7.9: Good emotional engagement that connects readers to the story
- 6.0-6.9: Adequate emotional content with some shallow or forced moments
- 5.0-5.9: Weak emotional impact that fails to engage readers deeply
- Below 5.0: Poor emotional content that feels artificial or manipulative

Focus on emotional impact and reader engagement, not overall story quality."""
    
    def _get_originality_assessment_prompt(self) -> str:
        """Get system prompt for originality assessment agent"""
        return """You are an expert originality and creativity assessor for creative writing.

Your task is to evaluate creative uniqueness and freshness based on:
- Unique plot elements, twists, and creative approaches
- Fresh perspective on common themes or genre tropes
- Original character types, relationships, or story concepts
- Creative and innovative use of genre conventions
- Avoidance of clichés, predictable elements, and overused tropes

Always provide precise numerical scores from 0.0 to 10.0 where:
- 9.0-10.0: Exceptional originality with truly unique and creative elements
- 8.0-8.9: Strong creativity with fresh approaches and original ideas
- 7.0-7.9: Good originality that brings something new to familiar concepts
- 6.0-6.9: Adequate creativity with some original elements mixed with familiar ones
- 5.0-5.9: Weak originality that relies heavily on common tropes
- Below 5.0: Poor originality that feels completely predictable or clichéd

Focus on creativity and uniqueness, not overall story quality."""
    
    def _get_technical_assessment_prompt(self) -> str:
        """Get system prompt for technical quality assessment agent"""
        return """You are an expert technical writing quality assessor for creative writing.

Your task is to evaluate technical writing craft based on:
- Grammar, syntax, and mechanical correctness
- Sentence structure variety, flow, and readability
- Word choice, vocabulary appropriateness, and precision
- Prose style, voice consistency, and overall writing polish
- Professional writing craft and technical execution

Always provide precise numerical scores from 0.0 to 10.0 where:
- 9.0-10.0: Exceptional technical quality with polished, professional prose
- 8.0-8.9: Strong technical execution with excellent grammar and style
- 7.0-7.9: Good technical quality with minor issues or areas for improvement
- 6.0-6.9: Adequate technical quality with some noticeable errors or awkward phrasing
- 5.0-5.9: Weak technical quality with frequent errors or poor prose style
- Below 5.0: Poor technical execution that significantly impacts readability

Focus on technical writing craft, not story content or creativity."""
    
    def _get_enhancement_prompt(self) -> str:
        """Get system prompt for enhancement agent"""
        return """You are an expert story enhancement specialist.

Your task is to improve stories based on specific enhancement strategies while maintaining:
- The original story's core narrative and character essence
- Exact target word count as specified in requirements
- Genre conventions and thematic coherence
- Story structure and plot progression

When enhancing stories:
- Focus on the specific strategy provided (structure, character, dialogue, etc.)
- Make targeted improvements that address identified weaknesses
- Preserve the story's strengths while addressing areas for improvement
- Maintain the author's voice and style while improving quality
- Ensure enhancements feel natural and integrated, not forced

Always provide enhanced stories in the requested format with clear title and content sections.
Count words carefully to meet exact target word count requirements."""