"""매칭공강 매칭방 UI

실행: python -m streamlit run app.py
같은 폴더에 matching_cmd_ngram_chat.py 필요
"""
import copy
import html
from datetime import datetime, time

import streamlit as st
from matching_cmd_ngram_chat import (#matching_cmd_ngram_chat에서 {}의 함수를 사용하기위해 선언
    ROOMS as INITIAL_ROOMS,
    USERS,
    DAY_ORDER,
    search_rooms,
    filter_by_time,
    sort_rooms,
)

st.set_page_config(page_title="CampusMate | 매칭방", page_icon="🎓", layout="wide")

ACTIVITIES = ("운동", "식사", "게임", "담화", "공부", "술", "문화활동")
DAYS = tuple(DAY_ORDER)
ACTIVITY_ICONS = {
    "운동": "⚽", "식사": "☕", "게임": "🎮", "담화": "💬",
    "공부": "📚", "술": "🍻", "문화활동": "🎬",
}
SORT_LABELS = ["검색 관련도·취향순", "시간순", "인원수순", "취미 선호도순", "시간대별"]

CSS = """
<style>
:root { --ink:#202344; --muted:#777d9f; --accent:#797ce2; --border:#e5e7f3; }
.stApp { background: linear-gradient(165deg,#ffffff 5%,#faf9ff 62%,#f6f5ff 100%); }
.block-container { max-width:1120px; padding-top:1.45rem; padding-bottom:4rem; }
#MainMenu, header[data-testid="stHeader"] { background:transparent; }
h1,h2,h3 { color:var(--ink); }
.cm-brand { text-align:center; font-size:2rem; font-weight:800; color:#353957; letter-spacing:-1px; margin:0 0 8px; }
.cm-brand span { color:#8e90ec; }
.cm-sub { color:#777d9f; text-align:center; margin-top:-4px; margin-bottom:1.5rem; font-size:.92rem; }
.cm-hero { border:1px solid #e6e6f4; background:#ffffffd9; border-radius:22px; padding:23px 26px; box-shadow:0 4px 20px #26265e0a; margin-bottom:18px; }
.cm-title { font-size:1.15rem; font-weight:750; color:#202344; }
.cm-muted { font-size:.9rem; color:#858aa4; }
.cm-room { padding:0; margin:0; background:transparent; }
/* st.container 안에 카드 본문과 버튼을 나란히 넣어 버튼 아래 빈 공간을 없앱니다. */
div[class*="st-key-room_card_"] { background:#fff; border-radius:20px; margin-bottom:5px; }
div[class*="st-key-room_card_"] [data-testid="stVerticalBlock"] { gap:.35rem; }
div[class*="st-key-room_card_"] [data-testid="stHorizontalBlock"] { align-items:center; }

.cm-room-top { display:flex; gap:17px; align-items:start; }
.cm-icon { flex-shrink:0; font-size:1.9rem; background:#f0efff; border-radius:17px; padding:13px; line-height:1.3; }
.cm-room-info { min-width:0; flex:1; }
.cm-extra { color:#737998; font-size:.84rem; margin-top:6px; white-space:pre-wrap; overflow-wrap:anywhere; }

.cm-room-title { font-size:1.14rem; font-weight:760; color:#242541; margin-bottom:6px; }
.cm-meta { color:#7c809c; font-size:.88rem; margin:6px 0; }
.cm-tag { display:inline-block; background:#eeedff; color:#6067ac; border-radius:40px; padding:3px 12px; font-size:.8rem; margin:4px 5px 0 0; }
.cm-full { background:#fff0f0;color:#bf5561; }
.cm-chat { background:#f3f2ff; border-radius:17px; padding:12px 16px; margin:7px 0; }
.cm-chat-author { font-size:.8rem; font-weight:700; color:#676c9a; margin-bottom:4px; }
.cm-chat-text { color:#303454; overflow-wrap:anywhere; }
.cm-panel { border:1px solid #e5e7f2; border-radius:20px; background:#fff; padding:18px; }
div.stButton>button[kind="primary"],div.stFormSubmitButton>button[kind="primary"] { background:#8183dc; border-color:#8183dc; color:white; border-radius:12px; }
div.stButton>button,div.stFormSubmitButton>button { border-radius:12px; }
[data-testid="stMetricValue"] { color:#5e63aa; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


def e(value): #예외 처리
    return html.escape(str(value), quote=True)


def init_state():
    defaults = { #프로그램 처음 실행시 사용할 기본값들
        "rooms": copy.deepcopy(INITIAL_ROOMS),  #현제 세션에서 관리하는 매칭방 전체
        "user_id": "user01", #현재 사용자 id
        "search_keyword": "", 
        "sort_label": SORT_LABELS[0],
        "time_condition": None,
        "joined_ids": set(), 
        "created_ids": set(),
        "next_room_id": max(room["id"] for room in INITIAL_ROOMS) + 1, #방생성시의 방id제작
        "flash": "", #화면에 한 번 보여줄 안내 메시지
        "selected_room_id": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state: #매번 사용자와 상호작용시 변경된 값은 변경/아니면 유지
            st.session_state[key] = value
    for room in st.session_state.rooms:
        room.setdefault("chats", []) #방에 채팅이 없으면 생성 + 채팅이 있었으면 유지 


def user():
    return USERS[st.session_state.user_id]


def find_room(room_id):
    return next((room for room in st.session_state.rooms if room["id"] == room_id), None)


def navigate(page, room_id=None): #거의 main함수라고 보면됨
    if page == "room":
        if room_id is None: #방 번호 입력x - home_page로 이동
            st.switch_page(HOME_PAGE)
        st.session_state.selected_room_id = int(room_id) #방id 저장후 room_page로 이동
        st.switch_page(ROOM_PAGE)
    elif page == "create":
        st.switch_page(CREATE_PAGE) #방생성 page로 이동
    else:
        st.switch_page(HOME_PAGE) #별도의 상호작용없으면 홈페이지에 유지


def flash(message):
    st.session_state.flash = message


def show_flash():
    if st.session_state.flash:
        st.success(st.session_state.flash)
        st.session_state.flash = ""


def header(subtitle="공강에 어울리는 사람들과 연결되는 공간"):
    st.markdown('<div class="cm-brand">🎓 Campus<span>Mate</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="cm-sub">{e(subtitle)}</div>', unsafe_allow_html=True)


def list_rooms(): #검색or정렬 시 보여줄 방 목록 만드는 함수
    keyword = st.session_state.search_keyword
    rooms = st.session_state.rooms
    result = search_rooms(rooms, keyword, user()) if keyword else rooms[:] #매칭알고리즘-기준에맞는 매칭방 반환받음
    if st.session_state.time_condition: #정렬 - 시간대 입력 정렬
        day, start, end = st.session_state.time_condition
        result = filter_by_time(result, day, start, end)
    mapping = {"시간순": "1", "인원수순": "2", "취미 선호도순": "3", "시간대별": "4"}
    mode = st.session_state.sort_label
    if mode in mapping: #정렬 - 시간/인원/선호
        result = sort_rooms(result, mapping[mode], user())
    return result


def room_card(room): #목록의 매칭방 한개의 ui
    icon = ACTIVITY_ICONS.get(room["activity"], "🎯")
    full = room["people"] >= room["capacity"]
    status = '<span class="cm-tag cm-full">마감</span>' if full else ""
    place_text = (room.get("location") or "").strip()
    with st.container(border=True, key=f"room_card_{room['id']}"):
        left, right = st.columns([5.2, 1.1], vertical_alignment="center", gap="medium")
        with left:
            location_meta = f' &nbsp; 📍 {e(place_text)}' if place_text else ""
            st.markdown(
                f'<div class="cm-room"><div class="cm-room-top">'
                f'<div class="cm-icon">{icon}</div><div class="cm-room-info">'
                f'<div class="cm-room-title">{e(room["title"])} {status}</div>'
                f'<div class="cm-meta">🗓 {e(room["day"])}요일 {e(room["start"])} ~ {e(room["end"])}'
                f' &nbsp; 👥 {room["people"]}/{room["capacity"]}명 &nbsp; · 방 #{room["id"]}'
                f'{location_meta}</div>'
                f'<span class="cm-tag">#{e(room["activity"])}</span>'
                f'</div></div></div>', unsafe_allow_html=True,
            )
        with right:
            if st.button("방 보기 →", key=f"open_{room['id']}", use_container_width=True):
                navigate("room", room["id"])


def home_page(): #list_rooms() + room_card()로 메인화면 구성 함수 / 홈페이지 함수
    header()
    show_flash()
    st.markdown('<div class="cm-title">매칭방 둘러보기</div><div class="cm-muted">기존 57개 방과 새로 생성한 방을 검색할 수 있습니다.</div>', unsafe_allow_html=True)

    search_area, create_area = st.columns([5.7, 1.3], vertical_alignment="bottom", gap="small") # 검색 입력 + 검색 버튼 + 방 생성 버튼을 모두 같은 가로줄에 배치
    with search_area:
        with st.form("search_form", border=False):
            input_col, submit_col = st.columns([5, 1.1], vertical_alignment="bottom", gap="small")
            with input_col:
                q = st.text_input("방 제목 또는 활동 검색", value=st.session_state.search_keyword, #검색어 값 변수 
                                  placeholder="예: 농구, 게임, 스터디", label_visibility="collapsed")
            with submit_col:
                submit = st.form_submit_button("검색", use_container_width=True) #검색 누르면 submit = true
            if submit:
                st.session_state.search_keyword = q.strip() #검색어 입력시 양쪽 공백 제거
                st.session_state.sort_label = SORT_LABELS[0] #정렬 기준을 기본값으로
                st.rerun()
    with create_area:
        if st.button("＋ 방 생성", type="primary", use_container_width=True):
            navigate("create") #방 생성 버튼 누르면 방생성 화면 객체로 이동

    if st.session_state.search_keyword:
        st.caption(f'현재 검색어: {st.session_state.search_keyword}')
        if st.button("✕ 검색어 취소", key="clear_search"): #검색어 입력후 검색어 취소시 검색어 값 초기화후 종료
            st.session_state.search_keyword = ""
            st.rerun()

    st.selectbox("정렬 및 시간대 조건", SORT_LABELS, key="sort_label") #정렬 조건중 시간/인원/선호 - 입력만
    if st.session_state.sort_label == "시간대별": #정렬 조건중 시간대별 선택 시 일정을 자세히 입력받음
        a, b, c = st.columns([1, 1, 1])
        with a:
            day = st.selectbox("요일", DAYS, key="filter_day")
        with b:
            start = st.time_input("검색 시작", value=time(12, 0), step=1800, key="filter_start")
        with c:
            end = st.time_input("검색 종료", value=time(15, 0), step=1800, key="filter_end")
        if start >= end:
            st.warning("종료 시간은 시작 시간보다 늦어야 합니다.")
            st.session_state.time_condition = None
        else:
            st.session_state.time_condition = (day, start.strftime("%H:%M"), end.strftime("%H:%M"))
    else:
        st.session_state.time_condition = None

    found = list_rooms() #검색 알고리즘 시작
    st.markdown(f"**검색된 매칭방 {len(found)}개**")
    if not found:
        st.info("조건에 맞는 매칭방이 없습니다. 검색어 또는 시간대를 변경해 보십시오.")
    else:
        for room in found:
            room_card(room) #검색된 매칭방을 ui로 구현


def create_page(): #방 생성 페이지 함수
    header("새로운 매칭방 만들기")
    if st.button("← 목록으로 돌아가기"): #목록으로 돌아가기 - home_page로 이동
        navigate("home")
    st.markdown("### 방 생성")
    with st.form("room_creation", clear_on_submit=False): #방 생성시 room데이터 입력받음
        title = st.text_input("방 제목 *", max_chars=80, placeholder="예: 점심 농구 같이 해요")
        activity = st.selectbox("활동 *", ACTIVITIES)
        day = st.selectbox("요일 *", DAYS)
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            start = st.time_input("시작 시간 *", value=time(12, 0), step=1800)
        with col2:
            end = st.time_input("종료 시간 *", value=time(13, 0), step=1800)
        with col3:
            capacity = st.number_input("정원 (방장 포함) *", min_value=1, max_value=100, value=4, step=1)
        location = st.text_input("장소", max_chars=120, placeholder="예: 교내 운동장, 중앙도서관 2층")
        notes = st.text_area("기타", max_chars=1500,
                             placeholder="준비물, 모임 안내, 참가 전 참고사항 등을 자유롭게 작성하세요.",
                             height=125)
        st.caption("장소와 기타는 참고 정보로만 표시되며 검색·매칭 정렬에는 사용되지 않습니다.") #부가 설명
        st.caption("방을 생성하면 현재 인원은 자동으로 1명(방장)으로 설정됩니다.") #부가 설명
        submitted = st.form_submit_button("방 생성하기", type="primary", use_container_width=True)
    if submitted: # 윗줄의 submitted 활성화시 room_page로 이동
        if not title.strip(): #예외처리
            st.error("방 제목을 입력하십시오.")
        elif start >= end: #예외처리
            st.error("종료 시간은 시작 시간보다 늦어야 합니다.")
        else: #정상작동
            room_id = st.session_state.next_room_id
            st.session_state.next_room_id += 1
            new_room = { #입력받은 정보로 room list한개 제작
                "id": room_id, "title": title.strip(), "activity": activity,
                "day": day, "start": start.strftime("%H:%M"), "end": end.strftime("%H:%M"),
                "people": 1, "capacity": int(capacity),
                "owner_id": st.session_state.user_id, "chats": [],
                "location": location.strip(), "notes": notes.strip(),
            }
            st.session_state.rooms.append(new_room) #기존 room리스트에 추가
            st.session_state.created_ids.add(room_id) #기존 room리스트에 id추가
            flash(f"방 #{room_id}이 생성되었습니다.")
            navigate("room", room_id)


def join(room): #해당 방 한개의 데이터만 / 방참가 함수
    room_id = room["id"]
    if room.get("owner_id") == st.session_state.user_id: #예외처리
        st.warning("내가 만든 방입니다.")
    elif room_id in st.session_state.joined_ids: #예외처리
        st.warning("이미 참가한 방입니다.")
    elif room["people"] >= room["capacity"]: #예외처리
        st.warning("방 정원이 마감되었습니다.")
    else: #정상작동
        room["people"] += 1
        st.session_state.joined_ids.add(room_id) #참가방 id 저장
        flash("방에 참가했습니다. 채팅을 이용할 수 있습니다.")
        st.rerun() 


def leave(room): #방 떠나기 함수
    room_id = room["id"]
    if room_id in st.session_state.joined_ids: #방에 참가중인지 확인
        room["people"] = max(0, room["people"] - 1)
        st.session_state.joined_ids.discard(room_id) #참가방 id 제거
        flash("방에서 나왔습니다.")
    navigate("home") #home_page로 이동


def remove_room(room, action): #방 삭제/마감 함수
    st.session_state.rooms.remove(room) #room리스트에서 해당 방 삭제
    st.session_state.created_ids.discard(room["id"]) #생성방 id삭제
    st.session_state.joined_ids.discard(room["id"]) #참가방 id삭제
    flash("방이 마감되었습니다." if action == "마감" else "방이 삭제되었습니다.")
    navigate("home") #home_page로 이동


def room_page(): #방 페이지 함수
    selected_room_id = st.session_state.get("selected_room_id") #(room,id)의 id를 저장
    room = find_room(selected_room_id) #방찾기 함수로 방정보 가져옴
    if room is None: #예외처리
        flash("해당 방을 찾을 수 없습니다.")
        navigate("home") #home_page로 이동
    is_owner = room.get("owner_id") == st.session_state.user_id #방장인지 확인
    joined = room["id"] in st.session_state.joined_ids #참가자인지 확인
    can_chat = is_owner or joined #방장or참가자면 채팅허락
    header("매칭방 상세 및 채팅")
    if st.button("← 매칭방 목록"): #매칭방 목록 - 버튼 누르면 home_page로 이동
        navigate("home")
    show_flash() 
    location_info = room.get("location", "") #장소 데이터 불러옴
    notes_info = room.get("notes", "") #기타 데이터 불러옴
    extra_html = (
        f'<div class="cm-extra">📍 장소: {e(location_info)}</div>' if location_info else ""
    )
    extra_html += (
        f'<div class="cm-extra">📝 기타: {e(notes_info)}</div>' if notes_info else ""
    )
    st.markdown( #room(1)데이터 ui
        '<div class="cm-hero">'
        f'<div class="cm-title">{ACTIVITY_ICONS.get(room["activity"], "🎯")} {e(room["title"])}</div>'
        f'<div class="cm-muted" style="margin-top:9px">'
        f'#{e(room["activity"])} &nbsp; · &nbsp; {e(room["day"])}요일 {e(room["start"])} ~ {e(room["end"])}'
        f' &nbsp; · &nbsp; 👥 {room["people"]}/{room["capacity"]}명'
        f' &nbsp; · &nbsp; 방 ID {room["id"]}</div>{extra_html}</div>',
        unsafe_allow_html=True,
    )

    if is_owner: #방장일시
        st.info("방장으로 참여 중입니다. 방 마감과 삭제는 모두 목록에서 방을 제거합니다.")
        c1, c2 = st.columns(2)
        with c1: #방 마감/삭제 ui + 입력 처리
            if st.button("방 마감", use_container_width=True):
                remove_room(room, "마감")
        with c2:
            if st.button("방 삭제", use_container_width=True):
                remove_room(room, "삭제")
    elif joined: #참가자일시 - (방참가 + 방나가기) ui + 입력 처리
        if st.button("방 나가기", use_container_width=True, type="primary"):
            leave(room)
    else:
        if st.button("방 참가하기" if room["people"] < room["capacity"] else "정원 마감", 
                     use_container_width=True, type="primary", disabled=room["people"] >= room["capacity"]):
            join(room)
    #room(2) ui 구현
    chat_col, info_col = st.columns([2.1, 1], gap="large")
    with chat_col:
        st.markdown("### 💬 채팅")
        chats = room.get("chats", []) #채팅 입력받음 - 초기데이터에 저장
        if chats:
            for message in chats:
                st.markdown(
                    f'<div class="cm-chat"><div class="cm-chat-author">{e(message["name"])}</div>'
                    f'<div class="cm-chat-text">{e(message["text"])}</div></div>',
                    unsafe_allow_html=True,
                )
        else:
            st.info("아직 채팅이 없습니다.")
        if can_chat:
            with st.form(f"chat_form_{room['id']}", clear_on_submit=True):
                message = st.text_input("메시지", placeholder="메시지를 입력하세요...", max_chars=500)
                sent = st.form_submit_button("전송", type="primary", use_container_width=True)
                if sent and message.strip():
                    room.setdefault("chats", []).append({
                        "user_id": st.session_state.user_id,
                        "name": user()["name"],
                        "text": message.strip(),
                        "time": datetime.now().strftime("%H:%M"),
                    })
                    st.rerun()
                elif sent:
                    st.warning("빈 메시지는 전송할 수 없습니다.")
        else:
            st.caption("채팅을 작성하려면 먼저 방에 참가하십시오.")
    with info_col:
        st.markdown("### 👥 참가 정보")
        st.metric("현재 인원", f'{room["people"]} / {room["capacity"]}')
        st.progress(min(room["people"] / room["capacity"], 1.0))
        st.write("**활동**", room["activity"])
        st.write("**요일**", room["day"])
        st.write("**시간**", f'{room["start"]} ~ {room["end"]}')
        st.write("**장소**", room.get("location") or "미입력")
        st.write("**기타**", room.get("notes") or "미입력")
        st.write("**내 역할**", "방장" if is_owner else ("참가자" if joined else "미참가"))
        st.caption("기존 방에는 장소·기타가 없을 수 있으며, 참가자 이름 목록은 현재 데이터에 없습니다.")


# Streamlit의 기본 멀티페이지 라우터를 이용합니다.
# URL 경로는 /, /create, /room이며 선택한 방 ID는 브라우저 세션 상태에 보관합니다.
init_state()
HOME_PAGE = st.Page(home_page, title="매칭방 둘러보기", url_path="home", default=True)
CREATE_PAGE = st.Page(create_page, title="방 생성", url_path="create")
ROOM_PAGE = st.Page(room_page, title="방 상세 및 채팅", url_path="room")
st.navigation([HOME_PAGE, CREATE_PAGE, ROOM_PAGE], position="hidden").run()
