import httpx
from google.adk.agents.llm_agent import Agent
from datetime import datetime
from typing import Any

def get_system_time() -> dict:
    """Returns the current system time with timezone information."""
    now = datetime.now().astimezone()
    return {
        "status": "success", 
        "system_time": now.strftime('%Y-%m-%d %H:%M:%S %Z'),
        "iso_format": now.isoformat()
    }

async def get_weather(latitude: float, longitude: float) -> dict[str, Any]:
    """Get current temperature for a location using coordinates

    Args:
        latitude: Latitude coordinate (e.g., 25.0330 for Taipei)
        longitude: Longitude coordinate (e.g., 121.5654 for Taipei)

    Returns:
        A dictionary containing temperature data or error message
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m",
        "temperature_unit": "fahrenheit"
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            if response.status_code != 200:
                return {"error": f"HTTP {response.status_code}"}

            data = response.json()
            temperature = data.get('current', {}).get('temperature_2m')

            if temperature is None:
                return {"error": "Temperature data not available"}

            return {
                "latitude": latitude,
                "longitude": longitude,
                "temperature": temperature,
                "unit": "fahrenheit"
            }

    except httpx.RequestError as e:
        return {"error": f"Network request failed: {e}"}
    except Exception as e:
        return {"error": str(e)}

system_prompt = """
You are a helpful assistant. Your native language is Traditional Chinese (zh-TW).
"""

llm_model = "gemini-3-flash-preview"
# llm_model = "gemini-2.0-flash-exp"

root_agent = Agent(
    model=llm_model,
    name='root_agent',
    instruction=system_prompt,
    tools=[get_weather, get_system_time],
)