"""친구 요청/친구/차단 관리 모듈. 현재 메모리 저장 방식입니다."""
class FriendManager:
    def __init__(self, user_ids):
        # dict이면 {user_id: nickname}, iterable이면 사용자 ID 목록
        self.users = dict(user_ids) if isinstance(user_ids, dict) else {uid: str(uid) for uid in user_ids}
        self.friends = set()       # frozenset({user_a, user_b})
        self.requests = set()      # (sender_id, receiver_id)
        self.blocks = set()        # (blocker_id, blocked_id)

    def _check_user(self, user_id):
        if user_id not in self.users:
            raise ValueError("존재하지 않는 사용자입니다.")

    def _check_pair(self, actor_id, target_id):
        self._check_user(actor_id)
        self._check_user(target_id)
        if actor_id == target_id:
            raise ValueError("자기 자신을 대상으로 할 수 없습니다.")

    def _is_blocked_either_way(self, a, b):
        return (a, b) in self.blocks or (b, a) in self.blocks

    def search_users(self, actor_id, keyword=""):
        """전체 가입자 검색. 본인과 차단 관계 사용자는 제외합니다."""
        self._check_user(actor_id)
        key = str(keyword).strip().casefold()
        return [
            {"user_id": uid, "nickname": str(name)}
            for uid, name in self.users.items()
            if uid != actor_id
            and not self._is_blocked_either_way(actor_id, uid)
            and (not key or key in str(name).casefold() or key in str(uid).casefold())
        ]

    def get_room_recommendations(self, actor_id, room):
        """현재 같은 방 참여자를 추천합니다. 방 퇴장 시 다음 조회부터 제외됩니다."""
        self._check_user(actor_id)
        from participant import get_participants
        members = get_participants(room)
        return [
            {"user_id": uid, "nickname": str(self.users[uid])}
            for uid in members
            if uid != actor_id and uid in self.users
            and not self._is_blocked_either_way(actor_id, uid)
        ]

    def get_friends(self, actor_id):
        self._check_user(actor_id)
        result = [next(iter(pair - {actor_id})) for pair in self.friends if actor_id in pair]
        return sorted(result, key=str)

    def get_sent_requests(self, actor_id):
        self._check_user(actor_id)
        result = [{"user_id": b, "nickname": str(self.users[b])}
                  for a, b in self.requests if a == actor_id]
        return sorted(result, key=lambda x: str(x["user_id"]))

    def get_received_requests(self, actor_id):
        self._check_user(actor_id)
        result = [{"user_id": a, "nickname": str(self.users[a])}
                  for a, b in self.requests if b == actor_id]
        return sorted(result, key=lambda x: str(x["user_id"]))

    def send_friend_request(self, actor_id, target_id):
        self._check_pair(actor_id, target_id)
        if self._is_blocked_either_way(actor_id, target_id):
            raise ValueError("차단 관계에서는 친구 요청을 보낼 수 없습니다.")
        pair = frozenset((actor_id, target_id))
        if pair in self.friends:
            raise ValueError("이미 친구인 사용자입니다.")
        if (actor_id, target_id) in self.requests:
            raise ValueError("이미 친구 요청을 보냈습니다.")
        if (target_id, actor_id) in self.requests:
            return "incoming_request_exists"
        self.requests.add((actor_id, target_id))
        return "pending"

    def accept_friend_request(self, actor_id, sender_id):
        self._check_pair(actor_id, sender_id)
        request = (sender_id, actor_id)
        if request not in self.requests:
            raise ValueError("수락할 친구 요청이 없습니다.")
        if self._is_blocked_either_way(actor_id, sender_id):
            self.requests.discard(request)
            raise ValueError("차단 관계에서는 친구가 될 수 없습니다.")
        self.requests.remove(request)
        self.friends.add(frozenset((actor_id, sender_id)))
        return True

    def reject_friend_request(self, actor_id, sender_id):
        self._check_pair(actor_id, sender_id)
        request = (sender_id, actor_id)
        if request not in self.requests:
            raise ValueError("거절할 친구 요청이 없습니다.")
        self.requests.remove(request)
        return True

    def cancel_friend_request(self, actor_id, target_id):
        self._check_pair(actor_id, target_id)
        request = (actor_id, target_id)
        if request not in self.requests:
            raise ValueError("취소할 친구 요청이 없습니다.")
        self.requests.remove(request)
        return True

    def remove_friend(self, actor_id, target_id):
        self._check_pair(actor_id, target_id)
        pair = frozenset((actor_id, target_id))
        if pair not in self.friends:
            raise ValueError("친구 관계가 아닙니다.")
        self.friends.remove(pair)

    def block_user(self, actor_id, target_id):
        self._check_pair(actor_id, target_id)
        self.blocks.add((actor_id, target_id))
        self.friends.discard(frozenset((actor_id, target_id)))
        self.requests.discard((actor_id, target_id))
        self.requests.discard((target_id, actor_id))

    def unblock_user(self, actor_id, target_id):
        self._check_pair(actor_id, target_id)
        if (actor_id, target_id) not in self.blocks:
            raise ValueError("차단한 사용자가 아닙니다.")
        self.blocks.remove((actor_id, target_id))

    def get_blocked_users(self, actor_id):
        self._check_user(actor_id)
        return sorted([b for a, b in self.blocks if a == actor_id], key=str)

    # 기존 데모 코드 호환: 이제 즉시 친구가 아니라 요청만 보냅니다.
    def add_friend(self, actor_id, target_id):
        return self.send_friend_request(actor_id, target_id)
