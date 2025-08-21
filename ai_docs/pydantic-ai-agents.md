# Pydantic AI Agents Documentation

Pydantic AI Agents are a primary interface for interacting with Large Language Models (LLMs). They are designed to be type-safe, reusable, and flexible.

## Key Features

Supports multiple ways of running agents:
1. `run()` - Async function returning complete response
2. `run_sync()` - Synchronous function returning response
3. `run_stream()` - Async context manager for streaming output
4. `iter()` - Allows iterating over agent's graph nodes

## Core Concepts

- Agents are generic and type-checked
- Can include system prompts, instructions, tools, and structured output types
- Support reflection, self-correction, and error handling

## Example Usage

```python
agent = Agent(
    'openai:gpt-4o',
    deps_type=str,
    output_type=bool,
    system_prompt="Use the customer's name while replying"
)
```

## Unique Characteristics

- Designed to work well with static type checkers
- Supports dynamic and static system prompts/instructions
- Provides detailed control over model interactions