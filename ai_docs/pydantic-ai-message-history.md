# Pydantic AI Message History

Pydantic AI provides flexible, programmatic control over conversation management across different AI models and use cases.

## Key Features

### 1. Accessing Messages
- Messages can be retrieved from `result` objects using methods like `all_messages()` and `new_messages()`
- Works with both synchronous and streamed agent runs
- Supports accessing messages from different model runs

### 2. Conversation Continuity
- Messages can be passed between agent runs via the `message_history` parameter
- Allows maintaining context across multiple interactions
- Supports using messages from different models

### 3. Message Processing Capabilities
- Supports "history processors" to modify message history before model requests
- Processors can:
  - Filter messages
  - Limit message count
  - Summarize old messages
  - Apply context-aware modifications

### 4. Serialization
- Messages can be converted to JSON using `ModelMessagesTypeAdapter`
- Supports storing and loading message histories
- Enables sharing conversation state between different systems

## Example Use Cases

- Maintaining conversational context
- Managing token usage
- Implementing privacy filters
- Creating multi-step agent workflows

The system provides flexible, programmatic control over conversation management across different AI models and use cases.