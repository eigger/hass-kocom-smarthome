<!-- hass-standards:header:start -->
# KOCOM Smart Home+ Energy (hass-kocom-smarthome)

**코콤 스마트홈+** 월패드에 연결해 세대 **에너지 검침 정보**를 가져오는 Home Assistant 커스텀 통합구성요소입니다.

[English](README.md) | **한국어**

<!-- hass-standards:badges:start -->
[![Release](https://img.shields.io/github/v/release/eigger/hass-kocom-smarthome?style=flat)](https://github.com/eigger/hass-kocom-smarthome/releases)
[![HACS Custom](https://img.shields.io/badge/HACS-Custom-41BDF5?style=flat)](#설치)
[![Home Assistant minimum](https://img.shields.io/badge/HA-%E2%89%A5%202025.8.0-41BDF5?style=flat)](hacs.json)
[![Tests](https://img.shields.io/github/actions/workflow/status/eigger/hass-kocom-smarthome/tests.yml?branch=main&style=flat&label=Tests)](https://github.com/eigger/hass-kocom-smarthome/actions/workflows/tests.yml)
[![Validate](https://img.shields.io/github/actions/workflow/status/eigger/hass-kocom-smarthome/validate.yml?branch=main&style=flat&label=Validate)](https://github.com/eigger/hass-kocom-smarthome/actions/workflows/validate.yml)
[![License](https://img.shields.io/github/license/eigger/hass-kocom-smarthome?style=flat)](LICENSE)
[![Downloads](https://img.shields.io/github/downloads/eigger/hass-kocom-smarthome/latest/total?style=flat&color=41BDF5&label=Downloads)](https://github.com/eigger/hass-kocom-smarthome/releases)
<!-- hass-standards:badges:end -->
<!-- hass-standards:header:end -->

- 휴대전화 번호로 월패드와 페어링하면, 단지 서버에서 **월간 검침 데이터**를 주기적으로 조회합니다.
- 전기·난방·온수·가스·수도 각각에 대해 **우리집 사용량 / 이번달 단지 평균 / 예상 요금** 센서가 생성됩니다.
- 조명·콘센트·난방 제어 기능은 **아직** 포함하지 않습니다. 현재는 에너지 검침만 지원합니다.

## 센서

세대에서 실제로 검침되는 항목만 생성됩니다. 단지·월패드 구성, 그리고 단지 서버가
내려주는 항목에 따라 일부는 없을 수 있습니다.

| 에너지 | 단위 | device_class | 생성되는 센서 |
| --- | --- | --- | --- |
| 전기 | kWh | `energy` | 사용량 / 단지 평균 / 예상 요금 |
| 난방 | m³ | — | 사용량 / 단지 평균 / 예상 요금 |
| 온수 | m³ | — | 사용량 / 단지 평균 / 예상 요금 |
| 가스 | m³ | `gas` | 사용량 / 단지 평균 / 예상 요금 |
| 수도 | m³ | `water` | 사용량 / 단지 평균 / 예상 요금 |

- **사용량** 은 우리집 검침값, **단지 평균** 은 같은 단지 세대들의 평균입니다.
- 센서는 월패드를 나타내는 **기기 아래**에 묶입니다. 기기 이름은 코콤 앱에서 지정한
  월패드 별칭이므로, 표시 이름은 `우리집 전기 사용량` 처럼 보입니다.
- 예상 요금 센서는 통화(`KRW`) 센서입니다. 해당 기간의 예상 총액이며, 단가가 아닙니다.

센서 이름은 [`translations/`](custom_components/kocom_smarthome/translations) 의
번역 파일에서 옵니다. 한국어·영어를 지원하며, Home Assistant 언어 설정을 따릅니다.

### 전월 데이터 폴백

단지 서버는 당월 검침이 확정되기 전까지 이번 달 데이터를 내려주지 않는 경우가 있습니다.
이때는 **전월 데이터**로 대체해 센서를 유지합니다.

- 전월 데이터로 생성된 센서는 이름에 `전월` 이 붙습니다 (`전월 전기 사용량` 등).
- 이번 달 데이터가 아예 없는 에너지 종류는, 전월 값을 이번 달 센서에도 채워 넣어 그래프가 끊기지 않게 합니다.
- 전월 센서는 `state_class` 를 `total_increasing` 대신 `total` 로 낮춰, 에너지 대시보드에서
  월이 바뀔 때 값이 튀지 않도록 합니다.

각 센서는 속성으로 `Registration Date`(검침 연월)와 `Sync date`(마지막 조회 시각)를 노출합니다.

## 설치

<!-- hass-standards:installation:start -->
[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=eigger&repository=hass-kocom-smarthome&category=integration)
<!-- hass-standards:installation:end -->

Home Assistant 2025.8.0 이상이 필요합니다. 배지는 HACS가 이미 설치된 인스턴스에서 저장소 화면을 열며, 아래 다운로드 및 재시작 절차를 완료해야 합니다. 사용자 지정 저장소를 추가할 때는 **통합구성요소(Integration)** 유형을 선택하세요.

1. 이 저장소를 HACS의 사용자 지정 저장소로 추가하거나, `custom_components/kocom_smarthome` 폴더를
   Home Assistant 설정 디렉터리의 `custom_components/` 아래에 복사합니다.
2. Home Assistant를 재시작합니다.
3. **설정 → 기기 및 서비스 → 통합구성요소 추가 → "코콤 스마트홈+ (에너지)"** 를 선택합니다.

### 준비물

- 월패드에 등록할 **휴대전화 번호** (하이픈 없이 11자리)
- **월패드 인증 번호** (8자리)

인증 절차는 월패드 모델·세대마다 다릅니다. 설정 메뉴에서 **휴대전화 연결**(또는 유사한
이름의) 항목을 찾아 선택하면 인증번호가 표시됩니다. 인증은 제한 시간 내에 완료해야 합니다.

> 코콤 스마트홈+ 앱에 해당 번호가 **이미 등록되어 있다면** 월패드 인증 단계는 자동으로 건너뜁니다.

## 옵션

**설정 → 기기 및 서비스 → 코콤 스마트홈+ (에너지) → 구성**:

| 옵션 | 기본값 | 설명 |
| --- | --- | --- |
| **에너지 스캔 간격 (시)** | 24 | 단지 서버에서 검침 데이터를 다시 조회하는 주기 |

검침 데이터는 하루 단위로 갱신되므로 간격을 짧게 잡아도 값이 자주 바뀌지 않습니다.
단지 서버에 부담을 주지 않도록 기본값 유지를 권장합니다.

## 디버깅

문제가 있으면 `configuration.yaml` 에 아래를 추가하고 Home Assistant를 재시작한 뒤,
생성된 로그를 이슈에 첨부해 주세요.

```yaml
logger:
  default: info
  logs:
    custom_components.kocom_smarthome: debug
```

전화번호·세대 ID·단지 서버 주소는 로그에 찍힐 때 뒤 4자리만 남기고 가려집니다.
그래도 이슈에 올리기 전에 한 번 확인해 주세요.

단지 서버가 저장된 인증 정보를 거부하면 Home Assistant에서 재인증을 요청합니다. 안내를 확인하면 저장된 전화번호로 다시 로그인하며, 갱신에 성공하면 기존 설정 항목을 업데이트하고 엔티티를 유지합니다. 월패드 페어링이 해제된 경우에는 통합구성요소를 삭제한 뒤 다시 추가하여 월패드 인증을 진행하세요.

## 개발

[개발 및 테스트 안내](docs/development.md)를 참고하세요.

<!-- hass-standards:support:start -->
## 지원

- [Issues](https://github.com/eigger/hass-kocom-smarthome/issues): 버그를 신고하거나 기능을 요청하세요.
- [Discussions](https://github.com/eigger/hass-kocom-smarthome/discussions): 질문하고 사용 경험을 공유하세요.
<!-- hass-standards:support:end -->

<!-- hass-standards:related-projects:start -->
<!-- hass-standards:related-projects:end -->

<!-- hass-standards:license:start -->
## 라이선스

[MIT License](LICENSE) 라이선스로 배포됩니다.
<!-- hass-standards:license:end -->
