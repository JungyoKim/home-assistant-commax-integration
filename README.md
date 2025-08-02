# Commax Home Assistant 통합구성요소

이 프로젝트는 Home Assistant용 Commax 시스템 통합구성요소입니다.

## 🏠 지원 기능

### 💡 조명 (Light)
- **5개 조명 제어**: 거실 조명1, 거실 조명2, 거실 조명3, 거실 조명4, 복도 조명
- **개별 ON/OFF 제어**: 각 조명을 독립적으로 제어
- **실시간 상태 모니터링**: 조명 상태 실시간 업데이트

### 🔥 보일러 (Climate)
- **4개 방 보일러 제어**: 거실, 안방, 공부방, 침대방 보일러
- **온도 설정**: 목표 온도 설정 (5-53°C)
- **ON/OFF 제어**: 보일러 켜기/끄기
- **모드 변경**: 난방 모드 전환
- **실시간 상태**: 현재 온도 및 동작 상태 모니터링

### 🚪 도어 (Switch)
- **잠금/해제**: 현관문 잠금 및 해제
- **상태 모니터링**: 도어 잠금 상태 실시간 확인

### 🔔 도어벨 (Binary Sensor)
- **도어벨 알림**: 도어벨 울림 감지
- **자동 리셋**: 3초 후 자동으로 상태 리셋

### 🛗 엘리베이터 (Switch)
- **엘리베이터 호출**: 엘리베이터 호출 버튼
- **층 선택**: 특정 층 호출 (1-9층)
- **상태 모니터링**: 엘리베이터 호출 상태 확인

### ⚡ 일괄소등 (Switch)
- **전체 ON/OFF**: 모든 조명을 한 번에 켜기/끄기
- **상태 모니터링**: 일괄소등 상태 확인

## 🔧 하드웨어 요구사항

- **USB to RS485 어댑터**: FTDI, Prolific, CH340 등 지원
- **Commax 시스템**: RS485 통신 지원
- **시리얼 포트**: 9600 baud, 8N1 설정

## 📋 통신 프로토콜

### 패킷 구조
- **조명**: `3001000000000031` ~ `3005000000000035` (상태 조회)
- **보일러**: `4001000000000041` (상태 조회)
- **도어**: `5001000000000051` (상태 조회)
- **도어벨**: `6001000000000061` (상태 조회)
- **엘리베이터**: `7001000000000071` (상태 조회)
- **일괄소등**: `8001000000000081` (상태 조회)

## 🚀 설치 및 설정

### 1. 파일 복사
Home Assistant의 `config/custom_components/` 디렉토리에 `commax` 폴더를 복사합니다.

### 2. Home Assistant 재시작
설정 > 시스템 > 재시작에서 Home Assistant를 재시작합니다.

### 3. 통합구성요소 추가
설정 > 통합구성요소 > 통합구성요소 추가에서 "Commax"를 검색하여 추가합니다.

### 4. 시리얼 포트 설정
기존 Go 코드에서 사용하던 포트 설정을 참고하여 설정합니다:

| 기기 | USB 포트 | 설명 |
|------|----------|------|
| 조명 | `/dev/ttyUSB3` | 5개 조명 제어 |
| 보일러 | `/dev/ttyUSB2` | 4개 방 보일러 제어 |
| 엘리베이터 | `/dev/ttyUSB0` | 엘리베이터 호출 |
| 도어벨 | `/dev/ttyUSB1` | 도어벨 감지 및 문열기 |

**Windows 환경에서는:**
- `COM1`, `COM2`, `COM3`, `COM4` 등으로 표시됩니다.
- 장치 관리자에서 USB to RS485 어댑터의 COM 포트를 확인하세요.

### 5. 설정 완료
- 시리얼 포트 선택
- 통신 속도: 9600 bps (기본값)
- 타임아웃: 0.1초 (기본값)
- 스캔 간격: 1초 (기본값)

설정이 완료되면 다음 엔티티들이 자동으로 생성됩니다:

## 🧪 테스트

### 1. 하드웨어 연결 확인
기존 Go 코드가 정상 작동하는지 먼저 확인하세요:
```bash
# 기존 Go 프로그램 실행
go run main.go
```

### 2. Home Assistant 통합구성요소 테스트
1. **조명 테스트**
   - Home Assistant UI에서 조명 엔티티 ON/OFF
   - 실제 조명이 켜지고 꺼지는지 확인

2. **보일러 테스트**
   - Home Assistant UI에서 보일러 엔티티 모드 변경
   - 온도 설정 기능 테스트
   - 실제 보일러가 반응하는지 확인

3. **도어벨 테스트**
   - 실제 도어벨 버튼을 눌러서 Home Assistant에서 이벤트 감지 확인
   - Home Assistant에서 문열기 기능 테스트

