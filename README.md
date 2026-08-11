# 코콤 스마트홈+ 에너지 Home Assistant Integration (hass-kocom-smarthome)

[![GitHub Release](https://img.shields.io/github/v/release/eigger/hass-kocom-smarthome?style=flat-square)](https://github.com/eigger/hass-kocom-smarthome/releases)
[![Tests](https://img.shields.io/github/actions/workflow/status/eigger/hass-kocom-smarthome/tests.yml?branch=main&style=flat-square&label=tests)](https://github.com/eigger/hass-kocom-smarthome/actions/workflows/tests.yml)
[![License](https://img.shields.io/github/license/eigger/hass-kocom-smarthome?style=flat-square)](LICENSE)
[![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
![integration usage](https://img.shields.io/badge/dynamic/json?color=41BDF5&logo=home-assistant&label=usage&suffix=%20installs&cacheSeconds=15600&query=%24.kocom_smarthome.total&url=https%3A%2F%2Fanalytics.home-assistant.io%2Fcustom_integrations.json)

**코콤 스마트홈+** 월패드에 연결해 세대 **에너지 검침 정보**를 가져오는 Home Assistant 커스텀 통합구성요소입니다.

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

1. 이 저장소를 HACS의 사용자 지정 저장소로 추가하거나, `custom_components/kocom_smarthome` 폴더를
   Home Assistant 설정 디렉터리의 `custom_components/` 아래에 복사합니다.
2. Home Assistant를 재시작합니다.
3. **설정 → 기기 및 서비스 → 통합구성요소 추가 → "코콤 스마트홈+ (에너지)"** 를 선택합니다.

### 준비물

- 월패드에 등록할 **휴대전화 번호** (하이픈 없이 11자리)
- **월패드 인증 번호** (8자리)

인증 절차는 월패드 모델마다 다릅니다. DWP-1000KC 기준으로 **부가 기능** 메뉴에서
휴대전화 연결을 선택하면 인증번호가 표시됩니다. 인증은 **200초 이내**에 완료해야 합니다.

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

## 피드백

- 버그를 찾으셨나요? [Issues](https://github.com/eigger/hass-kocom-smarthome/issues) 에 남겨 주세요.
- 아이디어나 질문은 [Discussions](https://github.com/eigger/hass-kocom-smarthome/discussions) 에 올려 주세요.

## 라이선스

[MIT](LICENSE)
