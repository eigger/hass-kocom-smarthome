# 적용한 공통 규칙

- 표준: https://github.com/eigger/hass-repo-standards/tree/0ec31111a81b0ee5702f1d8a17f03616a10a5db6
- 참조 커밋 SHA: 0ec31111a81b0ee5702f1d8a17f03616a10a5db6
- 채택 검토일: 2026-10-22
- profile: integration / ha
- 적용 점검표: [ADOPTION_CHECKLIST.md](ADOPTION_CHECKLIST.md)
- 중앙 현황표: https://github.com/eigger/hass-repo-standards/blob/main/docs/adoption-status.md
- 조율 / 구현 / 독립 리뷰·검증: root(kocom-20261022) / tests_ci, docs / independent_review
- 중앙 현황 갱신일: 2026-10-22, 중앙 원격 d317976에 자기 행 갱신; 최종 검증·배포 마감은 중앙 현황표/체크리스트 참조
- 실제 기본 브랜치: `main` (`gh repo view` 확인); branch protection 없음 (API 404)
- 검토 시작 통합 커밋: `34f6704`
- 테스트 경로: `tests/components/kocom_smarthome/`
- 변경 전/후 최소 HA: `2025.8.0`, 기존 `hacs.json.homeassistant` 보존
- current 환경: HA `2026.10.2` / Python `3.14` / pytest-homeassistant-custom-component `0.13.373`
- minimum 환경: HA `2025.8.0` / Python `3.13` / pytest-homeassistant-custom-component `0.13.269`; 기존 aiodns 호환 제한 `pycares<5` 보존
- 최소 package 검증: N/A — manifest에 별도 외부 Python requirements 없음
- imagespec DOC-08 및 Bluetooth DOC-07: N/A — 해당 의존성/import/기능 없음
- Tests/Validate/action 참조: 위 검토한 전체 SHA로 고정
- Hassfest 도구: `ec18d8b25d1ee39aa8b85a72a170e42bee33228c`의 공식 Core Dockerfile/전체 validator 사용. published Hassfest의 categories 스키마 지연을 중앙 지원 입력으로 해결하며 HA 지원 최소는 유지. 원격 실행 결과는 체크리스트 참조.
- HACS: Custom. 2026-10-22 공식 https://raw.githubusercontent.com/hacs/default/master/integration 에 저장소 없음 확인. 기본 목록 신청은 별도 범위.
- 브랜드: [로컬 PNG 및 출처](custom_components/kocom_smarthome/brand/README.md). 256/512 정사각형 RGBA PNG 직접 검사. HA 2026.3 미만의 UI 아이콘 표시는 미검증.
- 제품 분류: `energy.meters_monitoring` — 월패드를 통한 세대별 에너지 검침 조회가 실제 지원 목적. 조명/콘센트/난방 제어는 미지원. hub 유형·domain·entity unique ID·entry schema 유지.

## 예외

없음. 검증 미완료는 예외나 PASS로 처리하지 않고 체크리스트의 TODO로 기록합니다.

## 적용 영향

공용 SHA 고정 CI, 실제 HA 테스트 기반, 양언어 README와 HACS 설치 링크를 채택합니다. 중앙 AGENTS.md는 이 리포에 설치하지 않습니다. 인증 오류 및 민감 정보 처리에서 발견한 문제는 회귀 테스트와 함께 보완합니다. 실제 환경·원격 CI·독립 검증 결과는 체크리스트에 구분합니다. 실물 월패드/단지 서버/HA UI는 이번 자동 검증에 포함하지 않습니다.

## 검증과 배포

[PR #2](https://github.com/eigger/hass-kocom-smarthome/pull/2)를 main `04f23dfb6fe09b0dc673a97b38a9065a4dc47930`에 반영하고, 동일 커밋의 모든 원격 Tests/Validate 성공을 독립 확인한 후 [v1.0.1](https://github.com/eigger/hass-kocom-smarthome/releases/tag/v1.0.1)을 정식 배포했습니다. tag와 manifest.version 일치를 API로 확인했습니다. 양환경 각109passed/skip0·pipcheck, HACS10checks·Hassfest Invalid0 및 중앙/Ruff 검사가 성공했습니다. 세부 환경·CI 링크·독립 리뷰와 미검증 범위는 체크리스트에 기록합니다.
