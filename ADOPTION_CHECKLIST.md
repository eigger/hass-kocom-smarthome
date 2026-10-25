# 공통 규칙 적용 체크리스트

이 파일은 중앙 체크리스트에서 출발한 2026-10-22 채택 검증 기록입니다. 실행 결과와 미완료를 구분하며 실물 검증을 주장하지 않습니다. [사용법과 판정 기준](https://github.com/eigger/hass-repo-standards/blob/0ec31111a81b0ee5702f1d8a17f03616a10a5db6/docs/checklist.md)을 읽고, 아래 규칙은 `STANDARDS.md`에 기록한 표준 커밋에서 확인합니다. 태그·릴리스 대신 `main`의 검토 커밋을 기준으로 하며, 위 사용법 링크의 `main`은 채택 시 검토한 커밋 SHA로 바꿉니다.

## 검토 대상

| 항목 | 값 |
|---|---|
| 통합 리포 / 실제 기본 브랜치 | eigger/hass-kocom-smarthome / main (`gh repo view` 확인) |
| domain / 구현 경로 | kocom_smarthome / custom_components/kocom_smarthome/ |
| 검토 대상 통합 커밋 / 채택 PR | 시작34f6704; origin/main1e21f20(FUNDING 보존) 기반 구현0223c24; PR #2 squash/main04f23dfb6fe09b0dc673a97b38a9065a4dc47930; v1.0.1 |
| 검토한 표준 전체 커밋 SHA | 0ec31111a81b0ee5702f1d8a17f03616a10a5db6 (원격 main 확인) |
| 검토일 / 조율 담당 | 2026-10-22 / root(kocom-20261022) |
| 구현 서브 에이전트 / 독립 리뷰·검증 서브 에이전트 | tests_ci, docs / independent_review |
| 중앙 현황표 반영일 / 기록 | 2026-10-22 중앙 원격 d317976 자기 행 갱신; 마감은 중앙 현황표의 이 리포 행 참조 |
| 변경 전 지원 최소 HA / 근거 파일(hacs.json·manifest·README) | 2025.8.0 (hacs.json); 기존 CI도 해당 정확한 버전 검증 |
| 유지·변경할 지원 최소 / 변경 시 실제 비호환 근거·명시적 승인 | 2025.8.0 유지; 지원 상향 없음 |
| current 테스트 HA / 호환 Python·플러그인 | 2026.10.2 / Python3.14 / plugin0.13.373 |
| 최소 테스트 HA / 호환 Python·플러그인 | 2025.8.0 / Python3.13 / plugin0.13.269 / pycares<5 |
| profile / 테스트 경로 | integration / ha; tests/components/kocom_smarthome/ |
| 이전 검토 기록 | 최초 채택; 과거 CI 결과를 이번 변경의 PASS로 재사용하지 않음 |
| 채택 판정 | 필수 항목 PASS 또는 근거 있는 N/A; 승인 예외 없음. 검증 대상 구현은 배포 커밋04f23df |

상태: `TODO` = 미확인·미충족, `PASS` = 근거로 확인, `EXCEPTION` = 적용 대상의 기록된 예외, `N/A` = 적용 조건에 해당 없음. 모든 항목은 미확인으로 시작합니다. `TODO`를 해당 없음으로 처리하지 않습니다. 묶은 규칙의 결과가 다르면 행을 나눕니다. 권장 항목은 별도로 표시했으며 미채택 이유를 기록합니다.

## 채택·구조·사용자 데이터

| 규칙 ID | 확인 항목 | 상태 | 근거 / 남은 작업 |
|---|---|---|---|
| GOV-01, GOV-02 | `STANDARDS.md`에 표준 SHA·profile·실제 기본 브랜치·예외 기록, workflow/action은 검토 SHA로 고정 | PASS | STANDARDS.md의 full SHA와 모든 shared workflow/action 참조 일치; 중앙 check_integration.py 통과 |
| GOV-03 | 새 표준 채택 변경의 영향·이관 방법과 명시적 채택 PR 확인. 규칙 자체를 변경하면 공통 CHANGELOG 기록 | PASS | PR #2 merge 04f23df; CHANGELOG.md 1.0.1과 docs/development.md에 적용 영향·기존 지원 유지·재인증 안내 |
| GOV-04 | 중앙 표에 작업 시작·단계 변경·종료 상태, 담당·적용 내용·검증/리뷰 근거·남은 작업 갱신, 타 리포 기록 보존 | PASS | 중앙 원격 d317976에 자기 행 착수/단계 기록, 별도 깨끗한 checkout으로 타 세션 수정 보존; 종료 현황표는 아래 중앙 링크 |
| GOV-05 | 구현과 독립 리뷰·검증을 별도 서브 에이전트에게 위임, 지적 수정·재검증 및 결과 취합 | PASS | 구현·독립 별도 양환경 109passed/skip0 및 pipcheck, 최종 재인증·기존 월패드 유지·privacy 회귀 확인; 아래 실행 기록 참조 |
| HA-01, HA-13 | `custom_components/<domain>/`와 domain 일치, 필요한 모듈·공개 API·생명주기는 Core 대응 구조 | PASS | custom_components/kocom_smarthome 모듈과 tests/components/kocom_smarthome 구조; central checker PASS |
| HA-02 | manifest 필드·정렬·동작 선언, 실제 제품 categories 1–3개·주 분류 순서·공식 slug·선택 근거·categories_review 일치 또는 entity/system/virtual 키 생략 이유, 공식 품질 등급 자가 표기 없음 | PASS | manifest 정렬·cloud_polling/hub/config_flow/실제 energy.meters_monitoring 분류; category review 일치, 독립 의미 검토 완료 |
| HA-03 (권장) | 공통 상수·설정·갱신·플랫폼 역할 및 프로토콜 경계에 맞게 모듈 구성 | PASS | 기존 const/config_flow/coordinator/entity/sensor/API/digest/models 분리 보존 |
| HA-04, HA-08 | UI 설정·중복·안정적 식별 및 기능별 options/reauth/reconfigure, entity 의미·registry 영향 확인 | PASS | 구현·독립 별도 양환경 109passed/skip0 및 pipcheck, 최종 재인증·기존 월패드 유지·privacy 회귀 확인; 아래 실행 기록 참조 |
| HA-01, HA-04, HA-08, REL-01, REL-03 | domain·unique ID·entry schema·상태/통계 계약 변경 시 migration 테스트와 사용자 조치 안내 | PASS | domain·entity unique ID·entry schema 변경 없음; 기존 version1→2 migration 회귀 추가 |
| HA-05, HA-06 | setup 실패 구분, unload/reload·부분 실패의 task/listener/연결 정리, async·timeout·취소 처리 | PASS | 구현·독립 별도 양환경 109passed/skip0 및 pipcheck, 최종 재인증·기존 월패드 유지·privacy 회귀 확인; 아래 실행 기록 참조 |
| HA-07 | 중복 polling·property I/O 방지, push 보존, unavailable/unknown·실패 후 복구 | PASS | 구현·독립 별도 양환경 109passed/skip0 및 pipcheck, 최종 재인증·기존 월패드 유지·privacy 회귀 확인; 아래 실행 기록 참조 |
| HA-11, HA-12 | 번역·action/schema 일치, 로그/diagnostics/fixture 비식별화와 제공 시 redaction 테스트 | PASS | 구현·독립 별도 양환경 109passed/skip0 및 pipcheck, 최종 재인증·기존 월패드 유지·privacy 회귀 확인; 아래 실행 기록 참조 |

## 실제 HA 테스트·호환성·의존성

| 규칙 ID | 확인 항목 | 상태 | 근거 / 남은 작업 |
|---|---|---|---|
| TEST-08 | `tests/components/<domain>/`에 구현과 대응하는 테스트·domain fixture 배치, discovery·CI 경로 일치 | PASS | 정확한 중앙 init/conftest, domain fixtures 및 모든 기존 회귀 test 이동; 중앙 checker PASS |
| TEST-02, TEST-03, DEP-07 | 실제 HA·호환 플러그인과 `hass`/`enable_custom_integrations` fixture 사용, HA core stub/복사본/`--no-deps`로 대체하지 않음 | PASS | 실제 HA/plugin 설치, hass·enable_custom_integrations fixture 사용; HA stub 없음; 독립 양환경 실행 확인 |
| TEST-09 | 실제 loader·config entry manager로 setup/플랫폼 로딩, HA 상태·registry·service/action으로 결과 검증 | PASS | 구현·독립 별도 양환경 109passed/skip0 및 pipcheck, 최종 재인증·기존 월패드 유지·privacy 회귀 확인; 아래 실행 기록 참조 |
| TEST-01, TEST-06, TEST-07 | 구현 기능별 성공·실패·중복·migration·unload·복구 회귀 검증, 외부 통신 경계만 mock, skip 사유 | PASS | 구현·독립 별도 양환경 109passed/skip0 및 pipcheck, 최종 재인증·기존 월패드 유지·privacy 회귀 확인; 아래 실행 기록 참조 |
| TEST-04, HACS-01 | 변경 전 지원 최소·current·각 Python/플러그인 분리, 선언한 정확한 최소 검증, 상향 시 비호환 근거·명시적 승인 확인 | PASS | 구현·독립 별도 양환경 109passed/skip0 및 pipcheck, 최종 재인증·기존 월패드 유지·privacy 회귀 확인; 아래 실행 기록 참조 |
| TEST-05, HA-10, DEP-02, DEP-05 | imagespec·blesession 등 최소/현재 라이브러리 별도 환경, 실제 HA 테스트·정확한 설치값·API 경계 검증 | N/A | 외부 manifest Python requirements 및 imagespec/blesession/BLE 기능 없음 |
| DEP-01, DEP-06 | Python runtime은 manifest requirements, HA domain은 dependencies/after_dependencies, 테스트·린트 requirements는 별도 | PASS | HA 제공 aiohttp 사용; requirements_test/min 및 lint 파일 분리; manifest에 추가 외부 의존성 없음 |
| DEP-07, CI-06 | 실제 사용하는 HA 구성요소의 requirements·필수 재귀 의존성·선택 로딩 경로 설치, resolver·`pip check` 통과 | PASS | 독립 양환경 pip check 통과, plugin/HA 완전 설치; shared environment가 HA sensor requirements를 설치 |
| DEP-02, DEP-03, DEP-08 | 의존성 추가/변경의 버전·extras·marker·선언 위치·지원 플랫폼·라이선스 검토, 실제 HA 테스트와 문서 갱신 | N/A | 런타임 라이브러리 추가/하한 변경 없음; 테스트 requirements만 분리 고정 |

독립 리뷰는 변경 전후 지원 최소와 current를 비교하고, 봇 PR이 과거 최소 requirements·constraints까지 갱신하거나 expected-ha-version·Python을 누락하지 않았는지 확인합니다. 최신 테스트 실패는 호환 수정 대상으로 처리합니다.

환경마다 아래 행을 복사합니다. 최소 HA와 최소 라이브러리 검증을 혼동하지 않고, marker가 활성인 환경에서 대상 패키지 설치값을 확인합니다. 실행하지 않은 조합은 `TODO` 또는 근거가 있는 `EXCEPTION`으로 남깁니다.

| 검증 축 / 상태 | 통합 커밋 | Python / HA / 플러그인 실제 버전 | 대상 패키지 실제 버전·extras·marker | 명령·테스트 결과·pip check / CI run·job | skip·제외·미검증 범위 |
|---|---|---|---|---|---|
| 현재 환경 / PASS | 배포04f23df 및 구현0223c24 | Python3.14.7 / HA2026.10.2 / plugin0.13.373 | pycares5.2.1 / pytest9.0.3 / asyncio1.4.0 | 구현·독립 pytest109passed/skip0, pipcheck compatible | skip0; 실물·HAUI 미검증 |
| 정확한 최소 HA / PASS | 배포04f23df 및 구현0223c24 | Python3.13.15 / HA2025.8.0 / plugin0.13.269 | pycares4.11.0 / pytest8.4.1 / asyncio1.1.0 | 구현·독립 pytest109passed/skip0, pipcheck compatible | skip0; 실물·HAUI 미검증 |
| 정확한 최소 라이브러리 / N/A | 이번 변경 | N/A | manifest 외부 requirements 없음 | N/A | 하한 matrix 없음 |

## HACS·CI·의존성 업데이트

| 규칙 ID | 확인 항목 | 상태 | 근거 / 남은 작업 |
|---|---|---|---|
| HACS-01, HACS-02 | 루트 README/LICENSE/hacs.json, 검증한 최소 HA, 실제 배포 구조와 필요한 옵션 일치 | PASS | 루트 hacs.json/README/LICENSE, 최소2025.8.0 및 기존 custom_components 배포 구조 유지 |
| HACS-03, HACS-05 | Default 여부는 목록 근거로 확인, [로컬 brand/icon.png 또는 원격 brands 근거](https://github.com/eigger/hass-repo-standards/blob/0ec31111a81b0ee5702f1d8a17f03616a10a5db6/docs/hacs.md)와 HACS/Hassfest 실제 실행, ignore는 이유·해제 조건 기록 | PASS | Custom 공식 목록 확인, 로컬256/512PNG; PR/merge SHA 원격 HACS All10checks passed(brand/categories 포함)·공식 Hassfest1 integration/Invalid0; ignore 없음 |
| HACS-06 (권장) | description·topics·issue 경로·brands 및 사용하는 HACS 필드 지원 확인 | PASS | gh repo view로 description/hacs/homeassistant/kocom topics·Issues/Discussions 확인; local brand 제공, render_readme 기존 필드 유지 |
| CI-01, CI-02 | Validate/Tests 공통화, 확장 job 유지, 공용 파일명·표시 이름·PR 대상 제한 없는 기본 이벤트·실제 기본 브랜치 push·dispatch·기존 schedule, 전용 CI 명명 형식 | PASS | 중앙 SHA 고정 Tests/Validate 호출·기본 main push/모든 PR·수동 및 Validate weekly; minimum-ha 분리 |
| CI-03, CI-05, CI-08 | 최소 권한·checkout 자격증명 비보존·timeout·concurrency, full SHA·갱신 관리, 비신뢰 입력·secrets 경계 | PASS | read권한·persist-credentials:false·timeout/concurrency·fullSHA 및 Dependabot; secrets/외부PR shell 삽입 없음 |
| CI-04, CI-07, CI-12 | 실패를 숨기지 않는 실제 `ha` 필수 테스트, 버전별 환경·cache·Ruff 설정과 required checks 이름 확인 | PASS | PR·merge SHA Tests 양환경109passed/skip0·pipcheck·lint2 성공, test-profile:ha; main 보호설정 API404로 기존 required checks 없음 |
| DEP-03, DEP-04, CI-09 | updater의 선택 package·연산자/extras/marker 보존, 안정 버전·major 정책, 실제 기본 브랜치·단일 bot branch·PR만 제안 | N/A | manifest runtime requirement 없음, 업데이트할 외부 패키지 없어 updater 생성 안함; 도구는 Dependabot으로 관리 |
| CI-09, CI-10, DEP-08 | 변경 tree의 새 하한·실제 HA 검증 후 PR 동기화, 실패 시 중단·변경 없음 시 기존 PR 정리, 후속 required checks 충족 방식 확인 | N/A | 의존성 updater 없음, bot PR 후속 dispatch 계약 미적용 |

## README·Bluetooth·유지보수

| 규칙 ID | 확인 항목 | 상태 | 근거 / 남은 작업 |
|---|---|---|---|
| DOC-01, DOC-02, DOC-06 | 중앙 header/support/related-projects/license 관리 영역의 정확한 형식, 기존 공통 내용·고지 보존, 영역 밖 순서·제목·본문 유지, 양언어 같은 구조·내용·상호 링크, 독립 번역 의미·누락 리뷰, 실제 활성 지원 링크·실제 라이선스 | PASS | 중앙 렌더러/검사 통과, 기존 한국어 비공백 본문 전체 순서 보존, 독립 영한 의미 검토/활성 지원 링크 확인 |
| DOC-03, DOC-04, DOC-05 | 언어 링크 다음 중첩 배지 관리 블록, flat·Release/HACS/HA minimum/Tests/Validate/License/HACS Downloads(Default) 또는 Usage(Custom) 순서·실제 조건·고유 배지 보존, 실제 기본 브랜치·상태별 필수 동적 집계 배지·양언어 설치 절의 실제 저장소 My HACS 배지·미집계와 0 설치 구분 | PASS | v1.0.0 release 실제 확인; Custom Usage/flat badge 순서·양언어 MyHACS 저장소 링크, sync_badges --check PASS |
| HA-09, HA-10 | BLE 사용 시 HA Bluetooth API·라이브러리 공개 경계, 지원한 proxy 경로·재연결·취소·서비스 변경 검증 | N/A | BLE/Bluetooth proxy 기능 없음 |
| DOC-07 | blesession 사용 여부(manifest requirement extras·operator·marker/실제 import) 확인. 사용 통합은 중앙 양언어 docs/troubleshooting 템플릿의 고정 제목·순서·증상 표·실제 진단/로그·기존 Issues 연결, README와 로컬 문서의 언어별 상호/공통 blesession 원본 링크·placeholder 제거·공용 Validate 검사. 기존 본문/기기안내 보존, 새 제보 양식 금지. 프록시만 지원하면 기존 기기 조건·사용자 안내를 수동 확인 | N/A | blesession/Bluetooth proxy 미사용 |
| DOC-08 | imagespec 사용 여부·양언어 docs/payload 여섯 절·언어별 README/공통 원본/상호 링크·실제 액션/대상/전체 YAML·기기 출력/지원/제한·기존 예제/본문 보존·기존 지원 연결, 모든 로컬 연결 예제의 payload.examples 등록·실제 경로/payload_format(list 또는 yaml)/크기/모델 색상 | N/A | imagespec 및 payload/action 렌더링 기능 없음 |
| DOC-08, TEST-02, TEST-05, TEST-09 | 정확한 중앙 test_payload_examples scaffold·실제 HA entry/등록 action schema·production 준비 context/함수·기기 전송 없는 installed imagespec.validate/render 비교·각 예제 크기/색상, current/정확한 하한 실제 버전·pip check·명령/CI 결과, exact pin 재사용 근거·독립 adapter 리뷰 | N/A | imagespec dependency/import/예제 없음 |
| DOC-08, CI-05, CI-07, DEP-08 | 공용 Tests/updater의 standards-ref와 reusable full SHA 일치·caller checkout 보존·도구 별도 checkout·resolver 후 패키지 변경 없음·지원 최소 보존·미실행/skip/xfail/deselect를 PASS로 처리하지 않음 | N/A | imagespec 계약 미적용; 일반 Tests standards-ref는 reusable fullSHA와 일치 |
| DOC-07, HA-12 | 기기별 깨우기·인증·타 앱 연결·전송 제약, 실제 검증 경로와 미검증 범위, 공개 문제 로그 비식별화 | PASS | 구현·독립 별도 양환경 109passed/skip0 및 pipcheck, 최종 재인증·기존 월패드 유지·privacy 회귀 확인; 아래 실행 기록 참조 |
| HACS-04, REL-01, REL-02, REL-03, CI-11 | 통합 릴리스 시 같은 검증 commit/tag·manifest 버전·산출물·권한, 사용자 영향·지원 변경·제한 안내 | PASS | v1.0.1 정식 Release 발행(2026-10-22 14:12 KST), tag=04f23df/manifest.version1.0.1 일치. 같은 커밋 Tests/Validate 모두 성공. 기존 설정/지원 유지 및 재시작·재인증·실물 미검증을 릴리스 노트로 안내 |
| REL-04 | 이전/중단 시 README 상단 경로·유지보수 상태·재등록 여부, 자동 이전으로 오인하지 않는 안내 | N/A | 리포 이전/중단 없음 |
| REL-05 (권장) | 의존성/HA API 변경과 기능 변경 분리, 표준 변경은 명시적 채택 PR로 반영 | PASS | 표준 채택·발견 결함 수정만 수행, 기기 제어 기능/지원 최소 확장 없음 |

## 예외와 남은 작업

예외 원본은 `STANDARDS.md`입니다. 아래에 해당 위치를 연결하고, 예외가 실제 없음을 확인한 뒤에만 `없음`으로 바꿉니다.

| 규칙 ID | 예외 위치 / 이유 | 담당자 | 재검토 조건 |
|---|---|---|---|
| 없음 | 승인 예외 없음 | root | 기준/지원 변경 시 재검토 |

| 규칙 ID / TODO | 남은 작업 / issue·PR | 담당자 | 완료 근거 |
|---|---|---|---|
| 없음 | 적용 필수 미해결 항목·승인 예외 없음; 실물/HAUI는 미검증 범위 | root | 아래 PR·main 검증 및 release 증거 |

최종 검토 시 적용 대상 필수 `TODO`와 `EXCEPTION`, 이유가 있는 `N/A`, 권장 미채택을 구분해 적습니다. CI 성공만으로 실물 기기 검증을 주장하지 않습니다. 실물 검증을 수행했다면 모델·펌웨어·어댑터/proxy·연결 경로와 결과를 별도로 기록합니다.

중앙 보고는 [적용 현황표](https://github.com/eigger/hass-repo-standards/blob/0ec31111a81b0ee5702f1d8a17f03616a10a5db6/docs/adoption-status.md)의 자기 리포 행에 반영합니다. 리뷰 지적·수정·재검증 결과와 중앙 갱신 실패 사유가 있으면 남은 작업에도 기록합니다.

## 중앙 템플릿 검증

- `python -X utf8 ../hass-repo-standards/scripts/check_integration.py .`: root·독립 PASS (이번 작업 트리)
- 세 빈 init·정확한 루트 conftest·domain mock_config_entry/mock_client: 중앙 PASS; 기존60함수 모두 보존 AST 독립 확인; 실제 entry/platform 센서 로딩 검증
- 공통 fixture에서 오류 무시/전체 네트워크 허용 없음. loopback protocol 테스트 파일만 socket_enabled 및 allow_hosts127.0.0.1, 외부 통신 경계만 대체
- 양언어 본문 보존·의미 일치·기존 고지·배지 독립 리뷰 PASS, 원본 한국어 비공백 본문 모두 순서대로 보존
- 공용 CI 이름/파일/이벤트 중앙 검사 PASS, actionlint1.7.12 구현·독립 PASS; Ruff check/format 전체 PASS
- 승인 예외 없음 (.hass-standards.json.exceptions=[] / STANDARDS.md 일치)

## imagespec payload 예제 검증 환경

N/A — manifest requirements와 production import에 imagespec/blesession이 없으며 payload 렌더링·Bluetooth 기능을 제공하지 않습니다. 라이브러리 최소/current 별도 matrix와 updater도 해당 없음입니다.

## HA-02 제품 분류 검토 근거

| 항목 | 실제 판단 / 근거 |
|---|---|
| manifest integration_type | hub (기존 선언 보존) |
| categories (주 분류 먼저) | energy.meters_monitoring (주 분류 1개) |
| 주/보조 분류 선택 또는 제외 이유·출처 | 2026-10-22 root/docs/independent_review: 실제 월패드 세대 에너지 검침·평균·요금 조회 목적, 제어 미지원. README·coordinator/sensor/models 근거 |
| categories_review와 manifest의 값/순서/유형 일치 | manifest와 .hass-standards.json 값/순서/hub 유형 일치 |
| taxonomy snapshot·HACS warning/실패·실제 실행 결과 | 중앙 taxonomy snapshot Core ec18d8b25d1ee39aa8b85a72a170e42bee33228c; 오프라인 검사와 실제 원격 검증 결과를 별도 기록 |

## 로컬 실행 명령과 독립 검토

WSL Ubuntu에서 구현 환경 `/tmp/kocom-standards-current`, `/home/eigger/.cache/kocom-standards-min`과 별도 독립 환경 `/home/eigger/.cache/kocom-review-current`, `/home/eigger/.cache/kocom-review-min`을 사용했습니다. 각 환경은 대응 requirements를 resolver로 완전 설치했습니다.

```bash
python -m pytest tests/components/kocom_smarthome/ -q
python -m pip check
python -m ruff check .
python -m ruff format --check .
actionlint .github/workflows/tests.yml .github/workflows/validate.yml
PYTHONUTF8=1 python ../hass-repo-standards/scripts/check_integration.py .
PYTHONUTF8=1 python ../hass-repo-standards/scripts/sync_badges.py . --check
git diff --check
```

독립 리뷰에서 발견한 raw URL/응답/parse 예외/unknown energy 로그 노출을 sentinel 테스트와 함께 보완했습니다. 최소 HA의 인증 만료 시 UnknownStep을 실제 재인증으로 해결하고, branch Session과 wallpad Pair 식별자가 다를 수 있어 기존 Pair를 선택하도록 수정했습니다. 실패 후 credential 보존 및 재시도·다른 household 거부를 확인합니다. 로컬 Docker daemon 부재로 원격 HACS/Hassfest를 실행했으며 아래 PR 및 main에서 모두 성공했습니다.

## 원격 CI와 배포 증거

- [PR #2](https://github.com/eigger/hass-kocom-smarthome/pull/2): 구현 `0223c24ac5b04506bb55d58cb00955498d41435c`, [Tests](https://github.com/eigger/hass-kocom-smarthome/actions/runs/39726142648) 및 [Validate](https://github.com/eigger/hass-kocom-smarthome/actions/runs/39726142632) 모든 7 checks 성공. independent_review가 실제 로그를 독립 확인.
- main / release `04f23dfb6fe09b0dc673a97b38a9065a4dc47930`: [Tests](https://github.com/eigger/hass-kocom-smarthome/actions/runs/39726537100) 및 [Validate](https://github.com/eigger/hass-kocom-smarthome/actions/runs/39726537086) 모든 7 checks 독립 성공 확인. PR 구현과 트리 동일.
- 원격 current: Python3.14.8 / HA2026.10.2 / plugin0.13.373 / pycares5.2.1, 109passed/skip0, pipcheck 성공.
- 원격 minimum: Python3.13.16 / HA2025.8.0 / plugin0.13.269 / pycares4.11.0, 109passed/skip0, pipcheck 성공.
- HACS는 brands/categories 포함 All10checks passed, Hassfest는 검토한 공식 Core source/Dockerfile의 전체 validator로 Integrations1/Invalid0. 설치/빌드만의 성공으로 대체하지 않음.
- [정식 v1.0.1](https://github.com/eigger/hass-kocom-smarthome/releases/tag/v1.0.1): GitHub API로 draft=false/prerelease=false, tag commit04f23df와 해당 tag manifest.version1.0.1을 재확인.
- [중앙 현황표](https://github.com/eigger/hass-repo-standards/blob/main/docs/adoption-status.md)의 이 리포 행에 마감 기록. 중앙의 다른 리포 행과 기존 로컬 수정은 보존.
- 이 마감 문서는 검증·배포 증거만 갱신하며 배포된 production/test/workflow 파일을 변경하지 않습니다. 실물 월패드·단지 서버·HA UI 검증은 수행하지 않았습니다.


## 2026-10-23 HACS ZIP and Downloads (scoped)

- Target base: `8c62d619cc84bb7b2b3f262eeb207d37b1947564`; reviewed release central: `fd4162c0b93fbe8e109f99c787773ae09ba157e1`.
- Scope: HACS-04/CI-11 release ZIP and DOC-03/05 Downloads replacing Analytics Usage. No release is created during this update.
- Local scoped validation: PASS — canonical badge check, no Analytics Usage, release metadata/caller contract, actionlint 1.7.12, native git diff --check, unchanged tracked integration/manifest/dependencies/tests.
- Actual archive build: PASS at `f1776395f91a5382d0f72a5d40514ad3dbeca847`; `kocom_smarthome.zip`, 18 files, SHA256 `5da0c078a40afe0d4056645e7ae9342b9e2d2f925c28e5dae4c4440ebf063a32`. All archive members matched checkout bytes; manifest.json and __init__.py are at ZIP root. Final documentation-only follow-up preserves this integration tree. Windows Python 3.14.6; validation WSL Python 3.14.4/PyYAML 6.0.3/packaging 26.0.
- Full central integration checker: PASS.
- Existing CI workflows are preserved, except hass-kocom-smarthome where matching reviewed central references are synchronized. Existing support minimum and prior exceptions remain.
- Independent review and remote CI: tracked in this branch's pull request; merge requires resolved actionable findings and successful applicable checks. No real release upload, device or new real HA runtime validation is claimed by these local packaging checks.


## 2026-10-25 중앙 검사기 부분 갱신 검증

- 검토한 중앙 SHA: `1863343638014adb8a4001afc8fddc1a27dc500f`; 적용 시작 커밋: `0af1904872a7f58e39a6a5616de41847c006071b`.
- 범위: 중앙 pin·standards-ref·검토 기준 기록 정합화. HA 구현·요구 버전은 유지합니다.
- 로컬: Python 3.14.5 / PyYAML 6.0.3, `python scripts/check_integration.py <target>` (검토한 중앙 source에서 실행): PASS.
- actionlint: PASS. PR CI·독립 리뷰 결과는 PR 링크와 check 결과를 확인합니다. 이 로컬 결과만으로 전체 채택 완료를 주장하지 않습니다.
- 독립 리뷰: 별도 review_checker_rollout 담당자가 19개 리포의 workflow 69개·기존 job 100개를 구조 비교했습니다. 새 CI 회귀 지적 없음. 기존 job ID·입력·권한·지원 최소와 통합 코드 보존 및 새 standards job의 중앙 템플릿 일치 확인. 실행 변경 없는 이 기록 추가 전 작업 트리를 검토했습니다.
