"""
[main.py]
애플리케이션 실행 진입점 (Entry Point)

팀 프로젝트에서 앱을 실행할 때 실행하는 메인 파일입니다.
사용법:
    python main.py
"""

from database import JSONScheduleDatabase, JSONUserDatabase
from service import ProfileService
from ui_tkinter import ProfileAppUI
import tkinter as tk


def main():
    print("=" * 60)
    print("🚀 사용자 프로필 및 시간표 관리 시스템 시작")
    print("=" * 60)

    # 1. 데이터베이스 인스턴스 준비
    # 팀원들의 요구사항에 따라 MySQL, SQLite 등으로 database.py에서 교체할 수 있습니다.
    schedule_db = JSONScheduleDatabase(filepath="schedule_database.json")
    user_db = JSONUserDatabase(filepath="user_database.json")

    # 2. 비즈니스 로직 서비스 준비
    profile_service = ProfileService(schedule_db=schedule_db, user_db=user_db)

    # 3. Tkinter GUI 실행
    root = tk.Tk()
    app = ProfileAppUI(root=root, profile_service=profile_service)
    root.mainloop()


if __name__ == "__main__":
    main()
