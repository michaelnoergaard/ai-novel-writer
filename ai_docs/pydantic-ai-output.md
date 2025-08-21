# Pydantic AI Output Handling

Output refers to the final value returned from running an agent. It supports plain text, structured data, or function call results, wrapped in `AgentRunResult` or `StreamedRunResult` to preserve typing information.

## Output Types

### 1. Structured Data
- Can use Pydantic models, dataclasses, TypedDict
- Supports type unions and multiple output options
- Validates output against specified schema

### 2. Output Functions
- Can call functions with model-provided arguments
- Allows processing, validation, or handoff to other agents
- Supports synchronous and asynchronous functions

## Output Modes

### 1. Tool Output (Default)
- Uses tool calls to produce output
- Supported by most models
- Allows customizing tool names and descriptions

### 2. Native Output
- Uses model's native structured output feature
- Not supported by all models
- Forces model to output matching JSON schema

### 3. Prompted Output
- Instructs model to output matching schema via prompt
- Most flexible but least reliable method
- Useful for models without native structured output

## Streaming Support

- Can stream text or structured data
- Supports partial validation
- Allows fine-grained control over output processing

## Validation

- Uses Pydantic for schema validation
- Supports output validator functions
- Can retry model generation if validation fails

## Example Use Cases

- Extracting structured user profiles
- Generating SQL queries
- Routing between different agent types

The documentation emphasizes flexibility in handling agent outputs across various models and use cases.