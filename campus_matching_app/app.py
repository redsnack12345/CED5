from flask import Flask, render_template, request, jsonify
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

app = Flask(__name__)
DB = Path(__file__).with_name("campus.db")
USER_ID = 1
DAYS = ["월", "화", "수", "목", "금"]
SLOTS = [{"id": f"{n}{half}", "start": f"{9+(n-1)*2+(half=='B'):02d}:00",
          "end": f"{9+(n-1)*2+(half=='B'):02d}:50"}
         for n in range(1, 8) for half in ("A", "B")]

def db():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys=ON")
    return c

def init_db():
    c = db()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, nickname TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS timetable(
      id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
      day_of_week INTEGER NOT NULL, slot_id TEXT NOT NULL,
      course_name TEXT NOT NULL, classroom TEXT DEFAULT '',
      UNIQUE(user_id,day_of_week,slot_id),
      FOREIGN KEY(user_id) REFERENCES users(id));
    CREATE TABLE IF NOT EXISTS rooms(
      id INTEGER PRIMARY KEY AUTOINCREMENT, creator_id INTEGER NOT NULL,
      title TEXT NOT NULL, description TEXT DEFAULT '', category TEXT DEFAULT '기타',
      location TEXT DEFAULT '', activity_date TEXT NOT NULL, start_slot TEXT NOT NULL,
      end_slot TEXT NOT NULL, max_people INTEGER NOT NULL DEFAULT 4,
      status TEXT NOT NULL DEFAULT '모집 중', created_at TEXT NOT NULL,
      FOREIGN KEY(creator_id) REFERENCES users(id));
    CREATE TABLE IF NOT EXISTS room_members(
      id INTEGER PRIMARY KEY AUTOINCREMENT, room_id INTEGER NOT NULL,
      user_id INTEGER NOT NULL, joined_at TEXT NOT NULL,
      UNIQUE(room_id,user_id), FOREIGN KEY(room_id) REFERENCES rooms(id),
      FOREIGN KEY(user_id) REFERENCES users(id));
    """)
    c.execute("INSERT OR IGNORE INTO users VALUES(1,'사용자')")
    if c.execute("SELECT COUNT(*) FROM timetable WHERE user_id=1").fetchone()[0] == 0:
        sample = [
          (0,"1A","자료구조","IT관 201"),(0,"1B","자료구조","IT관 201"),(0,"2A","이산수학","IT관 305"),
          (1,"1A","프로그래밍","IT관 101"),(1,"1B","프로그래밍","IT관 101"),(1,"2A","미적분학","공학관 203"),
          (2,"2B","컴퓨터구조","IT관 302"),(2,"3A","컴퓨터구조","IT관 302"),
          (3,"1A","영어","인문관 110"),(3,"3A","알고리즘","IT관 205"),
          (4,"2A","운영체제","IT관 401"),(4,"2B","운영체제","IT관 401")]
        c.executemany("INSERT INTO timetable(user_id,day_of_week,slot_id,course_name,classroom) VALUES(1,?,?,?,?)", sample)
    c.commit()
    c.close()

def ix(slot):
    return next((i for i,s in enumerate(SLOTS) if s["id"] == slot), -1)

@app.route("/")
def home():
    return render_template("index.html")

@app.get("/api/timetable")
def timetable():
    start = request.args.get("week_start")
    if not start:
        today = datetime.now().date()
        start = (today-timedelta(days=today.weekday())).isoformat()
    c = db()
    rows = c.execute("SELECT * FROM timetable WHERE user_id=?", (USER_ID,)).fetchall()
    joined = c.execute("""SELECT r.* FROM rooms r JOIN room_members m ON r.id=m.room_id
                          WHERE m.user_id=? AND r.status!='취소'""",(USER_ID,)).fetchall()
    c.close()
    cells = {f"{r['day_of_week']}:{r['slot_id']}":
             {"type":"class","title":r["course_name"],"subtitle":r["classroom"]} for r in rows}
    dates=[]
    base=datetime.strptime(start,"%Y-%m-%d").date()
    for d, name in enumerate(DAYS):
        day=(base+timedelta(days=d)).isoformat()
        dates.append({"day":name,"date":day})
        for r in joined:
            if r["activity_date"] == day:
                for i in range(ix(r["start_slot"]),ix(r["end_slot"])+1):
                    if i >= 0:
                        cells[f"{d}:{SLOTS[i]['id']}"]={"type":"activity","title":r["title"],"room_id":r["id"]}
    return jsonify({"week_start":start,"week_dates":dates,"slots":SLOTS,"cells":cells})

@app.get("/api/rooms")
def rooms():
    date=request.args.get("date",""); start=ix(request.args.get("start_slot","")); end=ix(request.args.get("end_slot",request.args.get("start_slot","")))
    if not date or start<0 or end<start: return jsonify(error="날짜 또는 시간대가 올바르지 않습니다."),400
    c=db()
    rows=c.execute("""SELECT r.*,u.nickname creator_name,
      (SELECT COUNT(*) FROM room_members m WHERE m.room_id=r.id) member_count
      FROM rooms r JOIN users u ON u.id=r.creator_id
      WHERE r.activity_date=? AND r.status='모집 중' ORDER BY r.created_at DESC""",(date,)).fetchall()
    result=[dict(r) for r in rows if ix(r["start_slot"])<=end and ix(r["end_slot"])>=start]
    c.close()
    return jsonify(rooms=result)

@app.post("/api/rooms")
def create_room():
    d=request.get_json(silent=True) or {}
    for k in ("title","activity_date","start_slot","end_slot"):
        if not str(d.get(k,"")).strip(): return jsonify(error="방 제목, 날짜, 시간을 입력해 주세요."),400
    a,b=ix(d["start_slot"]),ix(d["end_slot"])
    if a<0 or b<a: return jsonify(error="시간대 설정이 올바르지 않습니다."),400
    try:
        capacity=int(d.get("max_people",4))
        if not 2<=capacity<=30: raise ValueError()
    except (TypeError,ValueError): return jsonify(error="모집 인원은 2~30명으로 설정해 주세요."),400
    c=db(); now=datetime.now().isoformat(timespec="seconds")
    cur=c.execute("""INSERT INTO rooms(creator_id,title,description,category,location,activity_date,
      start_slot,end_slot,max_people,created_at) VALUES(?,?,?,?,?,?,?,?,?,?)""",
      (USER_ID,d["title"].strip(),d.get("description",""),d.get("category","기타"),
       d.get("location",""),d["activity_date"],d["start_slot"],d["end_slot"],capacity,now))
    rid=cur.lastrowid
    c.execute("INSERT INTO room_members(room_id,user_id,joined_at) VALUES(?,?,?)",(rid,USER_ID,now))
    c.commit(); c.close()
    return jsonify(message="매칭방을 생성했습니다.",room_id=rid),201

@app.get("/api/rooms/<int:rid>")
def room_detail(rid):
    c=db()
    r=c.execute("""SELECT r.*,u.nickname creator_name,
      (SELECT COUNT(*) FROM room_members m WHERE m.room_id=r.id) member_count
      FROM rooms r JOIN users u ON u.id=r.creator_id WHERE r.id=?""",(rid,)).fetchone()
    c.close()
    return (jsonify(room=dict(r)),200) if r else (jsonify(error="매칭방을 찾을 수 없습니다."),404)

@app.post("/api/rooms/<int:rid>/join")
def join(rid):
    c=db()
    r=c.execute("""SELECT r.*,(SELECT COUNT(*) FROM room_members m WHERE m.room_id=r.id) member_count
                   FROM rooms r WHERE r.id=?""",(rid,)).fetchone()
    if not r: c.close(); return jsonify(error="매칭방을 찾을 수 없습니다."),404
    if r["status"]!="모집 중": c.close(); return jsonify(error="모집 중인 방이 아닙니다."),400
    if c.execute("SELECT 1 FROM room_members WHERE room_id=? AND user_id=?",(rid,USER_ID)).fetchone():
        c.close(); return jsonify(error="이미 참여한 방입니다."),409
    if r["member_count"]>=r["max_people"]: c.close(); return jsonify(error="모집 인원이 가득 찼습니다."),409
    c.execute("INSERT INTO room_members(room_id,user_id,joined_at) VALUES(?,?,?)",(rid,USER_ID,datetime.now().isoformat()))
    c.commit(); c.close()
    return jsonify(message="매칭방에 참여했습니다.")

if __name__=="__main__":
    init_db()
    app.run(debug=True)
