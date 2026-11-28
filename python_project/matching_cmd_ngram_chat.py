

# 실제 앱에서는 이 두 dict를 다른 모듈이나 DB에서 전달받으면 됩니다.
USERS = {
    "user01": {
        "name": "김민수",
        "free_time": {
            "월": [("12:00", "15:00")],
            "화": [("13:00", "18:00")],
            "수": [("10:00", "17:00")],
            "목": [("14:00", "19:00")],
            "금": [("12:00", "20:00")],
        },
        "preferred_people": 4,  # 본인을 포함해 원하는 총 인원
        "preferences": {
            "운동": 5, "식사": 4, "게임": 5, "담화": 3,
            "공부": 2, "술": 1, "문화활동": 4,
        },
    }
}

ROOMS = [
    {"id": 1, "title": "점심 농구 같이 해요", "activity": "운동", "day": "월", "start": "12:30", "end": "14:00", "people": 3, "capacity": 5},
    {"id": 2, "title": "보드게임 모임", "activity": "게임", "day": "화", "start": "15:00", "end": "17:00", "people": 2, "capacity": 4},
    {"id": 3, "title": "저녁 식사 같이", "activity": "식사", "day": "금", "start": "18:00", "end": "19:00", "people": 3, "capacity": 4},
    {"id": 4, "title": "시험 대비 스터디", "activity": "공부", "day": "수", "start": "13:00", "end": "15:00", "people": 2, "capacity": 6},
    {"id": 5, "title": "영화 보고 이야기", "activity": "문화활동", "day": "목", "start": "16:00", "end": "18:00", "people": 2, "capacity": 4},
    {"id": 6, "title": "심야 게임 파티", "activity": "게임", "day": "화", "start": "21:00", "end": "23:00", "people": 2, "capacity": 4},
    {"id": 7, "title": "월요일 커피 담화", "activity": "담화", "day": "월", "start": "13:00", "end": "14:00", "people": 4, "capacity": 4},
    {"id": 8, "title": "아침 배드민턴 한 게임", "activity": "운동", "day": "월", "start": "09:00", "end": "10:30", "people": 2, "capacity": 4},
    {"id": 9, "title": "공강 탁구 파트너", "activity": "운동", "day": "월", "start": "12:00", "end": "13:00", "people": 1, "capacity": 2},
    {"id": 10, "title": "점심 축구 미니게임", "activity": "운동", "day": "월", "start": "13:00", "end": "15:00", "people": 5, "capacity": 8},
    {"id": 11, "title": "도서관 앞 산책", "activity": "운동", "day": "월", "start": "16:00", "end": "17:00", "people": 2, "capacity": 5},
    {"id": 12, "title": "월요일 김밥 점심", "activity": "식사", "day": "월", "start": "12:00", "end": "13:00", "people": 2, "capacity": 4},
    {"id": 13, "title": "학식 새 메뉴 탐방", "activity": "식사", "day": "월", "start": "13:30", "end": "14:30", "people": 3, "capacity": 5},
    {"id": 14, "title": "월요일 카드게임", "activity": "게임", "day": "월", "start": "14:00", "end": "15:00", "people": 2, "capacity": 4},
    {"id": 15, "title": "점심시간 수다 모임", "activity": "담화", "day": "월", "start": "12:20", "end": "13:20", "people": 2, "capacity": 4},
    {"id": 16, "title": "월요 파이썬 스터디", "activity": "공부", "day": "월", "start": "13:00", "end": "14:30", "people": 3, "capacity": 5},
    {"id": 17, "title": "월요일 전시회 관람", "activity": "문화활동", "day": "월", "start": "18:00", "end": "20:00", "people": 2, "capacity": 6},
    {"id": 18, "title": "화요일 풋살 팀원", "activity": "운동", "day": "화", "start": "14:00", "end": "16:00", "people": 5, "capacity": 8},
    {"id": 19, "title": "공강 헬스 동행", "activity": "운동", "day": "화", "start": "16:00", "end": "17:00", "people": 1, "capacity": 3},
    {"id": 20, "title": "화요일 파스타 점심", "activity": "식사", "day": "화", "start": "13:00", "end": "14:00", "people": 2, "capacity": 4},
    {"id": 21, "title": "카페 디저트 탐방", "activity": "식사", "day": "화", "start": "15:00", "end": "16:00", "people": 2, "capacity": 5},
    {"id": 22, "title": "보드게임 루미큐브", "activity": "게임", "day": "화", "start": "13:30", "end": "15:00", "people": 3, "capacity": 4},
    {"id": 23, "title": "화요일 콘솔게임", "activity": "게임", "day": "화", "start": "16:00", "end": "18:00", "people": 2, "capacity": 4},
    {"id": 24, "title": "취업 고민 이야기", "activity": "담화", "day": "화", "start": "17:00", "end": "18:00", "people": 2, "capacity": 5},
    {"id": 25, "title": "알고리즘 문제 풀이", "activity": "공부", "day": "화", "start": "14:00", "end": "16:00", "people": 3, "capacity": 5},
    {"id": 26, "title": "화요 영화 관람", "activity": "문화활동", "day": "화", "start": "18:00", "end": "20:00", "people": 2, "capacity": 4},
    {"id": 27, "title": "화요일 맥주 모임", "activity": "술", "day": "화", "start": "19:00", "end": "21:00", "people": 3, "capacity": 6},
    {"id": 28, "title": "수요일 아침 조깅", "activity": "운동", "day": "수", "start": "09:00", "end": "10:00", "people": 2, "capacity": 4},
    {"id": 29, "title": "배구 연습 모임", "activity": "운동", "day": "수", "start": "12:00", "end": "14:00", "people": 4, "capacity": 6},
    {"id": 30, "title": "수요일 학식 동행", "activity": "식사", "day": "수", "start": "11:30", "end": "12:30", "people": 1, "capacity": 4},
    {"id": 31, "title": "수요일 분식 탐방", "activity": "식사", "day": "수", "start": "15:00", "end": "16:00", "people": 3, "capacity": 5},
    {"id": 32, "title": "공강 체스 대결", "activity": "게임", "day": "수", "start": "13:00", "end": "14:00", "people": 1, "capacity": 2},
    {"id": 33, "title": "수요일 마피아게임", "activity": "게임", "day": "수", "start": "14:00", "end": "16:00", "people": 4, "capacity": 7},
    {"id": 34, "title": "카페에서 자유 대화", "activity": "담화", "day": "수", "start": "11:00", "end": "12:00", "people": 2, "capacity": 4},
    {"id": 35, "title": "수요일 영어 회화", "activity": "공부", "day": "수", "start": "13:00", "end": "15:00", "people": 3, "capacity": 4},
    {"id": 36, "title": "캠퍼스 사진 산책", "activity": "문화활동", "day": "수", "start": "15:00", "end": "17:00", "people": 2, "capacity": 6},
    {"id": 37, "title": "수요일 저녁 소주", "activity": "술", "day": "수", "start": "19:00", "end": "21:00", "people": 3, "capacity": 5},
    {"id": 38, "title": "목요일 배드민턴", "activity": "운동", "day": "목", "start": "14:00", "end": "15:30", "people": 2, "capacity": 4},
    {"id": 39, "title": "목요일 클라이밍", "activity": "운동", "day": "목", "start": "16:00", "end": "18:00", "people": 2, "capacity": 5},
    {"id": 40, "title": "목요일 햄버거 모임", "activity": "식사", "day": "목", "start": "14:00", "end": "15:00", "people": 3, "capacity": 4},
    {"id": 41, "title": "저녁 라멘 탐방", "activity": "식사", "day": "목", "start": "18:00", "end": "19:00", "people": 2, "capacity": 4},
    {"id": 42, "title": "목요 전략 보드게임", "activity": "게임", "day": "목", "start": "15:00", "end": "17:00", "people": 2, "capacity": 5},
    {"id": 43, "title": "목요일 PC방 파티", "activity": "게임", "day": "목", "start": "17:00", "end": "19:00", "people": 3, "capacity": 5},
    {"id": 44, "title": "공강 고민 상담", "activity": "담화", "day": "목", "start": "15:30", "end": "16:30", "people": 1, "capacity": 3},
    {"id": 45, "title": "목요일 전공 스터디", "activity": "공부", "day": "목", "start": "14:30", "end": "16:30", "people": 3, "capacity": 6},
    {"id": 46, "title": "목요일 박물관 탐방", "activity": "문화활동", "day": "목", "start": "16:00", "end": "18:00", "people": 4, "capacity": 5},
    {"id": 47, "title": "목요일 뒤풀이", "activity": "술", "day": "목", "start": "19:00", "end": "21:00", "people": 5, "capacity": 5},
    {"id": 48, "title": "금요일 농구 3대3", "activity": "운동", "day": "금", "start": "13:00", "end": "15:00", "people": 4, "capacity": 6},
    {"id": 49, "title": "금요일 러닝크루", "activity": "운동", "day": "금", "start": "17:00", "end": "18:00", "people": 2, "capacity": 8},
    {"id": 50, "title": "금요일 점심 덮밥", "activity": "식사", "day": "금", "start": "12:30", "end": "13:30", "people": 2, "capacity": 4},
    {"id": 51, "title": "금요일 저녁 피자", "activity": "식사", "day": "금", "start": "18:00", "end": "19:30", "people": 3, "capacity": 6},
    {"id": 52, "title": "금요 협동게임", "activity": "게임", "day": "금", "start": "14:00", "end": "16:00", "people": 3, "capacity": 4},
    {"id": 53, "title": "한 주 마무리 수다", "activity": "담화", "day": "금", "start": "15:00", "end": "16:00", "people": 2, "capacity": 5},
    {"id": 54, "title": "금요일 코딩 스터디", "activity": "공부", "day": "금", "start": "16:00", "end": "18:00", "people": 2, "capacity": 4},
    {"id": 55, "title": "독립영화 같이 보기", "activity": "문화활동", "day": "금", "start": "17:00", "end": "19:00", "people": 2, "capacity": 4},
    {"id": 56, "title": "금요일 칵테일 모임", "activity": "술", "day": "금", "start": "20:00", "end": "22:00", "people": 2, "capacity": 5},
    {"id": 57, "title": "주말 전시회 탐방", "activity": "문화활동", "day": "토", "start": "13:00", "end": "15:00", "people": 2, "capacity": 6},
]

