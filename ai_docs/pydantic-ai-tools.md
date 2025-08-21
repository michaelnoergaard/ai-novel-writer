# Pydantic AI Function Tools

Function Tools enable models to perform actions and retrieve additional information, helping agents generate more deterministic and reliable responses.

## Tool Registration

Can be registered via:
1. `@agent.tool` decorator
2. `@agent.tool_plain` decorator
3. `tools` keyword argument in Agent constructor

## Key Features

- Support complex return types including JSON-serializable data
- Allow dynamic tool preparation and filtering
- Provide automatic argument validation
- Support concurrent tool execution
- Enable multi-modal content return

## Example Use Cases

1. Retrieving current time
2. Fetching user information
3. Capturing screenshots
4. Performing web searches

## Tool Registration Example

```python
@agent.tool_plain
def get_current_time() -> datetime:
    return datetime.now()
```

## Advanced Capabilities

- Custom tool schemas
- Dynamic tool generation
- Retry mechanisms for tool execution
- Support for third-party tools (LangChain, ACI.dev)

## Unique Characteristics

- Tools can modify their own schema dynamically
- Support agent-wide tool preparation
- Concurrent execution of multiple tool calls
- Rich error handling and retry mechanisms

The documentation emphasizes flexibility and extensibility in creating intelligent, context-aware AI agents through function tools.