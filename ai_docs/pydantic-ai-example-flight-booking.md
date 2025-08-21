# Pydantic AI Flight Booking Example

Multi-agent workflow for finding and booking flights, demonstrating agent delegation and programmatic hand-off using OpenAI's GPT-4o model.

## Agent Roles

### 1. Search Agent
Controls conversation flow and finds cheapest flight options

### 2. Extraction Agent
Extracts flight details from web page text

### 3. Seat Preference Agent
Helps user select seat preferences

## Workflow Diagram

```
graph TD
  START --> search_agent
  search_agent --> extraction_agent
  extraction_agent --> search_agent
  search_agent --> human_confirm
  human_confirm --> search_agent
  human_confirm --> find_seat_function
  find_seat_function --> find_seat_agent
  find_seat_agent --> buy_flights
```

## Key Technical Features

- **Pydantic Models**: Define structured data (FlightDetails, SeatPreference)
- **Usage Limits**: For AI model requests
- **Interactive Prompts**: User confirmation and input
- **Retry Logic**: Validation and error handling
- **Asynchronous Interactions**: Between agents

## Running the Example

```bash
python -m pydantic_ai_examples.flight_booking
# or
uv run -m pydantic_ai_examples.flight_booking
```

The example showcases a sophisticated, modular approach to building AI-powered booking assistants with clear separation of concerns between different agent responsibilities.