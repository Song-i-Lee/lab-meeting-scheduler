import streamlit as st
from datetime import datetime, timedelta
import itertools

st.set_page_config(page_title="랩미팅 스케줄러", layout="wide")

st.title("📅 랩미팅 스케줄 에이전트")

# -------------------------
# Sidebar (설정 영역)
# -------------------------
st.sidebar.header("⚙️ 설정")

start_time = st.sidebar.time_input("시작 시간", datetime.strptime("13:00", "%H:%M"))
end_time = st.sidebar.time_input("종료 시간", datetime.strptime("16:30", "%H:%M"))

participants = [
    "이기은", "소재현", "강민기", "송무빈",
    "임지은", "이송이", "박성준", "김형덕"
]

st.sidebar.markdown("### 👥 참여자 선택")

selected = []
for p in participants:
    if st.sidebar.checkbox(p):
        selected.append(p)

run_button = st.sidebar.button("🚀 스케줄 생성")

# -------------------------
# 함수
# -------------------------
def generate_slots(start, end, interval=30):
    slots = []

    # 🔥 핵심: time → datetime 변환
    current = datetime.combine(datetime.today(), start)
    end_dt = datetime.combine(datetime.today(), end)

    while current < end_dt:
        next_time = current + timedelta(minutes=interval)
        slots.append((current, next_time))
        current = next_time

    return slots

restricted_people = ["이송이", "임지은", "강민기"]
restricted_start = datetime.strptime("14:00", "%H:%M").time()
restricted_end = datetime.strptime("15:30", "%H:%M").time()

def is_available(person, slot):
    s, e = slot
    if person in restricted_people:
        if not (e.time() <= restricted_start or s.time() >= restricted_end):
            return False
    return True

def find_best_schedule(selected, slots):
    n = len(selected)

    # 이기은 분리
    people = selected.copy()
    last_person = None
    if "이기은" in people:
        people.remove("이기은")
        last_person = "이기은"

    # 각 슬롯별 가능한 사람
    slot_candidates = []
    for slot in slots:
        candidates = [p for p in people if is_available(p, slot)]
        slot_candidates.append((slot, candidates))

    # 연속된 window 탐색
    for i in range(len(slot_candidates)):
        window = slot_candidates[i:i+n]
        if len(window) < n:
            continue

        # 마지막 슬롯은 이기은용
        if last_person:
            last_slot, _ = window[-1]
            if not is_available(last_person, last_slot):
                continue

        # matching 시도
        used = set()
        schedule = []

        def backtrack(idx):
            if idx == len(window) - (1 if last_person else 0):
                return True

            slot, candidates = window[idx]

            for p in candidates:
                if p not in used:
                    used.add(p)
                    schedule.append((slot, p))
                    if backtrack(idx + 1):
                        return True
                    used.remove(p)
                    schedule.pop()

            return False

        success = backtrack(0)

        if success:
            # 마지막 이기은 추가
            if last_person:
                last_slot = window[-1][0]
                schedule.append((last_slot, last_person))

            return schedule

    return None
# -------------------------
# Main UI (결과 영역)
# -------------------------
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📋 선택 요약")
    st.write(f"🕒 시간: {start_time.strftime('%H:%M')} ~ {end_time.strftime('%H:%M')}")
    st.write(f"👥 인원: {len(selected)}명")

    if selected:
        st.markdown("#### 선택된 사람")
        for p in selected:
            st.write(f"• {p}")

with col2:
    st.subheader("📊 스케줄 결과")

    if run_button:

        if not selected:
            st.warning("참여자를 선택하세요")
        else:
            slots = generate_slots(start_time, end_time)
            result = find_best_schedule(selected, slots)

            if result:
                st.success("최적 스케줄 생성 완료")

                # 카드형 UI
                for (s, e), person in result:
                    st.markdown(
                        f"""
                        <div style="
                            padding:10px;
                            border-radius:10px;
                            background-color:#f5f7fa;
                            margin-bottom:8px;
                            display:flex;
                            justify-content:space-between;
                            font-weight:500;
                        ">
                            <span>{s.strftime('%H:%M')} ~ {e.strftime('%H:%M')}</span>
                            <span>👤 {person}</span>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

            else:
                st.error("가능한 스케줄을 찾을 수 없습니다")