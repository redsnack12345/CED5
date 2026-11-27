"""Local HTML demo using the existing management modules. python web_demo.py"""
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import json
import webbrowser
from participant import get_participants, kick_participant
from friend import FriendManager

USERS = {1: '김민수', 2: '이지훈', 3: '박서연', 4: '최유진'}

def reset():
    global room, manager
    room = {'owner_id': 1, 'participants': [1, 2, 3]}
    manager = FriendManager(USERS)

reset()

def state(actor):
    if actor not in USERS:
        raise ValueError('존재하지 않는 사용자입니다.')
    return dict(users=USERS, owner=room['owner_id'], members=get_participants(room),
                friends=sorted(manager.get_friends(actor)), blocks=sorted(manager.get_blocked_users(actor)),
                capacity=5)

def action(data):
    actor = data['actor']
    state(actor)
    name = data['action']
    if name == 'reset':
        reset()
    elif name == 'view':
        pass
    else:
        target = data['target']
        if target not in USERS:
            raise ValueError('존재하지 않는 사용자입니다.')
        if name == 'kick':
            kick_participant(room, actor, target)
        elif name in ('add_friend', 'remove_friend', 'block_user', 'unblock_user'):
            getattr(manager, name)(actor, target)
        else:
            raise ValueError('지원하지 않는 기능입니다.')
    return state(actor)

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
