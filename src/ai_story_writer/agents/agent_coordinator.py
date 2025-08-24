"""
AI Story Writer - Agent Coordinator
Manages agent lifecycle, registration, communication, and coordination.
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Type, TypeVar

from .base_agent import (
    BaseAgent, AgentMessage, AgentResult, AgentInfo, AgentType, 
    AgentStatus, MessageType, AgentCapability
)

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseAgent)


class AgentRegistry:
    """Registry for managing registered agents"""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.agents_by_type: Dict[AgentType, List[BaseAgent]] = {}
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.coordination_lock = asyncio.Lock()
    
    def register_agent(self, agent: BaseAgent) -> bool:
        """
        Register a new agent.
        
        Args:
            agent: Agent to register
            
        Returns:
            True if registration successful, False if agent ID already exists
        """
        if agent.agent_id in self.agents:
            logger.warning(f"Agent {agent.agent_id} already registered")
            return False
        
        self.agents[agent.agent_id] = agent
        
        # Add to type-based lookup
        if agent.agent_type not in self.agents_by_type:
            self.agents_by_type[agent.agent_type] = []
        self.agents_by_type[agent.agent_type].append(agent)
        
        logger.info(f"Registered agent: {agent.agent_id} ({agent.agent_type.value})")
        return True
    
    def unregister_agent(self, agent_id: str) -> bool:
        """
        Unregister an agent.
        
        Args:
            agent_id: ID of agent to unregister
            
        Returns:
            True if unregistration successful, False if agent not found
        """
        if agent_id not in self.agents:
            return False
        
        agent = self.agents[agent_id]
        
        # Remove from main registry
        del self.agents[agent_id]
        
        # Remove from type-based lookup
        if agent.agent_type in self.agents_by_type:
            self.agents_by_type[agent.agent_type] = [
                a for a in self.agents_by_type[agent.agent_type] 
                if a.agent_id != agent_id
            ]
            if not self.agents_by_type[agent.agent_type]:
                del self.agents_by_type[agent.agent_type]
        
        logger.info(f"Unregistered agent: {agent_id}")
        return True
    
    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """Get agent by ID"""
        return self.agents.get(agent_id)
    
    def get_agents_by_type(self, agent_type: AgentType) -> List[BaseAgent]:
        """Get all agents of a specific type"""
        return self.agents_by_type.get(agent_type, [])
    
    def get_all_agents(self) -> List[BaseAgent]:
        """Get all registered agents"""
        return list(self.agents.values())
    
    def get_active_agents(self) -> List[BaseAgent]:
        """Get all active (non-error) agents"""
        return [
            agent for agent in self.agents.values()
            if agent.info.status != AgentStatus.ERROR
        ]


class CoordinationStrategy:
    """Strategy for coordinating multiple agents"""
    
    @staticmethod
    async def execute_sequential(agents: List[BaseAgent], messages: List[AgentMessage]) -> List[AgentResult]:
        """Execute messages sequentially across agents"""
        results = []
        for agent, message in zip(agents, messages):
            result = await agent.handle_message(message)
            results.append(result)
        return results
    
    @staticmethod
    async def execute_parallel(agents: List[BaseAgent], messages: List[AgentMessage]) -> List[AgentResult]:
        """Execute messages in parallel across agents"""
        tasks = [
            agent.handle_message(message) 
            for agent, message in zip(agents, messages)
        ]
        return await asyncio.gather(*tasks)
    
    @staticmethod
    async def execute_pipeline(agents: List[BaseAgent], initial_message: AgentMessage) -> List[AgentResult]:
        """Execute messages in a pipeline where output of one agent feeds to the next"""
        results = []
        current_message = initial_message
        
        for agent in agents:
            result = await agent.handle_message(current_message)
            results.append(result)
            
            if not result.success:
                logger.error(f"Pipeline failed at agent {agent.agent_id}: {result.error_message}")
                break
            
            # Prepare next message with current result as input
            if agent != agents[-1]:  # Not the last agent
                current_message = AgentMessage(
                    message_type=MessageType.REQUEST,
                    sender_agent_id="coordinator",
                    recipient_agent_id=agents[agents.index(agent) + 1].agent_id,
                    operation=current_message.operation,
                    payload=result.data,
                    correlation_id=current_message.correlation_id
                )
        
        return results


class AgentCoordinator:
    """
    Coordinates multiple agents for complex workflows.
    
    Manages agent lifecycle, message routing, workflow orchestration,
    and performance monitoring across the agent ecosystem.
    """
    
    def __init__(self):
        """Initialize agent coordinator"""
        self.registry = AgentRegistry()
        self.coordination_strategies = CoordinationStrategy()
        self.workflow_history: List[Dict[str, Any]] = []
        self.message_handlers = {
            "health_check": self._handle_health_check,
            "get_capabilities": self._handle_get_capabilities,
            "get_metrics": self._handle_get_metrics
        }
        
        logger.info("AgentCoordinator initialized")
    
    async def register_agent(self, agent: BaseAgent) -> bool:
        """
        Register an agent with the coordinator.
        
        Args:
            agent: Agent to register
            
        Returns:
            True if registration successful
        """
        async with self.registry.coordination_lock:
            success = self.registry.register_agent(agent)
            
            if success:
                # Perform initial health check
                health = await agent.health_check()
                logger.info(f"Agent {agent.agent_id} health check: {health['healthy']}")
            
            return success
    
    async def unregister_agent(self, agent_id: str) -> bool:
        """
        Unregister an agent from the coordinator.
        
        Args:
            agent_id: ID of agent to unregister
            
        Returns:
            True if unregistration successful
        """
        async with self.registry.coordination_lock:
            return self.registry.unregister_agent(agent_id)
    
    async def send_message(self, message: AgentMessage) -> AgentResult:
        """
        Send a message to a specific agent.
        
        Args:
            message: Message to send
            
        Returns:
            Result from the target agent
        """
        agent = self.registry.get_agent(message.recipient_agent_id)
        if not agent:
            return AgentResult(
                agent_id="coordinator",
                operation=message.operation,
                success=False,
                error_message=f"Agent {message.recipient_agent_id} not found",
                execution_time=0.0
            )
        
        return await agent.handle_message(message)
    
    async def coordinate_workflow(
        self,
        agent_ids: List[str],
        operation: str,
        payload: Dict[str, Any],
        strategy: str = "sequential",
        correlation_id: Optional[str] = None
    ) -> List[AgentResult]:
        """
        Coordinate a workflow across multiple agents.
        
        Args:
            agent_ids: List of agent IDs to coordinate
            operation: Operation to perform
            payload: Data payload for the operation
            strategy: Coordination strategy ("sequential", "parallel", "pipeline")
            correlation_id: Optional correlation ID for tracking
            
        Returns:
            List of results from all agents
        """
        start_time = time.time()
        correlation_id = correlation_id or f"workflow_{int(time.time())}"
        
        # Get agents
        agents = []
        for agent_id in agent_ids:
            agent = self.registry.get_agent(agent_id)
            if not agent:
                logger.error(f"Agent {agent_id} not found for workflow")
                return []
            agents.append(agent)
        
        # Create messages
        messages = [
            AgentMessage(
                message_type=MessageType.REQUEST,
                sender_agent_id="coordinator",
                recipient_agent_id=agent.agent_id,
                operation=operation,
                payload=payload,
                correlation_id=correlation_id
            )
            for agent in agents
        ]
        
        # Execute workflow based on strategy
        try:
            if strategy == "sequential":
                results = await self.coordination_strategies.execute_sequential(agents, messages)
            elif strategy == "parallel":
                results = await self.coordination_strategies.execute_parallel(agents, messages)
            elif strategy == "pipeline":
                results = await self.coordination_strategies.execute_pipeline(agents, messages[0:1])
            else:
                raise ValueError(f"Unknown coordination strategy: {strategy}")
            
            # Record workflow execution
            workflow_record = {
                "correlation_id": correlation_id,
                "strategy": strategy,
                "agent_ids": agent_ids,
                "operation": operation,
                "execution_time": time.time() - start_time,
                "success": all(r.success for r in results),
                "timestamp": datetime.now().isoformat()
            }
            self.workflow_history.append(workflow_record)
            
            logger.info(f"Workflow {correlation_id} completed: {workflow_record['success']}")
            return results
            
        except Exception as e:
            logger.error(f"Workflow {correlation_id} failed: {e}")
            return []
    
    async def get_agent_info(self, agent_id: Optional[str] = None) -> List[AgentInfo]:
        """
        Get information about registered agents.
        
        Args:
            agent_id: Specific agent ID, or None for all agents
            
        Returns:
            List of agent information
        """
        if agent_id:
            agent = self.registry.get_agent(agent_id)
            return [agent.get_info()] if agent else []
        
        return [agent.get_info() for agent in self.registry.get_all_agents()]
    
    async def get_system_capabilities(self) -> Dict[AgentType, List[AgentCapability]]:
        """
        Get all capabilities available in the system.
        
        Returns:
            Dictionary mapping agent types to their capabilities
        """
        capabilities = {}
        
        for agent_type, agents in self.registry.agents_by_type.items():
            type_capabilities = []
            for agent in agents:
                type_capabilities.extend(agent.get_capabilities())
            capabilities[agent_type] = type_capabilities
        
        return capabilities
    
    async def health_check_all(self) -> Dict[str, Any]:
        """
        Perform health check on all registered agents.
        
        Returns:
            System-wide health status
        """
        health_results = {}
        for agent in self.registry.get_all_agents():
            health_results[agent.agent_id] = await agent.health_check()
        
        healthy_agents = sum(1 for h in health_results.values() if h['healthy'])
        total_agents = len(health_results)
        
        return {
            "system_healthy": healthy_agents == total_agents,
            "healthy_agents": healthy_agents,
            "total_agents": total_agents,
            "agent_health": health_results,
            "coordinator_uptime": time.time(),
            "active_workflows": len(self.workflow_history)
        }
    
    async def get_system_metrics(self) -> Dict[str, Any]:
        """
        Get comprehensive system metrics.
        
        Returns:
            System-wide performance metrics
        """
        agent_metrics = {}
        for agent in self.registry.get_all_agents():
            agent_metrics[agent.agent_id] = agent.get_metrics()
        
        # Aggregate metrics
        total_operations = sum(m['total_operations'] for m in agent_metrics.values())
        total_successful = sum(m['successful_operations'] for m in agent_metrics.values())
        
        return {
            "total_agents": len(self.registry.agents),
            "agents_by_type": {
                agent_type.value: len(agents)
                for agent_type, agents in self.registry.agents_by_type.items()
            },
            "total_operations": total_operations,
            "successful_operations": total_successful,
            "system_success_rate": total_successful / max(total_operations, 1),
            "total_workflows": len(self.workflow_history),
            "agent_metrics": agent_metrics
        }
    
    # Message handlers for coordinator operations
    async def _handle_health_check(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle health check request"""
        return await self.health_check_all()
    
    async def _handle_get_capabilities(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle capabilities request"""
        capabilities = await self.get_system_capabilities()
        return {
            "capabilities": {
                agent_type.value: [cap.dict() for cap in caps]
                for agent_type, caps in capabilities.items()
            }
        }
    
    async def _handle_get_metrics(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle metrics request"""
        return await self.get_system_metrics()