"""
[standalone_profile_app.py]
단일 파일 버전 (All-in-One) 사용자 프로필 및 시간표 시스템

팀원이 "일단 파일 하나로 합쳐서 줘봐!"라고 요청할 때 바로 전달할 수 있는 단일 파일 코드입니다.
models, database, service, UI가 모두 이 파일 하나에 깔끔하게 구조화되어 들어가 있습니다.

실행:
    python standalone_profile_app.py
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import json
import os
import uuid
import tkinter as tk
from tkinter import ttk, messagebox


# ==============================================================================
# 1. DATA MODELS (데이터 모델 정의)
# ==============================================================================

@dataclass
class TimeSlot:
    """30분 단위 시간 슬롯 (예: a1, 09:00 ~ 09:30)"""
    code: str
    start_time: str
    end_time: str

    @property
    def label(self) -> str:
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
    """시간표 데이터 모델"""
    all_slots: List[TimeSlot] = field(default_factory=list)
    selected_slot_codes: List[str] = field(default_factory=list)

    @property
    def selected_slots(self) -> List[TimeSlot]:
        selected_set = set(self.selected_slot_codes)
        return [slot for slot in self.all_slots if slot.code in selected_set]

    @property
    def selected_summary(self) -> str:
        if not self.selected_slot_codes:
            return "선택된 시간 없음"
        return ", ".join(f"{s.code}({s.start_time}~{s.end_time})" for s in self.selected_slots)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "selected_slot_codes": self.selected_slot_codes,
            "selected_summary": self.selected_summary,
            "all_slots": [s.to_dict() for s in self.all_slots]
        }


@dataclass
class PreferenceData:
    """인원 선호도 및 활동 선호도 모델 (1점 ~ 5점)"""
    people_preference: int = 3
    activity_preference: int = 3

    def to_dict(self) -> Dict[str, int]:
        return {
            "people_preference": self.people_preference,
            "activity_preference": self.activity_preference
        }


@dataclass
class UserProfile:
    """사용자 전체 프로필 모델 (이름, 학과, 취미 + 시간표 + 선호도)"""
    user_id: str
    name: str
    department: str
    hobby: str
    schedule: ScheduleData
    preference: PreferenceData
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "name": self.name,
            "department": self.department,
            "hobby": self.hobby,
            "schedule": self.schedule.to_dict(),
            "preference": self.preference.to_dict(),
            "created_at": self.created_at
        }


# ==============================================================================
# 2. DATABASE LAYER (데이터베이스 인터페이스 및 JSON 구현체)
# ==============================================================================

class BaseScheduleDatabase(ABC):
    @abstractmethod
    def save_schedule(self, user_id: str, schedule_data: ScheduleData) -> bool:
        pass


class BaseUserDatabase(ABC):
    @abstractmethod
    def save_user_profile(self, user_profile: UserProfile) -> bool:
        pass


class JSONScheduleDatabase(BaseScheduleDatabase):
    """시간표 데이터를 JSON 파일로 영구 저장하는 DB"""
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
        print(f"[시간표 DB 저장 완료] User ID: {user_id}")
        return True


class JSONUserDatabase(BaseUserDatabase):
    """사용자 프로필을 JSON 파일로 영구 저장하는 DB"""
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
        print(f"[사용자 프로필 DB 저장 완료] 이름: {user_profile.name}")
        return True


# ==============================================================================
# 3. SERVICE LAYER (비즈니스 로직)
# ==============================================================================

class ScheduleService:
    @staticmethod
    def generate_default_time_slots() -> List[TimeSlot]:
        """
        [요구사항 1] 9시부터 18시까지 30분 단위 시간표 생성 (a1, b1, a2, b2, ..., a9, b9)
        """
        slots: List[TimeSlot] = []
        for hour in range(9, 18):
            n = hour - 9 + 1
            # 30분 앞 (a)
            slots.append(TimeSlot(code=f"a{n}", start_time=f"{hour:02d}:00", end_time=f"{hour:02d}:30"))
            # 30분 뒤 (b)
            slots.append(TimeSlot(code=f"b{n}", start_time=f"{hour:02d}:30", end_time=f"{hour+1:02d}:00"))
        return slots

    @classmethod
    def create_schedule_data(cls, selected_slot_codes: List[str]) -> ScheduleData:
        return ScheduleData(
            all_slots=cls.generate_default_time_slots(),
            selected_slot_codes=selected_slot_codes
        )


class ProfileService:
    def __init__(self, schedule_db: BaseScheduleDatabase, user_db: BaseUserDatabase):
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
        # 유효성 검증
        if not name.strip():
            return False, "이름을 입력해주세요.", None
        if not department.strip():
            return False, "학과를 입력해주세요.", None
        if not hobby.strip():
            return False, "취미를 입력해주세요.", None
        if not (1 <= people_preference <= 5):
            return False, "인원 선호도는 1~5점이어야 합니다.", None
        if not (1 <= activity_preference <= 5):
            return False, "활동 선호도는 1~5점이어야 합니다.", None

        if not user_id:
            user_id = f"user_{name}_{uuid.uuid4().hex[:6]}"

        schedule_data = ScheduleService.create_schedule_data(selected_slot_codes)
        preference_data = PreferenceData(people_preference, activity_preference)
        user_profile = UserProfile(
            user_id=user_id,
            name=name.strip(),
            department=department.strip(),
            hobby=hobby.strip(),
            schedule=schedule_data,
            preference=preference_data
        )

        try:
            # 시간표 DB 및 프로필 DB 전송
            self.schedule_db.save_schedule(user_id, schedule_data)
            self.user_db.save_user_profile(user_profile)
            return True, "성공적으로 저장되었습니다.", user_profile
        except Exception as e:
            return False, f"DB 저장 실패: {str(e)}", None


# ==============================================================================
# 4. PRESENTATION LAYER (Tkinter GUI 화면)
# ==============================================================================

class ProfileAppUI:
    def __init__(self, root: tk.Tk, profile_service: ProfileService):
        self.root = root
        self.profile_service = profile_service

        self.root.title("사용자 프로필 & 시간표 등록 시스템 (팀 프로젝트용)")
        self.root.geometry("760x880")
        self.root.minsize(700, 750)

        self.selected_slots: Dict[str, tk.BooleanVar] = {}
        self.slot_buttons: Dict[str, tk.Button] = {}
        self.time_slots: List[TimeSlot] = ScheduleService.generate_default_time_slots()

        self.PRIMARY_COLOR = "#2563EB"
        self.BG_COLOR = "#F8FAFC"
        self.SLOT_DEFAULT_BG = "#E2E8F0"
        self.SLOT_SELECTED_BG = "#3B82F6"

        self.root.configure(bg=self.BG_COLOR)
        self.setup_ui()

    def setup_ui(self):
        # 스크롤 캔버스 설정
        canvas = tk.Canvas(self.root, bg=self.BG_COLOR, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas_window = canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.bind('<Configure>', lambda e: canvas.itemconfig(canvas_window, width=e.width))

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        # 1. 헤더
        header = tk.Frame(scroll_frame, bg=self.BG_COLOR, pady=15)
        header.pack(fill="x", padx=20)
        tk.Label(header, text="✨ 사용자 프로필 작성 모듈", font=("Malgun Gothic", 16, "bold"), bg=self.BG_COLOR, fg="#0F172A").pack(anchor="w")
        tk.Label(header, text="팀원들과 연동할 수 있도록 시간표(9~18시)와 선호도 및 인적사항을 입력받습니다.", font=("Malgun Gothic", 9), bg=self.BG_COLOR, fg="#64748B").pack(anchor="w")

        # 2. [요구사항 5] 기본 인적사항 (이름, 학과, 취미)
        sec1 = ttk.LabelFrame(scroll_frame, text=" 1. 사용자 인적사항 ", padding=12)
        sec1.pack(fill="x", padx=20, pady=6)
        
        g = tk.Frame(sec1)
        g.pack(fill="x")
        tk.Label(g, text="이름:", font=("Malgun Gothic", 9, "bold")).grid(row=0, column=0, sticky="w", pady=4)
        self.entry_name = ttk.Entry(g, width=20, font=("Malgun Gothic", 9))
        self.entry_name.grid(row=0, column=1, padx=6, pady=4)
        self.entry_name.insert(0, "홍길동")

        tk.Label(g, text="학과:", font=("Malgun Gothic", 9, "bold")).grid(row=0, column=2, sticky="w", padx=(15, 0), pady=4)
        self.entry_dept = ttk.Entry(g, width=25, font=("Malgun Gothic", 9))
        self.entry_dept.grid(row=0, column=3, padx=6, pady=4)
        self.entry_dept.insert(0, "컴퓨터공학과")

        tk.Label(g, text="취미:", font=("Malgun Gothic", 9, "bold")).grid(row=1, column=0, sticky="w", pady=4)
        self.entry_hobby = ttk.Entry(g, width=58, font=("Malgun Gothic", 9))
        self.entry_hobby.grid(row=1, column=1, columnspan=3, padx=6, pady=4, sticky="w")
        self.entry_hobby.insert(0, "코딩, 맛집 탐방, 영화 감상")

        # 3. [요구사항 1, 2] 시간표 슬롯 (a1 ~ b9)
        sec2 = ttk.LabelFrame(scroll_frame, text=" 2. 시간표 선택 (09:00 ~ 18:00, 30분 단위) ", padding=12)
        sec2.pack(fill="x", padx=20, pady=6)

        table = tk.Frame(sec2)
        table.pack(fill="x")

        for idx, slot in enumerate(self.time_slots):
            r, c = divmod(idx, 6)
            var = tk.BooleanVar(value=False)
            self.selected_slots[slot.code] = var

            btn = tk.Button(
                table,
                text=f"{slot.code}\n{slot.start_time}~{slot.end_time}",
                bg=self.SLOT_DEFAULT_BG,
                fg="#334155",
                font=("Malgun Gothic", 8, "bold"),
                width=12,
                height=2,
                relief="groove",
                cursor="hand2",
                command=lambda s=slot: self.toggle_slot(s)
            )
            btn.grid(row=r, column=c, padx=3, pady=3, sticky="nsew")
            self.slot_buttons[slot.code] = btn

        # 실시간 선택 시간 UI 표시
        disp_box = tk.Frame(sec2, bg="#F1F5F9", relief="solid", bd=1, padx=8, pady=6)
        disp_box.pack(fill="x", pady=(10, 0))
        tk.Label(disp_box, text="선택한 시간표:", font=("Malgun Gothic", 9, "bold"), bg="#F1F5F9").pack(anchor="w")
        self.lbl_selected_times = tk.Label(disp_box, text="선택된 슬롯 없음", font=("Malgun Gothic", 9), bg="#F1F5F9", fg=self.PRIMARY_COLOR, wraplength=640, justify="left")
        self.lbl_selected_times.pack(anchor="w")

        # 4. [요구사항 3, 4] 인원/활동 선호도 (1~5점)
        sec3 = ttk.LabelFrame(scroll_frame, text=" 3. 선호도 설정 (1점 ~ 5점) ", padding=12)
        sec3.pack(fill="x", padx=20, pady=6)

        # 인원 선호도
        tk.Label(sec3, text="• 인원 선호도 (1: 혼자/소수  ~  5: 다수)", font=("Malgun Gothic", 9, "bold")).pack(anchor="w")
        self.people_pref_var = tk.IntVar(value=3)
        pf = tk.Frame(sec3)
        pf.pack(anchor="w", padx=10, pady=(2, 8))
        for score in range(1, 6):
            ttk.Radiobutton(pf, text=f"{score}점", value=score, variable=self.people_pref_var).pack(side="left", padx=8)

        # 활동 선호도
        tk.Label(sec3, text="• 활동 선호도 (1: 정적인 휴식/공부  ~  5: 활발한 모임/운동)", font=("Malgun Gothic", 9, "bold")).pack(anchor="w")
        self.act_pref_var = tk.IntVar(value=3)
        af = tk.Frame(sec3)
        af.pack(anchor="w", padx=10, pady=2)
        for score in range(1, 6):
            ttk.Radiobutton(af, text=f"{score}점", value=score, variable=self.act_pref_var).pack(side="left", padx=8)

        # 5. 저장 버튼
        btn_box = tk.Frame(scroll_frame, pady=10)
        btn_box.pack(fill="x", padx=20)
        btn_submit = tk.Button(
            btn_box,
            text="💾 프로필 등록 및 시간표 DB 전송",
            bg=self.PRIMARY_COLOR,
            fg="white",
            font=("Malgun Gothic", 11, "bold"),
            relief="flat",
            pady=8,
            cursor="hand2",
            command=self.on_submit
        )
        btn_submit.pack(fill="x")

        # 6. [요구사항 5] 반환된 프로필 카드 표시 영역
        self.result_container = tk.Frame(scroll_frame, pady=5)
        self.result_container.pack(fill="x", padx=20, pady=(0, 20))

    def toggle_slot(self, slot: TimeSlot):
        var = self.selected_slots[slot.code]
        new_val = not var.get()
        var.set(new_val)
        btn = self.slot_buttons[slot.code]
        if new_val:
            btn.configure(bg=self.SLOT_SELECTED_BG, fg="white", relief="sunken")
        else:
            btn.configure(bg=self.SLOT_DEFAULT_BG, fg="#334155", relief="groove")
        self.update_selected_display()

    def update_selected_display(self):
        codes = [code for code, var in self.selected_slots.items() if var.get()]
        if not codes:
            self.lbl_selected_times.config(text="선택된 슬롯 없음", fg="#64748B")
            return
        slot_map = {s.code: s for s in self.time_slots}
        text_list = [f"{c}({slot_map[c].start_time}~{slot_map[c].end_time})" for c in codes if c in slot_map]
        self.lbl_selected_times.config(text=f"선택 {len(codes)}개: " + " | ".join(text_list), fg=self.PRIMARY_COLOR)

    def on_submit(self):
        name = self.entry_name.get()
        dept = self.entry_dept.get()
        hobby = self.entry_hobby.get()
        codes = [code for code, var in self.selected_slots.items() if var.get()]
        people_pref = self.people_pref_var.get()
        act_pref = self.act_pref_var.get()

        success, msg, profile = self.profile_service.register_profile(
            name=name,
            department=dept,
            hobby=hobby,
            selected_slot_codes=codes,
            people_preference=people_pref,
            activity_preference=act_pref
        )

        if not success:
            messagebox.showwarning("알림", msg)
            return

        messagebox.showinfo("성공", f"DB 저장 완료!\n유저: {profile.name} ({profile.department})")
        self.render_card(profile)

    def render_card(self, profile: UserProfile):
        """[요구사항 5] 사용자 이름, 학과, 취미, 시간표, 선호도를 카드 UI로 반환"""
        for w in self.result_container.winfo_children():
            w.destroy()

        card = tk.Frame(self.result_container, bg="white", relief="solid", bd=1, padx=15, pady=12)
        card.pack(fill="x")

        tk.Label(card, text=f"📋 [프로필 카드 반환] {profile.name} ({profile.department})", font=("Malgun Gothic", 11, "bold"), bg="white", fg=self.PRIMARY_COLOR).pack(anchor="w")
        tk.Label(card, text=f"🎨 취미: {profile.hobby}", font=("Malgun Gothic", 9), bg="white").pack(anchor="w", pady=(4, 0))

        # 시간표
        time_box = tk.Frame(card, bg="#F8FAFC", relief="groove", bd=1, padx=8, pady=6)
        time_box.pack(fill="x", pady=6)
        tk.Label(time_box, text=f"⏰ 선택 시간표: {profile.schedule.selected_summary}", font=("Malgun Gothic", 8), bg="#F8FAFC", fg="#2563EB", wraplength=640, justify="left").pack(anchor="w")

        # 선호도
        pref_text = f"👥 인원 선호도: {profile.preference.people_preference}/5점  |  🎯 활동 선호도: {profile.preference.activity_preference}/5점"
        tk.Label(card, text=pref_text, font=("Malgun Gothic", 9, "bold"), bg="white", fg="#059669").pack(anchor="w")


# ==============================================================================
# 5. ENTRY POINT
# ==============================================================================
if __name__ == "__main__":
    schedule_db = JSONScheduleDatabase("schedule_database.json")
    user_db = JSONUserDatabase("user_database.json")
    service = ProfileService(schedule_db, user_db)

    root = tk.Tk()
    app = ProfileAppUI(root, service)
    root.mainloop()
