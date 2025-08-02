"""Binary Sensor platform for Commax Doorbell Integration."""
from __future__ import annotations

import logging
import serial
import asyncio
from datetime import datetime
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.const import CONF_NAME

from .const import (
    DOMAIN,
    CONF_PORT,
    CONF_BAUD_RATE,
    CONF_TIMEOUT,
    DOORBELL_BELL_RING_PACKET,
    DOORBELL_CALL_END_PACKET,
    DOORBELL_OPEN_DOOR_PACKET,
    DOORBELL_NAMES,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Commax Doorbell platform."""
    config = hass.data[DOMAIN][config_entry.entry_id]
    
    # 도어벨 센서 생성
    doorbells = []
    for i, name in enumerate(DOORBELL_NAMES):
        doorbell = CommaxDoorbell(
            hass,
            config,
            i,
            name
        )
        doorbells.append(doorbell)
    
    async_add_entities(doorbells, True)


class CommaxDoorbell(BinarySensorEntity):
    """Representation of a Commax Doorbell."""

    def __init__(self, hass: HomeAssistant, config: dict[str, Any], index: int, name: str) -> None:
        """Initialize the doorbell."""
        self.hass = hass
        self.config = config
        self.index = index
        self._attr_name = name
        self._attr_unique_id = f"{DOMAIN}_doorbell"
        self._attr_is_on = False
        self._attr_device_class = BinarySensorDeviceClass.OCCUPANCY
        
        # 시리얼 통신 관련
        self._serial_port = None
        self._serial_lock = asyncio.Lock()
        
        # 상태 조회 관련
        self._last_status_check = None
        self._status_check_interval = config.get("scan_interval", 1)
        
        # 도어벨 상태
        self._state = "OFF"  # "ON"(벨 울림) or "OFF"(대기)
        
        _LOGGER.info(f"Commax Doorbell {name} (index: {index}) 초기화 완료")

    @property
    def name(self) -> str:
        """Return the name of the doorbell."""
        return self._attr_name

    @property
    def is_on(self) -> bool:
        """Return true if doorbell is ringing."""
        return self._attr_is_on

    @property
    def device_class(self) -> BinarySensorDeviceClass:
        """Return the device class."""
        return self._attr_device_class

    async def ring_doorbell(self) -> None:
        """도어벨을 울립니다."""
        await self._send_command(DOORBELL_OPEN_DOOR_PACKET)
        self._attr_is_on = True
        self.async_write_ha_state()
        
        # 3초 후 자동으로 끄기
        await asyncio.sleep(3)
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
                    _LOGGER.debug(f"도어벨 {self.index + 1} 명령 전송: {packet}")
                    await asyncio.sleep(0.075)
                    
            except Exception as e:
                _LOGGER.error(f"도어벨 {self.index + 1} 명령 전송 실패: {e}")
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
            _LOGGER.info(f"도어벨 시리얼 포트 {self.config[CONF_PORT]} 연결 성공")
        except Exception as e:
            _LOGGER.error(f"도어벨 시리얼 포트 연결 실패: {e}")
            self._serial_port = None

    async def _reconnect_serial(self) -> None:
        """시리얼 포트를 재연결합니다."""
        if self._serial_port:
            self._serial_port.close()
            self._serial_port = None
        await self._connect_serial()

    async def async_update(self) -> None:
        """도어벨 상태를 업데이트합니다."""
        # 도어벨은 상태 조회가 아닌 이벤트 감지 방식이므로
        # 주기적인 상태 업데이트는 하지 않습니다.
        # 대신 RS485 데이터를 지속적으로 모니터링합니다.
        pass

    async def _monitor_rs485(self) -> None:
        """RS485 데이터를 지속적으로 모니터링합니다."""
        if not self._serial_port:
            await self._connect_serial()
        
        if not self._serial_port:
            return
        
        try:
            # 읽기 버퍼 확인
            if self._serial_port.in_waiting > 0:
                data = self._serial_port.read(self._serial_port.in_waiting)
                if data:
                    self._process_rs485_data(data)
        except Exception as e:
            _LOGGER.error(f"도어벨 {self.index + 1} RS485 모니터링 실패: {e}")
            await self._reconnect_serial()

    def _process_rs485_data(self, data: bytes) -> None:
        """RS485 데이터를 처리합니다."""
        data_hex = data.hex().upper()
        _LOGGER.debug(f"도어벨 {self.index + 1} RS485 데이터 수신: {data_hex}")
        
        # 벨 울림 패킷 감지 (15바이트 패킷)
        if len(data) >= 15 and data_hex.startswith("100109120101091201"):
            if self._state != "ON":
                self._state = "ON"
                self._attr_is_on = True
                self.async_write_ha_state()
                _LOGGER.info(f"도어벨 {self.index + 1} 벨 울림 감지!")
        
        # 통화 종료 패킷 감지 (16바이트 패킷)
        elif len(data) >= 16 and data_hex.startswith("0212010912010109120161"):
            if self._state != "OFF":
                self._state = "OFF"
                self._attr_is_on = False
                self.async_write_ha_state()
                _LOGGER.info(f"도어벨 {self.index + 1} 통화 종료 감지!")
        
        # 알 수 없는 패킷
        else:
            _LOGGER.debug(f"도어벨 {self.index + 1} 알 수 없는 RS485 패킷: {data_hex}")

    async def async_added_to_hass(self) -> None:
        """엔티티가 Home Assistant에 추가될 때 호출됩니다."""
        await super().async_added_to_hass()
        
        # RS485 모니터링 시작
        self.hass.async_create_task(self._start_rs485_monitoring())

    async def _start_rs485_monitoring(self) -> None:
        """RS485 모니터링을 시작합니다."""
        while True:
            await self._monitor_rs485()
            await asyncio.sleep(0.05)  # 50ms 간격으로 모니터링 