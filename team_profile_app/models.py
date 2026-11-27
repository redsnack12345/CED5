"""
[models.py]
사용자 프로필 및 시간표 관련 데이터 모델 정의 모듈

이 모듈은 데이터의 형태(구조)를 정의합니다.
팀원들과 데이터를 주고받을 때 이 규격을 공유하면 쉽게 연동할 수 있습니다.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
from datetime import datetime


@dataclass
class TimeSlot:
    """
    30분 단위의 시간 슬롯을 나타내는 모델
    예: code="a1", start_time="09:00", end_time="09:30"
    """
    code: str        # 슬롯 코드 (예: a1, b1, a2, b2, ... a9, b9)
    start_time: str  # 시작 시간 (예: "09:00")
    end_time: str    # 종료 시간 (예: "09:30")

    @property
    def label(self) -> str:
        """UI에 표시하기 좋은 형태의 문자열 반환 (예: '[a1] 09:00 ~ 09:30')"""
        return f"[{self.code}] {self.start_time} ~ {self.end_time}"

    def to_dict(self) -> Dict[str, str]:
        return {
            "code": self.code,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "label": self.label
        }


@dataclass
class ScheduleData:
    """
    사용자의 시간표 데이터를 담는 모델
    - all_slots: 9:00 ~ 18:00까지의 전체 18개 슬롯
    - selected_slot_codes: 사용자가 선택한 슬롯 코드 리스트 (예: ["a1", "b1", "a3"])
    """
    all_slots: List[TimeSlot] = field(default_factory=list)
    selected_slot_codes: List[str] = field(default_factory=list)

    @property
    def selected_slots(self) -> List[TimeSlot]:
        """선택된 슬롯 코드에 해당하는 TimeSlot 객체 목록 반환"""
        selected_set = set(self.selected_slot_codes)
        return [slot for slot in self.all_slots if slot.code in selected_set]

    @property
    def selected_summary(self) -> str:
        """선택된 시간대를 사람이 읽기 쉽게 요약한 문자열"""
        if not self.selected_slot_codes:
            return "선택된 시간 없음"
        return ", ".join(f"{s.code}({s.start_time}~{s.end_time})" for s in self.selected_slots)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "selected_slot_codes": self.selected_slot_codes,
            "selected_summary": self.selected_summary,
            "all_slots": [slot.to_dict() for slot in self.all_slots]
        }


@dataclass
class PreferenceData:
    """
    사용자가 선택한 선호도 데이터 (1점 ~ 5점)
    - people_preference: 정한 시간에 함께 보낼 인원에 대한 선호도 (1~5점)
    - activity_preference: 정한 시간에 할 활동에 대한 선호도 (1~5점)
    """
    people_preference: int = 3    # 기본값 3점 (1 ~ 5)
    activity_preference: int = 3  # 기본값 3점 (1 ~ 5)

    def to_dict(self) -> Dict[str, int]:
        return {
            "people_preference": self.people_preference,
            "activity_preference": self.activity_preference
        }


@dataclass
class UserProfile:
    """
    사용자 전체 프로필 정보 모델
    기본 인적사항 + 시간표 + 선호도 정보를 모두 포함합니다.
    """
    user_id: str                   # 고유 식별자 (예: 학번, 아이디, UUID 등)
    name: str                      # 사용자 이름
    department: str                # 학과
    hobby: str                     # 취미
    schedule: ScheduleData         # 시간표 정보
    preference: PreferenceData     # 선호도 정보
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def to_dict(self) -> Dict[str, Any]:
        """팀원들이 JSON이나 딕셔너리로 쉽게 변환할 수 있도록 제공하는 메서드"""
        return {
            "user_id": self.user_id,
            "name": self.name,
            "department": self.department,
            "hobby": self.hobby,
            "schedule": self.schedule.to_dict(),
            "preference": self.preference.to_dict(),
            "created_at": self.created_at
        }
