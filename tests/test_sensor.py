"""Test the sensor platform."""
import pytest
from unittest.mock import AsyncMock, patch

from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.const import (
    ATTR_DEVICE_CLASS,
    ATTR_UNIT_OF_MEASUREMENT,
    CONF_NAME,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component

from custom_integration.const import DOMAIN, DEFAULT_NAME, DEFAULT_SCAN_INTERVAL


@pytest.fixture
def mock_setup_entry():
    """Mock async_setup_entry."""
    with patch("custom_integration.sensor.async_setup_entry", return_value=True) as mock:
        yield mock


async def test_sensor_config_flow(hass: HomeAssistant, mock_setup_entry) -> None:
    """Test sensor config flow."""
    config = {
        DOMAIN: {
            CONF_NAME: "Test Sensor",
            "scan_interval": 30,
        }
    }

    assert await async_setup_component(hass, DOMAIN, config)
    await hass.async_block_till_done()

    mock_setup_entry.assert_called_once()


async def test_sensor_attributes(hass: HomeAssistant) -> None:
    """Test sensor attributes."""
    config = {
        DOMAIN: {
            CONF_NAME: "Test Sensor",
            "scan_interval": 30,
        }
    }

    assert await async_setup_component(hass, DOMAIN, config)
    await hass.async_block_till_done()

    state = hass.states.get("sensor.test_sensor")
    assert state is not None
    assert state.attributes.get(ATTR_UNIT_OF_MEASUREMENT) == "count" 