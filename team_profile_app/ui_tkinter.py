"""
[ui_tkinter.py]
Tkinter 기반의 사용자 프로필 및 시간표 작성 GUI 화면

주요 기능:
1. 기본 인적사항 입력 (이름, 학과, 취미)
2. 9시~18시 30분 단위 시간표 그리드 (a1, b1, ..., a9, b9 토글 선택 및 실시간 UI 표시)
3. 인원 선호도 (1~5점), 활동 선호도 (1~5점) 라디오 버튼 선택
4. 프로필 등록 시 시간표 DB 및 프로필 DB 전송
5. 등록된 사용자의 이름, 학과, 취미, 시간표, 선호도를 예쁜 프로필 카드 UI로 반환/표시
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List, Optional
from models import TimeSlot, UserProfile
from service import ScheduleService, ProfileService
from database import JSONScheduleDatabase, JSONUserDatabase


class ProfileAppUI:
    """사용자 프로필 작성 UI 클래스"""

    def __init__(self, root: tk.Tk, profile_service: ProfileService):
        self.root = root
        self.profile_service = profile_service

        # 창 기본 설정
        self.root.title("사용자 프로필 및 시간표 등록 시스템")
        self.root.geometry("780x900")
        self.root.minsize(700, 750)

        # 상태 변수들
        self.selected_slots: Dict[str, tk.BooleanVar] = {}  # { 'a1': BooleanVar, ... }
        self.slot_buttons: Dict[str, tk.Button] = {}
        self.time_slots: List[TimeSlot] = ScheduleService.generate_default_time_slots()

        # UI 스타일 테마 설정
        self.setup_styles()

        # 스크롤 가능한 메인 프레임 구성
        self.setup_scrollable_container()

        # 각 UI 섹션 빌드
        self.build_header_section()
        self.build_user_info_section()
        self.build_schedule_section()
        self.build_preference_section()
        self.build_submit_section()
        self.build_profile_card_section()

    def setup_styles(self):
        """UI 위젯 스타일 지정"""
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # 색상 팔레트
        self.PRIMARY_COLOR = "#2563EB"       # 활성 파란색
        self.PRIMARY_HOVER = "#1D4ED8"
        self.BG_COLOR = "#F8FAFC"            # 배경색
        self.CARD_BG = "#FFFFFF"             # 카드 배경색
        self.SLOT_DEFAULT_BG = "#E2E8F0"     # 슬롯 기본색 (미선택)
        self.SLOT_SELECTED_BG = "#3B82F6"    # 슬롯 선택 색상
        self.TEXT_COLOR = "#1E293B"

        self.root.configure(bg=self.BG_COLOR)
        self.style.configure("TLabel", background=self.BG_COLOR, foreground=self.TEXT_COLOR, font=("Malgun Gothic", 10))
        self.style.configure("Header.TLabel", font=("Malgun Gothic", 16, "bold"), foreground="#0F172A")
        self.style.configure("Section.TLabelframe", background=self.BG_COLOR)
        self.style.configure("Section.TLabelframe.Label", font=("Malgun Gothic", 11, "bold"), foreground=self.PRIMARY_COLOR)

    def setup_scrollable_container(self):
        """마우스 휠 스크롤이 가능한 컨테이너 생성"""
        self.canvas = tk.Canvas(self.root, bg=self.BG_COLOR, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas_frame_id = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.bind('<Configure>', lambda event: self.canvas.itemconfig(self.canvas_frame_id, width=event.width))

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # 윈도우 마우스 휠 바인딩
        self.canvas.bind_all("<MouseWheel>", lambda event: self.canvas.yview_scroll(int(-1*(event.delta/120)), "units"))

    def build_header_section(self):
        """상단 타이틀 영역"""
        header_frame = tk.Frame(self.scrollable_frame, bg=self.BG_COLOR, pady=15)
        header_frame.pack(fill="x", padx=25)

        title = ttk.Label(header_frame, text="✨ 사용자 프로필 및 시간표 작성", style="Header.TLabel")
        title.pack(anchor="w")

        subtitle = ttk.Label(
            header_frame,
            text="시간표(9:00~18:00)와 인원/활동 선호도 및 기본 인적사항을 입력해주세요.",
            font=("Malgun Gothic", 9),
            foreground="#64748B"
        )
        subtitle.pack(anchor="w", pady=(3, 0))

    def build_user_info_section(self):
        """[요구사항 5] 사용자의 이름, 학과, 취미 입력 섹션"""
        section = ttk.LabelFrame(self.scrollable_frame, text=" 1. 기본 인적사항 ", style="Section.TLabelframe", padding=15)
        section.pack(fill="x", padx=25, pady=8)

        grid_frame = tk.Frame(section, bg=self.BG_COLOR)
        grid_frame.pack(fill="x")

        # 이름
        ttk.Label(grid_frame, text="이름:", font=("Malgun Gothic", 10, "bold")).grid(row=0, column=0, sticky="w", pady=6)
        self.entry_name = ttk.Entry(grid_frame, width=25, font=("Malgun Gothic", 10))
        self.entry_name.grid(row=0, column=1, sticky="w", padx=10, pady=6)
        self.entry_name.insert(0, "홍길동")

        # 학과
        ttk.Label(grid_frame, text="학과:", font=("Malgun Gothic", 10, "bold")).grid(row=0, column=2, sticky="w", padx=(20, 0), pady=6)
        self.entry_dept = ttk.Entry(grid_frame, width=25, font=("Malgun Gothic", 10))
        self.entry_dept.grid(row=0, column=3, sticky="w", padx=10, pady=6)
        self.entry_dept.insert(0, "컴퓨터공학과")

        # 취미
        ttk.Label(grid_frame, text="취미:", font=("Malgun Gothic", 10, "bold")).grid(row=1, column=0, sticky="w", pady=6)
        self.entry_hobby = ttk.Entry(grid_frame, width=63, font=("Malgun Gothic", 10))
        self.entry_hobby.grid(row=1, column=1, columnspan=3, sticky="w", padx=10, pady=6)
        self.entry_hobby.insert(0, "코딩, 맛집 탐방, 보드게임")

    def build_schedule_section(self):
        """[요구사항 1, 2] 9시부터 18시까지 30분 단위 시간표 생성 및 선택 UI"""
        section = ttk.LabelFrame(self.scrollable_frame, text=" 2. 시간표 선택 (09:00 ~ 18:00) ", style="Section.TLabelframe", padding=15)
        section.pack(fill="x", padx=25, pady=8)

        info_lbl = ttk.Label(
            section,
            text="💡 원하는 시간 슬롯 버튼을 클릭하여 선택/해제하세요 (30분 단위):",
            font=("Malgun Gothic", 9),
            foreground="#475569"
        )
        info_lbl.pack(anchor="w", pady=(0, 10))

        # 시간표 버튼들을 배치할 그리드 프레임
        table_frame = tk.Frame(section, bg=self.BG_COLOR)
        table_frame.pack(fill="x")

        # 시간표 버튼 생성 (9개 시간대 x 2개 슬롯 = 18개 버튼)
        # 3열(시간당 1행씩 총 9행) 또는 2행 9열 등으로 깔끔하게 배치
        columns_count = 6  # 한 행에 6개 슬롯(3시간 분량) 배치 -> 총 3개 행
        
        for idx, slot in enumerate(self.time_slots):
            row = idx // columns_count
            col = idx % columns_count

            is_selected = tk.BooleanVar(value=False)
            self.selected_slots[slot.code] = is_selected

            btn = tk.Button(
                table_frame,
                text=f"{slot.code}\n{slot.start_time}~{slot.end_time}",
                bg=self.SLOT_DEFAULT_BG,
                fg="#334155",
                activebackground="#CBD5E1",
                font=("Malgun Gothic", 8, "bold"),
                width=12,
                height=2,
                relief="groove",
                cursor="hand2",
                command=lambda s=slot: self.toggle_slot(s)
            )
            btn.grid(row=row, column=col, padx=4, pady=4, sticky="nsew")
            self.slot_buttons[slot.code] = btn

        # [요구사항 2] UI에 사용자가 선택한 시간 실시간 표시 영역
        display_frame = tk.Frame(section, bg="#F1F5F9", relief="solid", bd=1, padx=10, pady=8)
        display_frame.pack(fill="x", pady=(12, 0))

        display_title = tk.Label(display_frame, text="선택된 시간:", bg="#F1F5F9", font=("Malgun Gothic", 9, "bold"), fg="#1E293B")
        display_title.pack(anchor="w")

        self.lbl_selected_times = tk.Label(
            display_frame,
            text="아직 선택된 시간이 없습니다.",
            bg="#F1F5F9",
            fg=self.PRIMARY_COLOR,
            font=("Malgun Gothic", 9),
            wraplength=650,
            justify="left"
        )
        self.lbl_selected_times.pack(anchor="w", pady=(2, 0))

    def toggle_slot(self, slot: TimeSlot):
        """시간 슬롯 클릭 시 토글 처리 및 UI 실시간 갱신"""
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
        """[요구사항 2] 선택된 시간표 문자열 UI 갱신"""
        selected_codes = [code for code, var in self.selected_slots.items() if var.get()]
        if not selected_codes:
            self.lbl_selected_times.config(text="아직 선택된 시간이 없습니다.", fg="#64748B")
            return

        slot_dict = {s.code: s for s in self.time_slots}
        text_list = [f"{c}({slot_dict[c].start_time}~{slot_dict[c].end_time})" for c in selected_codes if c in slot_dict]
        summary_text = " | ".join(text_list)
        self.lbl_selected_times.config(text=f"총 {len(selected_codes)}개 슬롯 선택됨: {summary_text}", fg=self.PRIMARY_COLOR)

    def build_preference_section(self):
        """[요구사항 3, 4] 인원 선호도(1~5점) 및 활동 선호도(1~5점) 섹션"""
        section = ttk.LabelFrame(self.scrollable_frame, text=" 3. 선호도 설정 (1점 ~ 5점) ", style="Section.TLabelframe", padding=15)
        section.pack(fill="x", padx=25, pady=8)

        # 1) [요구사항 3] 인원 선호도
        people_frame = tk.Frame(section, bg=self.BG_COLOR)
        people_frame.pack(fill="x", pady=5)

        ttk.Label(
            people_frame,
            text="• 함께할 인원 선호도 (1점: 혼자/소수  ~  5점: 다수):",
            font=("Malgun Gothic", 9, "bold")
        ).pack(anchor="w")

        self.people_pref_var = tk.IntVar(value=3)
        p_radio_box = tk.Frame(people_frame, bg=self.BG_COLOR)
        p_radio_box.pack(anchor="w", padx=15, pady=4)

        for score in range(1, 6):
            r = ttk.Radiobutton(
                p_radio_box,
                text=f"{score}점",
                value=score,
                variable=self.people_pref_var
            )
            r.pack(side="left", padx=10)

        # 2) [요구사항 4] 활동 선호도
        act_frame = tk.Frame(section, bg=self.BG_COLOR)
        act_frame.pack(fill="x", pady=(10, 5))

        ttk.Label(
            act_frame,
            text="• 활동 적극성/선호도 (1점: 정적인 휴식/공부  ~  5점: 활발한 야외/소셜):",
            font=("Malgun Gothic", 9, "bold")
        ).pack(anchor="w")

        self.activity_pref_var = tk.IntVar(value=3)
        a_radio_box = tk.Frame(act_frame, bg=self.BG_COLOR)
        a_radio_box.pack(anchor="w", padx=15, pady=4)

        for score in range(1, 6):
            r = ttk.Radiobutton(
                a_radio_box,
                text=f"{score}점",
                value=score,
                variable=self.activity_pref_var
            )
            r.pack(side="left", padx=10)

    def build_submit_section(self):
        """데이터베이스 전송 버튼 영역"""
        btn_frame = tk.Frame(self.scrollable_frame, bg=self.BG_COLOR, pady=10)
        btn_frame.pack(fill="x", padx=25)

        self.btn_submit = tk.Button(
            btn_frame,
            text="💾 프로필 등록 및 시간표 DB 전송",
            bg=self.PRIMARY_COLOR,
            fg="white",
            activebackground=self.PRIMARY_HOVER,
            activeforeground="white",
            font=("Malgun Gothic", 11, "bold"),
            relief="flat",
            padx=20,
            pady=10,
            cursor="hand2",
            command=self.on_submit
        )
        self.btn_submit.pack(fill="x")

    def build_profile_card_section(self):
        """[요구사항 5] 등록된 사용자 프로필 UI 반환 및 출력 영역"""
        self.result_container = tk.Frame(self.scrollable_frame, bg=self.BG_COLOR, pady=10)
        self.result_container.pack(fill="x", padx=25, pady=(0, 25))

        # 초기에는 비워둠 (등록 시 생성)

    def on_submit(self):
        """
        [요구사항 2, 5]
        등록 버튼 클릭 핸들러:
        1. 시간표 데이터베이스로 전체 시간표 및 입력한 시간 전송
        2. 사용자 프로필 데이터베이스로 기본 정보(이름, 학과, 취미) 및 선호도 전송
        3. UI에 등록된 사용자 프로필 카드 반환 및 렌더링
        """
        name = self.entry_name.get()
        dept = self.entry_dept.get()
        hobby = self.entry_hobby.get()
        selected_codes = [code for code, var in self.selected_slots.items() if var.get()]
        people_pref = self.people_pref_var.get()
        activity_pref = self.activity_pref_var.get()

        # 비즈니스 로직(서비스) 호출
        success, message, profile = self.profile_service.register_profile(
            name=name,
            department=dept,
            hobby=hobby,
            selected_slot_codes=selected_codes,
            people_preference=people_pref,
            activity_preference=activity_pref
        )

        if not success:
            messagebox.showwarning("입력 확인", message)
            return

        # 성공 팝업
        messagebox.showinfo(
            "등록 완료",
            f"🎉 {profile.name}님의 프로필과 시간표가 데이터베이스에 성공적으로 전송되었습니다!\n"
            f"- 선택 슬롯 수: {len(profile.schedule.selected_slot_codes)}개\n"
            f"- 인원 선호도: {profile.preference.people_preference}점 / 활동 선호도: {profile.preference.activity_preference}점"
        )

        # [요구사항 5] 등록된 사용자 프로필 UI 반환 및 카드 렌더링
        self.render_user_profile_card(profile)

    def render_user_profile_card(self, profile: UserProfile):
        """
        [요구사항 5]
        저장된 사용자 정보를 바탕으로 결과 UI 카드 위젯을 생성하여 반환/표시합니다.
        """
        # 기존 카드 초기화
        for widget in self.result_container.winfo_children():
            widget.destroy()

        card = tk.Frame(self.result_container, bg="white", relief="solid", bd=1, padx=20, pady=15)
        card.pack(fill="x")

        # 카드 헤더
        card_header = tk.Frame(card, bg="white")
        card_header.pack(fill="x", pady=(0, 10))

        tk.Label(
            card_header,
            text=f"📋 [등록된 프로필] {profile.name}님의 프로필 카드",
            font=("Malgun Gothic", 12, "bold"),
            bg="white",
            fg=self.PRIMARY_COLOR
        ).pack(side="left")

        tk.Label(
            card_header,
            text=f"등록시각: {profile.created_at}",
            font=("Malgun Gothic", 8),
            bg="white",
            fg="#94A3B8"
        ).pack(side="right")

        # 구분선
        sep = tk.Frame(card, height=1, bg="#E2E8F0")
        sep.pack(fill="x", pady=5)

        # 인적사항 정보 뷰
        info_frame = tk.Frame(card, bg="white")
        info_frame.pack(fill="x", pady=5)

        tk.Label(info_frame, text="👤 이름:", font=("Malgun Gothic", 9, "bold"), bg="white", fg="#475569").grid(row=0, column=0, sticky="w", pady=2)
        tk.Label(info_frame, text=profile.name, font=("Malgun Gothic", 9), bg="white").grid(row=0, column=1, sticky="w", padx=10, pady=2)

        tk.Label(info_frame, text="🏫 학과:", font=("Malgun Gothic", 9, "bold"), bg="white", fg="#475569").grid(row=0, column=2, sticky="w", padx=(20, 0), pady=2)
        tk.Label(info_frame, text=profile.department, font=("Malgun Gothic", 9), bg="white").grid(row=0, column=3, sticky="w", padx=10, pady=2)

        tk.Label(info_frame, text="🎨 취미:", font=("Malgun Gothic", 9, "bold"), bg="white", fg="#475569").grid(row=1, column=0, sticky="w", pady=2)
        tk.Label(info_frame, text=profile.hobby, font=("Malgun Gothic", 9), bg="white").grid(row=1, column=1, columnspan=3, sticky="w", padx=10, pady=2)

        # 시간표 정보 뷰
        time_frame = tk.Frame(card, bg="#F8FAFC", padx=10, pady=8, relief="groove", bd=1)
        time_frame.pack(fill="x", pady=8)

        tk.Label(
            time_frame,
            text=f"⏰ 선택한 시간표 (총 {len(profile.schedule.selected_slot_codes)}개 슬롯)",
            font=("Malgun Gothic", 9, "bold"),
            bg="#F8FAFC",
            fg="#1E293B"
        ).pack(anchor="w")

        tk.Label(
            time_frame,
            text=profile.schedule.selected_summary,
            font=("Malgun Gothic", 8),
            bg="#F8FAFC",
            fg="#2563EB",
            wraplength=640,
            justify="left"
        ).pack(anchor="w", pady=(3, 0))

        # 선호도 수치 뷰
        pref_frame = tk.Frame(card, bg="white")
        pref_frame.pack(fill="x", pady=5)

        people_score = profile.preference.people_preference
        act_score = profile.preference.activity_preference

        tk.Label(
            pref_frame,
            text=f"👥 인원 선호도: {'★' * people_score}{'☆' * (5 - people_score)} ({people_score}/5점)",
            font=("Malgun Gothic", 9),
            bg="white",
            fg="#059669"
        ).pack(side="left", padx=(0, 20))

        tk.Label(
            pref_frame,
            text=f"🎯 활동 선호도: {'★' * act_score}{'☆' * (5 - act_score)} ({act_score}/5점)",
            font=("Malgun Gothic", 9),
            bg="white",
            fg="#D97706"
        ).pack(side="left")


def start_app():
    """앱 실행 진입점 함수"""
    root = tk.Tk()

    # 데이터베이스 인스턴스 생성 (JSON 영구 저장소 사용)
    schedule_db = JSONScheduleDatabase("schedule_database.json")
    user_db = JSONUserDatabase("user_database.json")

    # 서비스 계층 초기화
    profile_service = ProfileService(schedule_db=schedule_db, user_db=user_db)

    # UI 구동
    app = ProfileAppUI(root, profile_service)
    root.mainloop()


if __name__ == "__main__":
    start_app()
