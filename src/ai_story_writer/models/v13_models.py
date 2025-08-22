"""
Version 1.3 Enhanced Models - Advanced Workflow and Quality Assessment
Extended data structures for workflow orchestration, quality assessment, and performance monitoring
"""

from enum import Enum
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field

# Import existing models to maintain compatibility
from .basic_models import StoryGenre, StoryLength, StoryRequirements
from .enhanced_models import EnhancedGeneratedStory, GenerationMethod, ValidationResult, GenerationMetadata


class WorkflowStage(str, Enum):
    """Stages in the story generation workflow"""
    ANALYSIS = "analysis"
    STRATEGY_SELECTION = "strategy_selection"
    OUTLINE_GENERATION = "outline_generation"
    CONTENT_GENERATION = "content_generation"
    QUALITY_ASSESSMENT = "quality_assessment"
    ENHANCEMENT = "enhancement"
    FINALIZATION = "finalization"


class GenerationStrategy(str, Enum):
    """Available generation strategies for V1.3"""
    DIRECT = "direct"           # Single-pass generation
    OUTLINE = "outline"         # Multi-step with outline
    ITERATIVE = "iterative"     # Multiple passes with improvement
    ADAPTIVE = "adaptive"       # Dynamic approach based on requirements


class WorkflowState(BaseModel):
    """Tracks the state of a workflow execution"""
    workflow_id: str
    stage: WorkflowStage
    progress: float = Field(ge=0.0, le=1.0, description="Completion percentage")
    current_step: str
    steps_completed: List[str] = Field(default_factory=list)
    steps_remaining: List[str] = Field(default_factory=list)
    estimated_completion_time: Optional[datetime] = None
    error_count: int = Field(default=0, ge=0)
    last_error: Optional[str] = None
    
    # Performance tracking
    start_time: Optional[datetime] = Field(default_factory=datetime.now)
    stage_times: Dict[str, float] = Field(default_factory=dict)
    
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }


class QualityMetrics(BaseModel):
    """Comprehensive quality assessment metrics"""
    overall_score: float = Field(default=0.0, ge=0.0, le=10.0, description="Overall quality score")
    structure_score: float = Field(default=0.0, ge=0.0, le=10.0, description="Narrative structure quality")
    coherence_score: float = Field(default=0.0, ge=0.0, le=10.0, description="Story coherence and flow")
    genre_compliance: float = Field(default=0.0, ge=0.0, le=10.0, description="Genre convention adherence")
    character_development: float = Field(default=0.0, ge=0.0, le=10.0, description="Character depth and consistency")
    pacing_quality: float = Field(default=0.0, ge=0.0, le=10.0, description="Story pacing assessment")
    theme_integration: float = Field(default=0.0, ge=0.0, le=10.0, description="Theme incorporation quality")
    
    # Detailed assessments
    word_count_accuracy: float = Field(default=0.0, ge=0.0, le=1.0, description="Word count precision")
    grammar_quality: float = Field(default=0.0, ge=0.0, le=10.0, description="Grammar and style quality")
    originality_score: float = Field(default=0.0, ge=0.0, le=10.0, description="Story originality")
    
    # Assessment metadata
    assessment_time: Optional[datetime] = Field(default_factory=datetime.now)
    assessment_method: str = Field(default="automated", description="Method used for assessment")
    confidence_level: float = Field(default=0.0, ge=0.0, le=1.0, description="Assessment confidence")


class ImprovementSuggestion(BaseModel):
    """Specific suggestions for story improvement"""
    category: str = Field(description="Category of improvement (structure, character, etc.)")
    priority: str = Field(description="Priority level (high, medium, low)")
    suggestion: str = Field(description="Specific improvement suggestion")
    reasoning: str = Field(description="Why this improvement is suggested")
    estimated_impact: float = Field(ge=0.0, le=1.0, description="Expected quality improvement")


class PerformanceMetrics(BaseModel):
    """Performance and execution metrics for generation process"""
    total_generation_time: float = Field(ge=0.0, description="Total generation time in seconds")
    workflow_execution_time: float = Field(ge=0.0, description="Workflow orchestration time")
    ai_generation_time: float = Field(ge=0.0, description="AI model generation time")
    quality_assessment_time: float = Field(ge=0.0, description="Quality assessment time")
    
    # Stage-specific timing
    stage_times: Dict[str, float] = Field(default_factory=dict)
    
    # Resource utilization
    memory_usage_mb: Optional[float] = Field(default=None, ge=0.0)
    cpu_usage_percent: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    
    # API usage
    api_calls_made: int = Field(default=0, ge=0)
    tokens_used: int = Field(default=0, ge=0)
    
    # Success metrics
    retry_count: int = Field(default=0, ge=0)
    error_count: int = Field(default=0, ge=0)
    success_rate: float = Field(default=1.0, ge=0.0, le=1.0)


