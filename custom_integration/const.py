"""Constants for the Commax Integration."""
from __future__ import annotations

DOMAIN = "commax"

# Defaults
DEFAULT_NAME = "Commax"
DEFAULT_SCAN_INTERVAL = 1  # 1초마다 상태 조회
DEFAULT_BAUD_RATE = 9600
DEFAULT_TIMEOUT = 0.1

# Configuration
CONF_NAME = "name"
CONF_PORT = "port"
CONF_BAUD_RATE = "baud_rate"
CONF_TIMEOUT = "timeout"
CONF_SCAN_INTERVAL = "scan_interval"

# ===== 조명 (Lighting) =====
LIGHTING_DOMAIN = "lighting"
STATUS_QUERY_PACKETS = [
    "3001000000000031",  # 조명 1 상태 조회
    "3002000000000032",  # 조명 2 상태 조회
    "3003000000000033",  # 조명 3 상태 조회
    "3004000000000034",  # 조명 4 상태 조회
    "3005000000000035",  # 조명 5 상태 조회
]

LIGHT_ON_PACKETS = [
    "3101010000000033",  # 조명 1 ON
    "3102010000000034",  # 조명 2 ON
    "3103010000000035",  # 조명 3 ON
    "3104010000000036",  # 조명 4 ON
    "3105010000000037",  # 조명 5 ON
]

LIGHT_OFF_PACKETS = [
    "3101000000000032",  # 조명 1 OFF
    "3102000000000033",  # 조명 2 OFF
    "3103000000000034",  # 조명 3 OFF
    "3104000000000035",  # 조명 4 OFF
    "3105000000000036",  # 조명 5 OFF
]

# ===== 보일러 (Boiler) =====
BOILER_DOMAIN = "boiler"

# 보일러 상태 조회 패킷 (4개 방)
BOILER_STATUS_QUERY_PACKETS = [
    "0201000000000003",  # 방 1 상태 조회
    "0202000000000004",  # 방 2 상태 조회  
    "0203000000000005",  # 방 3 상태 조회
    "0204000000000006",  # 방 4 상태 조회
]

# 보일러 제어 패킷은 _make_boiler_packet() 메서드에서 동적 생성

# 보일러 응답 패턴
BOILER_STATUS_RESPONSE_HEADER = 0x82
BOILER_CONTROL_RESPONSE_HEADER = 0x84
BOILER_STATE_HEATING = 0x83
BOILER_STATE_IDLE = 0x81
BOILER_STATE_OFF = 0x84

# 보일러 온도 범위
BOILER_MIN_TEMP = 0x05  # 5도
BOILER_MAX_TEMP = 0x35  # 53도

# ===== 도어 (Door) =====
DOOR_DOMAIN = "door"

# 도어 패킷 (실제 도어벨 Go 코드에서 사용하던 문열기 패킷)
DOOR_OPEN_PACKET = "02110202090302020903054000017703"  # 문열기 명령

# ===== 도어벨 (Doorbell) =====
DOORBELL_DOMAIN = "doorbell"

# 도어벨 패킷 (실제 Go 코드에서 사용하던 패킷)
DOORBELL_BELL_RING_PACKET = "100109120101091201100000005A03"  # 벨 울림 감지
DOORBELL_CALL_END_PACKET = "0212010912010109120161000005B203"  # 통화 종료 감지
DOORBELL_OPEN_DOOR_PACKET = "02110202090302020903054000017703"  # 문열기 명령

# ===== 엘리베이터 (Elevator) =====
ELEVATOR_DOMAIN = "elevator"

# 엘리베이터 패킷 (실제 Go 코드에서 사용하던 패킷)
ELEVATOR_CALL_PACKET = "A0010100081500BF"  # 엘리베이터 호출

# ===== 일괄소등 (Master Switch) =====
MASTER_DOMAIN = "master"

# 일괄소등 패킷 (실제 Go 코드에서 사용하던 패킷)
MASTER_STATUS_QUERY = "2001000000000021"  # 상태 조회
MASTER_ALL_ON_PACKET = "2201010100000025"  # 일괄소등 ON
MASTER_ALL_OFF_PACKET = "2201000100000024"  # 일괄소등 OFF

# 상태 응답 패턴
STATUS_ON_PREFIX = "B001"
STATUS_OFF_PREFIX = "B000"

# 엔티티 정보
LIGHT_NAMES = [
    "거실 조명1",
    "거실 조명2", 
    "거실 조명3",
    "거실 조명4",
    "복도 조명"
]

BOILER_NAMES = [
    "거실 보일러",
    "안방 보일러", 
    "공부방 보일러",
    "침대방 보일러"
]

DOOR_NAMES = [
    "현관문"
]

DOORBELL_NAMES = [
    "도어벨"
]

ELEVATOR_NAMES = [
    "엘리베이터"
]

MASTER_NAMES = [
    "일괄소등"
] 