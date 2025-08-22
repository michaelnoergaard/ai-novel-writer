"""
Configuration and error handling for AI Short Story Writer - Version 1
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any
from dataclasses import dataclass

try:
    from dotenv import load_dotenv
    # Load .env file if it exists
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
    else:
        # Try to load from current directory
        load_dotenv()
except ImportError:
    # python-dotenv not installed, skip loading
    pass


@dataclass
class AgentConfig:
    """Configuration for PydanticAI agents"""
    model_name: str = "openai:gpt-4o"
    max_tokens: int = 4000
    temperature: float = 0.7
    timeout_seconds: int = 120
    max_retries: int = 3


@dataclass
class SystemConfig:
    """System-wide configuration"""
    agent_config: AgentConfig
    log_level: str = "INFO"
    output_encoding: str = "utf-8"
    
    @classmethod
    def from_env(cls) -> 'SystemConfig':
        """Create configuration from environment variables"""
        return cls(
            agent_config=AgentConfig(
                model_name=os.getenv("AI_WRITER_MODEL", "openai:gpt-4o"),
                temperature=float(os.getenv("AI_WRITER_TEMPERATURE", "0.7")),
                timeout_seconds=int(os.getenv("AI_WRITER_TIMEOUT", "120")),
                max_retries=int(os.getenv("AI_WRITER_MAX_RETRIES", "3"))
            ),
            log_level=os.getenv("AI_WRITER_LOG_LEVEL", "INFO"),
            output_encoding=os.getenv("AI_WRITER_ENCODING", "utf-8")
        )


class StoryGenerationError(Exception):
    """Base exception for story generation errors"""
    pass


class ValidationError(StoryGenerationError):
    """Error in input validation"""
    pass


class AgentError(StoryGenerationError):
    """Error in agent execution"""
    pass


class ConfigurationError(StoryGenerationError):
    """Error in system configuration"""
    pass


class WorkflowError(StoryGenerationError):
    """Error in workflow execution"""
    pass


def setup_logging(level: str = "INFO") -> None:
    """Setup logging for the application"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('ai_story_writer.log', encoding='utf-8')
        ]
    )


def validate_environment() -> Dict[str, Any]:
    """Validate that required environment variables are set"""
    required_vars = ["OPENAI_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        raise ConfigurationError(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )
    
    return {
        "openai_api_key_set": bool(os.getenv("OPENAI_API_KEY")),
        "model_name": os.getenv("AI_WRITER_MODEL", "openai:gpt-4o")
    }


# Global configuration instance
config = SystemConfig.from_env()