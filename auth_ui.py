# auth_ui.py - Campus Match 사용자 인증 화면 (Streamlit)
# 기존 auth.py, data.py, verification.py는 그대로 사용한다.
# 실행: python -m streamlit run auth_ui.py
import streamlit as st
from pathlib import Path
from tempfile import TemporaryDirectory

# 인증 알고리즘은 UI에서 다시 작성하지 않고 기존 함수를 호출한다.
from auth import (
    check_membership, register, login, get_public_user,
    can_use_service, MIN_PASSWORD_LENGTH,
)
from verification import find_school, submit_certificate, MAX_PDF_BYTES
from data import verification_requests


# 1. 페이지 설정 및 브라우저 세션 초기화
st.set_page_config(page_title="Campus Match", page_icon="🎓", layout="centered")

# Streamlit은 사용자 조작 후 스크립트를 다시 실행한다.
# session_state에는 현재 브라우저의 화면 및 로그인 상태만 저장한다.
# 전체 회원 정보는 기존 data.py의 공통 딕셔너리에 저장된다.
if "page" not in st.session_state:
    st.session_state.page = "start"
if "current_user_id" not in st.session_state:
    st.session_state.current_user_id = None


def move_page(page):
    """화면 식별자(str)를 세션에 저장하고 새 화면을 표시한다."""
    st.session_state.page = page
    st.rerun()


def show_flash():
    """화면 이동 직전에 저장된 성공/안내 메시지를 한 번 표시한다."""
    message = st.session_state.pop("auth_flash", None)
    if message:
        st.info(message)


def logout():
    """현재 브라우저의 로그인 상태만 초기화한다. 회원 정보는 유지한다."""
    st.session_state.current_user_id = None
    move_page("start")


# 2. 초기 화면 - 사용자가 기존 회원인지 직접 선택한다.
def start_page():
    show_flash()
    st.subheader("이미 회원가입을 하셨습니까?")
    if st.button("예, 기존 회원입니다.", key="start_login"):
        # True를 전달하면 auth.py에서 'login'을 반환한다.
        move_page(check_membership(True))
    if st.button("아니오, 회원가입을 하겠습니다.", key="start_register"):
        # False를 전달하면 'register'를 반환한다.
        move_page(check_membership(False))


# 3. 회원가입 - 학교 검색 및 필수 정보 입력
def register_page():
    st.subheader("회원가입")
    keyword = st.text_input("학교 검색", placeholder="경북대, 영남대, 계명대")

    # find_school(): 정식 학교 이름(str) 또는 정수 0을 반환한다.
    # 모호한 검색어나 지원하지 않는 학교는 0으로 처리된다.
    school = find_school(keyword)
    if keyword.strip():
        if school == 0:
            st.error("지원 학교의 이름을 정확하게 입력하세요.")
        else:
            st.success(f"검색된 학교: {school}")
    st.caption("지원 학교: 경북대학교 · 영남대학교 · 계명대학교")

    # form을 사용하면 제출 버튼을 누를 때 입력값을 한꺼번에 받는다.
    # type='password'는 비밀번호가 화면에 그대로 표시되지 않게 한다.
    with st.form("register_form", clear_on_submit=True):
        username = st.text_input("아이디")
        password = st.text_input("비밀번호", type="password")
        st.caption(f"비밀번호는 {MIN_PASSWORD_LENGTH}자 이상이어야 합니다.")
        confirm = st.text_input("비밀번호 확인", type="password")
        name = st.text_input("이름")
        department = st.text_input("학과")
        submitted = st.form_submit_button("회원가입", type="primary")

    if submitted:
        if school == 0:
            st.error("학교를 먼저 검색하세요.")
        else:
            # 아이디 중복 검사, 비밀번호 검증, PBKDF2 해시 연산 및
            # 딕셔너리 저장은 기존 auth.py의 register()에서 수행한다.
            result = register(username, password, confirm, name, department, school)
            if result["success"]:
                st.session_state.auth_flash = result["message"]
                move_page(result["next_page"])
            else:
                st.error(result["message"])

    if st.button("처음으로 돌아가기", key="register_back"):
        move_page("start")


