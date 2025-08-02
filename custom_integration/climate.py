"""Climate platform for Commax Boiler Integration."""
from __future__ import annotations

import logging
import serial
import asyncio
from datetime import datetime
from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
    HVACAction,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.const import (
    CONF_NAME,
    UnitOfTemperature,
    ATTR_TEMPERATURE,
)
from homeassistant.helpers.typing import StateType

from .const import (
    DOMAIN,
    CONF_PORT,
    CONF_BAUD_RATE,
    CONF_TIMEOUT,
    BOILER_STATUS_QUERY_PACKETS,
    BOILER_STATUS_RESPONSE_HEADER,
    BOILER_CONTROL_RESPONSE_HEADER,
    BOILER_STATE_HEATING,
    BOILER_STATE_IDLE,
    BOILER_STATE_OFF,
    BOILER_MIN_TEMP,
    BOILER_MAX_TEMP,
    BOILER_NAMES,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Commax Boiler platform."""
    config = hass.data[DOMAIN][config_entry.entry_id]
    
    # 4개 방의 보일러 엔티티 생성
    boilers = []
    for i, name in enumerate(BOILER_NAMES):
        boiler = CommaxBoiler(
            hass,
            config,
            i,
            name
        )
        boilers.append(boiler)
    
    async_add_entities(boilers, True)


class CommaxBoiler(ClimateEntity):
    """Representation of a Commax Boiler."""

    def __init__(self, hass: HomeAssistant, config: dict[str, Any], room_index: int, name: str) -> None:
        """Initialize the boiler."""
        self.hass = hass
        self.config = config
        self.room_index = room_index
        self.room_number = room_index + 1  # 1-4번 방
        self._attr_name = name
        self._attr_unique_id = f"{DOMAIN}_boiler_{room_index + 1}"
        
        # Climate 속성
        self._attr_hvac_modes = [HVACMode.HEAT, HVACMode.OFF]
        self._attr_hvac_mode = HVACMode.OFF
        self._attr_hvac_action = HVACAction.OFF
        self._attr_supported_features = (
            ClimateEntityFeature.TARGET_TEMPERATURE |
            ClimateEntityFeature.TURN_OFF |
            ClimateEntityFeature.TURN_ON
        )
        self._attr_temperature_unit = UnitOfTemperature.CELSIUS
        self._attr_target_temperature = 20
        self._attr_current_temperature = 20
        self._attr_min_temp = 5  # 0x05
        self._attr_max_temp = 53  # 0x35
        
        # 시리얼 통신 관련
        self._serial_port = None
        self._serial_lock = asyncio.Lock()
        
        # 상태 조회 관련
        self._last_status_check = None
        self._status_check_interval = config.get("scan_interval", 1)
        
        _LOGGER.info(f"Commax Boiler {name} (방 {self.room_number}) 초기화 완료")

    @property
    def name(self) -> str:
        """Return the name of the boiler."""
        return self._attr_name

    @property
    def hvac_mode(self) -> HVACMode:
        """Return the current HVAC mode."""
        return self._attr_hvac_mode

    @property
    def hvac_action(self) -> HVACAction:
        """Return the current HVAC action."""
        return self._attr_hvac_action

    @property
    def target_temperature(self) -> float:
        """Return the target temperature."""
        return self._attr_target_temperature

    @property
    def current_temperature(self) -> float:
        """Return the current temperature."""
        return self._attr_current_temperature

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set the HVAC mode."""
        if hvac_mode == HVACMode.HEAT:
            packet = self._make_boiler_packet(self.room_number, 0x04, 0x81)  # 모드 ON
            await self._send_command(packet)
            self._attr_hvac_mode = HVACMode.HEAT
            self._attr_hvac_action = HVACAction.HEATING
        elif hvac_mode == HVACMode.OFF:
            packet = self._make_boiler_packet(self.room_number, 0x04, 0x00)  # 모드 OFF
            await self._send_command(packet)
            self._attr_hvac_mode = HVACMode.OFF
            self._attr_hvac_action = HVACAction.OFF
        
        self.async_write_ha_state()

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set the target temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is not None:
            # 온도를 HEX로 변환 (5-53도 범위)
            temp_hex = max(BOILER_MIN_TEMP, min(BOILER_MAX_TEMP, int(temperature)))
            packet = self._make_boiler_packet(self.room_number, 0x03, temp_hex)  # 온도 설정
            await self._send_command(packet)
            self._attr_target_temperature = temperature
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
                    _LOGGER.debug(f"보일러 방 {self.room_number} 명령 전송: {packet}")
                    
                    # 응답 대기
                    await asyncio.sleep(0.075)  # 75ms 대기
                    
            except Exception as e:
                _LOGGER.error(f"보일러 방 {self.room_number} 명령 전송 실패: {e}")
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
        """보일러 상태를 업데이트합니다."""
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
                    # 해당 방의 상태 조회 패킷 전송
                    status_packet = BOILER_STATUS_QUERY_PACKETS[self.room_index]
                    data = bytes.fromhex(status_packet)
                    self._serial_port.write(data)
                    
                    # 응답 읽기
                    await asyncio.sleep(0.075)  # 75ms 대기
                    
                    if self._serial_port.in_waiting > 0:
                        response = self._serial_port.read(self._serial_port.in_waiting)
                        response_hex = response.hex().upper()
                        
                        # 상태 파싱
                        old_mode = self._attr_hvac_mode
                        old_action = self._attr_hvac_action
                        
                        if len(response) >= 8:
                            status = self._parse_boiler_status(response)
                            if status and status['room'] == self.room_number:
                                # HVAC 모드 설정
                                if status['state'] in [BOILER_STATE_HEATING, BOILER_STATE_IDLE]:
                                    self._attr_hvac_mode = HVACMode.HEAT
                                    if status['state'] == BOILER_STATE_HEATING:
                                        self._attr_hvac_action = HVACAction.HEATING
                                    else:
                                        self._attr_hvac_action = HVACAction.IDLE
                                else:
                                    self._attr_hvac_mode = HVACMode.OFF
                                    self._attr_hvac_action = HVACAction.OFF
                                
                                # 온도 설정
                                self._attr_current_temperature = status['current_temp']
                                self._attr_target_temperature = status['set_temp']
                                
                                if old_mode != self._attr_hvac_mode:
                                    _LOGGER.info(f"보일러 방 {self.room_number} 상태 변경: {old_mode} -> {self._attr_hvac_mode}")
                    
            except Exception as e:
                _LOGGER.error(f"보일러 방 {self.room_number} 상태 조회 실패: {e}")
                await self._reconnect_serial()

    def _parse_boiler_status(self, data: bytes) -> dict | None:
        """보일러 상태 응답 패킷을 파싱합니다."""
        if len(data) < 8:
            return None
        
        # 체크섬 검증
        checksum = sum(data[:7]) & 0xFF
        if data[7] != checksum:
            _LOGGER.warning(f"보일러 체크섬 불일치: 계산={checksum:02X}, 수신={data[7]:02X}")
            return None
        
        # 헤더 검증
        if data[0] not in [BOILER_STATUS_RESPONSE_HEADER, BOILER_CONTROL_RESPONSE_HEADER]:
            return None
        
        return {
            'room': data[2],
            'state': data[1], 
            'current_temp': data[3],
            'set_temp': data[4]
        } 

    def _make_boiler_packet(self, device_id: int, cmd_type: int, value: int) -> str:
        """보일러 제어 패킷을 생성합니다."""
        # 패킷 구조: 04 + 방번호 + 명령타입 + 값 + 000000 + 체크섬
        pkt = [0x04, device_id, cmd_type, value, 0x00, 0x00, 0x00]
        
        # 체크섬 계산 (Go 코드와 동일)
        checksum = sum(pkt) & 0xFF
        pkt.append(checksum)
        
        # HEX 문자열로 변환
        return ''.join(f'{b:02X}' for b in pkt) 