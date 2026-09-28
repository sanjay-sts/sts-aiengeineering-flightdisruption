import asyncio
import re

from mcp_servers.weather.server import WeatherServer, WeatherModel
from libs.models import get_model
import os
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool
from pydantic import BaseModel


load_dotenv()

model_detail = os.environ.get("MODEL_DEFAULT")
agent_model = get_model(model_detail)
print(agent_model)

class Answer(BaseModel):
    summary: str
    confidence: float

@tool
async def current_weather(city: str, state: str, country: str) -> dict:
    """
    Get the current weather for a given city, state, and country.
    state is the two-letter province or state code, country the two-letter ISO code.
    """
    async with WeatherServer() as ws:
        return (await ws.current_weather(city, state, country)).model_dump()


agent = create_agent(
    model=agent_model,
    tools=[current_weather],
    system_prompt="You are a helpful assistant. Be concise and accurate.",
    response_format=Answer
)

async def main():
    result = await agent.ainvoke({"messages": [{"role": "user", "content": "What is the current weather in Calgary, Alberta, Canada"}]})
    print(result)
    print(result["messages"])
    print(result["structured_response"].summary, result["structured_response"].confidence)

asyncio.run(main())
