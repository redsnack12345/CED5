"""독립 실행용 관리 기능 데모. python demo.py"""
import tkinter as tk
from tkinter import ttk, messagebox
from participant import get_participants, kick_participant
from friend import FriendManager

USERS = {1: '김민수', 2: '이지훈', 3: '박서연', 4: '최유진'}

class Demo:
    def __init__(self, root):
        self.root = root
        root.title('CampusMate | 관리 기능 데모')
        root.geometry('780x570')
        root.minsize(650, 500)
        self.room = {'owner_id': 1, 'participants': [1, 2, 3]}
        self.manager = FriendManager(USERS)
        self.actor = tk.StringVar(value=self.label(1))
        self.status = tk.StringVar(value='테스트할 기능을 선택하세요.')
        self.count = tk.StringVar()
        style = ttk.Style(root)
        style.configure('Title.TLabel', font=('Malgun Gothic', 20, 'bold'))
        style.configure('TButton', padding=7)
        main = ttk.Frame(root, padding=20)
        main.pack(fill='both', expand=True)
        ttk.Label(main, text='CampusMate 관리 기능', style='Title.TLabel').pack(anchor='w')
        ttk.Label(main, text='독립 테스트용 · 가상 사용자 4명 · 데이터는 메모리에 저장').pack(anchor='w', pady=(4,15))
        bar = ttk.Frame(main); bar.pack(fill='x', pady=(0,12))
        ttk.Label(bar, text='현재 사용자').pack(side='left')
        combo = ttk.Combobox(bar, textvariable=self.actor, values=[self.label(i) for i in USERS], state='readonly', width=20)
        combo.pack(side='left', padx=10); combo.bind('<<ComboboxSelected>>', lambda e: self.refresh())
        ttk.Button(bar, text='초기화', command=self.reset).pack(side='right')
        tabs = ttk.Notebook(main); tabs.pack(fill='both', expand=True)
        roomtab = ttk.Frame(tabs, padding=15); friendtab = ttk.Frame(tabs, padding=15)
        tabs.add(roomtab, text='참여자 관리'); tabs.add(friendtab, text='친구 및 차단 관리')
        ttk.Label(roomtab, text='점심 같이 먹어요', font=('Malgun Gothic', 15, 'bold')).pack(anchor='w')
        ttk.Label(roomtab, textvariable=self.count).pack(anchor='w', pady=8)
        self.members = self.make_list(roomtab)
        self.kick = ttk.Button(roomtab, text='선택한 참여자 추방', command=self.kick_member)
        self.kick.pack(anchor='e', pady=10)
        ttk.Label(roomtab, text='방장만 추방할 수 있으며 방장 자신은 추방할 수 없습니다.').pack(anchor='w')
        friendtab.columnconfigure((0,1,2), weight=1); friendtab.rowconfigure(1, weight=1)
        self.lists = {}
        for col, (key, title) in enumerate([('users','다른 사용자'),('friends','내 친구'),('blocks','내 차단 목록')]):
            ttk.Label(friendtab, text=title).grid(row=0,column=col,sticky='w',padx=5,pady=5)
            frame=ttk.Frame(friendtab); frame.grid(row=1,column=col,sticky='nsew',padx=5)
            self.lists[key]=self.make_list(frame)
            actions=ttk.Frame(friendtab); actions.grid(row=2,column=col,sticky='ew',padx=5,pady=8)
            for caption, method in {'users':[('친구 추가','add_friend'),('차단','block_user')], 'friends':[('친구 삭제','remove_friend'),('차단','block_user')], 'blocks':[('차단 해제','unblock_user')]}[key]:
                ttk.Button(actions,text=caption,command=lambda k=key,m=method:self.friend_action(k,m)).pack(fill='x',pady=3)
        ttk.Label(main, textvariable=self.status, wraplength=700).pack(anchor='w',pady=(12,0))
        self.refresh()

    def label(self, uid):
        return f'{uid} | {USERS[uid]}'

    def current(self):
        return int(self.actor.get().split(' | ')[0])

    def make_list(self, parent):
        box=tk.Listbox(parent, font=('Malgun Gothic',11), activestyle='none', exportselection=False, height=8)
        box.pack(fill='both',expand=True)
        return box

    def selected(self, box):
        if not box.curselection():
            raise ValueError('먼저 사용자를 선택하세요.')
        return int(box.get(box.curselection()[0]).split(' | ')[0])

    def fill(self, box, ids, room=False):
        box.delete(0,tk.END)
        for uid in sorted(ids):
            suffix=' (방장)' if room and uid==self.room['owner_id'] else ''
            box.insert(tk.END,self.label(uid)+suffix)

    def refresh(self):
        actor=self.current(); ids=get_participants(self.room)
        role='방장' if actor==self.room['owner_id'] else ('참여자' if actor in ids else '미참여')
        self.count.set(f'현재 인원: {len(ids)} / 5명   |   내 역할: {role}')
        self.fill(self.members,ids,True)
        self.kick.configure(state='normal' if role=='방장' else 'disabled')
        self.fill(self.lists['users'],[i for i in USERS if i!=actor])
        self.fill(self.lists['friends'],self.manager.get_friends(actor))
        self.fill(self.lists['blocks'],self.manager.get_blocked_users(actor))

    def kick_member(self):
        try:
            target=self.selected(self.members)
            if not messagebox.askyesno('추방 확인',f'{USERS[target]} 사용자를 추방할까요?'): return
            kick_participant(self.room,self.current(),target)
            self.refresh(); self.status.set(f'{USERS[target]} 사용자를 추방했습니다.')
        except (ValueError,PermissionError) as e:
            messagebox.showwarning('처리 실패',str(e))

    def friend_action(self,key,method):
        try:
            target=self.selected(self.lists[key])
            getattr(self.manager,method)(self.current(),target)
            self.refresh()
            action={'add_friend':'친구 추가','remove_friend':'친구 삭제','block_user':'차단','unblock_user':'차단 해제'}[method]
            self.status.set(f'{USERS[target]}: {action} 완료')
        except (ValueError,PermissionError) as e:
            messagebox.showwarning('처리 실패',str(e))

    def reset(self):
        if messagebox.askyesno('초기화','모든 데모 데이터를 초기화할까요?'):
            self.room={'owner_id':1,'participants':[1,2,3]}
            self.manager=FriendManager(USERS)
            self.actor.set(self.label(1)); self.refresh(); self.status.set('초기화 완료')

if __name__=='__main__':
    root=tk.Tk()
    Demo(root)
    root.mainloop()
