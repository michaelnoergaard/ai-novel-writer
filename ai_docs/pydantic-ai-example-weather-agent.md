# Pydantic AI Weather Agent Example

An intelligent agent that retrieves weather information across multiple locations, demonstrating tool chaining and interactive interfaces.

## Core Functionality

- **Sequential Tools**: Uses multiple tools to answer weather queries
- **Location Services**: Retrieves coordinates via `get_lat_lng` tool
- **Weather Data**: Fetches weather via `get_weather` tool
- **Multi-location Support**: Queries multiple locations in a single request

## Technical Implementation

### Model and Configuration
- Utilizes OpenAI's GPT-4.1-mini model
- Implements asynchronous tools with `AsyncClient`
- Supports streaming text responses
- Includes error handling and retries

### Tools Available
1. `get_lat_lng`: Geocoding service for location coordinates
2. `get_weather`: Weather data retrieval from tomorrow.io API

## Example Interaction

Users can ask questions like:
- "What is the weather like in London and in Wiltshire?"
- "Compare weather between New York and San Francisco"

## UI Components

### Gradio Interface
- Web-based chat application
- Multi-turn conversation support
- Displays tool calls and results interactively
- Real-time streaming responses

## Requirements

### API Keys (Optional)
- Weather API key from tomorrow.io
- Geocoding API key from geocode.maps.co

## Running the Example

```bash
python -m pydantic_ai_examples.weather_agent
# or
uv run -m pydantic_ai_examples.weather_agent
```

## Key Features Demonstrated

- **Tool Chaining**: Sequential execution of multiple tools
- **Asynchronous Operations**: Non-blocking API calls
- **Interactive UI**: User-friendly web interface
- **Error Handling**: Robust failure management
- **Streaming Responses**: Real-time output display

The example showcases advanced AI agent capabilities with sophisticated tool integration and user experience design.