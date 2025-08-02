"""Light platform for Commax Integration."""
from __future__ import annotations

import logging
import serial
import asyncio
from datetime import datetime
from typing import Any

from homeassistant.components.light import (
    LightEntity,
    ColorMode,
    ATTR_BRIGHTNESS,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.const import CONF_NAME

from .const import (
    DOMAIN,
    CONF_PORT,
    CONF_BAUD_RATE,
    CONF_TIMEOUT,
    STATUS_QUERY_PACKETS,
    LIGHT_ON_PACKETS,
    LIGHT_OFF_PACKETS,
    STATUS_ON_PREFIX,
    STATUS_OFF_PREFIX,
    LIGHT_NAMES,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Commax Lighting platform."""
    config = hass.data[DOMAIN][config_entry.entry_id]
    
    # 5개의 조명 엔티티 생성
    lights = []
    for i in range(5):
        light = CommaxLight(
            hass,
            config,
            i,
            LIGHT_NAMES[i] if i < len(LIGHT_NAMES) else f"조명 {i+1}"
        )
        lights.append(light)
    
    async_add_entities(lights, True)


class CommaxLight(LightEntity):
    """Representation of a Commax Light."""

    def __init__(self, hass: HomeAssistant, config: dict[str, Any], light_index: int, name: str) -> None:
        """Initialize the light."""
        self.hass = hass
        self.config = config
        self.light_index = light_index
        self._attr_name = name
        self._attr_unique_id = f"{DOMAIN}_light_{light_index + 1}"
        self._attr_is_on = False
        self._attr_color_mode = ColorMode.ONOFF
        self._attr_supported_color_modes = {ColorMode.ONOFF}
        
        # 시리얼 통신 관련
        self._serial_port = None
        self._serial_lock = asyncio.Lock()
        
        # 상태 조회 관련
        self._last_status_check = None
        self._status_check_interval = config.get("scan_interval", 1)
        
        _LOGGER.info(f"Commax Light {name} (index: {light_index}) 초기화 완료")

    @property
    def name(self) -> str:
        """Return the name of the light."""
        return self._attr_name

    @property
    def is_on(self) -> bool:
        """Return true if light is on."""
        return self._attr_is_on

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the light on."""
        await self._send_command(LIGHT_ON_PACKETS[self.light_index])
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the light off."""
        await self._send_command(LIGHT_OFF_PACKETS[self.light_index])
        self._attr_is_on = False
        self.async_write_ha_state()

    async def _send_command(self, packet: str) -> None:
        """시리얼 포트로 명령을 전송합니다."""
        async with self._serial_lock:
            try:
                if not self._serial_port:
                    await self._connect_serial()
                
                if self._serial_port:
                    # HEX 문자열을 바이트로 변환
                    data = bytes.fromhex(packet)
                    self._serial_port.write(data)
                    _LOGGER.debug(f"조명 {self.light_index + 1} 명령 전송: {packet}")
                    
                    # 응답 대기
                    await asyncio.sleep(0.075)  # 75ms 대기
                    
            except Exception as e:
                _LOGGER.error(f"조명 {self.light_index + 1} 명령 전송 실패: {e}")
                await self._reconnect_serial()

    async def _connect_serial(self) -> None:
        """시리얼 포트에 연결합니다."""
        try:
            self._serial_port = serial.Serial(
                port=self.config[CONF_PORT],
                baudrate=self.config[CONF_BAUD_RATE],
                timeout=self.config[CONF_TIMEOUT],
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            _LOGGER.info(f"시리얼 포트 {self.config[CONF_PORT]} 연결 성공")
        except Exception as e:
            _LOGGER.error(f"시리얼 포트 연결 실패: {e}")
            self._serial_port = None

    async def _reconnect_serial(self) -> None:
        """시리얼 포트를 재연결합니다."""
        if self._serial_port:
            self._serial_port.close()
            self._serial_port = None
        await self._connect_serial()

    async def async_update(self) -> None:
        """조명 상태를 업데이트합니다."""
        # 상태 조회 간격 체크
        now = datetime.now()
        if (self._last_status_check and 
            (now - self._last_status_check).total_seconds() < self._status_check_interval):
            return
        
        self._last_status_check = now
        
        async with self._serial_lock:
            try:
                if not self._serial_port:
                    await self._connect_serial()
                
                if self._serial_port:
                    # 상태 조회 패킷 전송
                    packet = STATUS_QUERY_PACKETS[self.light_index]
                    data = bytes.fromhex(packet)
                    self._serial_port.write(data)
                    
                    # 응답 읽기
                    await asyncio.sleep(0.075)  # 75ms 대기
                    
                    if self._serial_port.in_waiting > 0:
                        response = self._serial_port.read(self._serial_port.in_waiting)
                        response_hex = response.hex().upper()
                        
                        # 상태 파싱
                        old_state = self._attr_is_on
                        if response_hex.startswith(STATUS_ON_PREFIX):
                            self._attr_is_on = True
                        elif response_hex.startswith(STATUS_OFF_PREFIX):
                            self._attr_is_on = False
                        
                        if old_state != self._attr_is_on:
                            _LOGGER.info(f"조명 {self.light_index + 1} 상태 변경: {old_state} -> {self._attr_is_on}")
                    
            except Exception as e:
                _LOGGER.error(f"조명 {self.light_index + 1} 상태 조회 실패: {e}")
                await self._reconnect_serial() 