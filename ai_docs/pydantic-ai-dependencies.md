# Pydantic AI Dependency Injection

Pydantic AI's dependency injection system allows developers to provide data and services to agents through a type-safe, Pythonic approach.

## Dependencies Definition

- Can be any Python type, but dataclasses are recommended
- Defined with a specific type passed to the Agent constructor
- Instantiated and passed when running an agent

## Accessing Dependencies

- Used through `RunContext` in system prompts, tools, and output validators
- Supports both synchronous and asynchronous dependencies
- Accessed via `ctx.deps` attribute

## Key Features

- **Type-safe**: Static type checkers can validate dependency types
- **Flexible**: Can be used in system prompts, tools, and output validators
- **Testable**: Supports dependency overriding for unit testing

## Example Structure

```python
@dataclass
class MyDeps:
    api_key: str
    http_client: httpx.AsyncClient

agent = Agent('openai:gpt-4o', deps_type=MyDeps)

@agent.system_prompt
async def get_system_prompt(ctx: RunContext[MyDeps]) -> str:
    # Access dependencies here
    response = await ctx.deps.http_client.get(...)
```

The system aims to use "existing best practice in Python development rather than inventing esoteric 'magic'".