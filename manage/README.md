# 참여자 및 친구 관리 모듈 (독립 프로토타입)

Python 표준 라이브러리만 사용합니다. `python test_manage.py`로 테스트합니다.

- `participant.py`: `get_participants(room)`, `kick_participant(room, actor_id, target_id)`.
- 방 데이터 예시: `{'owner_id': 1, 'participants': [1, 2, 3]}`. 추방은 목록을 직접 변경하며 변경 후 인원수를 반환합니다.
- `friend.py`: `FriendManager(user_ids)` 생성 후 `add_friend`, `remove_friend`, `get_friends`, `block_user`, `unblock_user`, `get_blocked_users` 사용.
- 친구는 즉시 양방향 등록, 차단은 단방향이며 친구 관계를 삭제합니다. 어느 방향으로든 차단된 상태에서는 친구 등록을 금지합니다. 차단 해제는 친구 관계를 복원하지 않습니다.

임시 규칙이며 팀의 합의에 따라 변경할 수 있습니다. 현재 메모리 기반으로 실행 종료 시 데이터가 사라집니다. 로그인 연동, 영구 저장, UI, 재참여 제한 및 매칭 차단은 미구현입니다. 통합할 때 actor_id는 서버에서 인증된 사용자 ID로 전달해야 하며 데이터 변경을 공통 저장소에 반영해야 합니다. 기존 app.py는 변경하지 않습니다.
