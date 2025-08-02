"""Test the light platform."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ColorMode,
)
from homeassistant.const import (
    CONF_NAME,
    CONF_PORT,
    CONF_BAUD_RATE,
    CONF_TIMEOUT,
    CONF_SCAN_INTERVAL,
)
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component

from custom_integration.const import (
    DOMAIN, 
    DEFAULT_NAME, 
    DEFAULT_BAUD_RATE, 
    DEFAULT_TIMEOUT,
    DEFAULT_SCAN_INTERVAL,
    STATUS_QUERY_PACKETS,
    ON_PACKETS,
    OFF_PACKETS,
    STATUS_ON_PREFIX,
    STATUS_OFF_PREFIX,
)


@pytest.fixture
def mock_serial():
    """Mock serial port."""
    with patch('custom_integration.light.serial') as mock_serial:
        mock_port = MagicMock()
        mock_serial.Serial.return_value = mock_port
        yield mock_serial


async def test_light_config_flow(hass: HomeAssistant, mock_serial) -> None:
    """Test light config flow."""
    config = {
        DOMAIN: {
            CONF_NAME: "Commax Lighting",
            CONF_PORT: "/dev/ttyUSB0",
            CONF_BAUD_RATE: DEFAULT_BAUD_RATE,
            CONF_TIMEOUT: DEFAULT_TIMEOUT,
            CONF_SCAN_INTERVAL: DEFAULT_SCAN_INTERVAL,
        }
    }

    assert await async_setup_component(hass, DOMAIN, config)
    await hass.async_block_till_done()


async def test_light_attributes(hass: HomeAssistant, mock_serial) -> None:
    """Test light attributes."""
    config = {
        DOMAIN: {
            CONF_NAME: "Commax Lighting",
            CONF_PORT: "/dev/ttyUSB0",
            CONF_BAUD_RATE: DEFAULT_BAUD_RATE,
            CONF_TIMEOUT: DEFAULT_TIMEOUT,
            CONF_SCAN_INTERVAL: DEFAULT_SCAN_INTERVAL,
        }
    }

    assert await async_setup_component(hass, DOMAIN, config)
    await hass.async_block_till_done()

    # 조명 엔티티들이 생성되었는지 확인
    light_entities = hass.states.async_all("light")
    assert len(light_entities) == 5  # 5개의 조명


async def test_light_turn_on(hass: HomeAssistant, mock_serial) -> None:
    """Test turning on a light."""
    config = {
        DOMAIN: {
            CONF_NAME: "Commax Lighting",
            CONF_PORT: "/dev/ttyUSB0",
            CONF_BAUD_RATE: DEFAULT_BAUD_RATE,
            CONF_TIMEOUT: DEFAULT_TIMEOUT,
            CONF_SCAN_INTERVAL: DEFAULT_SCAN_INTERVAL,
        }
    }

    assert await async_setup_component(hass, DOMAIN, config)
    await hass.async_block_till_done()

    # 첫 번째 조명 켜기
    await hass.services.async_call(
        "light", "turn_on", {"entity_id": "light.commax_lighting_0"}
    )
    await hass.async_block_till_done()

    # 시리얼 포트에 ON 패킷이 전송되었는지 확인
    mock_port = mock_serial.Serial.return_value
    mock_port.write.assert_called_with(bytes.fromhex(ON_PACKETS[0]))


async def test_light_turn_off(hass: HomeAssistant, mock_serial) -> None:
    """Test turning off a light."""
    config = {
        DOMAIN: {
            CONF_NAME: "Commax Lighting",
            CONF_PORT: "/dev/ttyUSB0",
            CONF_BAUD_RATE: DEFAULT_BAUD_RATE,
            CONF_TIMEOUT: DEFAULT_TIMEOUT,
            CONF_SCAN_INTERVAL: DEFAULT_SCAN_INTERVAL,
        }
    }

    assert await async_setup_component(hass, DOMAIN, config)
    await hass.async_block_till_done()

    # 첫 번째 조명 끄기
    await hass.services.async_call(
        "light", "turn_off", {"entity_id": "light.commax_lighting_0"}
    )
    await hass.async_block_till_done()

    # 시리얼 포트에 OFF 패킷이 전송되었는지 확인
    mock_port = mock_serial.Serial.return_value
    mock_port.write.assert_called_with(bytes.fromhex(OFF_PACKETS[0])) 