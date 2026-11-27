"""매칭방 참여자 관리 모듈."""
def _validate_room(room):
    if not isinstance(room, dict):
        raise TypeError("방 정보는 dict여야 합니다.")
    if "owner_id" not in room or "participants" not in room:
        raise ValueError("방 정보에 owner_id와 participants가 필요합니다.")
    if not isinstance(room["participants"], list):
        raise TypeError("participants는 list여야 합니다.")

def get_participants(room):
    """현재 매칭방 참여자 ID 목록을 반환합니다."""
    _validate_room(room)
    return list(room["participants"])

def is_participant(room, user_id):
    """사용자가 현재 매칭방에 참여 중인지 반환합니다."""
    _validate_room(room)
    return user_id in room["participants"]

def kick_participant(room, actor_id, target_id):
    """방장만 다른 참여자를 추방하고 변경 후 인원수를 반환합니다."""
    _validate_room(room)
    if actor_id != room["owner_id"]:
        raise PermissionError("방장만 참여자를 추방할 수 있습니다.")
    if target_id == room["owner_id"]:
        raise ValueError("방장은 추방할 수 없습니다.")
    if target_id not in room["participants"]:
        raise ValueError("현재 방에 참여 중인 사용자가 아닙니다.")
    room["participants"].remove(target_id)
    return len(room["participants"])
