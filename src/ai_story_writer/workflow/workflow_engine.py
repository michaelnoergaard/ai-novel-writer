"""
Workflow Engine - Version 1.3 Implementation
Advanced workflow orchestration for story generation with multi-step pipelines
"""

import asyncio
import logging
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Awaitable
from enum import Enum

from ..models.basic_models import StoryRequirements
from ..models.v13_models import (
    WorkflowState, WorkflowStage, AdvancedGeneratedStory,
    GenerationStrategy, PerformanceMetrics, QualityMetrics, ToolUsageReport
)
from ..utils.config import StoryGenerationError, WorkflowError

# Setup logging
logger = logging.getLogger(__name__)


class WorkflowStep:
    """Represents a single step in the workflow pipeline"""
    
    def __init__(
        self,
        name: str,
        stage: WorkflowStage,
        handler: Callable[..., Awaitable[Any]],
        timeout: int = 60,
        retry_count: int = 2,
        required: bool = True
    ):
        self.name = name
        self.stage = stage
        self.handler = handler
        self.timeout = timeout
        self.retry_count = retry_count
        self.required = required


class WorkflowEngine:
    """
    Orchestrates multi-step story generation workflows with intelligent routing,
    progress tracking, and error recovery.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.workflows: Dict[str, WorkflowState] = {}
        self.steps: List[WorkflowStep] = []
        self.performance_data: Dict[str, List[float]] = {}
        
        # Default configuration
        self.max_workflow_time = self.config.get('max_workflow_time', 300)
        self.enable_quality_enhancement = self.config.get('enable_quality_enhancement', True)
        self.quality_threshold = self.config.get('quality_threshold', 7.0)
        self.max_enhancement_iterations = self.config.get('max_enhancement_iterations', 2)
        
        logger.info("WorkflowEngine initialized with configuration")
    
    def register_step(
        self,
        name: str,
        stage: WorkflowStage,
        handler: Callable[..., Awaitable[Any]],
        **kwargs
    ) -> None:
        """Register a workflow step with the engine"""
        step = WorkflowStep(name, stage, handler, **kwargs)
        self.steps.append(step)
        logger.debug(f"Registered workflow step: {name} ({stage.value})")
    
    async def execute_workflow(
        self,
        requirements: StoryRequirements,
        strategy: GenerationStrategy,
        progress_callback: Optional[Callable[[WorkflowState], None]] = None
    ) -> AdvancedGeneratedStory:
        """
        Execute a complete workflow for story generation
        
        Args:
            requirements: Story generation requirements
            strategy: Selected generation strategy
            progress_callback: Optional callback for progress updates
            
        Returns:
            AdvancedGeneratedStory with complete workflow results
        """
        workflow_id = str(uuid.uuid4())
        start_time = time.time()
        
        try:
            # Initialize workflow state
            workflow_state = WorkflowState(
                workflow_id=workflow_id,
                stage=WorkflowStage.ANALYSIS,
                progress=0.0,
                current_step="initialization",
                steps_completed=[],
                steps_remaining=[step.name for step in self.steps],
                estimated_completion_time=datetime.now() + timedelta(seconds=self.max_workflow_time),
                error_count=0,
                last_error=None
            )
            
            self.workflows[workflow_id] = workflow_state
            logger.info(f"Starting workflow {workflow_id} with strategy {strategy.value}")
            
            # Execute workflow steps
            context = {
                'requirements': requirements,
                'strategy': strategy,
                'workflow_id': workflow_id,
                'results': {},
                'quality_metrics': None,
                'story_content': None,
                'story_title': None
            }
            
            total_steps = len(self.steps)
            
            for i, step in enumerate(self.steps):
                try:
                    # Update workflow state
                    workflow_state.stage = step.stage
                    workflow_state.current_step = step.name
                    workflow_state.progress = i / total_steps
                    
                    if progress_callback:
                        progress_callback(workflow_state)
                    
                    logger.debug(f"Executing step: {step.name}")
                    
                    # Execute step with timeout and retry
                    result = await self._execute_step_with_retry(step, context)
                    
                    # Update context with results
                    context['results'][step.name] = result
                    
                    # Update workflow state
                    workflow_state.steps_completed.append(step.name)
                    workflow_state.steps_remaining.remove(step.name)
                    
                    logger.debug(f"Completed step: {step.name}")
                    
                except Exception as e:
                    workflow_state.error_count += 1
                    workflow_state.last_error = str(e)
                    
                    logger.error(f"Error in workflow step {step.name}: {e}")
                    
                    if step.required:
                        # Critical step failed, abort workflow
                        raise WorkflowError(f"Required step '{step.name}' failed: {e}")
                    else:
                        # NO OPTIONAL STEPS - ALL MUST SUCCEED
                        raise StoryGenerationError(f"Critical workflow step '{step.name}' failed")
            
            # Finalize workflow
            workflow_state.stage = WorkflowStage.FINALIZATION
            workflow_state.progress = 1.0
            workflow_state.current_step = "finalization"
            
            if progress_callback:
                progress_callback(workflow_state)
            
            # Build final result
            generation_time = time.time() - start_time
            
            # Create performance metrics
            performance_metrics = PerformanceMetrics(
                total_generation_time=generation_time,
                workflow_execution_time=generation_time * 0.1,  # Approximate 10% workflow overhead
                ai_generation_time=generation_time * 0.8,  # Approximate 80% AI generation time
                quality_assessment_time=generation_time * 0.1,  # Approximate 10% assessment time
                api_calls_made=len(workflow_state.steps_completed)
            )
            
            # Create tool usage report
            tool_usage_report = ToolUsageReport(
                tools_used=['agent_run'],  # Since we're using direct agent.run() calls
                total_tool_calls=len(workflow_state.steps_completed),
                successful_calls=len(workflow_state.steps_completed) - workflow_state.error_count,
                failed_calls=workflow_state.error_count
            )
            
            result = AdvancedGeneratedStory(
                # Core story content
                title=context.get('story_title', 'Untitled Story'),
                content=context.get('story_content', ''),
                word_count=len(context.get('story_content', '').split()),
                genre=requirements.genre,
                
                # V1.3 enhancements
                workflow_state=workflow_state,
                quality_metrics=context.get('quality_metrics') or QualityMetrics(),
                generation_strategy=strategy,
                performance_metrics=performance_metrics,
                tool_usage_report=tool_usage_report,
                generation_time=generation_time,
                workflow_id=workflow_id,
                strategy_used=strategy.value,
                
                # Metadata from V1.2
                requirements=requirements,
                generation_method=strategy.value,
                outline_used=context['results'].get('outline_generation'),
                validation_results=context['results'].get('quality_assessment'),
                metadata={
                    'workflow_steps': len(workflow_state.steps_completed),
                    'total_errors': workflow_state.error_count,
                    'generation_time': generation_time
                }
            )
            
            logger.info(f"Workflow {workflow_id} completed successfully in {generation_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Workflow {workflow_id} failed: {e}")
            raise WorkflowError(f"Workflow execution failed: {e}") from e
        
        finally:
            # Cleanup workflow state
            if workflow_id in self.workflows:
                del self.workflows[workflow_id]
    
    async def _execute_step_with_retry(
        self,
        step: WorkflowStep,
        context: Dict[str, Any]
    ) -> Any:
        """Execute a workflow step with timeout and retry logic"""
        
        for attempt in range(step.retry_count + 1):
            try:
                # Execute step with timeout
                result = await asyncio.wait_for(
                    step.handler(context),
                    timeout=step.timeout
                )
                
                # Record successful execution
                self._record_step_performance(step.name, time.time())
                
                return result
                
            except asyncio.TimeoutError:
                logger.warning(f"Step {step.name} timed out on attempt {attempt + 1}")
                if attempt == step.retry_count:
                    raise WorkflowError(f"Step {step.name} timed out after {step.retry_count + 1} attempts")
            
            except Exception as e:
                logger.warning(f"Step {step.name} failed on attempt {attempt + 1}: {e}")
                if attempt == step.retry_count:
                    raise
                
                # Wait before retry
                await asyncio.sleep(min(2 ** attempt, 10))  # Exponential backoff
    
    def _record_step_performance(self, step_name: str, execution_time: float) -> None:
        """Record performance data for a workflow step"""
        if step_name not in self.performance_data:
            self.performance_data[step_name] = []
        
        self.performance_data[step_name].append(execution_time)
        
        # Keep only recent performance data (last 100 executions)
        if len(self.performance_data[step_name]) > 100:
            self.performance_data[step_name] = self.performance_data[step_name][-100:]
    
    def get_workflow_state(self, workflow_id: str) -> Optional[WorkflowState]:
        """Get the current state of a running workflow"""
        return self.workflows.get(workflow_id)
    
    def get_performance_statistics(self) -> Dict[str, Dict[str, float]]:
        """Get performance statistics for all workflow steps"""
        stats = {}
        
        for step_name, times in self.performance_data.items():
            if times:
                stats[step_name] = {
                    'avg_time': sum(times) / len(times),
                    'min_time': min(times),
                    'max_time': max(times),
                    'executions': len(times)
                }
        
        return stats
    
    def cleanup_completed_workflows(self, max_age_seconds: int = 3600) -> int:
        """Clean up old completed workflows"""
        cutoff_time = datetime.now() - timedelta(seconds=max_age_seconds)
        cleaned = 0
        
        workflows_to_remove = []
        for workflow_id, state in self.workflows.items():
            if (state.stage == WorkflowStage.FINALIZATION and 
                state.estimated_completion_time and 
                state.estimated_completion_time < cutoff_time):
                workflows_to_remove.append(workflow_id)
        
        for workflow_id in workflows_to_remove:
            del self.workflows[workflow_id]
            cleaned += 1
        
        logger.debug(f"Cleaned up {cleaned} completed workflows")
        return cleaned