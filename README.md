# Global Weather MCP Server

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server that gives AI assistants access to weather data without API keys.

- US weather alerts from the [National Weather Service API](https://api.weather.gov)
- US point forecasts from the National Weather Service
- Global 5-day forecasts from [Open-Meteo](https://open-meteo.com), including India

## Requirements

| Requirement | Version |
| --- | --- |
| Python | 3.14+ |
| uv | Latest |
| Claude Desktop or another MCP client | Latest |

Check your local versions:

```bash
python --version
uv --version
```

## Installation

```bash
git clone https://github.com/YOUR-USERNAME/global-weather-mcp-server.git
cd global-weather-mcp-server
uv sync
```

No API keys are required.

## Connect to Claude Desktop on Windows

For the Microsoft Store/package install of Claude Desktop, open this config file:

```text
%LOCALAPPDATA%\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\claude_desktop_config.json
```

Add only this server entry inside the `mcpServers` object:

```json
{
  "mcpServers": {
    "global-weather": {
      "command": "uv",
      "args": [
        "--directory",
        "C:\\path\\to\\weather-mcp",
        "run",
        "global_weather_mcp_server.py"
      ]
    }
  }
}
```

If the config file already has other MCP servers, keep them and add only the `global-weather` block. Restart Claude Desktop after saving the file. The server should expose these tools:

- `get_alerts`
- `get_forecast`
- `get_forecast_global`

## Tools

### `get_alerts`

Get active weather alerts for a US state.

Example:

```text
What are the active weather alerts in California?
```

### `get_forecast`

Get a detailed National Weather Service forecast for a US location by latitude and longitude.

Example:

```text
What's the weather forecast for latitude 40.71, longitude -74.01?
```

### `get_forecast_global`

Get current conditions and a 5-day forecast for any location worldwide by latitude and longitude.

Examples:

```text
What's the weather forecast for latitude 19.0760, longitude 72.8777?
Get the weather for latitude 28.6139, longitude 77.2090.
```

Useful Indian city coordinates:

| City | Latitude | Longitude |
| --- | --- | --- |
| New Delhi | 28.6139 | 77.2090 |
| Mumbai | 19.0760 | 72.8777 |
| Bangalore | 12.9716 | 77.5946 |
| Chennai | 13.0827 | 80.2707 |
| Kolkata | 22.5726 | 88.3639 |
| Hyderabad | 17.3850 | 78.4867 |
| Pune | 18.5204 | 73.8567 |

## Test Locally

Run the MCP server directly:

```bash
uv run global_weather_mcp_server.py
```

If it starts and waits silently, the server is ready for an MCP client.

## Project Structure

```text
global-weather-mcp-server/
|-- global_weather_mcp_server.py
|-- pyproject.toml
|-- uv.lock
|-- README.md
`-- .gitignore
```
