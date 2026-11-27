"""
[service.py]
비즈니스 로직 및 서비스 레이어 모듈

요구사항:
1. 9시부터 18시까지 30분 단위 시간표 생성 (a1, b1, a2, b2, ..., a9, b9 문자열)
2. 사용자가 선택한 시간표 검증 및 데이터베이스 전송
3. 인원 선호도(1~5점) 및 활동 선호도(1~5점) 수치 데이터 처리
4. 사용자 이름, 학과, 취미 입력 처리 및 DB 저장
"""

from typing import List, Tuple, Optional
import uuid
from models import TimeSlot, ScheduleData, PreferenceData, UserProfile
from database import BaseScheduleDatabase, BaseUserDatabase


class ScheduleService:
    """
    시간표 생성 및 시간표 관련 연산을 담당하는 서비스 클래스
    """

    @staticmethod
    def generate_default_time_slots() -> List[TimeSlot]:
        """
        [요구사항 1] 
        9시부터 18시까지 30분 단위로 a1, b1, a2, b2... 규칙의 슬롯 리스트 생성
        
        규칙:
        - 시작 시간: 09:00, 종료 시간: 18:00 (총 9시간 = 18개 30분 슬롯)
        - 시간대(index=1~9):
          - 9시 (index 1) : 09:00~09:30 -> 'a1', 09:30~10:00 -> 'b1'
          - 10시(index 2) : 10:00~10:30 -> 'a2', 10:30~11:00 -> 'b2'
          - ...
          - 17시(index 9) : 17:00~17:30 -> 'a9', 17:30~18:00 -> 'b9'
        """
        slots: List[TimeSlot] = []
        start_hour = 9
        end_hour = 18

        for hour in range(start_hour, end_hour):
            index_num = hour - start_hour + 1  # 1부터 9까지
            
            # 앞 30분 (예: 09:00 ~ 09:30 => a1)
            slot_a_code = f"a{index_num}"
            start_a = f"{hour:02d}:00"
            end_a = f"{hour:02d}:30"
            slots.append(TimeSlot(code=slot_a_code, start_time=start_a, end_time=end_a))

            # 뒤 30분 (예: 09:30 ~ 10:00 => b1)
            slot_b_code = f"b{index_num}"
            start_b = f"{hour:02d}:30"
            end_b = f"{hour + 1:02d}:00"
            slots.append(TimeSlot(code=slot_b_code, start_time=start_b, end_time=end_b))

        return slots

    @classmethod
    def create_schedule_data(cls, selected_slot_codes: List[str]) -> ScheduleData:
        """
        선택된 슬롯 코드 목록을 받아 전체 슬롯과 매핑된 ScheduleData 객체 생성
        """
        all_slots = cls.generate_default_time_slots()
        return ScheduleData(all_slots=all_slots, selected_slot_codes=selected_slot_codes)


class ProfileService:
    """
    사용자 프로필 생성, 검증, DB 저장을 총괄하는 서비스 클래스
    팀 프로젝트에서 다른 팀원이 이 서비스를 호출해 사용하기 매우 좋습니다.
    """

    def __init__(self, schedule_db: BaseScheduleDatabase, user_db: BaseUserDatabase):
        # 의존성 주입(Dependency Injection): 팀원이 만든 실제 DB로 쉽게 교체 가능
        self.schedule_db = schedule_db
        self.user_db = user_db

    def register_profile(
        self,
        name: str,
        department: str,
        hobby: str,
        selected_slot_codes: List[str],
        people_preference: int,
        activity_preference: int,
        user_id: Optional[str] = None
    ) -> Tuple[bool, str, Optional[UserProfile]]:
        """
        [통합 등록 함수]
        사용자 프로필 정보와 시간표, 선호도를 받아 유효성 검사 후 각 데이터베이스로 전송합니다.

        반환값:
            (성공여부: bool, 결과메시지: str, 생성된 UserProfile 객체: Optional[UserProfile])
        """
        # 1. 유효성 검증
        if not name.strip():
            return False, "이름을 입력해주세요.", None
        if not department.strip():
            return False, "학과를 입력해주세요.", None
        if not hobby.strip():
            return False, "취미를 입력해주세요.", None
        
        # 선호도 수치 검증 (1 ~ 5)
        if not (1 <= people_preference <= 5):
            return False, "인원 선호도는 1점에서 5점 사이여야 합니다.", None
        if not (1 <= activity_preference <= 5):
            return False, "활동 선호도는 1점에서 5점 사이여야 합니다.", None

        # 사용자 식별자 생성 (전달받지 않은 경우 자동 생성)
        if not user_id:
            user_id = f"user_{name}_{uuid.uuid4().hex[:6]}"

        # 2. 모델 객체 생성
        # [요구사항 1, 2] 시간표 생성 및 사용자가 선택한 시간 처리
        schedule_data = ScheduleService.create_schedule_data(selected_slot_codes)

        # [요구사항 3, 4] 인원 선호도 및 활동 선호도 처리 (1~5점)
        preference_data = PreferenceData(
            people_preference=people_preference,
            activity_preference=activity_preference
        )

        # [요구사항 5] 이름, 학과, 취미를 포함한 전체 프로필 생성
        user_profile = UserProfile(
            user_id=user_id,
            name=name.strip(),
            department=department.strip(),
            hobby=hobby.strip(),
            schedule=schedule_data,
            preference=preference_data
        )

        # 3. 데이터베이스 전송
        try:
            # [요구사항 2] 시간표 데이터베이스로 전송
            self.schedule_db.save_schedule(user_id, schedule_data)

            # [요구사항 5] 사용자 프로필 데이터베이스로 전송
            self.user_db.save_user_profile(user_profile)

            return True, "성공적으로 프로필과 시간표가 저장되었습니다.", user_profile
        except Exception as e:
            return False, f"데이터베이스 저장 중 오류 발생: {str(e)}", None
