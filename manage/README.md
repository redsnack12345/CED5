# 참여자 및 친구 관리 모듈

## 실행 및 테스트
`python test_manage.py`

## 친구 관리 함수
- `search_users(actor_id, keyword="")`: 전체 사용자 검색
- `get_room_recommendations(actor_id, room)`: 같은 방 참여자 추천
- `send_friend_request(actor_id, target_id)`: 친구 요청
- `get_received_requests(actor_id)` / `get_sent_requests(actor_id)`: 요청 목록
- `accept_friend_request(actor_id, sender_id)`: 수락 및 양방향 친구 성립
- `reject_friend_request(actor_id, sender_id)`: 거절 및 요청 삭제
- `cancel_friend_request(actor_id, target_id)`: 보낸 요청 취소
- `get_friends`, `remove_friend`, `block_user`, `unblock_user`, `get_blocked_users`

## 참여자 관리 함수
- `get_participants(room)`, `is_participant(room, user_id)`
- `kick_participant(room, actor_id, target_id)`

현재는 메모리 저장 프로토타입입니다. 서버 종료 시 데이터가 사라집니다.
실제 프로젝트 연결 시 로그인 사용자 ID를 서버에서 확인하고, 친구/요청/차단 상태를 공통 저장소에 영구 저장해야 합니다.
