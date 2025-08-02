"""Sensor platform for My Custom Integration."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from .const import DOMAIN, CONF_NAME, CONF_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    config = hass.data[DOMAIN][config_entry.entry_id]
    
    async_add_entities([MyCustomSensor(config)], True)


class MyCustomSensor(SensorEntity):
    """Representation of a My Custom Sensor."""

    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize the sensor."""
        self._config = config
        self._attr_name = config[CONF_NAME]
        self._attr_unique_id = f"{DOMAIN}_{config[CONF_NAME]}"
        self._attr_native_value = None
        self._attr_native_unit_of_measurement = "count"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self._attr_name

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        return self._attr_native_value

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return the unit of measurement."""
        return self._attr_native_unit_of_measurement

    async def async_update(self) -> None:
        """Fetch new state data for the sensor."""
        # 여기에 실제 센서 데이터를 가져오는 로직을 구현하세요
        # 예시: 현재 시간을 초 단위로 반환
        self._attr_native_value = int(datetime.now().timestamp())
        _LOGGER.debug("Updated sensor value: %s", self._attr_native_value) 