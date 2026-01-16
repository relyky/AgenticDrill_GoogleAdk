from google.adk.agents.llm_agent import Agent
from .tools import get_system_time, get_weather

system_prompt = """
You are a helpful assistant. Your native language is Traditional Chinese (zh-TW).
"""

root_agent = Agent(
    model="gemini-3-flash-preview",
    name='root_agent',
    instruction=system_prompt,
    tools=[get_weather, get_system_time],
)
