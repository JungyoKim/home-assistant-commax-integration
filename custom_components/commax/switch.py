"""Switch platform for Commax Integration."""
from __future__ import annotations

import logging
import serial
import asyncio
from datetime import datetime
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.const import CONF_NAME

from .const import (
    DOMAIN,
    CONF_PORT,
    CONF_BAUD_RATE,
    CONF_TIMEOUT,
    # 도어 관련
    DOOR_OPEN_PACKET,
    DOOR_NAMES,
    # 엘리베이터 관련
    ELEVATOR_CALL_PACKET,
    ELEVATOR_NAMES,
    # 일괄소등 관련
    MASTER_STATUS_QUERY,
    MASTER_ALL_ON_PACKET,
    MASTER_ALL_OFF_PACKET,
    MASTER_NAMES,
    # 공통
    STATUS_ON_PREFIX,
    STATUS_OFF_PREFIX,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Commax Switch platform."""
    config = hass.data[DOMAIN][config_entry.entry_id]
    
    switches = []
    
    # 도어 스위치
    for i, name in enumerate(DOOR_NAMES):
        door = CommaxDoor(
            hass,
            config,
            i,
            name
        )
        switches.append(door)
    
    # 엘리베이터 스위치
    for i, name in enumerate(ELEVATOR_NAMES):
        elevator = CommaxElevator(
            hass,
            config,
            i,
            name
        )
        switches.append(elevator)
    
    # 일괄소등 스위치
    for i, name in enumerate(MASTER_NAMES):
        master = CommaxMasterSwitch(
            hass,
            config,
            i,
            name
        )
        switches.append(master)
    
    async_add_entities(switches, True)


class CommaxDoor(SwitchEntity):
    """Representation of a Commax Door."""

    def __init__(self, hass: HomeAssistant, config: dict[str, Any], index: int, name: str) -> None:
        """Initialize the door."""
        self.hass = hass
        self.config = config
        self.index = index
        self._attr_name = name
        self._attr_unique_id = f"{DOMAIN}_door"
        self._attr_is_on = False
        
        # 시리얼 통신 관련
        self._serial_port = None
        self._serial_lock = asyncio.Lock()
        
        # 상태 조회 관련
        self._last_status_check = None
        self._status_check_interval = config.get("scan_interval", 1)
        
        _LOGGER.info(f"Commax Door {name} (index: {index}) 초기화 완료")

    @property
    def name(self) -> str:
        """Return the name of the door."""
        return self._attr_name

    @property
    def is_on(self) -> bool:
        """Return true if door is open."""
        return self._attr_is_on

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Open the door."""
        await self._send_command(DOOR_OPEN_PACKET)
        self._attr_is_on = True
        self.async_write_ha_state()
        
        # 3초 후 자동으로 끄기 (문열기 완료)
        await asyncio.sleep(3)
        self._attr_is_on = False
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Door cannot be closed remotely."""
        # 도어는 원격으로 닫을 수 없으므로 아무 동작 안함
        pass

    async def _send_command(self, packet: str) -> None:
        """시리얼 포트로 명령을 전송합니다."""
        async with self._serial_lock:
            try:
                if not self._serial_port:
                    await self._connect_serial()
                
                if self._serial_port:
                    data = bytes.fromhex(packet)
                    self._serial_port.write(data)
                    _LOGGER.debug(f"도어 {self.index + 1} 명령 전송: {packet}")
                    await asyncio.sleep(0.075)
                    
            except Exception as e:
                _LOGGER.error(f"도어 {self.index + 1} 명령 전송 실패: {e}")
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
        """도어 상태를 업데이트합니다."""
        # 도어는 상태 조회가 아닌 문열기 명령만 있으므로
        # 주기적인 상태 업데이트는 하지 않습니다.
        pass


class CommaxElevator(SwitchEntity):
    """Representation of a Commax Elevator."""

    def __init__(self, hass: HomeAssistant, config: dict[str, Any], index: int, name: str) -> None:
        """Initialize the elevator."""
        self.hass = hass
        self.config = config
        self.index = index
        self._attr_name = name
        self._attr_unique_id = f"{DOMAIN}_elevator"
        self._attr_is_on = False
        
        # 시리얼 통신 관련
        self._serial_port = None
        self._serial_lock = asyncio.Lock()
        
        # 상태 조회 관련
        self._last_status_check = None
        self._status_check_interval = config.get("scan_interval", 1)
        
        _LOGGER.info(f"Commax Elevator {name} (index: {index}) 초기화 완료")

    @property
    def name(self) -> str:
        """Return the name of the elevator."""
        return self._attr_name

    @property
    def is_on(self) -> bool:
        """Return true if elevator is called."""
        return self._attr_is_on

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Call the elevator."""
        await self._send_command(ELEVATOR_CALL_PACKET)
        self._attr_is_on = True
        self.async_write_ha_state()
        
        # 2초 후 자동으로 끄기 (호출 완료)
        await asyncio.sleep(2)
        self._attr_is_on = False
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Cancel elevator call."""
        # 엘리베이터 호출 취소는 별도 패킷이 필요할 수 있음
        self._attr_is_on = False
        self.async_write_ha_state()

    async def _send_command(self, packet: str) -> None:
        """시리얼 포트로 명령을 전송합니다."""
        async with self._serial_lock:
            try:
                if not self._serial_port:
                    await self._connect_serial()
                
                if self._serial_port:
                    data = bytes.fromhex(packet)
                    self._serial_port.write(data)
                    _LOGGER.debug(f"엘리베이터 {self.index + 1} 명령 전송: {packet}")
                    await asyncio.sleep(0.075)
                    
            except Exception as e:
                _LOGGER.error(f"엘리베이터 {self.index + 1} 명령 전송 실패: {e}")
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
        """엘리베이터 상태를 업데이트합니다."""
        # 엘리베이터는 상태 조회가 아닌 호출 명령만 있으므로
        # 주기적인 상태 업데이트는 하지 않습니다.
        pass


class CommaxMasterSwitch(SwitchEntity):
    """Representation of a Commax Master Switch."""

    def __init__(self, hass: HomeAssistant, config: dict[str, Any], index: int, name: str) -> None:
        """Initialize the master switch."""
        self.hass = hass
        self.config = config
        self.index = index
        self._attr_name = name
        self._attr_unique_id = f"{DOMAIN}_master"
        self._attr_is_on = False
        
        # 시리얼 통신 관련
        self._serial_port = None
        self._serial_lock = asyncio.Lock()
        
        # 상태 조회 관련
        self._last_status_check = None
        self._status_check_interval = config.get("scan_interval", 1)
        
        _LOGGER.info(f"Commax Master Switch {name} (index: {index}) 초기화 완료")

    @property
    def name(self) -> str:
        """Return the name of the master switch."""
        return self._attr_name

    @property
    def is_on(self) -> bool:
        """Return true if all lights are on."""
        return self._attr_is_on

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on all lights."""
        await self._send_command(MASTER_ALL_ON_PACKET)
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off all lights."""
        await self._send_command(MASTER_ALL_OFF_PACKET)
        self._attr_is_on = False
        self.async_write_ha_state()

    async def _send_command(self, packet: str) -> None:
        """시리얼 포트로 명령을 전송합니다."""
        async with self._serial_lock:
            try:
                if not self._serial_port:
                    await self._connect_serial()
                
                if self._serial_port:
                    data = bytes.fromhex(packet)
                    self._serial_port.write(data)
                    _LOGGER.debug(f"일괄소등 {self.index + 1} 명령 전송: {packet}")
                    await asyncio.sleep(0.075)
                    
            except Exception as e:
                _LOGGER.error(f"일괄소등 {self.index + 1} 명령 전송 실패: {e}")
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
        """일괄소등 상태를 업데이트합니다."""
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
                    data = bytes.fromhex(MASTER_STATUS_QUERY)
                    self._serial_port.write(data)
                    await asyncio.sleep(0.1)  # 100ms 대기
                    
                    if self._serial_port.in_waiting > 0:
                        response = self._serial_port.read(self._serial_port.in_waiting)
                        if len(response) >= 8:
                            status = self._parse_master_status(response)
                            if status is not None:
                                old_state = self._attr_is_on
                                self._attr_is_on = status
                                
                                if old_state != self._attr_is_on:
                                    _LOGGER.info(f"일괄소등 {self.index + 1} 상태 변경: {old_state} -> {self._attr_is_on}")
                    
            except Exception as e:
                _LOGGER.error(f"일괄소등 {self.index + 1} 상태 조회 실패: {e}")
                await self._reconnect_serial()

    def _parse_master_status(self, data: bytes) -> bool | None:
        """일괄소등 상태 응답 패킷을 파싱합니다."""
        if len(data) < 8:
            return None
        
        # Go 코드의 parseAlloffStatusPacket 로직과 동일
        if data[0] != 0xA0:
            return None
        
        if data[1] == 0x01 and data[2] == 0x01:
            return True  # ON
        elif data[1] == 0x00 and data[2] == 0x01:
            return False  # OFF
        
        return None 