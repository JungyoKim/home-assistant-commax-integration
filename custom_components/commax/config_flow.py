"""Config flow for Commax Lighting Integration."""
from __future__ import annotations

import logging
import serial
import serial.tools.list_ports
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import (
    DOMAIN, 
    DEFAULT_NAME, 
    DEFAULT_BAUD_RATE, 
    DEFAULT_TIMEOUT,
    DEFAULT_SCAN_INTERVAL,
    CONF_NAME, 
    CONF_PORT,
    CONF_BAUD_RATE,
    CONF_TIMEOUT,
    CONF_SCAN_INTERVAL
)

_LOGGER = logging.getLogger(__name__)


class CommaxLightingConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Commax Lighting Integration."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            # 사용 가능한 시리얼 포트 목록 가져오기
            ports = await self.hass.async_add_executor_job(self._get_available_ports)
            
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(
                    {
                        vol.Required(CONF_NAME, default=DEFAULT_NAME): str,
                        vol.Required(CONF_PORT): vol.In(ports) if ports else str,
                        vol.Optional(CONF_BAUD_RATE, default=DEFAULT_BAUD_RATE): int,
                        vol.Optional(CONF_TIMEOUT, default=DEFAULT_TIMEOUT): float,
                        vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): int,
                    }
                ),
                description_placeholders={
                    "ports": ", ".join(ports) if ports else "사용 가능한 포트 없음"
                }
            )

        # 시리얼 포트 연결 테스트
        try:
            await self.hass.async_add_executor_job(
                self._test_serial_connection, user_input[CONF_PORT]
            )
        except Exception as ex:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(
                    {
                        vol.Required(CONF_NAME, default=user_input[CONF_NAME]): str,
                        vol.Required(CONF_PORT, default=user_input[CONF_PORT]): str,
                        vol.Optional(CONF_BAUD_RATE, default=user_input[CONF_BAUD_RATE]): int,
                        vol.Optional(CONF_TIMEOUT, default=user_input[CONF_TIMEOUT]): float,
                        vol.Optional(CONF_SCAN_INTERVAL, default=user_input[CONF_SCAN_INTERVAL]): int,
                    }
                ),
                errors={"base": f"시리얼 포트 연결 실패: {str(ex)}"}
            )

        return self.async_create_entry(
            title=user_input[CONF_NAME],
            data=user_input,
        )

    def _get_available_ports(self) -> list[str]:
        """사용 가능한 시리얼 포트 목록을 반환합니다."""
        ports = []
        for port in serial.tools.list_ports.comports():
            ports.append(port.device)
        return ports

    def _test_serial_connection(self, port: str) -> None:
        """시리얼 포트 연결을 테스트합니다."""
        try:
            ser = serial.Serial(
                port=port,
                baudrate=DEFAULT_BAUD_RATE,
                timeout=DEFAULT_TIMEOUT
            )
            ser.close()
        except Exception as e:
            raise HomeAssistantError(f"시리얼 포트 {port} 연결 실패: {str(e)}") 