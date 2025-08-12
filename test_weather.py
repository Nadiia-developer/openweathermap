import pytest
import asyncio
from unittest.mock import patch, AsyncMock
from main import (
    get_current_weather_text,
    get_forecast_text,
    start_command,
    help_command,
    current_command,
    forecast_command,
)


# Mock requests.get to avoid real API calls during tests
class MockResponse:
    def __init__(self, json_data, status_code=200):
        self._json = json_data
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception("HTTP error")

    def json(self):
        return self._json


@pytest.mark.parametrize(
    "city,expected_substring",
    [
        ("Kyiv", "Current weather in Kyiv,UA"),
        ("Lviv", "Current weather in Lviv,UA"),
    ],
)
@patch("main.requests.get")
def test_get_current_weather_text(mock_get, city, expected_substring):
    mock_get.return_value = MockResponse(
        {
            "main": {"temp": 20, "humidity": 50},
            "wind": {"speed": 5},
        }
    )
    text = get_current_weather_text(city)
    assert expected_substring in text
    assert "Temperature: 20" in text
    assert "Humidity: 50" in text
    assert "Wind speed: 5" in text


@pytest.mark.parametrize(
    "city,expected_substring",
    [
        ("Kyiv", "5-day / 3-hour forecast for Kyiv,UA"),
        ("Lviv", "5-day / 3-hour forecast for Lviv,UA"),
    ],
)
@patch("main.requests.get")
def test_get_forecast_text(mock_get, city, expected_substring):
    mock_get.return_value = MockResponse(
        {
            "list": [
                {
                    "dt_txt": "2025-08-12 12:00:00",
                    "main": {"temp": 22},
                    "weather": [{"description": "clear sky"}],
                }
            ] * 5
        }
    )
    text = get_forecast_text(city)
    assert expected_substring in text
    assert "2025-08-12 12:00:00 — 22 °C — clear sky" in text


@pytest.mark.asyncio
async def test_start_command():
    mock_update = AsyncMock()
    mock_update.message.reply_text = AsyncMock()
    mock_context = AsyncMock()

    await start_command(mock_update, mock_context)
    mock_update.message.reply_text.assert_called_once()
    assert "Welcome" in mock_update.message.reply_text.call_args[0][0]


@pytest.mark.asyncio
async def test_help_command():
    mock_update = AsyncMock()
    mock_update.message.reply_text = AsyncMock()
    mock_context = AsyncMock()

    await help_command(mock_update, mock_context)
    mock_update.message.reply_text.assert_called_once()
    assert "Help" in mock_update.message.reply_text.call_args[0][0]


@pytest.mark.asyncio
@patch("main.get_current_weather_text")
async def test_current_command_with_city(mock_get_current_weather_text):
    mock_get_current_weather_text.return_value = "Weather info"
    mock_update = AsyncMock()
    mock_update.message.reply_text = AsyncMock()
    mock_context = AsyncMock()
    mock_context.args = ["Kyiv"]

    await current_command(mock_update, mock_context)
    mock_update.message.reply_text.assert_called_once_with("Weather info")


@pytest.mark.asyncio
async def test_current_command_no_city():
    mock_update = AsyncMock()
    mock_update.message.reply_text = AsyncMock()
    mock_context = AsyncMock()
    mock_context.args = []

    await current_command(mock_update, mock_context)
    mock_update.message.reply_text.assert_called_once_with("Usage: /current <city>")


@pytest.mark.asyncio
@patch("main.get_forecast_text")
async def test_forecast_command_with_city(mock_get_forecast_text):
    mock_get_forecast_text.return_value = "Forecast info"
    mock_update = AsyncMock()
    mock_update.message.reply_text = AsyncMock()
    mock_context = AsyncMock()
    mock_context.args = ["Lviv"]

    await forecast_command(mock_update, mock_context)
    mock_update.message.reply_text.assert_called_once_with("Forecast info")


@pytest.mark.asyncio
async def test_forecast_command_no_city():
    mock_update = AsyncMock()
    mock_update.message.reply_text = AsyncMock()
    mock_context = AsyncMock()
    mock_context.args = []

    await forecast_command(mock_update, mock_context)
    mock_update.message.reply_text.assert_called_once_with("Usage: /forecast <city>")