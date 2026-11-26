const slots=["1A","1B","2A","2B","3A","3B","4A","4B","5A","5B","6A","6B","7A","7B"];
let monday=getMonday(new Date()), selected=null;
function getMonday(d){d=new Date(d);d.setDate(d.getDate()-(d.getDay()+6)%7);return d}
function fmt(d){return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,"0")}-${String(d.getDate()).padStart(2,"0")}`}
function add(d,n){let x=new Date(d);x.setDate(x.getDate()+n);return x}
function safe(s){return String(s??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]))}
function modal(title,html){document.getElementById("modalTitle").textContent=title;document.getElementById("modalBody").innerHTML=html;document.getElementById("backdrop").classList.add("show")}
function close(){document.getElementById("backdrop").classList.remove("show")}
async function refresh(){
 const res=await fetch(`/api/timetable?week_start=${fmt(monday)}`),data=await res.json();
 const end=add(monday,4);document.getElementById("weekLabel").textContent=`${monday.getMonth()+1}.${monday.getDate()} - ${end.getMonth()+1}.${end.getDate()}`;
 const head=document.querySelector("#timetable thead tr");head.innerHTML="<th>교시</th>";
 data.week_dates.forEach(d=>head.innerHTML+=`<th>${d.day}<br>${Number(d.date.slice(5,7))}.${Number(d.date.slice(8,10))}</th>`);
 const body=document.querySelector("#timetable tbody");body.innerHTML="";
 data.slots.forEach(slot=>{let tr=document.createElement("tr");tr.innerHTML=`<td>${slot.id}</td>`;
 data.week_dates.forEach((day,i)=>{let c=data.cells[`${i}:${slot.id}`],td=document.createElement("td");td.className="cell";
 if(c?.type==="class"){td.classList.add("class");td.innerHTML=`<span class="cell-title">${safe(c.title)}</span><span class="cell-sub">${safe(c.subtitle)}</span>`}
 else if(c?.type==="activity"){td.classList.add("activity");td.innerHTML=`<span class="cell-title">${safe(c.title)}</span><span class="cell-sub">참여 활동</span>`;td.onclick=()=>detail(c.room_id)}
 else td.onclick=()=>choose({date:day.date,day:day.day,slot:slot.id,start_slot:slot.id,end_slot:slot.id});
 tr.appendChild(td)});body.appendChild(tr)});
}
function choose(s){selected=s;modal(`${s.day}요일 ${s.slot} 공강`,`<div class="actions"><button class="action" id="create">방 생성</button><button class="action" id="find">방 찾기</button></div>`);document.getElementById("create").onclick=createForm;document.getElementById("find").onclick=findRooms}
async function findRooms(){
 let s=selected,r=await fetch(`/api/rooms?date=${s.date}&start_slot=${s.start_slot}&end_slot=${s.end_slot}`),d=await r.json();
 if(!r.ok)return modal("오류",safe(d.error));
 let html=d.rooms.length?d.rooms.map(x=>`<article class="room" data-id="${x.id}"><h3>${safe(x.title)}</h3><p>${x.activity_date} · ${x.start_slot} ~ ${x.end_slot}</p><p>${safe(x.category)} · ${safe(x.location||"장소 미정")}</p><p>참여 ${x.member_count}/${x.max_people}명</p></article>`).join(""):'<div class="empty">해당 시간대에 모집 중인 방이 없습니다.</div>';
 modal("매칭방 찾기",html);document.querySelectorAll("[data-id]").forEach(e=>e.onclick=()=>detail(e.dataset.id))
}
function options(v){return slots.map(s=>`<option ${s===v?"selected":""}>${s}</option>`).join("")}
function createForm(){let s=selected;modal("방 생성",`<form id="roomForm">
<label>방 제목<input name="title" required placeholder="예: 점심 같이 먹어요"></label>
<label>설명<textarea name="description" placeholder="활동 내용을 작성해 주세요."></textarea></label>
<div class="form-row"><label>날짜<input name="activity_date" type="date" value="${s.date}" required></label><label>활동 종류<select name="category"><option>식사</option><option>운동</option><option>게임</option><option>소통</option><option>스터디</option><option>기타</option></select></label></div>
<div class="form-row"><label>시작 교시<select name="start_slot">${options(s.slot)}</select></label><label>종료 교시<select name="end_slot">${options(s.slot)}</select></label></div>
<div class="form-row"><label>장소<input name="location" placeholder="예: 학생식당"></label><label>최대 인원<input name="max_people" type="number" min="2" max="30" value="4"></label></div>
<button class="primary">방 생성</button><div class="notice" id="notice"></div></form>`);
 document.getElementById("roomForm").onsubmit=async e=>{e.preventDefault();let p=Object.fromEntries(new FormData(e.target));p.max_people=Number(p.max_people);
 let r=await fetch("/api/rooms",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(p)}),d=await r.json();
 if(!r.ok){document.getElementById("notice").textContent=d.error;return}close();await refresh();alert(d.message)}
}
async function detail(id){let r=await fetch(`/api/rooms/${id}`),d=await r.json();if(!r.ok)return modal("오류",safe(d.error));let x=d.room;
 modal("매칭방 상세",`<h2>${safe(x.title)}</h2><p class="detail-line">${x.activity_date} · ${x.start_slot} ~ ${x.end_slot}</p><p class="detail-line">${safe(x.category)} · ${safe(x.location||"장소 미정")}</p><p class="detail-line">방장 ${safe(x.creator_name)} · 참여 ${x.member_count}/${x.max_people}명</p><div class="description">${safe(x.description||"설명이 없습니다.")}</div><button class="primary" id="join">참여</button><p class="notice" id="notice"></p>`);
 document.getElementById("join").onclick=async()=>{let q=await fetch(`/api/rooms/${id}/join`,{method:"POST"}),z=await q.json();if(!q.ok){document.getElementById("notice").textContent=z.error;return}close();await refresh();alert(z.message)}
}
document.getElementById("close").onclick=close;document.getElementById("backdrop").onclick=e=>{if(e.target.id==="backdrop")close()};
document.getElementById("prevWeek").onclick=()=>{monday=add(monday,-7);refresh()};
document.getElementById("nextWeek").onclick=()=>{monday=add(monday,7);refresh()};
refresh();