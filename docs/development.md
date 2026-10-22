# 개발 및 테스트

[English README](../README.md) | [한국어 README](../README.ko.md)

이 저장소는 HACS 커스텀 통합입니다. 구현은 `custom_components/kocom_smarthome/`에, 실제 Home Assistant 테스트는 `tests/components/kocom_smarthome/`에 둡니다. config flow, coordinator, entity, sensor 및 config entry 생명주기는 Core의 공개 API를 사용합니다. 외부 KOCOM 통신 경계만 mock하고 실제 HA fixture로 설정·플랫폼 로딩·센서 상태·unload를 검사합니다. 기존 digest 인증·모델 파싱·번역 회귀 테스트도 같은 테스트 경로에서 실행합니다.

## 환경과 실행

Home Assistant는 Linux 환경에서 테스트하세요. Windows에서는 WSL을 사용할 수 있습니다. 현재 환경과 최소 지원 환경은 별도 가상환경으로 설치합니다. 아래 명령은 저장소 루트의 Linux 셸에서 실행합니다.

```bash
python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements_test.txt -r requirements_lint.txt
python -m ruff check custom_components tests
python -m ruff format --check custom_components tests
python -m pytest tests/components/kocom_smarthome/ -v
python -m pip check
```

최소 지원 환경은 Python 3.13으로 별도 가상환경을 만들고 `requirements_test_min.txt`를 설치하여 같은 pytest 및 `pip check`를 실행합니다. 정확한 최소 HA의 전이 의존성 제한도 해당 requirements를 통해 설치합니다.

| 환경 | Python | HA | pytest-homeassistant-custom-component | 검증 결과 |
|---|---|---|---|---|
| current | 3.14 | 2026.10.2 | 0.13.373 | 실제 실행 증거는 [채택 체크리스트](../ADOPTION_CHECKLIST.md) 참조 |
| minimum | 3.13 | 2025.8.0 | 0.13.269 | 실제 실행 증거는 [채택 체크리스트](../ADOPTION_CHECKLIST.md) 참조 |

최소 지원은 `hacs.json`의 HA 2025.8.0을 유지합니다. current 테스트 버전은 지원 최소와 별개입니다. 테스트는 실물 월패드·단지 서버·HA UI 연결 확인을 대신하지 않습니다. 원격 HACS/Hassfest 실행 결과도 체크리스트에 별도로 기록합니다.

## 공용 검사와 의존성

[공용 표준](https://github.com/eigger/hass-repo-standards/tree/0ec31111a81b0ee5702f1d8a17f03616a10a5db6)의 [Core 대응 구조](https://github.com/eigger/hass-repo-standards/blob/0ec31111a81b0ee5702f1d8a17f03616a10a5db6/docs/home-assistant.md), [실제 HA 테스트 구조](https://github.com/eigger/hass-repo-standards/blob/0ec31111a81b0ee5702f1d8a17f03616a10a5db6/docs/testing.md), [의존성 규칙](https://github.com/eigger/hass-repo-standards/blob/0ec31111a81b0ee5702f1d8a17f03616a10a5db6/docs/dependencies.md)을 따릅니다. 별도 Python 런타임 라이브러리 요구사항은 현재 없으며 HA 제공 라이브러리를 사용합니다. 새 런타임 의존성이 필요하면 manifest에 선언하고 호환 범위·최소/current 테스트를 함께 검토합니다. 테스트·린트 도구는 각각 requirements 파일에서 관리하며 과거 최소 환경의 자동 상향을 피합니다.

중앙 checkout이 인접한 경우 다음 명령으로 README 관리 영역·배지·테스트 및 CI 구조를 검사할 수 있습니다.

```bash
python ../hass-repo-standards/scripts/check_integration.py .
python ../hass-repo-standards/scripts/sync_badges.py . --check
```

`STANDARDS.md`는 검토 기준과 예외, `ADOPTION_CHECKLIST.md`는 해당 변경의 실제 검증 근거를 기록합니다.