4. **엘리베이터 테스트**
   - Home Assistant UI에서 엘리베이터 호출 버튼 테스트
   - 실제 엘리베이터가 호출되는지 확인

5. **일괄소등 테스트**
   - Home Assistant UI에서 일괄소등 ON/OFF 테스트
   - 모든 조명이 동시에 켜지고 꺼지는지 확인

### 3. 로그 확인
Home Assistant 개발자 도구 > 로그에서 다음을 확인:
- 시리얼 포트 연결 성공/실패
- 패킷 전송/수신 로그
- 엔티티 상태 변경 로그

### 4. 문제 해결
- **시리얼 포트 연결 실패**: 포트 번호 확인, 권한 확인
- **패킷 전송 실패**: USB to RS485 어댑터 드라이버 확인
- **엔티티 응답 없음**: RS485 케이블 연결 상태 확인

## 📁 프로젝트 구조
```
custom_integration/
├── __init__.py          # 메인 초기화
├── manifest.json        # 통합구성요소 메타데이터
├── const.py            # 상수 정의
├── config_flow.py      # 설정 플로우
├── light.py            # 조명 플랫폼
├── climate.py          # 보일러 플랫폼
├── switch.py           # 도어/엘리베이터/일괄소등 플랫폼
├── binary_sensor.py    # 도어벨 플랫폼
└── translations/       # 번역 파일
    └── ko.json
```

## 🔄 기존 MQTT에서 마이그레이션

기존 Go MQTT 코드에서 Home Assistant 통합구성요소로 마이그레이션:

### MQTT 토픽 매핑
- **기존**: `commax/lights/1/set` → **새로운**: Home Assistant 조명 엔티티
- **기존**: `commax/lights/1/state` → **새로운**: 자동 상태 업데이트

### 장점
- ✅ Home Assistant 네이티브 지원
- ✅ 자동화 및 스크립트 통합
- ✅ 사용자 친화적 UI
- ✅ 설정 관리 간소화
- ✅ 모든 Commax 기기 통합 관리

## 🎯 사용 예시

### 자동화 예시
```yaml
# 도어벨이 울리면 모든 조명 켜기
automation:
  - alias: "도어벨 알림 시 조명 켜기"
    trigger:
      platform: state
      entity_id: binary_sensor.commax_doorbell_0
      to: "on"
    action:
      - service: light.turn_on
        target:
          entity_id: light.commax_light_0, light.commax_light_1

# 외출 시 모든 조명 끄기
automation:
  - alias: "외출 시 일괄소등"
    trigger:
      platform: state
      entity_id: switch.commax_door_0
      to: "off"
    action:
      - service: switch.turn_off
        target:
          entity_id: switch.commax_master_0
```

## 🤖 자동화 예시

### 1. 도어벨 자동화
```yaml
# 도어벨이 울리면 알림 보내기
automation:
  - alias: "도어벨 알림"
    trigger:
      platform: state
      entity_id: binary_sensor.commax_doorbell
      to: "on"
    action:
      - service: notify.mobile_app
        data:
          title: "도어벨"
          message: "누군가 도어벨을 눌렀습니다!"
```

### 2. 외출 시 일괄소등
```yaml
# 외출 모드 활성화 시 모든 조명 끄기
automation:
  - alias: "외출 시 일괄소등"
    trigger:
      platform: state
      entity_id: input_boolean.away_mode
      to: "on"
    action:
      - service: switch.turn_off
        target:
          entity_id: switch.commax_master
```

### 3. 보일러 자동 제어
```yaml
# 온도에 따른 보일러 자동 제어
automation:
  - alias: "보일러 자동 제어"
    trigger:
      platform: numeric_state
      entity_id: sensor.living_room_temperature
      below: 18
    action:
      - service: climate.set_hvac_mode
        target:
          entity_id: climate.commax_boiler_1
        data:
          hvac_mode: heat
```

### 4. 엘리베이터 호출 자동화
```yaml
# 특정 시간에 엘리베이터 자동 호출
automation:
  - alias: "아침 엘리베이터 호출"
    trigger:
      platform: time
      at: "07:00:00"
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.commax_elevator
```

## 🐛 문제 해결

### 시리얼 포트 연결 실패
1. USB to RS485 어댑터 드라이버 확인
2. 포트 권한 확인 (Linux: `sudo usermod -a -G dialout $USER`)
3. 다른 프로그램에서 포트 사용 중인지 확인

### 기기 제어 안됨
1. RS485 통신 상태 확인
2. 패킷 형식 확인
3. 기기 시스템 전원 상태 확인

## 📝 라이센스

MIT License

## 🤝 기여

버그 리포트 및 기능 요청은 GitHub Issues를 이용해 주세요. 