# Claude Code Sub-agents Documentation

Sub-agents are specialized AI assistants within Claude Code that can be delegated specific tasks. Key characteristics include:

## Core Features
- Operate in a separate context window
- Have a specific purpose and expertise area
- Can be configured with custom system prompts
- Can be granted specific tool access

## Key Benefits
- **Context preservation** by maintaining a separate conversation context
- Specialized expertise for specific domains
- Reusability across projects
- Flexible permissions for tool access

## Creation Process
1. Use `/agents` command to open subagent interface
2. Choose project-level or user-level subagent
3. Define:
   - Name
   - Description
   - Optional tool restrictions
   - System prompt

## Example Sub-agents
- **Code Reviewer**: "Expert code review specialist. Proactively reviews code for quality, security, and maintainability."
- **Debugger**: "Debugging specialist for errors, test failures, and unexpected behavior."
- **Data Scientist**: "Data analysis expert for SQL queries, BigQuery operations, and data insights."

## Invocation Methods
- Automatic delegation based on task context
- Explicit invocation by mentioning the subagent
- Chaining multiple subagents for complex workflows

## Best Practices
- Create focused, single-responsibility subagents
- Write detailed system prompts
- Limit tool access
- Version control project subagents

## Performance Considerations
- Helps preserve main conversation context
- May add slight latency due to context gathering