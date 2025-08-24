"""
AI Story Writer V1.5 - Optimization and Efficiency Systems
Resource optimization and efficiency analysis for adaptive intelligence.
"""

import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from collections import defaultdict

from ..models.story_models import (
    AdaptiveGenerationConfig, GenerationPredictions, EfficiencyMetrics,
    OptimizationOpportunity, SystemContext, QualityEnhancedResult
)
from ..utils import StoryGenerationError

logger = logging.getLogger(__name__)


class ResourceOptimizationEngine:
    """Optimizes computational resource usage for story generation"""
    
    def __init__(self, config: AdaptiveGenerationConfig):
        """Initialize resource optimization engine - must succeed"""
        self.config = config
        self.resource_history: List[Dict[str, Any]] = []
        self.optimization_cache: Dict[str, Any] = {}
        self.peak_usage_patterns: Dict[str, float] = {}
        
        # Resource optimization thresholds
        self.thresholds = {
            "token_efficiency_min": 0.3,      # Min quality points per 1000 tokens
            "time_efficiency_min": 1.5,       # Min quality points per second
            "cache_hit_target": 0.4,          # Target cache hit rate
            "adaptation_overhead_max": 0.2,   # Max adaptation overhead ratio
            "parallel_threshold": 3000        # Token count for parallel processing
        }
        
        logger.info("ResourceOptimizationEngine initialized")
    
    async def optimize_resource_allocation(
        self,
        requirements: Any,
        predictions: GenerationPredictions,
        system_context: Optional[SystemContext] = None
    ) -> Dict[str, Any]:
        """Optimize resource allocation for generation"""
        
        try:
            optimization_plan = {
                "token_optimization": {},
                "time_optimization": {},
                "cache_strategy": {},
                "parallel_processing": {},
                "resource_limits": {}
            }
            
            # Token optimization
            if predictions.predicted_token_usage > 8000:
                optimization_plan["token_optimization"] = {
                    "enable_token_streaming": True,
                    "use_cached_components": True,
                    "optimize_prompts": True,
                    "estimated_savings": min(0.2, (predictions.predicted_token_usage - 8000) / 10000)
                }
            
            # Time optimization
            if predictions.predicted_generation_time > 90:
                optimization_plan["time_optimization"] = {
                    "enable_parallel_assessment": True,
                    "use_prediction_shortcuts": True,
                    "optimize_workflow_order": True,
                    "estimated_speedup": 1.2 if system_context and system_context.current_load < 0.5 else 1.1
                }
            
            # Cache strategy
            cache_key = self._generate_cache_key(requirements)
            if cache_key in self.optimization_cache:
                optimization_plan["cache_strategy"] = {
                    "use_cached_outline": True,
                    "use_cached_analysis": True,
                    "cache_hit_probability": 0.7,
                    "estimated_time_savings": 15.0  # seconds
                }
            
            # Parallel processing
            if predictions.predicted_token_usage > self.thresholds["parallel_threshold"]:
                optimization_plan["parallel_processing"] = {
                    "enable_concurrent_assessment": True,
                    "parallel_enhancement_analysis": True,
                    "max_concurrent_tasks": 3,
                    "estimated_efficiency_gain": 1.3
                }
            
            # Resource limits based on system context
            if system_context:
                load_factor = system_context.current_load
                optimization_plan["resource_limits"] = {
                    "max_parallel_tasks": max(1, int(4 * (1 - load_factor))),
                    "token_rate_limit": int(1000 * (1.5 - load_factor)),
                    "priority_adjustment": "high" if load_factor < 0.3 else "normal"
                }
            
            logger.debug(f"Resource optimization plan generated with {len(optimization_plan)} strategies")
            return optimization_plan
            
        except Exception as e:
            logger.warning(f"Resource optimization failed: {e}")
            return {"optimization_disabled": True, "error": str(e)}
    
    async def apply_optimizations(
        self,
        optimization_plan: Dict[str, Any],
        generation_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply optimization strategies to generation process"""
        
        applied_optimizations = {}
        
        try:
            # Apply token optimization
            if "token_optimization" in optimization_plan:
                token_opts = optimization_plan["token_optimization"]
                if token_opts.get("use_cached_components", False):
                    generation_context["enable_component_cache"] = True
                    applied_optimizations["component_cache"] = "enabled"
                
                if token_opts.get("optimize_prompts", False):
                    generation_context["use_optimized_prompts"] = True
                    applied_optimizations["prompt_optimization"] = "enabled"
            
            # Apply time optimization
            if "time_optimization" in optimization_plan:
                time_opts = optimization_plan["time_optimization"]
                if time_opts.get("enable_parallel_assessment", False):
                    generation_context["parallel_assessment"] = True
                    applied_optimizations["parallel_assessment"] = "enabled"
                
                if time_opts.get("optimize_workflow_order", False):
                    generation_context["optimized_workflow"] = True
                    applied_optimizations["workflow_optimization"] = "enabled"
            
            # Apply caching strategy
            if "cache_strategy" in optimization_plan:
                cache_opts = optimization_plan["cache_strategy"]
                generation_context["cache_enabled"] = True
                generation_context["cache_level"] = "aggressive" if cache_opts.get("use_cached_analysis", False) else "standard"
                applied_optimizations["caching"] = generation_context["cache_level"]
            
            # Apply parallel processing
            if "parallel_processing" in optimization_plan:
                parallel_opts = optimization_plan["parallel_processing"]
                generation_context["max_concurrent"] = parallel_opts.get("max_concurrent_tasks", 2)
                applied_optimizations["parallel_processing"] = f"{generation_context['max_concurrent']} tasks"
            
            # Apply resource limits
            if "resource_limits" in optimization_plan:
                limits = optimization_plan["resource_limits"]
                generation_context["resource_limits"] = limits
                applied_optimizations["resource_limits"] = "applied"
            
            logger.info(f"Applied {len(applied_optimizations)} optimization strategies")
            return applied_optimizations
            
        except Exception as e:
            logger.warning(f"Failed to apply optimizations: {e}")
            return {"optimization_application_failed": str(e)}
    
    def _generate_cache_key(self, requirements: Any) -> str:
        """Generate cache key for requirements"""
        if hasattr(requirements, 'dict'):
            req_dict = requirements.dict()
        else:
            req_dict = str(requirements)
        
        # Create simplified cache key based on key attributes
        cache_components = [
            str(getattr(requirements, 'genre', 'unknown')),
            str(getattr(requirements, 'target_word_count', 0)),
            str(hash(str(getattr(requirements, 'prompt', ''))))[:8]
        ]
        
        return "_".join(cache_components)


class EfficiencyAnalyzer:
    """Analyzes generation efficiency and identifies optimization opportunities"""
    
    def __init__(self, config: AdaptiveGenerationConfig):
        """Initialize efficiency analyzer - must succeed"""
        self.config = config
        self.efficiency_history: List[Dict[str, Any]] = []
        self.benchmark_metrics: Dict[str, float] = self._initialize_benchmarks()
        
        logger.info("EfficiencyAnalyzer initialized")
    
    def _initialize_benchmarks(self) -> Dict[str, float]:
        """Initialize efficiency benchmarks"""
        return {
            "tokens_per_quality_point": 800,    # Target tokens per quality point
            "seconds_per_quality_point": 8,     # Target seconds per quality point  
            "quality_points_per_pass": 0.5,     # Expected quality gain per enhancement pass
            "cache_hit_rate_target": 0.4,       # Target cache utilization
            "prediction_accuracy_target": 0.8,  # Target prediction accuracy
            "adaptation_overhead_limit": 0.15   # Max acceptable adaptation overhead
        }
    
    async def analyze_efficiency(
        self,
        result: QualityEnhancedResult,
        predictions: GenerationPredictions,
        actual_time: float
    ) -> EfficiencyMetrics:
        """Analyze generation efficiency comprehensively"""
        
        try:
            # Extract metrics
            quality_score = result.quality_metrics.overall_score
            enhancement_passes = len(result.enhancement_history)
            
            # Estimate token usage (would be tracked in real implementation)
            estimated_tokens = predictions.predicted_token_usage
            
            # Calculate core efficiency metrics
            token_efficiency = quality_score / max(estimated_tokens / 1000, 1.0)  # Quality per 1k tokens
            time_efficiency = quality_score / max(actual_time, 1.0)               # Quality per second
            
            # Calculate overhead metrics
            predicted_time = predictions.predicted_generation_time
            adaptation_overhead = max(0.0, (actual_time - predicted_time) / max(predicted_time, 1.0))
            prediction_overhead = 2.0  # Estimated prediction computation time
            learning_overhead = 1.0    # Estimated learning update time
            
            # Cache metrics (simulated - would be tracked in real implementation)
            cache_hit_rate = 0.3  # Placeholder
            
            # Resource optimization impact (would be calculated from applied optimizations)
            resource_optimization_impact = 0.0
            if hasattr(result, 'optimization_data'):
                resource_optimization_impact = getattr(result.optimization_data, 'savings', 0.0)
            
            efficiency_metrics = EfficiencyMetrics(
                token_efficiency=token_efficiency,
                time_efficiency=time_efficiency,
                adaptation_overhead=min(1.0, adaptation_overhead),
                prediction_overhead=prediction_overhead,
                learning_overhead=learning_overhead,
                cache_hit_rate=cache_hit_rate,
                resource_optimization_impact=resource_optimization_impact
            )
            
            # Store efficiency data for learning
            self._record_efficiency_data(efficiency_metrics, result, predictions, actual_time)
            
            logger.debug(f"Efficiency analysis: token={token_efficiency:.2f}, time={time_efficiency:.2f}")
            
            return efficiency_metrics
            
        except Exception as e:
            logger.warning(f"Efficiency analysis failed: {e}")
            # Return default metrics on failure
            return EfficiencyMetrics(
                token_efficiency=1.0,
                time_efficiency=1.0,
                adaptation_overhead=0.1,
                prediction_overhead=2.0,
                learning_overhead=1.0,
                cache_hit_rate=0.0,
                resource_optimization_impact=0.0
            )
    
    async def identify_optimization_opportunities(
        self,
        efficiency_metrics: EfficiencyMetrics,
        result: QualityEnhancedResult,
        predictions: GenerationPredictions
    ) -> List[OptimizationOpportunity]:
        """Identify specific optimization opportunities"""
        
        opportunities = []
        
        try:
            # Token efficiency opportunity
            if efficiency_metrics.token_efficiency < self.benchmark_metrics["tokens_per_quality_point"] / 1000:
                impact = self._calculate_impact_score(
                    efficiency_metrics.token_efficiency,
                    self.benchmark_metrics["tokens_per_quality_point"] / 1000
                )
                opportunities.append(OptimizationOpportunity(
                    opportunity_type="token_efficiency",
                    description=f"Token efficiency ({efficiency_metrics.token_efficiency:.2f}) below target",
                    potential_impact=impact,
                    implementation_complexity="moderate",
                    recommendation="Implement prompt optimization and component caching"
                ))
            
            # Time efficiency opportunity
            if efficiency_metrics.time_efficiency < 1 / self.benchmark_metrics["seconds_per_quality_point"]:
                impact = self._calculate_impact_score(
                    efficiency_metrics.time_efficiency,
                    1 / self.benchmark_metrics["seconds_per_quality_point"]
                )
                opportunities.append(OptimizationOpportunity(
                    opportunity_type="time_efficiency",
                    description=f"Time efficiency ({efficiency_metrics.time_efficiency:.2f}) below target",
                    potential_impact=impact,
                    implementation_complexity="low",
                    recommendation="Enable parallel processing and optimize workflow ordering"
                ))
            
            # Cache optimization opportunity
            if efficiency_metrics.cache_hit_rate < self.benchmark_metrics["cache_hit_rate_target"]:
                opportunities.append(OptimizationOpportunity(
                    opportunity_type="cache_optimization",
                    description=f"Cache hit rate ({efficiency_metrics.cache_hit_rate:.2f}) below target",
                    potential_impact=6.0,
                    implementation_complexity="low",
                    recommendation="Implement smarter caching strategies for similar requests"
                ))
            
            # Adaptation overhead opportunity
            if efficiency_metrics.adaptation_overhead > self.benchmark_metrics["adaptation_overhead_limit"]:
                opportunities.append(OptimizationOpportunity(
                    opportunity_type="adaptation_overhead",
                    description=f"Adaptation overhead ({efficiency_metrics.adaptation_overhead:.2f}) too high",
                    potential_impact=5.0,
                    implementation_complexity="moderate",
                    recommendation="Optimize adaptation algorithms and reduce unnecessary processing"
                ))
            
            # Enhancement efficiency opportunity
            if len(result.enhancement_history) > 0:
                avg_improvement_per_pass = self._calculate_average_improvement_per_pass(result)
                if avg_improvement_per_pass < self.benchmark_metrics["quality_points_per_pass"]:
                    opportunities.append(OptimizationOpportunity(
                        opportunity_type="enhancement_efficiency",
                        description=f"Enhancement passes inefficient ({avg_improvement_per_pass:.2f} points/pass)",
                        potential_impact=7.0,
                        implementation_complexity="high",
                        recommendation="Improve enhancement strategy selection and targeting"
                    ))
            
            # Resource allocation opportunity
            if predictions.resource_efficiency_score < 6.0:
                opportunities.append(OptimizationOpportunity(
                    opportunity_type="resource_allocation",
                    description=f"Resource allocation inefficient (score: {predictions.resource_efficiency_score:.1f})",
                    potential_impact=6.5,
                    implementation_complexity="moderate",
                    recommendation="Implement adaptive resource allocation based on requirements complexity"
                ))
            
            logger.debug(f"Identified {len(opportunities)} optimization opportunities")
            return opportunities
            
        except Exception as e:
            logger.warning(f"Failed to identify optimization opportunities: {e}")
            return []
    
    def _record_efficiency_data(
        self,
        efficiency_metrics: EfficiencyMetrics,
        result: QualityEnhancedResult,
        predictions: GenerationPredictions,
        actual_time: float
    ):
        """Record efficiency data for trend analysis"""
        
        efficiency_record = {
            "timestamp": datetime.now(),
            "quality_score": result.quality_metrics.overall_score,
            "token_efficiency": efficiency_metrics.token_efficiency,
            "time_efficiency": efficiency_metrics.time_efficiency,
            "actual_time": actual_time,
            "predicted_time": predictions.predicted_generation_time,
            "enhancement_passes": len(result.enhancement_history),
            "cache_hit_rate": efficiency_metrics.cache_hit_rate,
            "adaptation_overhead": efficiency_metrics.adaptation_overhead
        }
        
        self.efficiency_history.append(efficiency_record)
        
        # Keep history manageable
        max_history = self.config.learning_history_window
        if len(self.efficiency_history) > max_history:
            self.efficiency_history = self.efficiency_history[-max_history:]
    
    def _calculate_impact_score(self, current_value: float, target_value: float) -> float:
        """Calculate optimization impact score (0-10)"""
        if target_value <= 0:
            return 5.0
        
        improvement_ratio = max(0.0, (target_value - current_value) / target_value)
        impact_score = min(10.0, improvement_ratio * 10.0)
        
        return impact_score
    
    def _calculate_average_improvement_per_pass(self, result: QualityEnhancedResult) -> float:
        """Calculate average quality improvement per enhancement pass"""
        if not result.enhancement_history:
            return 0.0
        
        total_improvement = 0.0
        for pass_data in result.enhancement_history:
            if hasattr(pass_data, 'quality_improvement'):
                total_improvement += pass_data.quality_improvement
            else:
                total_improvement += 0.3  # Default improvement estimate
        
        return total_improvement / len(result.enhancement_history)
    
    async def get_efficiency_trends(self, window_days: int = 7) -> Dict[str, Any]:
        """Get efficiency trends over specified time window"""
        
        if not self.efficiency_history:
            return {"error": "No efficiency history available"}
        
        cutoff_date = datetime.now() - timedelta(days=window_days)
        recent_data = [
            record for record in self.efficiency_history
            if record["timestamp"] > cutoff_date
        ]
        
        if not recent_data:
            return {"error": "No recent efficiency data available"}
        
        # Calculate trends
        trends = {
            "avg_token_efficiency": sum(r["token_efficiency"] for r in recent_data) / len(recent_data),
            "avg_time_efficiency": sum(r["time_efficiency"] for r in recent_data) / len(recent_data),
            "avg_quality_score": sum(r["quality_score"] for r in recent_data) / len(recent_data),
            "avg_cache_hit_rate": sum(r["cache_hit_rate"] for r in recent_data) / len(recent_data),
            "avg_adaptation_overhead": sum(r["adaptation_overhead"] for r in recent_data) / len(recent_data),
            "data_points": len(recent_data),
            "window_days": window_days
        }
        
        # Calculate trend direction
        if len(recent_data) >= 5:
            first_half = recent_data[:len(recent_data)//2]
            second_half = recent_data[len(recent_data)//2:]
            
            first_avg_quality = sum(r["quality_score"] for r in first_half) / len(first_half)
            second_avg_quality = sum(r["quality_score"] for r in second_half) / len(second_half)
            
            trends["quality_trend"] = "improving" if second_avg_quality > first_avg_quality else "declining"
            trends["quality_trend_magnitude"] = abs(second_avg_quality - first_avg_quality)
        
        return trends