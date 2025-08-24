"""
Quality Assessor - Version 1.3 Implementation
Comprehensive quality assessment for generated stories with detailed scoring
"""

import logging
import re
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from ..models.basic_models import StoryRequirements, StoryGenre
from ..models.story_models import QualityMetrics, ImprovementSuggestion
from ..utils.config import StoryGenerationError

# Setup logging
logger = logging.getLogger(__name__)


class QualityAssessor:
    """
    Provides comprehensive quality assessment for generated stories with
    detailed scoring across multiple dimensions and improvement suggestions.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Genre-specific quality criteria weights
        self.genre_weights = {
            StoryGenre.LITERARY: {
                'character_development': 0.25,
                'theme_integration': 0.20,
                'structure_score': 0.15,
                'coherence_score': 0.15,
                'originality_score': 0.15,
                'pacing_quality': 0.10
            },
            StoryGenre.MYSTERY: {
                'structure_score': 0.25,
                'pacing_quality': 0.20,
                'coherence_score': 0.20,
                'genre_compliance': 0.15,
                'character_development': 0.10,
                'theme_integration': 0.10
            },
            StoryGenre.FANTASY: {
                'originality_score': 0.20,
                'coherence_score': 0.20,
                'character_development': 0.15,
                'structure_score': 0.15,
                'theme_integration': 0.15,
                'genre_compliance': 0.15
            },
            StoryGenre.SCIENCE_FICTION: {
                'originality_score': 0.25,
                'coherence_score': 0.20,
                'genre_compliance': 0.15,
                'structure_score': 0.15,
                'theme_integration': 0.15,
                'character_development': 0.10
            },
            StoryGenre.ROMANCE: {
                'character_development': 0.25,
                'pacing_quality': 0.20,
                'theme_integration': 0.15,
                'coherence_score': 0.15,
                'structure_score': 0.15,
                'genre_compliance': 0.10
            }
        }
        
        logger.info("QualityAssessor initialized")
    
    async def assess_quality(
        self,
        story_content: str,
        story_title: str,
        requirements: StoryRequirements
    ) -> QualityMetrics:
        """
        Perform comprehensive quality assessment of a generated story
        
        Args:
            story_content: The generated story content
            story_title: The story title
            requirements: Original story requirements
            
        Returns:
            QualityMetrics with detailed scoring
        """
        start_time = time.time()
        
        try:
            logger.debug(f"Starting quality assessment for story: {story_title}")
            
            # Basic content validation - must succeed
            if not story_content or not story_content.strip():
                raise StoryGenerationError("Empty story content provided for assessment")
            
            # Perform individual assessments
            structure_score = self._assess_structure(story_content, requirements)
            coherence_score = self._assess_coherence(story_content)
            genre_compliance = self._assess_genre_compliance(story_content, requirements.genre)
            character_development = self._assess_character_development(story_content, requirements)
            pacing_quality = self._assess_pacing(story_content, requirements)
            theme_integration = self._assess_theme_integration(story_content, requirements)
            word_count_accuracy = self._assess_word_count_accuracy(story_content, requirements)
            grammar_quality = self._assess_grammar_quality(story_content)
            originality_score = self._assess_originality(story_content, requirements)
            
            # Calculate weighted overall score
            overall_score = self._calculate_overall_score(
                {
                    'structure_score': structure_score,
                    'coherence_score': coherence_score,
                    'genre_compliance': genre_compliance,
                    'character_development': character_development,
                    'pacing_quality': pacing_quality,
                    'theme_integration': theme_integration,
                    'originality_score': originality_score
                },
                requirements.genre
            )
            
            # Calculate confidence based on content length and complexity
            confidence_level = self._calculate_confidence(story_content, requirements)
            
            assessment_time = time.time() - start_time
            
            metrics = QualityMetrics(
                overall_score=overall_score,
                structure_score=structure_score,
                coherence_score=coherence_score,
                genre_compliance=genre_compliance,
                character_development=character_development,
                pacing_quality=pacing_quality,
                theme_integration=theme_integration,
                word_count_accuracy=word_count_accuracy,
                grammar_quality=grammar_quality,
                originality_score=originality_score,
                assessment_time=datetime.now(),
                assessment_method="automated_v13",
                confidence_level=confidence_level
            )
            
            logger.info(f"Quality assessment completed in {assessment_time:.2f}s - Overall score: {overall_score:.1f}")
            return metrics
            
        except Exception as e:
            logger.error(f"Quality assessment failed: {e}")
            raise StoryGenerationError(f"Quality assessment failed: {e}") from e
    
    def generate_improvement_suggestions(
        self,
        metrics: QualityMetrics,
        story_content: str,
        requirements: StoryRequirements
    ) -> List[ImprovementSuggestion]:
        """
        Generate specific improvement suggestions based on quality assessment
        
        Args:
            metrics: Quality assessment results
            story_content: The story content
            requirements: Original requirements
            
        Returns:
            List of improvement suggestions
        """
        suggestions = []
        
        try:
            # Structure improvements
            if metrics.structure_score < 7.0:
                suggestions.append(ImprovementSuggestion(
                    category="structure",
                    priority="high",
                    suggestion="Improve story structure with clearer beginning, middle, and end",
                    reasoning=f"Structure score is {metrics.structure_score:.1f}, below target of 7.0",
                    estimated_impact=0.3
                ))
            
            # Character development improvements
            if metrics.character_development < 7.0:
                suggestions.append(ImprovementSuggestion(
                    category="character",
                    priority="medium",
                    suggestion="Enhance character development with more detailed motivations and growth",
                    reasoning=f"Character development score is {metrics.character_development:.1f}",
                    estimated_impact=0.25
                ))
            
            # Pacing improvements
            if metrics.pacing_quality < 7.0:
                suggestions.append(ImprovementSuggestion(
                    category="pacing",
                    priority="medium",
                    suggestion="Improve story pacing by balancing action and reflection",
                    reasoning=f"Pacing quality score is {metrics.pacing_quality:.1f}",
                    estimated_impact=0.2
                ))
            
            # Genre compliance improvements
            if metrics.genre_compliance < 7.0:
                suggestions.append(ImprovementSuggestion(
                    category="genre",
                    priority="high",
                    suggestion=f"Better adhere to {requirements.genre.value} genre conventions",
                    reasoning=f"Genre compliance score is {metrics.genre_compliance:.1f}",
                    estimated_impact=0.25
                ))
            
            # Theme integration improvements
            if metrics.theme_integration < 7.0 and requirements.theme:
                suggestions.append(ImprovementSuggestion(
                    category="theme",
                    priority="medium",
                    suggestion=f"Better integrate the theme '{requirements.theme}' throughout the story",
                    reasoning=f"Theme integration score is {metrics.theme_integration:.1f}",
                    estimated_impact=0.2
                ))
            
            # Word count accuracy
            if metrics.word_count_accuracy < 0.8:
                suggestions.append(ImprovementSuggestion(
                    category="length",
                    priority="low",
                    suggestion=f"Adjust story length to better match target of {requirements.target_word_count} words",
                    reasoning=f"Word count accuracy is {metrics.word_count_accuracy:.1%}",
                    estimated_impact=0.1
                ))
            
            # Sort suggestions by priority and impact
            priority_order = {"high": 3, "medium": 2, "low": 1}
            suggestions.sort(key=lambda x: (priority_order[x.priority], x.estimated_impact), reverse=True)
            
            logger.debug(f"Generated {len(suggestions)} improvement suggestions")
            return suggestions
            
        except Exception as e:
            logger.error(f"Failed to generate improvement suggestions: {e}")
            return []
    
    def _assess_structure(self, content: str, requirements: StoryRequirements) -> float:
        """Assess the narrative structure of the story"""
        try:
            paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
            if len(paragraphs) < 3:
                return 4.0  # Too short for proper structure
            
            # Basic structure heuristics
            word_count = len(content.split())
            
            # Check for clear beginning (establishes setting/character)
            beginning_score = 7.0  # Default assumption
            if len(paragraphs[0].split()) < 30:
                beginning_score = 5.0  # Very short opening
            
            # Check for development in middle sections
            middle_score = 7.0
            if len(paragraphs) < 5:
                middle_score = 6.0  # Limited development
            
            # Check for conclusion
            ending_score = 7.0
            last_para = paragraphs[-1]
            if len(last_para.split()) < 20:
                ending_score = 6.0  # Abrupt ending
            
            # Weight the scores
            structure_score = (beginning_score * 0.3 + middle_score * 0.4 + ending_score * 0.3)
            
            return min(max(structure_score, 0.0), 10.0)
            
        except Exception as e:
            raise StoryGenerationError(f"Structure assessment failed: {e}")
    
    def _assess_coherence(self, content: str) -> float:
        """Assess story coherence and logical flow"""
        try:
            # Basic coherence indicators
            sentences = re.split(r'[.!?]+', content)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            if len(sentences) < 5:
                return 4.0  # Too short to assess coherence
            
            # Check for transition words and logical connections
            transition_words = [
                'however', 'meanwhile', 'therefore', 'consequently', 'furthermore',
                'moreover', 'nevertheless', 'finally', 'then', 'next', 'suddenly',
                'later', 'before', 'after', 'during', 'while'
            ]
            
            transition_count = sum(1 for word in transition_words if word in content.lower())
            transition_ratio = transition_count / len(sentences)
            
            # Basic coherence score based on transitions and structure
            coherence_score = 6.0 + min(transition_ratio * 20, 3.0)  # Max boost of 3 points
            
            return min(max(coherence_score, 0.0), 10.0)
            
        except Exception as e:
            raise StoryGenerationError(f"Coherence assessment failed: {e}")
    
    def _assess_genre_compliance(self, content: str, genre: StoryGenre) -> float:
        """Assess adherence to genre conventions"""
        try:
            content_lower = content.lower()
            
            genre_keywords = {
                StoryGenre.MYSTERY: ['mystery', 'clue', 'detective', 'investigation', 'crime', 'suspect', 'solve'],
                StoryGenre.FANTASY: ['magic', 'fantasy', 'enchanted', 'mystical', 'dragon', 'wizard', 'spell'],
                StoryGenre.SCIENCE_FICTION: ['future', 'technology', 'space', 'alien', 'robot', 'scientist', 'discovery'],
                StoryGenre.ROMANCE: ['love', 'heart', 'relationship', 'romantic', 'passion', 'kiss', 'feelings'],
                StoryGenre.LITERARY: ['character', 'emotion', 'human', 'society', 'meaning', 'reflection', 'insight']
            }
            
            keywords = genre_keywords.get(genre, [])
            if not keywords:
                return 7.0  # Default for unknown genres
            
            keyword_count = sum(1 for keyword in keywords if keyword in content_lower)
            keyword_ratio = keyword_count / len(keywords)
            
            # Genre compliance score
            compliance_score = 5.0 + min(keyword_ratio * 10, 5.0)
            
            return min(max(compliance_score, 0.0), 10.0)
            
        except Exception as e:
            raise StoryGenerationError(f"Genre compliance assessment failed: {e}")
    
    def _assess_character_development(self, content: str, requirements: StoryRequirements) -> float:
        """Assess character development and depth"""
        try:
            # Look for character indicators
            character_indicators = [
                'he said', 'she said', 'they said', 'thought', 'felt', 'realized',
                'remembered', 'decided', 'wondered', 'hoped', 'feared', 'loved',
                'character', 'person', 'man', 'woman', 'boy', 'girl'
            ]
            
            content_lower = content.lower()
            indicator_count = sum(1 for indicator in character_indicators if indicator in content_lower)
            
            # Look for dialogue (rough indicator of character interaction)
            dialogue_count = content.count('"')
            
            # Character development score based on indicators
            word_count = len(content.split())
            indicator_ratio = indicator_count / max(word_count / 100, 1)  # Per 100 words
            dialogue_ratio = dialogue_count / max(word_count / 50, 1)  # Per 50 words
            
            character_score = 5.0 + min(indicator_ratio * 3, 2.5) + min(dialogue_ratio * 2, 2.5)
            
            return min(max(character_score, 0.0), 10.0)
            
        except Exception as e:
            raise StoryGenerationError(f"Character development assessment failed: {e}")
    
    def _assess_pacing(self, content: str, requirements: StoryRequirements) -> float:
        """Assess story pacing and rhythm"""
        try:
            paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
            if len(paragraphs) < 3:
                return 5.0
            
            # Analyze paragraph length variation (good pacing has variety)
            para_lengths = [len(p.split()) for p in paragraphs]
            avg_length = sum(para_lengths) / len(para_lengths)
            
            # Calculate variation
            variance = sum((length - avg_length) ** 2 for length in para_lengths) / len(para_lengths)
            std_dev = variance ** 0.5
            
            # Good pacing has moderate variation
            variation_score = min(std_dev / avg_length * 10, 5.0) if avg_length > 0 else 0
            
            # Base pacing score
            pacing_score = 5.0 + variation_score
            
            return min(max(pacing_score, 0.0), 10.0)
            
        except Exception as e:
            raise StoryGenerationError(f"Pacing assessment failed: {e}")
    
    def _assess_theme_integration(self, content: str, requirements: StoryRequirements) -> float:
        """Assess how well the theme is integrated into the story"""
        try:
            if not requirements.theme:
                return 8.0  # No theme requirement, good score
            
            theme_lower = requirements.theme.lower()
            content_lower = content.lower()
            
            # Direct theme mentions
            direct_mentions = content_lower.count(theme_lower)
            
            # Related concept words (simple heuristic)
            theme_words = theme_lower.split()
            related_mentions = sum(content_lower.count(word) for word in theme_words)
            
            # Theme integration score
            word_count = len(content.split())
            theme_ratio = (direct_mentions + related_mentions * 0.5) / max(word_count / 100, 1)
            
            theme_score = 4.0 + min(theme_ratio * 6, 6.0)
            
            return min(max(theme_score, 0.0), 10.0)
            
        except Exception as e:
            raise StoryGenerationError(f"Theme integration assessment failed: {e}")
    
    def _assess_word_count_accuracy(self, content: str, requirements: StoryRequirements) -> float:
        """Assess how accurately the word count matches the target"""
        try:
            actual_count = len(content.split())
            target_count = requirements.target_word_count
            
            if target_count <= 0:
                return 1.0  # Perfect if no target
            
            accuracy = 1.0 - abs(actual_count - target_count) / target_count
            return max(accuracy, 0.0)
            
        except Exception as e:
            raise StoryGenerationError(f"Word count accuracy assessment failed: {e}")
    
    def _assess_grammar_quality(self, content: str) -> float:
        """Basic grammar quality assessment"""
        try:
            # Simple heuristics for grammar quality
            sentences = re.split(r'[.!?]+', content)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            if not sentences:
                return 0.0
            
            # Check for very short or very long sentences (potential issues)
            avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
            
            # Ideal sentence length is around 15-20 words
            length_score = 10.0 - abs(avg_sentence_length - 17.5) / 2.5
            length_score = max(min(length_score, 10.0), 5.0)
            
            # Check for basic punctuation
            punctuation_score = 8.0  # Default assumption of decent punctuation
            
            # Basic grammar score
            grammar_score = (length_score + punctuation_score) / 2
            
            return min(max(grammar_score, 0.0), 10.0)
            
        except Exception as e:
            raise StoryGenerationError(f"Grammar quality assessment failed: {e}")
    
    def _assess_originality(self, content: str, requirements: StoryRequirements) -> float:
        """Assess story originality and creativity"""
        try:
            # Simple originality heuristics
            word_count = len(content.split())
            unique_words = len(set(content.lower().split()))
            
            # Vocabulary diversity ratio
            diversity_ratio = unique_words / word_count if word_count > 0 else 0
            
            # Originality score based on vocabulary diversity
            originality_score = 4.0 + diversity_ratio * 12  # Scale to 0-10
            
            return min(max(originality_score, 0.0), 10.0)
            
        except Exception as e:
            raise StoryGenerationError(f"Originality assessment failed: {e}")
    
    def _calculate_overall_score(self, scores: Dict[str, float], genre: StoryGenre) -> float:
        """Calculate weighted overall quality score"""
        try:
            weights = self.genre_weights.get(genre, {
                'structure_score': 0.2,
                'coherence_score': 0.2,
                'genre_compliance': 0.15,
                'character_development': 0.15,
                'pacing_quality': 0.15,
                'theme_integration': 0.15
            })
            
            weighted_score = sum(scores.get(metric, 6.0) * weight for metric, weight in weights.items())
            
            return min(max(weighted_score, 0.0), 10.0)
            
        except Exception as e:
            raise StoryGenerationError(f"Overall score calculation failed: {e}")
    
    def _calculate_confidence(self, content: str, requirements: StoryRequirements) -> float:
        """Calculate confidence level in the assessment"""
        try:
            word_count = len(content.split())
            target_count = requirements.target_word_count
            
            # Confidence based on content length (more content = higher confidence)
            length_confidence = min(word_count / max(target_count, 100), 1.0)
            
            # Confidence based on content complexity
            sentences = re.split(r'[.!?]+', content)
            complexity_confidence = min(len(sentences) / 10, 1.0)
            
            # Overall confidence
            confidence = (length_confidence + complexity_confidence) / 2
            
            return min(max(confidence, 0.1), 1.0)
            
        except Exception as e:
            raise StoryGenerationError(f"Confidence calculation failed: {e}")