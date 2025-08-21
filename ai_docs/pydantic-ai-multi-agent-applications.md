# Pydantic AI Multi-Agent Applications

Multi-agent applications in Pydantic AI support four levels of complexity for building sophisticated AI workflows.

## Four Levels of Complexity

### 1. Single Agent Workflows
Basic single-agent operations for straightforward tasks.

### 2. Agent Delegation
- Allows one agent to delegate work to another agent
- Can use different models
- Typically passes usage context between agents
- Supports complex interaction patterns

### 3. Programmatic Agent Hand-off
- Multiple agents called in succession
- Application code controls agent transitions
- Allows for more flexible workflow design

### 4. Graph-based Control Flow
Advanced workflow modeling with finite state machines and typed nodes.

## Key Code Patterns

### Agent Tools
- Using `@agent.tool` decorators
- Passing `ctx.usage` between agents
- Defining custom dependency types
- Structured output with type annotations

## Implementation Examples

Multi-agent applications can be seen in practice through various examples:
- Flight booking workflows
- Bank support systems
- Weather information agents

These patterns enable developers to build sophisticated AI applications that leverage multiple specialized agents working together to accomplish complex tasks.