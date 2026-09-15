# 2026 가을 대동제 백엔드

동국대학교 2026 가을 대동제 축제 사이트의 백엔드 저장소입니다.

현재 저장소는 팀 개발을 위한 **Django REST Framework 기본 골격**만 제공합니다.

도메인 모델, 마이그레이션, 실제 API는 기능 정책과 API 명세가 확정된 뒤 각 담당자가 구현합니다.

## 기술 스택

- Python 3.11+
- Django 5.2 LTS
- Django REST Framework
- PostgreSQL (운영)
- SQLite (로컬 개발 및 테스트 기본값)
- Gunicorn (운영 WSGI 서버)
- drf-spectacular (OpenAPI 문서)
- pytest / pytest-django
- Ruff

## 프로젝트 구조

```text
.
├── api/
│   ├── health.py               # 서버 상태 확인
│   └── v1/urls.py              # v1 API 라우팅 진입점
├── apps/
│   ├── accounts/               # 카카오 사용자 인증
│   ├── admins/                 # 서비스 관리자 인증·권한
│   ├── booths/                 # 부스 식별, 지도 조회, 등불 집계
│   ├── lanterns/               # 등불 등록·조회·수정·삭제·신고
│   ├── coupons/                # 쿠폰 발급·추첨·스크래치·사용
│   ├── notices/                # 공지사항
│   ├── lost_items/             # 분실물·이미지·해시태그
│   └── performances/           # 공연·셋리스트
├── common/                     # 공통 예외·권한·응답·검증 기반
├── config/
│   ├── settings/               # 환경별 Django 설정
│   ├── urls.py                 # 루트 URL
│   ├── asgi.py
│   └── wsgi.py
├── deploy/                     # 서버·배포 관련 문서 및 설정
├── docs/                       # API 계약과 기술 결정 기록
├── tests/                      # 프로젝트 단위 통합 테스트
├── manage.py
├── pyproject.toml
└── .env.example
```

각 도메인 앱은 다음 책임을 기준으로 구성합니다.

```text
apps/<domain>/
├── migrations/     # Django 마이그레이션
├── tests/          # 도메인 단위 테스트
├── models.py       # 데이터 모델
├── serializers.py  # 요청·응답 스키마
├── selectors.py    # 조회 로직
├── services.py     # 생성·수정·삭제 및 트랜잭션 로직
├── views.py        # HTTP 요청 처리
└── urls.py         # 도메인 URL
```

### 구조 원칙

- 담당자 이름이 아니라 **도메인 기준**으로 코드를 나눕니다.
- 조회 로직은 `selectors.py`, 상태를 변경하는 로직은 `services.py`에 둡니다.
- 등불 생성·삭제와 부스 집계, 쿠폰 발급처럼 함께 성공해야 하는 변경은 하나의 DB 트랜잭션으로 처리합니다.
- 사용자용 API와 관리자용 API가 같은 데이터를 다루더라도 권한과 URL을 분리합니다.
- 공통 코드로 승격하기 전에는 각 도메인 안에 코드를 둡니다.
- `common/`이 특정 도메인의 비즈니스 로직을 소유하지 않도록 합니다.

## 담당 도메인

| 도메인 | 주요 범위 | 담당 |
| --- | --- | --- |
| 관리자 | 관리자 인증, 등불·공지 관리 | 희수 |
| 관리자 분실물·공연 | 분실물 CRUD, 공연 조회 | 수아 |
| 지도·부스 | 지도 및 부스 관련 조회 | 세호 |
| 등불 | 등불 등록·조회·수정·삭제·신고 | 준호 |
| 쿠폰 발급 | 쿠폰 발급·추첨 | 교현 |
| 쿠폰 사용 | 쿠폰 조회·스크래치·소비 | 예진 |
| 안내 | 사용자 공지·분실물 조회 | 수연 |
| 로그인 | 카카오 로그인·로그아웃 | 은서 |

담당 범위가 변경되더라도 폴더는 사람별로 재구성하지 않고 도메인 구조를 유지합니다.

## 로컬 실행

### 1. 가상환경 생성

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS/Linux에서는 다음 명령을 사용합니다.

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. 패키지 설치

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

### 3. 환경변수 준비

```powershell
Copy-Item .env.example .env
```

macOS/Linux에서는 다음 명령을 사용합니다.

```bash
cp .env.example .env
```

`.env`에는 로컬 값과 비밀값을 넣고 Git에 커밋하지 않습니다. 공유가 필요한 키 이름만 `.env.example`에 추가합니다.

### 4. 서버 실행

```bash
python manage.py check
python manage.py migrate
python manage.py runserver
```

기본 확인 주소:

- Health check: `GET /api/health/`
- OpenAPI schema: `GET /api/schema/`
- Swagger UI: `GET /api/docs/`

## 테스트와 정적 검사

```bash
pytest
ruff check .
ruff format --check .
```

자동 수정이 필요할 때만 아래 명령을 실행합니다.

```bash
ruff check . --fix
ruff format .
```

## Git 협업 방식

이 저장소는 개인 포크에서 작업한 뒤 단체 저장소로 Pull Request를 보내는 방식을 사용합니다.

- `origin`: 본인의 개인 포크
- `upstream`: `LikeLion-at-DGU/2026_fall_festival_back`
- `main`: 배포 가능한 안정 버전을 관리하는 브랜치
- `develop`: 기능을 통합하는 기본 개발 브랜치이자 일반 PR의 대상 브랜치
- PR base: `upstream/develop`
- PR head: `origin`의 작업 브랜치
- `upstream/main`과 `upstream/develop`에 직접 push하지 않습니다.
- 기능이 충분히 통합되고 배포 준비가 끝나면 `develop`에서 `main`으로 별도 PR을 생성합니다.

