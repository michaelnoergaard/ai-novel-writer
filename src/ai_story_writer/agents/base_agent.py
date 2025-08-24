"""
AI Story Writer - Base Agent Interface
Abstract base classes and interfaces for multi-agent coordination.
"""

import asyncio
import logging
import time
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Type, TypeVar, Generic, Union

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Type variables for generic agent patterns
T = TypeVar('T', bound=BaseModel)
R = TypeVar('R', bound=BaseModel)


class AgentType(str, Enum):
    """Types of agents in the system"""
    MASTER = "master"
    STORY_GENERATION = "story_generation" 
    QUALITY_ASSESSMENT = "quality_assessment"
    STORY_ENHANCEMENT = "story_enhancement"
    PLANNING = "planning"
    CHARACTER_DEVELOPMENT = "character_development"
    FORMATTING = "formatting"


class AgentStatus(str, Enum):
    """Agent execution status"""
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"


class MessageType(str, Enum):
    """Types of inter-agent messages"""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    ERROR = "error"


class AgentMessage(BaseModel):
    """Message for inter-agent communication"""
    
    # Message identification
    message_id: str = Field(default_factory=lambda: f"msg_{uuid.uuid4().hex[:8]}")
    message_type: MessageType
    timestamp: datetime = Field(default_factory=datetime.now)
    
    # Source and destination
    sender_agent_id: str
    recipient_agent_id: str
    
    # Message content
    operation: str = Field(description="The operation being requested/responded to")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Message payload data")
    
    # Context and metadata
    correlation_id: Optional[str] = None  # For request/response correlation
    priority: int = Field(default=1, ge=1, le=10, description="Message priority (1=low, 10=high)")
    timeout: Optional[float] = None  # Timeout in seconds
    
    model_config = {"use_enum_values": True}


class AgentResult(BaseModel):
    """Result from an agent operation"""
    
    # Result identification
    result_id: str = Field(default_factory=lambda: f"result_{uuid.uuid4().hex[:8]}")
    agent_id: str
    operation: str
    timestamp: datetime = Field(default_factory=datetime.now)
    
    # Result data
    success: bool
    data: Dict[str, Any] = Field(default_factory=dict)
    error_message: Optional[str] = None
    
    # Performance metrics
    execution_time: float = Field(description="Execution time in seconds")
    tokens_used: Optional[int] = None
    api_calls: Optional[int] = None
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    model_config = {"use_enum_values": True}


class AgentCapability(BaseModel):
    """Describes an agent's capability"""
    
    name: str
    description: str
    input_types: List[str] = Field(default_factory=list)
    output_types: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    estimated_time: Optional[float] = None  # Estimated execution time in seconds


class AgentInfo(BaseModel):
    """Agent information and status"""
    
    agent_id: str
    agent_type: AgentType
    name: str
    description: str
    version: str = "1.6"
    
    # Status information
    status: AgentStatus = AgentStatus.IDLE
    capabilities: List[AgentCapability] = Field(default_factory=list)
    
    # Performance metrics
    total_operations: int = 0
    successful_operations: int = 0
    average_execution_time: float = 0.0
    
    # Runtime information
    created_at: datetime = Field(default_factory=datetime.now)
    last_operation: Optional[datetime] = None
    
    model_config = {"use_enum_values": True}


