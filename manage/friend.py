"""Framework-independent friend and block management."""

class FriendManager:
    def __init__(self, user_ids):
        self.user_ids = set(user_ids)
        self.friends = set()
        self.blocks = set()

    def _check(self, actor, target):
        if actor not in self.user_ids or target not in self.user_ids:
            raise ValueError('존재하지 않는 사용자입니다.')
        if actor == target:
            raise ValueError('자기 자신은 대상이 될 수 없습니다.')

    def get_friends(self, actor):
        return [uid for uid in self.user_ids if uid != actor and
                frozenset((actor, uid)) in self.friends]

    def add_friend(self, actor, target):
        self._check(actor, target)
        if (actor, target) in self.blocks or (target, actor) in self.blocks:
            raise ValueError('차단 관계에서는 친구를 추가할 수 없습니다.')
        pair = frozenset((actor, target))
        if pair in self.friends:
            raise ValueError('이미 친구입니다.')
        self.friends.add(pair)

    def remove_friend(self, actor, target):
        self._check(actor, target)
        self.friends.discard(frozenset((actor, target)))

    def block_user(self, actor, target):
        self._check(actor, target)
        self.blocks.add((actor, target))
        self.remove_friend(actor, target)

    def unblock_user(self, actor, target):
        self._check(actor, target)
        self.blocks.discard((actor, target))

    def get_blocked_users(self, actor):
        return [target for source, target in self.blocks if source == actor]
