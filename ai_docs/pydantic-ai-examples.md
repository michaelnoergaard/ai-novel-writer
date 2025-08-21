# Pydantic AI Examples

Examples demonstrate various use cases for Pydantic AI and can be run by installing `pydantic-ai` from PyPI or cloning the GitHub repository.

## Installation Requirements

- Install extra dependencies with `pip install "pydantic-ai[examples]"`
- Set up authentication for LLMs (e.g., OpenAI, Google Gemini) by setting API key environment variables

## Running Examples

- Use command: `python -m pydantic_ai_examples.<example_module_name>`
- Quick one-liner with uv: `OPENAI_API_KEY='your-api-key' uv run --with "pydantic-ai[examples]" -m pydantic_ai_examples.pydantic_model`

## Example Categories

- Agent User Interaction
- Pydantic Model
- Weather Agent
- Bank Support
- SQL Generation
- Flight Booking
- RAG (Retrieval-Augmented Generation)
- Streaming Examples
- Chat App with FastAPI
- Question Graph
- Slack Lead Qualifier
- Data Analyst

## Copying Examples

Can copy examples to a new directory using: `python -m pydantic_ai_examples --copy-to examples/`

The documentation provides a comprehensive guide for developers to explore and implement various AI-powered applications using Pydantic AI.