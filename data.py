# data.py: 모든 인증 기능에서 공통으로 사용하는 메모리 저장소
from itertools import count

# 아이디를 key로, 회원 정보를 value로 저장한다.
# 별도의 DB를 사용하지 않으므로 프로그램 종료 시 데이터가 사라진다.
users = {}
# 사용자 고유 번호를 key로 증명서 제출 정보를 저장한다.
verification_requests = {}
# 같은 실행 중에 회원 번호를 중복 발급하지 않도록 한다.
user_id_counter = count(1)


def get_user_by_id(user_id):
    """고유 ID(int)로 회원을 찾아 내부 회원 딕셔너리 또는 None을 반환한다."""
    for user in users.values():
        if user['user_id'] == user_id:
            return user
    return None