class BaseAgent(ABC, Generic[T, R]):
    """
    Abstract base class for all agents in the AI Story Writer system.
    
    Provides common functionality for agent lifecycle, communication,
    monitoring, and error handling.
    """
    
    def __init__(self, agent_id: str, name: str, description: str, agent_type: AgentType):
        """Initialize base agent"""
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.info = AgentInfo(
            agent_id=agent_id,
            agent_type=agent_type,
            name=name,
            description=description
        )
        self.message_handlers: Dict[str, Any] = {}
        self.operation_metrics: Dict[str, List[float]] = {}
        
        logger.info(f"Initialized {agent_type} agent: {name} ({agent_id})")
    
    @abstractmethod
    async def execute(self, request: T) -> R:
        """
        Execute the main operation for this agent.
        
        Args:
            request: Typed request object for this agent
            
        Returns:
            Typed response object from this agent
        """
        pass
    
    @abstractmethod  
    def get_capabilities(self) -> List[AgentCapability]:
        """
        Get list of capabilities this agent provides.
        
        Returns:
            List of agent capabilities
        """
        pass
    
    async def handle_message(self, message: AgentMessage) -> AgentResult:
        """
        Handle incoming inter-agent message.
        
        Args:
            message: Message to handle
            
        Returns:
            Result of handling the message
        """
        start_time = time.time()
        
        try:
            self.info.status = AgentStatus.BUSY
            
            # Route message to appropriate handler
            if message.operation in self.message_handlers:
                handler = self.message_handlers[message.operation]
                result_data = await handler(message.payload)
                
                execution_time = time.time() - start_time
                self._update_metrics(message.operation, execution_time, True)
                
                return AgentResult(
                    agent_id=self.agent_id,
                    operation=message.operation,
                    success=True,
                    data=result_data,
                    execution_time=execution_time
                )
            else:
                error_msg = f"Unknown operation: {message.operation}"
                logger.warning(f"Agent {self.agent_id}: {error_msg}")
                
                return AgentResult(
                    agent_id=self.agent_id,
                    operation=message.operation,
                    success=False,
                    error_message=error_msg,
                    execution_time=time.time() - start_time
                )
                
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Error handling message: {e}"
            logger.error(f"Agent {self.agent_id}: {error_msg}")
            
            self._update_metrics(message.operation, execution_time, False)
            self.info.status = AgentStatus.ERROR
            
            return AgentResult(
                agent_id=self.agent_id,
                operation=message.operation,
                success=False,
                error_message=error_msg,
                execution_time=execution_time
            )
        finally:
            self.info.status = AgentStatus.IDLE
            self.info.last_operation = datetime.now()
    
    def register_operation(self, operation: str, handler):
        """
        Register a message handler for an operation.
        
        Args:
            operation: Operation name
            handler: Async function to handle the operation
        """
        self.message_handlers[operation] = handler
        logger.debug(f"Agent {self.agent_id}: Registered handler for '{operation}'")
    
    def get_info(self) -> AgentInfo:
        """Get current agent information and status"""
        self.info.capabilities = self.get_capabilities()
        return self.info
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for this agent"""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type.value,
            "total_operations": self.info.total_operations,
            "successful_operations": self.info.successful_operations,
            "success_rate": self.info.successful_operations / max(self.info.total_operations, 1),
            "average_execution_time": self.info.average_execution_time,
            "operation_metrics": {
                op: {
                    "count": len(times),
                    "average_time": sum(times) / len(times) if times else 0,
                    "min_time": min(times) if times else 0,
                    "max_time": max(times) if times else 0
                }
                for op, times in self.operation_metrics.items()
            }
        }
    
    def _update_metrics(self, operation: str, execution_time: float, success: bool):
        """Update performance metrics"""
        self.info.total_operations += 1
        if success:
            self.info.successful_operations += 1
        
        # Update operation-specific metrics
        if operation not in self.operation_metrics:
            self.operation_metrics[operation] = []
        self.operation_metrics[operation].append(execution_time)
        
        # Update average execution time
        total_time = sum(
            sum(times) for times in self.operation_metrics.values()
        )
        self.info.average_execution_time = total_time / self.info.total_operations
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform agent health check.
        
        Returns:
            Health status information
        """
        return {
            "agent_id": self.agent_id,
            "status": self.info.status.value,
            "healthy": self.info.status != AgentStatus.ERROR,
            "last_operation": self.info.last_operation.isoformat() if self.info.last_operation else None,
            "uptime": (datetime.now() - self.info.created_at).total_seconds(),
            "success_rate": self.info.successful_operations / max(self.info.total_operations, 1)
        }