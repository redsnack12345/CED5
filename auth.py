# auth.py: 사용자 인증 핵심 로직. 화면 입력 및 출력은 별도 모듈에서 담당한다.
import hashlib  # PBKDF2-HMAC-SHA256 연산
import secrets  # 암호학적으로 안전한 무작위 Salt 생성
import hmac     # 해시 결과를 비교할 때 시간 차이 노출을 줄이는 함수 제공
from data import users, user_id_counter, get_user_by_id
from verification import find_school

ITERATIONS = 600_000  # PBKDF2 반복 횟수
MIN_PASSWORD_LENGTH = 8  # 프로토타입 임시 정책, 팀 협의 후 변경 가능


def check_membership(choice):
    """입력: 기존 회원 여부(bool). 반환: 화면 식별자(str) 또는 정수 0."""
    # 사용자 스스로 회원 여부를 선택하는 단계이며 실제 계정 검사는 아니다.
    if choice is True:
        return 'login'
    if choice is False:
        return 'register'
    return 0


def check_id(username):
    """입력: 아이디(str). 반환: 사용 가능한 아이디인지 여부(bool)."""
    username = username.strip()
    return bool(username) and username not in users


def check_password(password):
    """입력: 비밀번호(str). 반환: 최소 길이 충족 여부(bool)."""
    return len(password) >= MIN_PASSWORD_LENGTH


def hash_password(password, salt, iterations=ITERATIONS):
    """비밀번호(str), Salt(bytes), 반복 횟수(int)를 받아 32바이트 결과를 반환한다."""
    # 로그인할 때는 새로운 Salt가 아니라 회원가입 당시의 Salt와 반복 횟수를 사용한다.
    return hashlib.pbkdf2_hmac(
        'sha256',                  # HMAC에 사용하는 해시함수
        password.encode('utf-8'),  # Python 문자열을 바이트로 변환
        salt,                      # 회원마다 생성한 무작위 값
        iterations,                # 추측 공격에 필요한 연산 비용을 높인다.
        dklen=32                   # 결과 길이: 256비트
    )


def result(success, message, user_id=None, next_page=None):
    """UI에 전달할 공통 반환값(dict). 비밀번호 관련 비밀 정보는 제외한다."""
    return {'success': success, 'message': message,
            'user_id': user_id, 'next_page': next_page}


def register(username, password, confirm, name, department, school):
    """회원가입 입력값(str)을 검사하고 결과 딕셔너리를 반환한다."""
    # 아이디와 일반 회원 정보의 앞뒤 공백을 제거한다. 비밀번호는 그대로 사용한다.
    username, name, department = username.strip(), name.strip(), department.strip()
    if not all([username, password, name, department, school.strip()]):
        return result(False, '모든 정보를 입력하세요.')
    if not check_id(username):
        return result(False, '이미 존재하는 아이디입니다.')
    if not check_password(password):
        return result(False, f'비밀번호는 {MIN_PASSWORD_LENGTH}자 이상이어야 합니다.')
    if password != confirm:
        return result(False, '비밀번호가 일치하지 않습니다.')

    # 약칭을 입력해도 공통 저장소에는 정식 학교 이름을 저장한다.
    school = find_school(school)
    if school == 0:
        return result(False, '학교를 정확하게 입력하세요.')

    # 사용자마다 별도의 Salt를 발급한다. 비밀번호 원문은 저장하지 않는다.
    salt = secrets.token_bytes(16)
    user_id = next(user_id_counter)
    users[username] = {
        'user_id': user_id,
        'username': username,
        'password_hash': hash_password(password, salt),
        'salt': salt,
        'iterations': ITERATIONS,
        'name': name,
        'department': department,
        'school': school,
        'verified': False,  # 학교 인증 여부
        'is_banned': False  # 관리자의 이용 제재 여부: 학교 인증과 별개
    }
    return result(True, '회원가입 성공', user_id, 'login')


def login(username, password):
    """아이디와 비밀번호를 확인하고 UI용 결과(dict)를 반환한다."""
    user = users.get(username.strip())
    if user is None:
        return result(False, '아이디 또는 비밀번호 오류')
    # 기존 설정과 동일한 값으로 PBKDF2 연산을 수행한다.
    new_hash = hash_password(password, user['salt'], user['iterations'])
    # 비밀번호 원문 대신 계산된 결과끼리 비교한다.
    if not hmac.compare_digest(new_hash, user['password_hash']):
        return result(False, '아이디 또는 비밀번호 오류')
    if user['is_banned']:
        return result(False, '이용이 정지된 계정입니다.')
    # 미인증 회원도 로그인은 가능하지만 매칭 기능은 이용할 수 없다.
    page = 'profile' if user['verified'] else 'verification'
    return result(True, '로그인 성공', user['user_id'], page)


def can_use_service(user_id):
    """회원 존재, 학교 인증, 제재 상태를 확인하고 bool을 반환한다."""
    # 호출자는 현재 로그인한 사용자의 ID를 전달해야 한다.
    user = get_user_by_id(user_id)
    return bool(user and user['verified'] and not user['is_banned'])


def get_public_user(user_id):
    """다른 모듈용 기본 정보(dict) 또는 None. 해시와 Salt는 반환하지 않는다."""
    user = get_user_by_id(user_id)
    if user is None:
        return None
    fields = ('user_id', 'name', 'school', 'department', 'verified', 'is_banned')
    return {field: user[field] for field in fields}