# 4. 로그인 - 기존 해시값 비교 및 이용자 제재 확인
def login_page():
    st.subheader("로그인")
    show_flash()
    with st.form("login_form", clear_on_submit=True):
        username = st.text_input("아이디")
        password = st.text_input("비밀번호", type="password")
        submitted = st.form_submit_button("로그인", type="primary")

    if submitted:
        # login()은 기존 Salt와 반복 횟수로 비밀번호를 다시 연산한다.
        # 해시 일치 및 이용 정지 여부 검사 결과가 딕셔너리로 반환된다.
        result = login(username, password)
        if result["success"]:
            # 사용자 ID만 세션에 저장한다. 비밀번호와 해시는 저장하지 않는다.
            st.session_state.current_user_id = result["user_id"]
            st.session_state.auth_flash = result["message"]
            move_page(result["next_page"])
        else:
            st.error(result["message"])

    if st.button("아이디 / 비밀번호 찾기", key="login_recovery"):
        move_page("recovery")
    if st.button("처음으로 돌아가기", key="login_back"):
        move_page("start")


# 5. 계정 복구 - 본인 확인 수단이 정해지기 전에는 실제 복구를 허용하지 않는다.
def recovery_page():
    st.subheader("아이디 / 비밀번호 찾기")
    st.info("안전한 본인 확인 방식이 확정된 후 구현할 기능입니다.")
    if st.button("로그인으로 돌아가기", key="recovery_back"):
        move_page("login")


# 6. 증명서 제출 - 업로드한 PDF를 기존 검사 함수에 전달한다.
def certificate_form(user_id):
    st.subheader("재학·등록증명서 제출")
    st.caption("텍스트 기반 PDF만 지원합니다. 시연에는 가상 증명서를 사용하세요.")
    uploaded = st.file_uploader("증명서 PDF", type=["pdf"], key="certificate_pdf")

    if st.button("증명서 제출", key="certificate_submit", type="primary"):
        if uploaded is None:
            st.error("파일을 선택하세요.")
        elif uploaded.size > MAX_PDF_BYTES:
            st.error(f"PDF는 {MAX_PDF_BYTES // (1024 * 1024)} MiB 이하여야 합니다.")
        else:
            try:
                # 기존 submit_certificate()는 파일 경로를 입력받는다.
                # 업로드 바이트를 임시 파일에 저장하고 검사 직후 자동 삭제한다.
                # 사용자 파일명을 경로로 쓰지 않고 고정된 파일명을 사용한다.
                with TemporaryDirectory() as folder:
                    path = Path(folder) / "certificate.pdf"
                    path.write_bytes(uploaded.getvalue())
                    result = submit_certificate(user_id, path)
            except OSError:
                st.error("임시 파일을 만들 수 없습니다.")
            else:
                if result["success"]:
                    st.success(result["message"])
                else:
                    st.error(result["message"])

    # 제출 기록은 data.py에 있으므로 화면 재실행 후에도 확인할 수 있다.
    # 현재 로그인한 사용자 자신의 검사 결과만 표시한다.
    request = verification_requests.get(user_id)
    if request is not None:
        check = request["check_result"]
        if check["matched"]:
            st.success("증명서 필수 정보가 일치합니다.")
        else:
            st.warning("증명서 정보 불일치: " + ", ".join(check["missing"]))
        # 정보가 일치해도 실제 재학 상태나 증명서 진위가 확인된 것은 아니다.
        st.info("최종 검토 대기 중 · 최종 승인 기능은 아직 구현되지 않았습니다.")


# 7. 로그인 후 화면 - 현재 계정의 접근 권한을 매번 확인한다.
def member_page():
    user_id = st.session_state.current_user_id
    user = get_public_user(user_id)
    # 로그인하지 않았거나 계정이 정지되면 보호된 화면을 표시하지 않는다.
    if user is None or user["is_banned"]:
        st.session_state.auth_flash = "이용할 수 없는 계정이거나 로그인이 필요합니다."
        logout()
        return

    show_flash()
    st.subheader(f'{user["name"]}님, 환영합니다!')
    st.write("학교:", user["school"])
    st.write("학과:", user["department"])
    if user["verified"]:
        st.success("학교 인증 완료")
    else:
        st.warning("학교 인증 미완료")
        certificate_form(user_id)

    # 매칭 담당자와 통합할 때 이 함수의 bool 반환값을 활용할 수 있다.
    if can_use_service(user_id):
        st.success("매칭 서비스 이용 가능")
        st.caption("프로필 및 매칭 화면은 추후 팀원 코드와 연결합니다.")
    else:
        st.warning("현재 매칭 서비스 이용 제한")

    if st.button("로그아웃", key="member_logout"):
        logout()


# 8. 전체 화면 실행부 - 현재 화면 식별자에 해당하는 함수만 호출한다.
st.title("🎓 Campus Match")
st.caption("교내 학생 매칭 서비스 · 로컬 시연용")
st.divider()

pages = {
    "start": start_page,
    "register": register_page,
    "login": login_page,
    "recovery": recovery_page,
    "verification": member_page,
    "profile": member_page,
}
pages.get(st.session_state.page, start_page)()