DEMO_NAMES = ("이지훈", "박서연", "최현우", "정유진", "강지민", "윤서준", "한수빈", "오민재") #임시 사용자 이름
for room in ROOMS:
    member_ids = [] #기존 인원수에 맞춰 임시 참가자 제작
    for index in range(room["people"]):
        member_id = f"demo_{room['id']}_{index}" #방마다 다른 사용자 ID 부여
        USERS[member_id] = {**USERS["user01"], "name": DEMO_NAMES[(room["id"] + index) % len(DEMO_NAMES)]} #임시 사용자 정보
        member_ids.append(member_id)
    room["member_ids"] = member_ids #방장 포함 참가자 ID 목록
    room["owner_id"] = member_ids[0] if member_ids else None #첫번째 사용자를 방장으로 지정
    room["closed"] = False #수동 마감 여부
    room["chats"] = []

DAY_ORDER = {day: index for index, day in enumerate(("월", "화", "수", "목", "금", "토", "일"))} #enum

def to_minutes(hhmm): #mm:nn을 자정기준 흐른 시간으로 변경
    hour, minute = map(int, hhmm.split(":"))
    return hour * 60 + minute


def parse_time(text): #시간 입력 예외처리
    parts = text.strip().split(":")
    if len(parts) != 2 or not all(part.isdigit() for part in parts):
        raise ValueError("시간은 HH:MM 형식이어야 합니다.")
    hour, minute = map(int, parts)
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        raise ValueError("유효한 시간(00:00~23:59)을 입력하십시오.")
    return f"{hour:02d}:{minute:02d}"


