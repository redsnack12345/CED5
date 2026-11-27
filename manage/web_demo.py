"""Local HTML demo using the existing management modules. python web_demo.py"""
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import json
import webbrowser
from participant import get_participants, kick_participant, is_participant
from friend import FriendManager

USERS = {1: '김민수', 2: '이지훈', 3: '박서연', 4: '최유진'}

def reset():
    global room, manager
    room = {'owner_id': 1, 'participants': [1, 2, 3]}
    manager = FriendManager(USERS)

reset()

def state(actor, keyword=""):
    if type(actor) is not int or actor not in USERS:
        raise ValueError('존재하지 않는 사용자입니다.')
    members = get_participants(room)
    return dict(users=USERS, owner=room['owner_id'], members=members,
                friends=manager.get_friends(actor), blocks=manager.get_blocked_users(actor),
                received=manager.get_received_requests(actor), sent=manager.get_sent_requests(actor),
                results=manager.search_users(actor, keyword) if keyword.strip() else [],
                recommended=manager.get_room_recommendations(actor, room) if is_participant(room, actor) else [],
                capacity=5)


def action(data):
    if not isinstance(data, dict):
        raise ValueError('잘못된 요청입니다.')
    actor = data['actor']
    keyword = data.get('keyword', '')
    if not isinstance(keyword, str) or len(keyword) > 100:
        raise ValueError('검색어가 올바르지 않습니다.')
    state(actor, keyword)
    name = data['action']
    message = '목록을 불러왔습니다.'
    if name == 'reset':
        reset()
        message = '초기화했습니다.'
    elif name in ('view', 'search'):
        pass
    elif name == 'leave':
        if actor == room['owner_id']:
            raise ValueError('방장은 이 데모에서 퇴장할 수 없습니다.')
        if not is_participant(room, actor):
            raise ValueError('참여 중인 방이 아닙니다.')
        room['participants'].remove(actor)
        message = '방에서 나왔습니다.'
    else:
        target = data['target']
        if type(target) is not int or target not in USERS:
            raise ValueError('존재하지 않는 사용자입니다.')
        if name == 'kick':
            kick_participant(room, actor, target)
            message = '참여자를 추방했습니다.'
        elif name in ('send_friend_request', 'accept_friend_request', 'reject_friend_request',
                      'cancel_friend_request', 'remove_friend', 'block_user', 'unblock_user'):
            result = getattr(manager, name)(actor, target)
            message = {
                'send_friend_request': '친구 요청을 보냈습니다.',
                'accept_friend_request': '친구가 되었습니다.',
                'reject_friend_request': '요청을 거절했습니다.',
                'cancel_friend_request': '요청을 취소했습니다.',
                'remove_friend': '친구를 삭제했습니다.',
                'block_user': '사용자를 차단했습니다.',
                'unblock_user': '차단을 해제했습니다.'
            }[name]
            if result == 'incoming_request_exists':
                message = '이미 받은 요청이 있습니다. 받은 요청에서 수락하세요.'
        else:
            raise ValueError('지원하지 않는 기능입니다.')
    return dict(state(actor, keyword), message=message)

class Handler(BaseHTTPRequestHandler):
    def send_body(self, status, content, mime):
        self.send_response(status)
        self.send_header('Content-Type', mime)
        self.send_header('Content-Length', str(len(content)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(content)

    def send_json(self, status, obj):
        self.send_body(status, json.dumps(obj, ensure_ascii=False).encode(), 'application/json; charset=utf-8')

    def do_GET(self):
        if self.path == '/':
            self.send_body(200, Path(__file__).with_name('web_demo.html').read_bytes(), 'text/html; charset=utf-8')
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path != '/api/action':
            self.send_error(404)
            return
        try:
            if self.headers.get_content_type() != 'application/json':
                raise ValueError('JSON 요청만 허용합니다.')
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length <= 4096:
                raise ValueError('잘못된 요청 크기입니다.')
            self.send_json(200, action(json.loads(self.rfile.read(length))))
        except PermissionError as exc:
            self.send_json(403, {'error': str(exc)})
        except (ValueError, KeyError, TypeError) as exc:
            self.send_json(400, {'error': str(exc)})

if __name__ == '__main__':
    with HTTPServer(('127.0.0.1', 8765), Handler) as server:
        url = 'http://127.0.0.1:8765'
        print(f'CampusMate 데모: {url}\n종료: Ctrl+C', flush=True)
        webbrowser.open(url)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
