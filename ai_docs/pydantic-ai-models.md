# Pydantic AI Model Providers

Pydantic AI supports multiple model providers with a flexible, model-agnostic architecture.

## Supported Model Providers

- OpenAI
- Anthropic
- Google (Gemini)
- Groq
- Mistral
- Cohere
- Bedrock
- Hugging Face

## OpenAI-Compatible Providers

Available via OpenAI API:
- DeepSeek
- Grok (xAI)
- Ollama
- OpenRouter
- Vercel AI Gateway
- Perplexity
- Fireworks AI
- Together AI
- Azure AI Foundry
- Heroku
- GitHub Models

## Key Concepts

1. **Model**: Pydantic AI class for making requests to specific LLM APIs
2. **Provider**: Handles authentication and connections to LLM vendors
3. **Profile**: Describes how to construct requests for optimal results

## Special Features

- **Fallback Model**: Automatically switches between models if one fails
- **Custom Model Support**: Can implement new model APIs by subclassing base Model
- **Per-Model Settings**: Configure individual model parameters

Developers can easily switch between models without changing agent code, providing significant flexibility in AI application development.