def make_ngrams(text, n=2): #n-gram알고리즘-함수(문자를 n개로 분리하여 비교)
    text = text.strip().lower()
    text = "".join(text.split()) #문자의 공백제거, 소문자 변경, 하나로 쭉이음
    if len(text) < n: #n보다 작은 문자는 그대로
        return {text} if text else set()
    return {text[i:i + n] for i in range(len(text) - n + 1)} #연속 n글자씩 잘라 집합(set)에 저장/ 예: "배드민턴", n=2 -> {"배드", "드민", "민턴"}


def ngram_similarity(keyword, candidate, n=2): #n-gram알고리즘-두 문자열의 유사도를 계산
    n = 1 if len("".join(keyword.split())) == 1 else n #n=1인 예외처리
    a = make_ngrams(keyword, n)
    b = make_ngrams(candidate, n)
    if not a or not b: #a,b중 빈 집합 판별
        return 0.0
    common_count = len(a & b) #교집합
    total_count = len(a | b) #합집합
    return common_count / total_count #Jaccard 유사도 = 교집합 크기 / 합집합 크기


def search_rooms(rooms, keyword, user): #n-gram + 활동 선호도 + 인원 선호로 검색
    keyword = keyword.strip().lower()
    if not keyword: #검색어가 빈 예외처리
        return rooms[:]
    ranked = [] # 포함관계/유사도/활동선호/인원선호/매칭방목록 - 순으로 저장
    for room in rooms:
        title = room["title"].lower()
        activity = room["activity"].lower()
        words = title.split()
        similarity = max( #검색어 vs 제목/활동/제목을 잘라만든 문자열 - 높은 유사도값 저장
            ngram_similarity(keyword, text)
            for text in (title, activity, *words)
        )
        included = keyword in title or keyword in activity #대놓고 검색어가 포함되있으면 해당방 포함

        if included or similarity >= 0.25: #0.25는 검색의 정밀도를 결정하는 상수(정확도-0.3, 디버깅용-0.25)
            activity_preference = user["preferences"].get(room["activity"], 0) #사용자 정보에서 선호도 가져옴
            expected_people = room["people"] + 1
            people_difference = abs(expected_people - user["preferred_people"]) #선호인원도 - 작을수록 선호한다고 판단
            ranked.append((included, similarity, activity_preference, people_difference, room))

    ranked.sort(key=lambda x: (not x[0], -x[1], -x[2], x[3], x[4]["id"])) #해당 우선도를 가지고 정렬
    return [room for _, _, _, _, room in ranked]


def filter_by_time(rooms, day, start, end): #매칭방 정렬 - 시간대 입력 후 정렬
    start_minutes = to_minutes(start)
    end_minutes = to_minutes(end)
    return [
        room for room in rooms
        if room["day"] == day
        and to_minutes(room["start"]) < end_minutes
        and start_minutes < to_minutes(room["end"])
    ]


def sort_rooms(rooms, sort_type, user): #매칭방 정렬 - 조건
    if sort_type in ("1", "4"):  # 시간순 / 시간대별 결과
        return sorted(rooms, key=lambda r: (DAY_ORDER[r["day"]], r["start"], r["id"]))
    if sort_type == "2":  # 인원 많은 순
        return sorted(rooms, key=lambda r: (-r["people"], r["id"]))
    if sort_type == "3":  # 사용자 활동 선호도 높은 순
        return sorted(
            rooms,
            key=lambda r: (-user["preferences"].get(r["activity"], 0), r["id"])
        )
    return rooms[:]


if __name__ == "__main__":
    main()
