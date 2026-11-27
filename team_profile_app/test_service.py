"""
[test_service.py]
비즈니스 로직 및 DB 연동 단위 테스트
"""

from service import ScheduleService, ProfileService
from database import InMemoryScheduleDatabase, InMemoryUserDatabase, JSONScheduleDatabase, JSONUserDatabase


def test_time_slot_generation():
    print(">>> 1. 시간표 슬롯 생성 테스트 (9:00 ~ 18:00, 30분 단위)")
    slots = ScheduleService.generate_default_time_slots()
    assert len(slots) == 18, f"총 18개 슬롯이어야 합니다. 현재: {len(slots)}"
    
    # 시작과 끝 검증
    assert slots[0].code == "a1" and slots[0].start_time == "09:00" and slots[0].end_time == "09:30"
    assert slots[1].code == "b1" and slots[1].start_time == "09:30" and slots[1].end_time == "10:00"
    assert slots[2].code == "a2" and slots[2].start_time == "10:00" and slots[2].end_time == "10:30"
    assert slots[-2].code == "a9" and slots[-2].start_time == "17:00" and slots[-2].end_time == "17:30"
    assert slots[-1].code == "b9" and slots[-1].start_time == "17:30" and slots[-1].end_time == "18:00"

    print("생성된 슬롯 목록:")
    print([s.code for s in slots])
    print("✅ 시간표 슬롯 생성 테스트 통과!")


def test_profile_registration():
    print("\n>>> 2. 프로필 등록 및 DB 전송 테스트")
    schedule_db = InMemoryScheduleDatabase()
    user_db = InMemoryUserDatabase()
    service = ProfileService(schedule_db, user_db)

    # 샘플 데이터로 등록
    success, msg, profile = service.register_profile(
        name="김철수",
        department="소프트웨어학과",
        hobby="알고리즘 문제 풀이, 농구",
        selected_slot_codes=["a1", "b1", "a3"],  # 9:00~10:00, 11:00~11:30
        people_preference=4,
        activity_preference=5
    )

    assert success is True, f"등록 실패: {msg}"
    assert profile is not None
    assert profile.name == "김철수"
    assert profile.department == "소프트웨어학과"
    assert profile.preference.people_preference == 4
    assert profile.preference.activity_preference == 5
    assert len(profile.schedule.selected_slots) == 3
    print("선택된 시간 요약:", profile.schedule.selected_summary)

    # DB에 잘 들어갔는지 검증
    saved_schedule = schedule_db.get_schedule(profile.user_id)
    assert saved_schedule is not None
    assert saved_schedule["selected_slot_codes"] == ["a1", "b1", "a3"]

    saved_user = user_db.get_user_profile(profile.user_id)
    assert saved_user is not None
    assert saved_user.name == "김철수"

    print("✅ 프로필 등록 및 DB 전송 테스트 통과!")


def test_json_database():
    print("\n>>> 3. JSON 파일 DB 영구 저장 테스트")
    s_db = JSONScheduleDatabase("test_schedule.json")
    u_db = JSONUserDatabase("test_user.json")
    service = ProfileService(s_db, u_db)

    success, msg, profile = service.register_profile(
        name="이영희",
        department="데이터사이언스학과",
        hobby="음악 감상",
        selected_slot_codes=["b2", "a4"],
        people_preference=2,
        activity_preference=3
    )

    assert success is True
    print("✅ JSON 영구 저장 테스트 통과!")


if __name__ == "__main__":
    test_time_slot_generation()
    test_profile_registration()
    test_json_database()
    print("\n🎉 모든 단위 테스트를 성공적으로 통과했습니다!")