전체 흐름은 다음과 같습니다.

```text
개인 작업 브랜치 -> 중앙 저장소 develop -> 중앙 저장소 main
```

### 1. 최초 한 번 개인 develop 준비

```bash
git fetch upstream
git switch -c develop upstream/develop
git push -u origin develop
```

이미 로컬에 `develop` 브랜치가 있다면 새로 만들지 않고 해당 브랜치로 이동합니다.

### 2. 작업 전 개인 develop 동기화

```bash
git switch develop
git fetch upstream
git merge --ff-only upstream/develop
git push origin develop
```

### 3. Issue 생성 후 작업 브랜치 생성

```bash
git switch -c feat/12-lantern-create
```

브랜치 형식은 `<작업유형>/<이슈번호>-<기능명>`을 사용합니다.

| 작업 유형 | 용도 |
| --- | --- |
| `feat` | 새로운 기능 |
| `fix` | 버그 수정 |
| `refactor` | 기능 변화 없는 구조 개선 |
| `test` | 테스트 추가·수정 |
| `docs` | 문서 변경 |
| `chore` | 설정·의존성·개발환경 변경 |

작업 브랜치는 최신 `develop`에서 생성합니다. 개인 포크 안에서 브랜치를 어떻게 관리할지는 자유지만, 하나의 브랜치에는 하나의 Issue에 해당하는 작업만 담는 것을 권장합니다.

### 4. 커밋과 개인 포크 push

```bash
git add <변경한 파일>
git commit -m "feat: 등불 등록 API 구현 (#12)"
git push -u origin feat/12-lantern-create
```

커밋 형식은 `<작업유형>: <변경 내용> (#이슈번호)`를 권장합니다.

### 5. Pull Request

GitHub에서 다음 방향으로 PR을 생성합니다.

```text
개인 포크의 작업 브랜치 -> LikeLion-at-DGU/2026_fall_festival_back의 develop
```

PR에는 아래 내용을 포함합니다.

- 작업 요약
- 관련 Issue (`Closes #12`)
- API 계약 변경 여부
- 테스트 방법과 결과
- 새로운 환경변수나 마이그레이션 여부

승인 담당 팀원(조수아, 장진호, 이희수, 이승우 중 2명)에게 리뷰받고, 리뷰가 끝난 뒤 머지합니다. 충돌은 본인의 작업 브랜치에 최신 `upstream/develop`을 반영해 해결한 후 PR을 갱신합니다.

### 6. main 반영

`develop`에 기능이 충분히 쌓이고 테스트가 완료되면 `develop`에서 `main`으로 별도 PR을 생성합니다. `main`에는 개별 기능 브랜치를 바로 머지하지 않습니다.

## 환경변수

| 이름 | 설명 |
| --- | --- |
| `DJANGO_SETTINGS_MODULE` | 사용할 설정 모듈 |
| `DJANGO_SECRET_KEY` | Django 비밀키 |
| `DJANGO_DEBUG` | 디버그 모드 |
| `DJANGO_ALLOWED_HOSTS` | 허용 호스트 목록 |
| `CORS_ALLOWED_ORIGINS` | 허용 프론트엔드 Origin 목록 |
| `DATABASE_URL` | 운영 PostgreSQL 연결 문자열 |
| `KAKAO_REST_API_KEY` | 카카오 REST API 키 |
| `KAKAO_REDIRECT_URI` | 카카오 로그인 Redirect URI |

## 현재 확정된 주요 정책

- 축제 기간은 `2026-09-29`, `2026-09-30`, `2026-10-01`입니다.
- 등불은 사용자당 하루 최대 3개이며 미사용 횟수는 이월되지 않습니다.
- 등불을 삭제해도 일일 작성 횟수는 복구되지 않습니다.
- 삭제된 등불은 집계에서는 제외하지만 작성자의 내역에는 삭제 상태로 남깁니다.
- 당일 첫 등불 등록 시에만 쿠폰을 1개 발급합니다.
- 등불을 삭제해도 이미 발급된 쿠폰은 회수하지 않습니다.
- 장소 최근 검색어는 서버가 아닌 프론트엔드 로컬스토리지에서 관리합니다.
- 모든 삭제 정책은 확정 전까지 ERD의 Soft Delete 원칙을 따릅니다.

## 구현 전 확인이 필요한 정책

아래 항목은 관련 문서의 내용이 다르거나 최종 결정이 필요하므로, 모델과 API를 구현하기 전에 팀에서 확인해야 합니다.

- 부스·협업·배너·개발진 데이터의 프론트 정적 관리 범위
- 사용자당 같은 부스에 등불을 등록할 수 있는 횟수와 DB 제약조건
- 쿠폰 확인 코드가 상품별인지 부스별인지 여부
- 관리자 인증 방식과 토큰 만료 정책
- 부스 등불 수 집계를 DB에서 처리할지 Redis를 사용할지 여부

결정된 내용은 `docs/decisions/`에 기록하고 관련 API 명세와 ERD를 함께 갱신합니다.

## 문서

- [기능 명세서](https://app.notion.com/p/3da70852f3ab80e3a5b2d1bce291b414)
- [백엔드 역할 배분](https://app.notion.com/p/3da70852f3ab8046b10acee0c1c683fd)
- [Figma](https://www.figma.com/design/Zey36rBJUx84YqwX20b2ot/%EC%B6%95%EC%A0%9C%EC%82%AC%EC%9D%B4%ED%8A%B8?node-id=416-3472)
