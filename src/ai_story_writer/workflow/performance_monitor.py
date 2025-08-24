"""
Performance Monitor - Version 1.3 Implementation
Comprehensive monitoring and metrics collection for story generation workflows
"""

import logging
import time
import threading
import psutil
import os
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from collections import defaultdict, deque

from ..models.story_models import PerformanceMetrics, WorkflowState, GenerationStrategy
from ..utils.config import StoryGenerationError

# Setup logging
logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """
    Monitors and collects comprehensive performance metrics for story generation
    workflows, including timing, resource usage, and success rates.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Configuration
        self.enable_metrics_collection = self.config.get('enable_metrics_collection', True)
        self.metrics_retention_days = self.config.get('metrics_retention_days', 30)
        self.enable_performance_optimization = self.config.get('enable_performance_optimization', True)
        self.resource_monitoring_interval = self.config.get('resource_monitoring_interval', 5.0)
        
        # Metrics storage
        self.workflow_metrics: Dict[str, PerformanceMetrics] = {}
        self.aggregated_metrics: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.resource_usage_history: deque = deque(maxlen=1000)
        
        # Active monitoring
        self.active_workflows: Dict[str, Dict[str, Any]] = {}
        self.monitoring_lock = threading.Lock()
        
        # Resource monitoring thread
        self.resource_monitor_thread: Optional[threading.Thread] = None
        self.stop_monitoring = threading.Event()
        
        if self.enable_metrics_collection:
            self._start_resource_monitoring()
        
        logger.info("PerformanceMonitor initialized")
    
    def start_workflow_monitoring(
        self,
        workflow_id: str,
        strategy: GenerationStrategy,
        requirements_data: Dict[str, Any]
    ) -> None:
        """
        Start monitoring a workflow execution
        
        Args:
            workflow_id: Unique workflow identifier
            strategy: Generation strategy being used
            requirements_data: Story requirements data for context
        """
        if not self.enable_metrics_collection:
            return
        
        try:
            with self.monitoring_lock:
                self.active_workflows[workflow_id] = {
                    'start_time': time.time(),
                    'strategy': strategy.value,
                    'requirements': requirements_data,
                    'stage_times': {},
                    'current_stage': None,
                    'api_calls': 0,
                    'tokens_used': 0,
                    'errors': [],
                    'resource_snapshots': []
                }
            
            logger.debug(f"Started monitoring workflow {workflow_id}")
            
        except Exception as e:
            logger.warning(f"Failed to start workflow monitoring: {e}")
    
    def record_stage_start(self, workflow_id: str, stage: str) -> None:
        """Record the start of a workflow stage"""
        if not self.enable_metrics_collection or workflow_id not in self.active_workflows:
            return
        
        try:
            with self.monitoring_lock:
                workflow_data = self.active_workflows[workflow_id]
                
                # End previous stage if any
                if workflow_data['current_stage']:
                    previous_stage = workflow_data['current_stage']
                    stage_duration = time.time() - workflow_data.get(f'{previous_stage}_start', time.time())
                    workflow_data['stage_times'][previous_stage] = stage_duration
                
                # Start new stage
                workflow_data['current_stage'] = stage
                workflow_data[f'{stage}_start'] = time.time()
                
                # Take resource snapshot
                self._take_resource_snapshot(workflow_id)
            
            logger.debug(f"Workflow {workflow_id} started stage: {stage}")
            
        except Exception as e:
            logger.warning(f"Failed to record stage start: {e}")
    
    def record_stage_end(self, workflow_id: str, stage: str, success: bool = True, error: Optional[str] = None) -> None:
        """Record the end of a workflow stage"""
        if not self.enable_metrics_collection or workflow_id not in self.active_workflows:
            return
        
        try:
            with self.monitoring_lock:
                workflow_data = self.active_workflows[workflow_id]
                
                if workflow_data['current_stage'] == stage:
                    stage_start = workflow_data.get(f'{stage}_start', time.time())
                    stage_duration = time.time() - stage_start
                    workflow_data['stage_times'][stage] = stage_duration
                    workflow_data['current_stage'] = None
                
                if not success and error:
                    workflow_data['errors'].append({
                        'stage': stage,
                        'error': error,
                        'timestamp': datetime.now().isoformat()
                    })
            
            logger.debug(f"Workflow {workflow_id} ended stage: {stage} (success: {success})")
            
        except Exception as e:
            logger.warning(f"Failed to record stage end: {e}")
    
    def record_api_usage(self, workflow_id: str, api_calls: int = 1, tokens_used: int = 0) -> None:
        """Record API usage for a workflow"""
        if not self.enable_metrics_collection or workflow_id not in self.active_workflows:
            return
        
        try:
            with self.monitoring_lock:
                workflow_data = self.active_workflows[workflow_id]
                workflow_data['api_calls'] += api_calls
                workflow_data['tokens_used'] += tokens_used
            
        except Exception as e:
            logger.warning(f"Failed to record API usage: {e}")
    
    def finish_workflow_monitoring(
        self,
        workflow_id: str,
        success: bool,
        quality_score: float = 0.0,
        word_count: int = 0
    ) -> PerformanceMetrics:
        """
        Finish monitoring a workflow and generate performance metrics
        
        Args:
            workflow_id: Workflow identifier
            success: Whether the workflow completed successfully
            quality_score: Quality score achieved
            word_count: Final word count
            
        Returns:
            PerformanceMetrics with comprehensive data
        """
        if not self.enable_metrics_collection:
            return PerformanceMetrics()
        
        try:
            with self.monitoring_lock:
                if workflow_id not in self.active_workflows:
                    logger.warning(f"Workflow {workflow_id} not found in active monitoring")
                    return PerformanceMetrics()
                
                workflow_data = self.active_workflows[workflow_id]
                
                # Calculate total time
                total_time = time.time() - workflow_data['start_time']
                
                # End current stage if any
                if workflow_data['current_stage']:
                    stage = workflow_data['current_stage']
                    stage_start = workflow_data.get(f'{stage}_start', time.time())
                    workflow_data['stage_times'][stage] = time.time() - stage_start
                
                # Calculate resource usage
                memory_usage, cpu_usage = self._calculate_resource_usage(workflow_data['resource_snapshots'])
                
                # Create performance metrics
                metrics = PerformanceMetrics(
                    total_generation_time=total_time,
                    workflow_execution_time=sum(workflow_data['stage_times'].values()),
                    ai_generation_time=workflow_data['stage_times'].get('content_generation', 0.0),
                    quality_assessment_time=workflow_data['stage_times'].get('quality_assessment', 0.0),
                    stage_times=workflow_data['stage_times'],
                    memory_usage_mb=memory_usage,
                    cpu_usage_percent=cpu_usage,
                    api_calls_made=workflow_data['api_calls'],
                    tokens_used=workflow_data['tokens_used'],
                    retry_count=0,  # Would need to be tracked separately
                    error_count=len(workflow_data['errors']),
                    success_rate=1.0 if success else 0.0
                )
                
                # Store metrics
                self.workflow_metrics[workflow_id] = metrics
                
                # Add to aggregated metrics
                self._add_to_aggregated_metrics(workflow_data, metrics, quality_score, word_count)
                
                # Clean up active workflow
                del self.active_workflows[workflow_id]
            
            logger.info(f"Finished monitoring workflow {workflow_id} - Total time: {total_time:.2f}s")
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to finish workflow monitoring: {e}")
            return PerformanceMetrics()
    
    def get_performance_summary(self, days: int = 7) -> Dict[str, Any]:
        """
        Get performance summary for the specified number of days
        
        Args:
            days: Number of days to include in summary
            
        Returns:
            Performance summary statistics
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Filter recent metrics
            recent_metrics = []
            for metrics_list in self.aggregated_metrics.values():
                recent_metrics.extend([
                    m for m in metrics_list 
                    if datetime.fromisoformat(m['timestamp']) > cutoff_date
                ])
            
            if not recent_metrics:
                return {
                    'total_workflows': 0,
                    'success_rate': 0.0,
                    'avg_generation_time': 0.0,
                    'avg_quality_score': 0.0
                }
            
            # Calculate summary statistics
            total_workflows = len(recent_metrics)
            successful_workflows = sum(1 for m in recent_metrics if m['success'])
            success_rate = successful_workflows / total_workflows
            
            avg_generation_time = sum(m['total_time'] for m in recent_metrics) / total_workflows
            avg_quality_score = sum(m['quality_score'] for m in recent_metrics if m['success']) / max(successful_workflows, 1)
            
            # Strategy performance
            strategy_stats = defaultdict(lambda: {'count': 0, 'success': 0, 'avg_time': 0.0, 'avg_quality': 0.0})
            
            for m in recent_metrics:
                strategy = m['strategy']
                strategy_stats[strategy]['count'] += 1
                if m['success']:
                    strategy_stats[strategy]['success'] += 1
                strategy_stats[strategy]['avg_time'] += m['total_time']
                if m['success']:
                    strategy_stats[strategy]['avg_quality'] += m['quality_score']
            
            # Finalize strategy stats
            for strategy, stats in strategy_stats.items():
                stats['success_rate'] = stats['success'] / stats['count']
                stats['avg_time'] /= stats['count']
                if stats['success'] > 0:
                    stats['avg_quality'] /= stats['success']
            
            # Resource usage trends
            resource_summary = self._get_resource_usage_summary()
            
            summary = {
                'period_days': days,
                'total_workflows': total_workflows,
                'success_rate': success_rate,
                'avg_generation_time': avg_generation_time,
                'avg_quality_score': avg_quality_score,
                'strategy_performance': dict(strategy_stats),
                'resource_usage': resource_summary,
                'error_analysis': self._analyze_errors(recent_metrics)
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to generate performance summary: {e}")
            return {}
    
    def get_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """Get recommendations for performance optimization"""
        if not self.enable_performance_optimization:
            return []
        
        try:
            recommendations = []
            summary = self.get_performance_summary(days=14)
            
            if not summary or summary['total_workflows'] == 0:
                return recommendations
            
            # Time-based recommendations
            if summary['avg_generation_time'] > 180:
                recommendations.append({
                    'category': 'performance',
                    'priority': 'medium',
                    'recommendation': 'Consider using faster generation strategies for simple requirements',
                    'reason': f'Average generation time is {summary["avg_generation_time"]:.1f}s, above optimal range',
                    'impact': 'Reduce generation time by 20-30%'
                })
            
            # Success rate recommendations
            if summary['success_rate'] < 0.9:
                recommendations.append({
                    'category': 'reliability',
                    'priority': 'high',
                    'recommendation': 'Improve error handling and add more validation',
                    'reason': f'Success rate is {summary["success_rate"]:.1%}, below target of 90%',
                    'impact': 'Increase success rate and user satisfaction'
                })
            
            # Quality recommendations
            if summary['avg_quality_score'] < 7.0:
                recommendations.append({
                    'category': 'quality',
                    'priority': 'medium',
                    'recommendation': 'Enhance quality assessment and use iterative strategies more often',
                    'reason': f'Average quality score is {summary["avg_quality_score"]:.1f}, below target of 7.0',
                    'impact': 'Improve story quality and user satisfaction'
                })
            
            # Strategy-specific recommendations
            strategy_perf = summary.get('strategy_performance', {})
            for strategy, stats in strategy_perf.items():
                if stats['count'] > 5:  # Only recommend for strategies with sufficient data
                    if stats['success_rate'] < 0.8:
                        recommendations.append({
                            'category': 'strategy',
                            'priority': 'medium',
                            'recommendation': f'Review and improve {strategy} strategy implementation',
                            'reason': f'{strategy} strategy has {stats["success_rate"]:.1%} success rate',
                            'impact': 'Improve strategy-specific performance'
                        })
            
            # Resource usage recommendations
            resource_usage = summary.get('resource_usage', {})
            if resource_usage.get('avg_memory_mb', 0) > 500:
                recommendations.append({
                    'category': 'resource',
                    'priority': 'low',
                    'recommendation': 'Optimize memory usage in generation workflows',
                    'reason': f'Average memory usage is {resource_usage["avg_memory_mb"]:.0f}MB',
                    'impact': 'Reduce resource consumption'
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to generate optimization recommendations: {e}")
            return []
    
    def cleanup_old_metrics(self) -> int:
        """Clean up old metrics data"""
        try:
            cutoff_date = datetime.now() - timedelta(days=self.metrics_retention_days)
            cleaned_count = 0
            
            # Clean aggregated metrics
            for strategy in list(self.aggregated_metrics.keys()):
                original_count = len(self.aggregated_metrics[strategy])
                self.aggregated_metrics[strategy] = [
                    m for m in self.aggregated_metrics[strategy]
                    if datetime.fromisoformat(m['timestamp']) > cutoff_date
                ]
                cleaned_count += original_count - len(self.aggregated_metrics[strategy])
            
            # Clean workflow metrics (keep recent ones)
            workflows_to_remove = []
            for workflow_id, metrics in self.workflow_metrics.items():
                # Assuming we can derive timestamp from workflow_id or add timestamp field
                # For now, just keep last 100 workflow metrics
                pass
            
            if len(self.workflow_metrics) > 100:
                sorted_workflows = sorted(self.workflow_metrics.items(), key=lambda x: x[0])
                workflows_to_remove = sorted_workflows[:-100]
                for workflow_id, _ in workflows_to_remove:
                    del self.workflow_metrics[workflow_id]
                cleaned_count += len(workflows_to_remove)
            
            logger.info(f"Cleaned up {cleaned_count} old metrics records")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup old metrics: {e}")
            return 0
    
    def stop(self) -> None:
        """Stop the performance monitor"""
        try:
            self.stop_monitoring.set()
            if self.resource_monitor_thread and self.resource_monitor_thread.is_alive():
                self.resource_monitor_thread.join(timeout=5.0)
            
            logger.info("PerformanceMonitor stopped")
            
        except Exception as e:
            logger.error(f"Error stopping PerformanceMonitor: {e}")
    
    def _start_resource_monitoring(self) -> None:
        """Start background resource monitoring"""
        try:
            self.resource_monitor_thread = threading.Thread(
                target=self._resource_monitoring_loop,
                daemon=True
            )
            self.resource_monitor_thread.start()
            logger.debug("Started resource monitoring thread")
            
        except Exception as e:
            logger.warning(f"Failed to start resource monitoring: {e}")
    
    def _resource_monitoring_loop(self) -> None:
        """Background loop for resource monitoring"""
        while not self.stop_monitoring.is_set():
            try:
                # Get current resource usage
                memory_usage = psutil.Process().memory_info().rss / 1024 / 1024  # MB
                cpu_usage = psutil.Process().cpu_percent()
                
                # Store in history
                self.resource_usage_history.append({
                    'timestamp': datetime.now().isoformat(),
                    'memory_mb': memory_usage,
                    'cpu_percent': cpu_usage
                })
                
                # Wait for next interval
                self.stop_monitoring.wait(self.resource_monitoring_interval)
                
            except Exception as e:
                logger.warning(f"Resource monitoring error: {e}")
                self.stop_monitoring.wait(self.resource_monitoring_interval)
    
    def _take_resource_snapshot(self, workflow_id: str) -> None:
        """Take a resource usage snapshot for a workflow"""
        try:
            if workflow_id in self.active_workflows:
                memory_usage = psutil.Process().memory_info().rss / 1024 / 1024  # MB
                cpu_usage = psutil.Process().cpu_percent()
                
                self.active_workflows[workflow_id]['resource_snapshots'].append({
                    'timestamp': time.time(),
                    'memory_mb': memory_usage,
                    'cpu_percent': cpu_usage
                })
        except Exception as e:
            logger.warning(f"Failed to take resource snapshot: {e}")
    
    def _calculate_resource_usage(self, snapshots: List[Dict[str, Any]]) -> tuple[float, float]:
        """Calculate average resource usage from snapshots"""
        if not snapshots:
            return 0.0, 0.0
        
        avg_memory = sum(s['memory_mb'] for s in snapshots) / len(snapshots)
        avg_cpu = sum(s['cpu_percent'] for s in snapshots) / len(snapshots)
        
        return avg_memory, avg_cpu
    
    def _add_to_aggregated_metrics(
        self,
        workflow_data: Dict[str, Any],
        metrics: PerformanceMetrics,
        quality_score: float,
        word_count: int
    ) -> None:
        """Add workflow data to aggregated metrics"""
        try:
            strategy = workflow_data['strategy']
            
            aggregated_record = {
                'timestamp': datetime.now().isoformat(),
                'strategy': strategy,
                'success': metrics.success_rate > 0.5,
                'total_time': metrics.total_generation_time,
                'quality_score': quality_score,
                'word_count': word_count,
                'api_calls': metrics.api_calls_made,
                'tokens_used': metrics.tokens_used,
                'error_count': metrics.error_count,
                'genre': workflow_data['requirements'].get('genre', 'unknown'),
                'target_word_count': workflow_data['requirements'].get('target_word_count', 0)
            }
            
            self.aggregated_metrics[strategy].append(aggregated_record)
            
            # Keep only recent records per strategy
            if len(self.aggregated_metrics[strategy]) > 200:
                self.aggregated_metrics[strategy] = self.aggregated_metrics[strategy][-200:]
                
        except Exception as e:
            logger.warning(f"Failed to add to aggregated metrics: {e}")
    
    def _get_resource_usage_summary(self) -> Dict[str, float]:
        """Get summary of resource usage"""
        try:
            if not self.resource_usage_history:
                return {}
            
            memory_values = [r['memory_mb'] for r in self.resource_usage_history]
            cpu_values = [r['cpu_percent'] for r in self.resource_usage_history]
            
            return {
                'avg_memory_mb': sum(memory_values) / len(memory_values),
                'max_memory_mb': max(memory_values),
                'avg_cpu_percent': sum(cpu_values) / len(cpu_values),
                'max_cpu_percent': max(cpu_values)
            }
            
        except Exception as e:
            logger.warning(f"Failed to get resource usage summary: {e}")
            return {}
    
    def _analyze_errors(self, metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze error patterns in metrics"""
        try:
            failed_metrics = [m for m in metrics if not m['success']]
            
            if not failed_metrics:
                return {'total_errors': 0, 'error_rate': 0.0}
            
            error_analysis = {
                'total_errors': len(failed_metrics),
                'error_rate': len(failed_metrics) / len(metrics),
                'errors_by_strategy': defaultdict(int),
                'errors_by_genre': defaultdict(int)
            }
            
            for m in failed_metrics:
                error_analysis['errors_by_strategy'][m['strategy']] += 1
                error_analysis['errors_by_genre'][m['genre']] += 1
            
            return dict(error_analysis)
            
        except Exception as e:
            logger.warning(f"Failed to analyze errors: {e}")
            return {'total_errors': 0}