class ToolUsageReport(BaseModel):
    """Report on tool usage during generation"""
    tools_used: List[str] = Field(default_factory=list)
    tool_execution_times: Dict[str, float] = Field(default_factory=dict)
    tool_success_rates: Dict[str, float] = Field(default_factory=dict)
    tool_effectiveness_scores: Dict[str, float] = Field(default_factory=dict)
    
    # Tool recommendations
    recommended_tools: List[str] = Field(default_factory=list)
    unused_beneficial_tools: List[str] = Field(default_factory=list)


class AdvancedGeneratedStory(BaseModel):
    """Enhanced story result with V1.3 workflow and quality features"""
    
    # Core story content (inherited from V1.2)
    title: str
    content: str
    word_count: int
    genre: StoryGenre
    
    # V1.3 enhancements
    workflow_state: WorkflowState
    quality_metrics: QualityMetrics
    generation_strategy: GenerationStrategy
    performance_metrics: PerformanceMetrics
    tool_usage_report: ToolUsageReport
    improvement_suggestions: List[ImprovementSuggestion] = Field(default_factory=list)
    
    # Metadata
    generation_time: float
    workflow_id: str
    strategy_used: str
    quality_passes: int = Field(default=1, ge=1)
    
    # V1.2 compatibility fields
    requirements: StoryRequirements
    generation_method: str  # For backward compatibility
    outline_used: Optional[Any] = None
    validation_results: Optional[Any] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }


class WorkflowConfiguration(BaseModel):
    """Configuration for workflow execution"""
    default_strategy: GenerationStrategy = GenerationStrategy.ADAPTIVE
    max_workflow_time: int = Field(default=300, ge=60, description="Maximum workflow time in seconds")
    enable_quality_enhancement: bool = Field(default=True)
    quality_threshold: float = Field(default=7.0, ge=0.0, le=10.0)
    max_enhancement_iterations: int = Field(default=2, ge=0, le=5)
    
    # Strategy-specific settings
    direct_timeout: int = Field(default=120, ge=30)
    outline_timeout: int = Field(default=180, ge=60)
    iterative_timeout: int = Field(default=300, ge=120)
    adaptive_timeout: int = Field(default=240, ge=90)
    
    # Quality settings
    enable_real_time_monitoring: bool = Field(default=True)
    quality_check_interval: int = Field(default=30, ge=10)
    minimum_quality_score: float = Field(default=6.0, ge=0.0, le=10.0)
    enable_improvement_suggestions: bool = Field(default=True)


class StrategyRecommendation(BaseModel):
    """Recommendation for generation strategy selection"""
    recommended_strategy: GenerationStrategy
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence in recommendation")
    reasoning: str = Field(description="Why this strategy is recommended")
    estimated_time: float = Field(ge=0.0, description="Estimated generation time")
    estimated_quality: float = Field(ge=0.0, le=10.0, description="Expected quality score")
    
    # Alternative strategies
    alternatives: List[Dict[str, Union[GenerationStrategy, float, str]]] = Field(default_factory=list)


class RequirementAnalysis(BaseModel):
    """Analysis of story requirements for strategy selection"""
    complexity_score: float = Field(ge=0.0, le=1.0, description="Requirement complexity")
    feasibility_score: float = Field(ge=0.0, le=1.0, description="Generation feasibility")
    estimated_difficulty: str = Field(description="Difficulty level (easy, medium, hard)")
    
    # Requirement assessment
    word_count_feasibility: float = Field(ge=0.0, le=1.0)
    genre_familiarity: float = Field(ge=0.0, le=1.0)
    theme_complexity: float = Field(ge=0.0, le=1.0)
    setting_specificity: float = Field(ge=0.0, le=1.0)
    
    # Recommendations
    recommended_tools: List[str] = Field(default_factory=list)
    potential_challenges: List[str] = Field(default_factory=list)
    success_predictors: List[str] = Field(default_factory=list)