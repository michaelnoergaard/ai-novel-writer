"""
Enhanced Dependencies for AI Short Story Writer - Version 1.2
Extended dependencies with detailed guidelines and enhanced capabilities
"""

from typing import Dict, List, Any
from basic_models import StoryGenre, StoryLength
from enhanced_models import ValidationLevel, GenerationMethod


class EnhancedStoryDependencies:
    """Enhanced dependencies for V1.2 story agent with detailed guidelines"""
    
    def __init__(self):
        # Enhanced genre guidelines with structure hints
        self.genre_guidelines = {
            StoryGenre.LITERARY: """Focus on character development, internal conflict, and meaningful themes. 
            Use subtle, elegant prose with deep psychological insight. Emphasize emotional truth over plot mechanics.
            Structure: Strong character voice, internal journey, moment of revelation or change.
            Themes: Human nature, relationships, identity, mortality, meaning, social commentary.
            Style: Nuanced prose, subtext, symbolism, careful attention to language and rhythm.""",
            
            StoryGenre.MYSTERY: """Include a central puzzle or crime to solve. Build suspense through clues and red herrings. 
            Provide a satisfying resolution that feels both surprising and inevitable.
            Structure: Setup mystery, investigation with clues, red herrings, revelation, resolution.
            Elements: Detective/investigator character, suspects with motives, logical deduction.
            Pacing: Tension building, strategic revelation of information, climactic solve.""",
            
            StoryGenre.SCIENCE_FICTION: """Incorporate speculative technology or scientific concepts. 
            Explore how these elements impact characters and society.
            Structure: Establish speculative element, explore implications, character adaptation.
            Elements: Scientific plausibility, technological impact, future societies, ethical dilemmas.
            Themes: Progress vs tradition, humanity vs technology, exploration, evolution.""",
            
            StoryGenre.FANTASY: """Include magical or supernatural elements. Create an immersive world with its own rules.
            Structure: Establish magical world/rules, character discovery/growth, magical resolution.
            Elements: Magic system, fantastical creatures, quest elements, world-building.
            Themes: Good vs evil, power and responsibility, coming of age, heroism.""",
            
            StoryGenre.ROMANCE: """Focus on emotional connection between characters. Build tension through relationship conflicts.
            Structure: Meet cute/conflict, developing attraction, obstacles, emotional resolution.
            Elements: Character chemistry, emotional growth, relationship obstacles, satisfying resolution.
            Themes: Love conquers all, personal growth, trust, vulnerability, commitment."""
        }
        
        # Enhanced length guidelines with structure recommendations
        self.length_guidelines = {
            StoryLength.FLASH: """Tell a complete story in under 1000 words. Focus on a single moment, revelation, 
            or emotional truth. Every word must count.
            Structure: Immediate opening, swift development, powerful conclusion.
            Techniques: In medias res, tight focus, powerful imagery, emotional punch.
            Word allocation: 100-200 opening, 400-600 development, 200-300 conclusion.""",
            
            StoryLength.SHORT: """Develop a full narrative arc in 1000-7500 words. Include character development, 
            plot progression, and satisfying resolution.
            Structure: Engaging opening (10%), rising action (60%), climax (20%), resolution (10%).
            Elements: Character arc, subplot potential, detailed world-building, complex themes.
            Pacing: Allow for character development, scene changes, multiple conflicts."""
        }
        
        # Character development guidelines per genre and length
        self.character_guidelines = {
            (StoryGenre.LITERARY, StoryLength.FLASH): """Single protagonist with clear internal conflict. 
            Focus on moment of change or realization. Deep psychological insight in few words.""",
            
            (StoryGenre.LITERARY, StoryLength.SHORT): """Well-developed protagonist with complex internal life. 
            Supporting characters that illuminate main character. Character arc with meaningful change.""",
            
            (StoryGenre.MYSTERY, StoryLength.FLASH): """Detective/investigator with clear motivation. 
            Suspect(s) with believable motives. Focus on deduction process.""",
            
            (StoryGenre.MYSTERY, StoryLength.SHORT): """Compelling detective with personal stakes. 
            Multiple suspects with layered motives. Character development through investigation.""",
            
            (StoryGenre.SCIENCE_FICTION, StoryLength.FLASH): """Character confronting technological/scientific change. 
            Clear reaction to speculative element. Adaptation or transformation.""",
            
            (StoryGenre.SCIENCE_FICTION, StoryLength.SHORT): """Character navigating complex future society. 
            Multiple characters representing different viewpoints on technology/change.""",
            
            (StoryGenre.FANTASY, StoryLength.FLASH): """Character discovering or using magical ability. 
            Clear connection between character and magical element.""",
            
            (StoryGenre.FANTASY, StoryLength.SHORT): """Hero's journey elements. Character growth through magical challenges. 
            Supporting characters in magical world.""",
            
            (StoryGenre.ROMANCE, StoryLength.FLASH): """Two characters with immediate chemistry and conflict. 
            Focus on emotional connection and single relationship obstacle.""",
            
            (StoryGenre.ROMANCE, StoryLength.SHORT): """Well-developed romantic leads with individual character arcs. 
            Believable relationship progression through multiple obstacles."""
        }
        
        # Theme integration patterns by genre
        self.theme_integration = {
            StoryGenre.LITERARY: """Weave theme naturally through character actions and dialogue. 
            Use symbolism and subtext. Let theme emerge from character journey rather than stating explicitly.""",
            
            StoryGenre.MYSTERY: """Connect theme to the mystery being solved. 
            What the crime reveals about human nature, society, or justice.""",
            
            StoryGenre.SCIENCE_FICTION: """Link theme to speculative elements. 
            How does the science fiction concept illuminate the theme?""",
            
            StoryGenre.FANTASY: """Embed theme in magical world rules and character quests. 
            What does the fantasy element teach about the theme?""",
            
            StoryGenre.ROMANCE: """Express theme through relationship dynamics. 
            How does the romantic journey embody the larger theme?"""
        }
        
        # Enhanced validation rules
        self.validation_rules = {
            ValidationLevel.BASIC: {
                "word_count_tolerance": 0.3,  # 30% variance allowed
                "require_theme_check": False,
                "require_structure_check": False,
                "require_character_check": False
            },
            ValidationLevel.STANDARD: {
                "word_count_tolerance": 0.2,  # 20% variance allowed
                "require_theme_check": True,
                "require_structure_check": True,
                "require_character_check": False
            },
            ValidationLevel.STRICT: {
                "word_count_tolerance": 0.1,  # 10% variance allowed
                "require_theme_check": True,
                "require_structure_check": True,
                "require_character_check": True
            }
        }
        
        # Outline generation patterns by genre and length
        self.outline_patterns = {
            (StoryGenre.LITERARY, StoryLength.FLASH): {
                "focus": "single transformative moment",
                "structure": "setup → realization → change",
                "character_emphasis": "internal state",
                "theme_approach": "subtle revelation"
            },
            (StoryGenre.LITERARY, StoryLength.SHORT): {
                "focus": "character journey and growth",
                "structure": "setup → complications → insight → resolution",
                "character_emphasis": "development arc",
                "theme_approach": "layered exploration"
            },
            (StoryGenre.MYSTERY, StoryLength.FLASH): {
                "focus": "single clue or revelation",
                "structure": "mystery → investigation → solution",
                "character_emphasis": "deduction process",
                "theme_approach": "justice or truth"
            },
            (StoryGenre.MYSTERY, StoryLength.SHORT): {
                "focus": "full investigation with red herrings",
                "structure": "crime → investigation → false leads → true solution",
                "character_emphasis": "detective's method",
                "theme_approach": "broader implications"
            },
            # Add patterns for other genres...
        }
        
        # Tool usage tracking
        self.tool_usage_log: List[str] = []
        
        # Performance metrics
        self.metrics = {
            "tools_called": 0,
            "generation_attempts": 0,
            "validation_runs": 0
        }
    
    def log_tool_usage(self, tool_name: str, context: str = "") -> None:
        """Log tool usage for metadata tracking"""
        entry = f"{tool_name}"
        if context:
            entry += f"({context})"
        self.tool_usage_log.append(entry)
        self.metrics["tools_called"] += 1
    
    def get_character_guidelines_for(self, genre: StoryGenre, length: StoryLength) -> str:
        """Get specific character guidelines for genre/length combination"""
        return self.character_guidelines.get(
            (genre, length), 
            "Create compelling characters appropriate for the genre and length."
        )
    
    def get_theme_integration_for(self, genre: StoryGenre) -> str:
        """Get theme integration guidance for specific genre"""
        return self.theme_integration.get(
            genre,
            "Integrate theme naturally through character actions and story events."
        )
    
    def get_outline_pattern_for(self, genre: StoryGenre, length: StoryLength) -> Dict[str, str]:
        """Get outline pattern for specific genre/length combination"""
        return self.outline_patterns.get(
            (genre, length),
            {
                "focus": "engaging narrative",
                "structure": "beginning → middle → end",
                "character_emphasis": "clear motivation",
                "theme_approach": "natural integration"
            }
        )
    
    def get_validation_rules_for(self, level: ValidationLevel) -> Dict[str, Any]:
        """Get validation rules for specified level"""
        return self.validation_rules.get(level, self.validation_rules[ValidationLevel.STANDARD])
    
    def reset_metrics(self) -> None:
        """Reset performance metrics for new generation"""
        self.tool_usage_log.clear()
        self.metrics = {
            "tools_called": 0,
            "generation_attempts": 0,
            "validation_runs": 0
        }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get summary of performance metrics"""
        return {
            "tools_used": self.tool_usage_log.copy(),
            "metrics": self.metrics.copy(),
            "total_tools_called": len(self.tool_usage_log)
        }