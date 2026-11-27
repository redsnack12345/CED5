# 👥 사용자 프로필 및 시간표 작성 모듈 (팀 프로젝트용)

이 프로젝트는 팀 프로젝트 중 **"사용자 프로필 작성 및 시간표/선호도 등록"** 파트 구현 결과물입니다.  
다른 팀원이 작성한 코드(예: 다른 페이지 UI, 백엔드 서버, 메인 네비게이션, 매칭 알고리즘 등)와 쉽게 합칠 수 있도록 **계층형 구조(MVC 패턴)**로 깔끔하게 모듈화되어 있으며, 각 기능마다 친절한 한글 주석이 포함되어 있습니다.

---

## 📌 구현된 요구사항 매핑

| 요구사항 번호 | 요구사항 내용 | 구현 위치 |
| :--- | :--- | :--- |
| **요구사항 1** | 9시~18시 30분 단위 시간표 생성 (`a1, b1, a2, b2, ... a9, b9`) | `service.py` (`ScheduleService.generate_default_time_slots()`) |
| **요구사항 2** | 선택한 시간을 UI에 실시간 표시 & 전체 시간표/선택 시간을 '시간표 DB'로 전송 | `ui_tkinter.py` (토글 버튼 및 표시 라벨) & `database.py` (`save_schedule`) |
| **요구사항 3** | 정한 시간에 함께 보낼 **인원 선호도(1~5점)** 입력 | `ui_tkinter.py` (인원 선호도 라디오 버튼) & `models.py` |
| **요구사항 4** | 정한 시간에 할 **활동 선호도(1~5점)** 입력 | `ui_tkinter.py` (활동 선호도 라디오 버튼) & `models.py` |
| **요구사항 5** | **이름, 학과, 취미** 입력 받아 DB 저장 및 프로필 UI 카드 반환 | `service.py` & `ui_tkinter.py` (`render_user_profile_card`) |
| **요구사항 6** | 팀 프로젝트 통합을 위한 모듈화 & 친절한 주석 | 전체 소스코드 주석 및 인터페이스 기반 분리 |

---

## 📁 파일 구조 및 역할

```text
team_profile_app/
├── models.py                 # 데이터 모델 정의 (TimeSlot, ScheduleData, PreferenceData, UserProfile)
├── database.py               # DB 인터페이스 (BaseScheduleDatabase, BaseUserDatabase) 및 JSON/메모리 구현체
├── service.py                # 비즈니스 로직 (30분 단위 슬롯 생성 알고리즘, 유효성 검사, DB 전송 로직)
├── ui_tkinter.py             # Tkinter GUI 화면 (시간표 그리드 토글, 입력 폼, 실시간 표시, 프로필 카드 뷰)
├── main.py                   # 애플리케이션 실행 메인 파일
├── standalone_profile_app.py # 팀원 공유용 올인원(단일 파일) 버전
├── test_service.py           # 기능 검증용 단위 테스트 스크립트
└── README.md                 # 본 가이드 문서
```

---

## 🚀 실행 방법

### 1) 모듈형 실행 (추천)
```bash
python main.py
```

### 2) 단일 파일 실행 (팀원에게 파일 하나만 넘겨주고 싶을 때)
```bash
python standalone_profile_app.py
```

### 3) 단위 테스트 실행
```bash
python test_service.py
```

---

## 🤝 팀원들과 합칠 때 (협업 가이드)

### 1. 데이터베이스(DB) 담당자와 합칠 때
`database.py` 파일의 추상 클래스(`BaseScheduleDatabase`, `BaseUserDatabase`)를 상속받아 팀원의 실제 DB(MySQL, SQLite, MongoDB, Firebase 등) 로직을 채워 넣으면 됩니다.
```python
from database import BaseScheduleDatabase, BaseUserDatabase

class MyTeamMySQLScheduleDB(BaseScheduleDatabase):
    def save_schedule(self, user_id: str, schedule_data: ScheduleData) -> bool:
        # 팀원의 MySQL INSERT 쿼리 작성
        # schedule_data.selected_slot_codes: ['a1', 'b1' ...]
        # schedule_data.to_dict() 로 직렬화 가능
        return True
```
그 후 `main.py`에서 `ProfileService(schedule_db=MyTeamMySQLScheduleDB(), ...)`로 주입하기만 하면 기존 UI나 로직을 전혀 수정하지 않고 바로 연동됩니다!

### 2. UI 담당자 또는 웹 프레임워크(Flask/FastAPI/Streamlit/PyQt)와 합칠 때
UI가 Tkinter가 아닌 웹이나 다른 GUI로 결정되더라도, `service.py`의 `ProfileService`와 `ScheduleService`는 UI와 완전히 분리되어 있으므로 그대로 재사용할 수 있습니다.
```python
from service import ProfileService, ScheduleService

# 웹 API 엔드포인트 예시 (FastAPI / Flask)
@app.post("/api/profile")
def create_profile(req: ProfileRequest):
    success, msg, profile = profile_service.register_profile(
        name=req.name,
        department=req.department,
        hobby=req.hobby,
        selected_slot_codes=req.slots,
        people_preference=req.people_pref,
        activity_preference=req.activity_pref
    )
    return profile.to_dict()
```
