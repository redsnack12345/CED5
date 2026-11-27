"""Framework-independent room membership operations."""

def get_participants(room):
    return list(room['participants'])


def kick_participant(room, actor_id, target_id):
    """Remove a member in place; return the new member count."""
    if actor_id != room['owner_id']:
        raise PermissionError('방장만 추방할 수 있습니다.')
    if target_id == room['owner_id']:
        raise ValueError('방장은 추방할 수 없습니다.')
    if target_id not in room['participants']:
        raise ValueError('참여 중인 사용자가 아닙니다.')
    room['participants'].remove(target_id)
    return len(room['participants'])
