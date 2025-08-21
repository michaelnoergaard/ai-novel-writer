# Pydantic AI Graph-Based Control Flow

Graphs are a powerful but complex workflow modeling tool designed for advanced users with heavy use of Python generics and type hints.

## Key Concepts

Provides a way to create finite state machines (FSMs) with typed nodes and edges for sophisticated workflow management.

## Core Components

### 1. GraphRunContext
Holds graph state and dependencies

### 2. Nodes
Dataclasses defining graph logic with:
- Input parameters
- Execution method (`run`)
- Return type determining graph flow

### 3. Graph
Execution structure combining nodes

## Key Features

- **Async execution**: Full asynchronous support
- **State persistence**: Across interruptions
- **Dependency injection**: Built-in support
- **Mermaid diagram generation**: Visual workflow representation
- **Stateful and stateless workflows**: Flexible execution models

## Design Philosophy

"Don't use a nail gun unless you need a nail gun" - graphs are powerful but not universally applicable. They're recommended for complex workflows where traditional control flow becomes unwieldy.

## State Persistence Modes

- **SimpleStatePersistence**: Latest snapshot
- **FullStatePersistence**: Snapshot history
- **FileStatePersistence**: JSON file storage

## Unique Characteristics

- Heavily leverages Python type hints
- Supports "human in the loop" workflows
- Enables distributed and interruptible execution

## Recommended Use Cases

- Complex multi-step processes
- Workflows requiring external input
- Scenarios needing detailed state tracking