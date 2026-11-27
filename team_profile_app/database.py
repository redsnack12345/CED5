"""
[database.py]
데이터베이스 처리 모듈

팀 프로젝트에서 데이터베이스 담당자가 실제 DB(MySQL, SQLite, MongoDB 등)로
연결할 때 이 모듈의 클래스를 교체하거나 상속하여 구현하면 됩니다.
인터페이스(추상 클래스)를 분리해두었기 때문에 팀원들이 쉽게 코드를 합칠 수 있습니다.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import json
import os
from models import ScheduleData, UserProfile


# ==============================================================================
# 1. 시간표 데이터베이스 인터페이스 (추상 클래스)
# ==============================================================================
class BaseScheduleDatabase(ABC):
    """
    시간표 데이터베이스 접근 인터페이스
    팀원이 실제 DB로 바꿀 때 이 메서드 규격만 맞추면 UI나 서비스 로직을 고칠 필요가 없습니다.
    """

    @abstractmethod
    def save_schedule(self, user_id: str, schedule_data: ScheduleData) -> bool:
        """사용자의 시간표 데이터를 저장/전송"""
        pass

    @abstractmethod
    def get_schedule(self, user_id: str) -> Optional[ScheduleData]:
        """사용자의 시간표 데이터 조회"""
        pass


# ==============================================================================
# 2. 사용자 프로필 데이터베이스 인터페이스 (추상 클래스)
# ==============================================================================
class BaseUserDatabase(ABC):
    """
    사용자 기본 정보(이름, 학과, 취미 등) 데이터베이스 접근 인터페이스
    """

    @abstractmethod
    def save_user_profile(self, user_profile: UserProfile) -> bool:
        """사용자 프로필 저장"""
        pass

    @abstractmethod
    def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """사용자 프로필 조회"""
        pass

    @abstractmethod
    def list_all_users(self) -> List[UserProfile]:
        """전체 사용자 목록 조회"""
        pass


# ==============================================================================
# 3. [구현체] 메모리 기반 데이터베이스 (개발 및 테스트용 Mock DB)
#    - 별도의 DB 서버 없이 메모리(Dictionary)에 저장합니다.
# ==============================================================================
class InMemoryScheduleDatabase(BaseScheduleDatabase):
    """메모리에 시간표를 저장하는 임시 DB"""
    def __init__(self):
        self._db: Dict[str, Dict[str, Any]] = {}

    def save_schedule(self, user_id: str, schedule_data: ScheduleData) -> bool:
        # 시간표 데이터베이스로 전송 및 저장
        self._db[user_id] = schedule_data.to_dict()
        print(f"[시간표 DB 전송 완료] 유저 ID: {user_id}, 선택 슬롯: {schedule_data.selected_slot_codes}")
        return True

    def get_schedule(self, user_id: str) -> Optional[Dict[str, Any]]:
        return self._db.get(user_id)


class InMemoryUserDatabase(BaseUserDatabase):
    """메모리에 사용자 프로필을 저장하는 임시 DB"""
    def __init__(self):
        self._db: Dict[str, UserProfile] = {}

    def save_user_profile(self, user_profile: UserProfile) -> bool:
        self._db[user_profile.user_id] = user_profile
        print(f"[사용자 프로필 DB 저장 완료] 이름: {user_profile.name}, 학과: {user_profile.department}")
        return True

    def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        return self._db.get(user_id)

    def list_all_users(self) -> List[UserProfile]:
        return list(self._db.values())


# ==============================================================================
# 4. [구현체] JSON 파일 기반 데이터베이스 (영구 보관용)
#    - 프로그램을 껐다 켜도 데이터가 로컬 JSON 파일에 남아있어 팀 시연 시 유용합니다.
# ==============================================================================
class JSONScheduleDatabase(BaseScheduleDatabase):
    """JSON 파일에 시간표 데이터를 저장하는 DB"""
    def __init__(self, filepath: str = "schedule_database.json"):
        self.filepath = filepath
        if not os.path.exists(self.filepath):
            self._save_file({})

    def _load_file(self) -> Dict[str, Any]:
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_file(self, data: Dict[str, Any]):
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def save_schedule(self, user_id: str, schedule_data: ScheduleData) -> bool:
        data = self._load_file()
        data[user_id] = schedule_data.to_dict()
        self._save_file(data)
        print(f"[JSON 시간표 DB] '{self.filepath}'에 저장되었습니다. (User: {user_id})")
        return True

    def get_schedule(self, user_id: str) -> Optional[Dict[str, Any]]:
        data = self._load_file()
        return data.get(user_id)


class JSONUserDatabase(BaseUserDatabase):
    """JSON 파일에 사용자 프로필 데이터를 저장하는 DB"""
    def __init__(self, filepath: str = "user_database.json"):
        self.filepath = filepath
        if not os.path.exists(self.filepath):
            self._save_file({})

    def _load_file(self) -> Dict[str, Any]:
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_file(self, data: Dict[str, Any]):
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def save_user_profile(self, user_profile: UserProfile) -> bool:
        data = self._load_file()
        data[user_profile.user_id] = user_profile.to_dict()
        self._save_file(data)
        print(f"[JSON 사용자 DB] '{self.filepath}'에 저장되었습니다. (Name: {user_profile.name})")
        return True

    def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        # 파일에서 불러와서 UserProfile 객체로 복원 필요시 구현 가능
        data = self._load_file()
        return data.get(user_id)

    def list_all_users(self) -> List[Any]:
        data = self._load_file()
        return list(data.values())
