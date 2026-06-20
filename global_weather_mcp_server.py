from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("global-weather")

# Constants
NWS_API_BASE = "https://api.weather.gov"
OPEN_METEO_API_BASE = "https://api.open-meteo.com/v1"
USER_AGENT = "global-weather-mcp-server/1.0"


async def make_nws_request(url: str) -> dict[str, Any] | None:
    """Make a request to the NWS API with proper error handling."""
    headers = {"User-Agent": USER_AGENT, "Accept": "application/geo+json"}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None


def format_alert(feature: dict) -> str:
    """Format an alert feature into a readable string."""
    props = feature["properties"]
    return f"""
Event: {props.get("event", "Unknown")}
Area: {props.get("areaDesc", "Unknown")}
Severity: {props.get("severity", "Unknown")}
Description: {props.get("description", "No description available")}
Instructions: {props.get("instruction", "No specific instructions provided")}
"""


@mcp.tool()
async def get_alerts(state: str) -> str:
    """Get weather alerts for a US state.

    Args:
        state: Two-letter US state code (e.g. CA, NY)
    """
    url = f"{NWS_API_BASE}/alerts/active/area/{state}"
    data = await make_nws_request(url)

    if not data or "features" not in data:
        return "Unable to fetch alerts or no alerts found."

    if not data["features"]:
        return "No active alerts for this state."

    alerts = [format_alert(feature) for feature in data["features"]]
    return "\n---\n".join(alerts)


@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """Get weather forecast for a location.

    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location
    """
    # First get the forecast grid endpoint
    points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
    points_data = await make_nws_request(points_url)

    if not points_data:
        return "Unable to fetch forecast data for this location."

    # Get the forecast URL from the points response
    forecast_url = points_data["properties"]["forecast"]
    forecast_data = await make_nws_request(forecast_url)

    if not forecast_data:
        return "Unable to fetch detailed forecast."

    # Format the periods into a readable forecast
    periods = forecast_data["properties"]["periods"]
    forecasts = []
    for period in periods[:5]:  # Only show next 5 periods
        forecast = f"""
{period["name"]}:
Temperature: {period["temperature"]} deg {period["temperatureUnit"]}
Wind: {period["windSpeed"]} {period["windDirection"]}
Forecast: {period["detailedForecast"]}
"""
        forecasts.append(forecast)

    return "\n---\n".join(forecasts)


@mcp.tool()
async def get_forecast_global(latitude: float, longitude: float) -> str:
    """Get weather forecast for any location worldwide including India.

    Uses the Open-Meteo API (free, no API key required).

    Args:
        latitude: Latitude of the location (e.g. 28.6139 for New Delhi)
        longitude: Longitude of the location (e.g. 77.2090 for New Delhi)
    """
    url = (
        f"{OPEN_METEO_API_BASE}/forecast"
        f"?latitude={latitude}&longitude={longitude}"
        f"&current=temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code"
        f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,weather_code"
        f"&timezone=auto&forecast_days=5"
    )

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=30.0)
            response.raise_for_status()
            data = response.json()
        except Exception:
            return "Unable to fetch forecast data. Please check the coordinates."

    current = data.get("current", {})
    daily = data.get("daily", {})
    timezone = data.get("timezone", "Unknown")

    current_section = f"""Current Conditions (Timezone: {timezone}):
Temperature: {current.get("temperature_2m", "N/A")} deg C
Humidity: {current.get("relative_humidity_2m", "N/A")}%
Wind Speed: {current.get("wind_speed_10m", "N/A")} km/h
"""

    days = daily.get("time", [])
    max_temps = daily.get("temperature_2m_max", [])
    min_temps = daily.get("temperature_2m_min", [])
    precipitation = daily.get("precipitation_sum", [])

    daily_lines = []
    for i, day in enumerate(days):
        daily_lines.append(
            f"{day}: Max {max_temps[i]} deg C / Min {min_temps[i]} deg C | Rain: {precipitation[i]} mm"
        )

    daily_section = "5-Day Forecast:\n" + "\n".join(daily_lines)

    return current_section + "\n" + daily_section


def main():
    # Initialize and run the server
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
