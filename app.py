import streamlit as st
import random

st.set_page_config(layout="wide", page_title="삼권분립 마블")

# --- [게임 설정 및 초기화] ---
if 'game_started' not in st.session_state:
    st.session_state.game_started = False

if not st.session_state.game_started:
    st.title("🏛️ 삼권분립 마블 보드게임 - 게임 설정")
    st.write("플레이할 인원수를 선택하고 게임을 시작하세요.")
    
    num_players = st.number_input("플레이어 수 (1~5명)", min_value=1, max_value=5, value=4)
    
    if st.button("게임 시작", use_container_width=True):
        st.session_state.num_players = num_players
        st.session_state.player_positions = [0] * num_players
        st.session_state.player_scores = [50] * num_players
        st.session_state.owned_spaces = {}
        st.session_state.current_turn = 0
        st.session_state.current_quiz = None
        st.session_state.message = "게임이 시작되었습니다! P1의 차례입니다. 주사위를 굴려주세요."
        st.session_state.last_dice = None
        st.session_state.teacher_eval_pending = False
        st.session_state.game_over = False
        st.session_state.game_started = True
        st.rerun()
    st.stop()

# --- [데이터 설정] ---
board = [
    {"name": "출발선", "type": "시작"},
    {"name": "국회 상임위원회", "type": "입법부"},
    {"name": "국회 본회의장", "type": "입법부"},
    {"name": "황금열쇠", "type": "찬스"},
    {"name": "행정 각 부처", "type": "행정부"},
    {"name": "국무회의", "type": "행정부"},
    {"name": "경찰서 (형법 위반)", "type": "감옥"},
    {"name": "대통령실", "type": "행정부"},
    {"name": "지방법원", "type": "사법부"},
    {"name": "고등법원", "type": "사법부"},
    {"name": "황금열쇠", "type": "찬스"},
    {"name": "대법원", "type": "사법부"},
    {"name": "헌법재판소", "type": "독립기관"},
    {"name": "선거관리위원회", "type": "독립기관"},
    {"name": "경찰서 (형법 위반)", "type": "감옥"},
    {"name": "감사원", "type": "행정부"}
]

purchasable_indices = [i for i, space in enumerate(board) if space["type"] not in ["시작", "찬스", "감옥"]]

quizzes = [
    {"q": "국가의 최고 규범이자 국민의 기본권을 보장하는 가장 으뜸이 되는 법은?", "options": ["민법", "형법", "헌법", "상법"], "answer": "헌법"},
    {"q": "모든 국민이 인간으로서의 존엄과 가치를 가지며, 차별받지 않을 권리는?", "options": ["자유권", "평등권", "사회권", "청구권"], "answer": "평등권"},
    {"q": "국민이 국가 기관 형성에 참여하거나, 선거에 참여할 수 있는 권리는?", "options": ["참정권", "사회권", "자유권", "청구권"], "answer": "참정권"},
    {"q": "국민이 인간다운 생활을 할 수 있도록 국가에 요구할 수 있는 권리는?", "options": ["자유권", "참정권", "평등권", "사회권"], "answer": "사회권"},
    {"q": "기본권이 침해되었을 때 이를 구제해 달라고 국가에 요구할 수 있는 수단적 권리는?", "options": ["청구권", "자유권", "평등권", "참정권"], "answer": "청구권"},
    {"q": "헌법을 개정하기 위해 최종적으로 반드시 거쳐야 하는 절차는?", "options": ["국회 상임위 통과", "국무회의 의결", "국민 투표", "대법원 판결"], "answer": "국민 투표"},
    {"q": "우리나라 헌법 제1조 1항, '대한민국은 (  ) 공화국이다.' 빈칸에 알맞은 말은?", "options": ["민주", "입헌", "자유", "복지"], "answer": "민주"},
    {"q": "국가의 주권이 국민에게 있다는 민주주의의 기본 원리는?", "options": ["입헌주의", "권력 분립", "국민 주권", "복지 국가"], "answer": "국민 주권"},
    {"q": "국민의 기본권은 무엇을 위해서만 법률로써 제한할 수 있을까요?", "options": ["대통령의 명령", "국가안전보장, 질서유지, 공공복리", "경제 발전", "국회의원의 동의"], "answer": "국가안전보장, 질서유지, 공공복리"},
    {"q": "기본권을 제한할 때에도 절대 침해할 수 없는 것은?", "options": ["자유와 권리의 본질적인 내용", "재산권", "거주 이전의 자유", "직업 선택의 자유"], "answer": "자유와 권리의 본질적인 내용"},
    {"q": "국회의원의 임기는 몇 년인가요?", "options": ["3년", "4년", "5년", "6년"], "answer": "4년"},
    {"q": "법률안을 제정하거나 개정하는 국가 기관은?", "options": ["국회", "정부", "대법원", "헌법재판소"], "answer": "국회"},
    {"q": "국회에서 국가의 1년 예산안을 심의하고 확정하는 권한은?", "options": ["입법 권한", "재정 권한", "국정 통제 권한", "사법 권한"], "answer": "재정 권한"},
    {"q": "매년 정기적으로 국회에서 행정부의 국정 운영 전반을 조사하는 활동은?", "options": ["국정 감사", "위헌 법률 심판", "조약 체결", "인사 청문회"], "answer": "국정 감사"},
    {"q": "고위 공직자를 임명하기 전에 국회에서 그 사람의 능력과 도덕성을 검증하는 제도는?", "options": ["국정 감사", "탄핵 소추", "인사 청문회", "국무회의"], "answer": "인사 청문회"},
    {"q": "법률안을 국회에 제출할 수 있는 권한을 가진 곳은 국회의원과 또 어디일까요?", "options": ["대법원", "정부(행정부)", "헌법재판소", "경찰청"], "answer": "정부(행정부)"},
    {"q": "국회의원을 선출할 때, 정당의 득표율에 따라 의석을 나누어 주는 제도는?", "options": ["지역구 선거", "비례 대표제", "다수결", "결선 투표"], "answer": "비례 대표제"},
    {"q": "국회의 회의 중 매년 1회, 9월에 열리는 정기적인 회의는?", "options": ["임시회", "정기회", "본회의", "상임위원회"], "answer": "정기회"},
    {"q": "국회에서 법안을 본회의에 올리기 전에 미리 전문적으로 심사하는 곳은?", "options": ["국무회의", "상임위원회", "감사원", "선거관리위원회"], "answer": "상임위원회"},
    {"q": "대통령 등 고위 공직자가 헌법이나 법률을 위반했을 때, 국회가 헌법재판소에 파면을 요구하는 권한은?", "options": ["탄핵 소추권", "면책 특권", "불체포 특권", "사면권"], "answer": "탄핵 소추권"},
    {"q": "우리나라 행정부의 최고 책임자는 누구인가요?", "options": ["국무총리", "국회의장", "대법원장", "대통령"], "answer": "대통령"},
    {"q": "우리나라 대통령의 임기는 몇 년이며, 연임이 가능한가요?", "options": ["4년, 연임 가능", "5년, 단임제(불가능)", "5년, 연임 가능", "6년, 단임제"], "answer": "5년, 단임제(불가능)"},
    {"q": "대통령을 보좌하며, 대통령이 직무를 수행할 수 없을 때 권한을 대행하는 사람은?", "options": ["국회의장", "헌법재판소장", "국무총리", "감사원장"], "answer": "국무총리"},
    {"q": "행정부의 주요 정책을 심의하는 최고 심의 기관(회의)은?", "options": ["국회 본회의", "대법원 전원합의체", "국무회의", "인사청문회"], "answer": "국무회의"},
    {"q": "대통령 소속이지만 독립적인 지위를 가지며, 국가의 세금 사용과 공무원의 직무를 검사하는 기관은?", "options": ["국세청", "국회", "감사원", "기획재정부"], "answer": "감사원"},
    {"q": "국회에서 통과된 법률안에 대해 대통령이 이의가 있을 때, 다시 심의해 달라고 요구하는 권한은?", "options": ["조약 체결권", "법률안 거부권", "사면권", "계엄 선포권"], "answer": "법률안 거부권"},
    {"q": "국민의 실생활과 밀접한 교육, 국방, 외교 등의 구체적인 행정 업무를 담당하는 곳은?", "options": ["행정 각 부처", "법원", "국회 상임위원회", "헌법재판소"], "answer": "행정 각 부처"},
    {"q": "대통령이 외국과 조약을 맺을 때, 반드시 동의를 받아야 하는 기관은?", "options": ["대법원", "국회", "감사원", "헌법재판소"], "answer": "국회"},
    {"q": "대통령은 국가 원수로서의 지위와 (    ) 수반으로서의 지위를 동시에 가집니다. 빈칸은?", "options": ["입법부", "사법부", "행정부", "언론"], "answer": "행정부"},
    {"q": "행정부의 각 부처의 장(예: 교육부 장관)을 다른 말로 무엇이라고 하나요?", "options": ["국무위원", "국회의원", "대법관", "헌법재판관"], "answer": "국무위원"},
    {"q": "법관은 무엇에 따라 독립하여 심판할까요?", "options": ["대통령의 지시", "여론", "헌법과 법률, 그 양심", "국회의원의 의견"], "answer": "헌법과 법률, 그 양심"},
    {"q": "우리나라 사법부의 최고 법원으로, 최종(3심) 재판을 담당하는 곳은?", "options": ["고등법원", "지방법원", "대법원", "헌법재판소"], "answer": "대법원"},
    {"q": "재판의 공정성을 위해 원칙적으로 한 사건에 대해 세 번까지 재판을 받을 수 있는 제도는?", "options": ["위헌 법률 심판", "심급 제도(3심제)", "배심원제", "국민 참여 재판"], "answer": "심급 제도(3심제)"},
    {"q": "1심 판결에 불복하여 2심 법원에 재판을 다시 청구하는 것을 무엇이라고 하나요?", "options": ["상고", "항소", "항고", "재심"], "answer": "항소"},
    {"q": "2심 판결에 불복하여 3심(대법원)에 재판을 청구하는 것을 무엇이라고 하나요?", "options": ["상고", "항소", "항고", "위헌 제청"], "answer": "상고"},
    {"q": "개인과 개인 사이의 권리나 이익 다툼을 해결하기 위한 재판은?", "options": ["형사 재판", "행정 재판", "민사 재판", "헌법 재판"], "answer": "민사 재판"},
    {"q": "범죄 유무를 판단하고 형벌을 부과하기 위한 재판은?", "options": ["형사 재판", "행정 재판", "민사 재판", "가사 재판"], "answer": "형사 재판"},
    {"q": "헌법재판소의 재판관은 총 몇 명으로 구성되나요?", "options": ["3명", "5명", "7명", "9명"], "answer": "9명"},
    {"q": "국가 기관의 공권력 행사로 기본권이 침해되었을 때 헌법재판소에 구제를 요청하는 심판은?", "options": ["탄핵 심판", "위헌 법률 심판", "헌법 소원 심판", "권한 쟁의 심판"], "answer": "헌법 소원 심판"},
    {"q": "국회에서 만든 법률이 헌법에 위반되는지 여부를 판단하여 효력을 상실시키는 심판은?", "options": ["권한 쟁의 심판", "정당 해산 심판", "위헌 법률 심판", "탄핵 심판"], "answer": "위헌 법률 심판"}
]

jail_events = [
    {"desc": "주차된 오토바이를 훔쳐 탔습니다. (절도죄) 20포인트 차감.", "penalty": -20},
    {"desc": "칠판에 친구를 놀렸습니다. (모욕죄) 15포인트 차감.", "penalty": -15},
    {"desc": "사람을 때렸습니다. (폭행죄) 25포인트 차감.", "penalty": -25},
    {"desc": "담배를 사기 위해 신분증 숫자를 위조했습니다. (공문서위조죄) 20포인트 차감.", "penalty": -20}
]

chance_events = [
    {"type": "normal", "desc": "국정감사에서 훌륭한 시민 제보를 하여 표창을 받습니다! 20포인트 획득.", "reward": 20},
    {"type": "normal", "desc": "길에 떨어진 지갑을 찾아주어 모범 시민이 되었습니다. 15포인트 획득.", "reward": 15},
    {"type": "normal", "desc": "무단횡단을 하다 적발되어 과태료를 냅니다. 5포인트 차감.", "reward": -5},
    {"type": "teacher_eval", "desc": "🔥 [도전!] 5초 안에 '삼권분립의 세 가지 국가 기관(입법, 행정, 사법)'을 큰 소리로 말하세요! (선생님이 결과를 판정합니다.)"},
    {"type": "branch_penalty", "target_types": ["입법부"], "penalty": 10, "desc": "⚖️ [대통령->국회] 대통령이 국회를 통과한 법률안에 대해 **'거부권'**을 행사했습니다! '입법부' 구역을 소유한 플레이어들은 각각 10포인트씩 잃습니다."},
    {"type": "lose_space", "targets": [1, 2], "desc": "⚖️ [헌법재판소->국회] 헌법재판소가 국회에서 만든 법률에 대해 **'위헌 결정'**을 내렸습니다! '국회 상임위원회'와 '국회 본회의장'의 소유권이 즉시 초기화됩니다."},
    {"type": "lose_space", "targets": [11], "desc": "⚖️ [국회->사법부] 국회가 대법원장 **'임명 동의안'**을 부결시켜 법원을 견제했습니다! '대법원' 구역의 소유권이 즉시 초기화됩니다."},
    {"type": "lose_space", "targets": [4], "desc": "⚖️ [국회->행정부] 국회가 행정부 장관에 대해 **'해임 건의권'**을 행사했습니다! '행정 각 부처' 구역의 소유권이 즉시 초기화됩니다."},
    {"type": "branch_penalty", "target_types": ["행정부"], "penalty": 15, "desc": "⚖️ [국회->행정부] 국회가 매서운 **'국정 감사'**를 실시하여 행정부의 잘못을 적발했습니다! '행정부' 구역을 소유한 플레이어들은 각각 15포인트씩 잃습니다."},
    {"type": "branch_penalty", "target_types": ["사법부"], "penalty": 10, "desc": "⚖️ [대통령->사법부] 대통령이 특별 **'사면권'**을 행사하여 법원 판결의 효력을 없앴습니다! '사법부' 구역을 소유한 플레이어들은 각각 10포인트씩 잃습니다."},
    {"type": "lose_space", "targets": [5], "desc": "⚖️ [대법원->행정부] 대법원이 행정부가 만든 명령이 헌법에 어긋난다며 **'명령·규칙 심사권'**을 행사했습니다! '국무회의' 구역의 소유권이 초기화됩니다."},
    {"type": "lose_space", "targets": [7], "desc": "⚖️ [헌법재판소->대통령] 🚨 헌법재판소가 국회의 탄핵 소추안을 인용하여 대통령이 파면되었습니다! **'대통령실'** 구역의 소유권이 즉시 초기화됩니다."}
]

player_colors = ["#e74c3c", "#3498db", "#2ecc71", "#e67e22", "#9b59b6"]
color_map = {
    "시작": "#ffe6e6", "입법부": "#ffcccc", "행정부": "#cce5ff",
    "사법부": "#ccffcc", "독립기관": "#e6ccff", "찬스": "#fff2cc", "감옥": "#d9d9d9"
}

def get_tile_html(index):
    space = board[index]
    bg_color = color_map.get(space["type"], "#ffffff")

    players_here = []
    for p_idx, pos in enumerate(st.session_state.player_positions):
        if pos == index:
            marker = f"<span style='display:inline-block; width:22px; height:22px; border-radius:50%; background-color:{player_colors[p_idx]}; color:white; font-size:12px; line-height:22px; text-align:center; margin:1px;'>P{p_idx+1}</span>"
            players_here.append(marker)
    player_marker = "".join(players_here)

    owner_marker = ""
    if index in st.session_state.owned_spaces:
        owner_idx = st.session_state.owned_spaces[index]
        owner_color = player_colors[owner_idx]
        owner_marker = f"<div style='color:{owner_color}; font-size:12px; font-weight:bold;'>[P{owner_idx+1} 소유]</div>"

    html_content = (
        f"<div style='background-color: {bg_color}; border: 2px solid #555; border-radius: 8px; "
        f"padding: 8px; height: 130px; display: flex; flex-direction: column; "
        f"justify-content: space-between; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);'>"
        f"<div style='font-weight: bold; font-size: 13px; text-align: center; word-break: keep-all;'>{space['name']}</div>"
        f"<div style='text-align: center; min-height: 18px;'>{owner_marker}</div>"
        f"<div style='text-align: center; min-height: 25px;'>{player_marker}</div>"
        f"</div>"
    )
    return html_content

def check_game_over():
    if len(st.session_state.owned_spaces) >= len(purchasable_indices):
        st.session_state.game_over = True
        max_score = max(st.session_state.player_scores)
        winners = [f"P{i+1}" for i, score in enumerate(st.session_state.player_scores) if score == max_score]
        st.session_state.message = f"🎉 **게임 종료!** 모든 땅이 점령되었습니다. 최종 우승은 **{', '.join(winners)}** (점수: {max_score}점) 입니다! 🎉"

# ────────────────────────────────────────────
#  주사위 굴리기 로직 (보드 렌더링과 완전 분리)
# ────────────────────────────────────────────
def handle_dice_roll():
    current_p = st.session_state.current_turn
    dice_roll = random.randint(1, 6)
    st.session_state.last_dice = dice_roll

    old_pos = st.session_state.player_positions[current_p]
    new_pos = old_pos + dice_roll

    if new_pos >= len(board):
        new_pos = new_pos % len(board)
        st.session_state.player_scores[current_p] += 20
        st.session_state.message = f"[P{current_p+1}] 출발선을 통과하여 월급 20점을 받았습니다! "
    else:
        st.session_state.message = f"[P{current_p+1}] {board[new_pos]['name']}에 도착했습니다. "

    st.session_state.player_positions[current_p] = new_pos
    current_space = board[new_pos]
    turn_ends_now = True

    if current_space['type'] == "감옥":
        event = random.choice(jail_events)
        st.session_state.player_scores[current_p] += event['penalty']
        st.session_state.message += f"<br>🚨 <b>경찰서:</b> {event['desc']}"

    elif current_space['type'] == "찬스":
        event = random.choice(chance_events)
        if event["type"] == "normal":
            st.session_state.player_scores[current_p] += event['reward']
            st.session_state.message += f"<br>🔑 <b>황금열쇠:</b> {event['desc']}"

        elif event["type"] == "lose_space":
            st.session_state.message += f"<br>🔑 <b>황금열쇠:</b> {event['desc']}"
            lost_someone = False
            for ts in event["targets"]:
                if ts in st.session_state.owned_spaces:
                    owner = st.session_state.owned_spaces[ts]
                    del st.session_state.owned_spaces[ts]
                    st.session_state.message += f"<br>➡ 앗! P{owner+1}님이 소유했던 '{board[ts]['name']}'의 주인이 사라졌습니다!"
                    lost_someone = True
            if not lost_someone:
                st.session_state.message += "<br>➡ 아직 아무도 해당 구역을 소유하지 않아 무사히 넘어갑니다."

        elif event["type"] == "branch_penalty":
            st.session_state.message += f"<br>🔑 <b>황금열쇠:</b> {event['desc']}"
            penalized_players = set()
            for space_idx, owner_idx in st.session_state.owned_spaces.items():
                if board[space_idx]["type"] in event["target_types"]:
                    penalized_players.add(owner_idx)
            for p_idx in penalized_players:
                st.session_state.player_scores[p_idx] -= event["penalty"]
                st.session_state.message += f"<br>➡ P{p_idx+1}님이 {event['penalty']}포인트를 잃었습니다."
            if not penalized_players:
                st.session_state.message += "<br>➡ 다행히 해당 기관을 소유한 플레이어가 없어 아무 일도 일어나지 않았습니다."

        elif event["type"] == "teacher_eval":
            st.session_state.message += f"<br>🔑 <b>황금열쇠:</b> {event['desc']}"
            st.session_state.teacher_eval_pending = True
            turn_ends_now = False

    elif current_space['type'] not in ["시작", "감옥", "찬스"]:
        if new_pos in st.session_state.owned_spaces:
            owner = st.session_state.owned_spaces[new_pos]
            if owner == current_p:
                st.session_state.message += "<br>나의 구역입니다. 편안하게 휴식합니다."
            else:
                st.session_state.message += f"<br>앗! P{owner+1}의 구역입니다. 통행료 5포인트를 지불합니다."
                st.session_state.player_scores[current_p] -= 5
                st.session_state.player_scores[owner] += 5
        else:
            st.session_state.current_quiz = random.choice(quizzes)
            turn_ends_now = False

    if turn_ends_now:
        st.session_state.current_turn = (current_p + 1) % st.session_state.num_players
        check_game_over()


# ════════════════════════════════════════════
#  UI 렌더링
# ════════════════════════════════════════════
st.title("🏛️ 헌법 마블 보드게임")

# 점수판
score_cols = st.columns(st.session_state.num_players)
for i in range(st.session_state.num_players):
    with score_cols[i]:
        if i == st.session_state.current_turn and not st.session_state.game_over:
            st.success(f"P{i+1} 점수: {st.session_state.player_scores[i]} (현재 차례)")
        else:
            st.info(f"P{i+1} 점수: {st.session_state.player_scores[i]}")

st.write("---")

# ── 보드 렌더링 (인터랙티브 요소 없음) ──
current_p = st.session_state.current_turn

board_layout = [
    [0,  1,  2,  3,  4],
    [15, -1, -1, -1, 5],
    [14, -1, -1, -1, 6],
    [13, -1, -1, -1, 7],
    [12, 11, 10,  9,  8]
]

for r_idx, row in enumerate(board_layout):
    cols = st.columns(5)
    for c_idx, cell_index in enumerate(row):
        with cols[c_idx]:
            if cell_index != -1:
                st.markdown(get_tile_html(cell_index), unsafe_allow_html=True)
            else:
                # 가운데 빈 셀: 현재 플레이어 정보 + 주사위 결과만 표시
                if r_idx == 2 and c_idx == 2:
                    if st.session_state.game_over:
                        st.markdown(
                            "<h2 style='text-align:center; color:#e74c3c;'>게임 종료!</h2>",
                            unsafe_allow_html=True
                        )
                    else:
                        color = player_colors[current_p]
                        dice_display = (
                            f"🎲 {st.session_state.last_dice}"
                            if st.session_state.last_dice
                            else "🎲 ?"
                        )
                        st.markdown(
                            f"<div style='text-align:center;'>"
                            f"<h3 style='color:{color}; margin-bottom:4px;'>P{current_p+1} 차례</h3>"
                            f"<h1 style='font-size:40px; margin:0;'>{dice_display}</h1>"
                            f"</div>",
                            unsafe_allow_html=True
                        )

st.write("---")

# ── 이벤트 메시지 ──
st.markdown(
    f"<div style='padding: 15px; background-color: #f8f9fa; border-left: 5px solid #ccc; font-size: 16px;'>"
    f"{st.session_state.message}</div>",
    unsafe_allow_html=True
)
st.write("")

# ══════════════════════════════════════════════════════════
#  컨트롤 패널 (보드 아래에 독립적으로 배치 — 핵심 수정 사항)
#  모든 버튼/폼을 루프 밖, 최상위 레이아웃에서 렌더링하여
#  Streamlit의 위젯 키 충돌 및 st.empty() 추적 오류 방지
# ══════════════════════════════════════════════════════════

if not st.session_state.game_over:

    # [1] 주사위 굴리기 버튼
    if (st.session_state.current_quiz is None
            and not st.session_state.teacher_eval_pending):
        if st.button("🎲 주사위 굴리기", use_container_width=True, key="dice_button"):
            handle_dice_roll()
            st.rerun()

    # [2] 선생님 평가 폼
    if st.session_state.teacher_eval_pending:
        st.error(
            f"👨‍🏫 **선생님 평가 대기 중:** "
            f"[P{current_p+1}] 학생이 5초 안에 '입법부, 행정부, 사법부'를 정확히 말했나요?"
        )
        col_succ, col_fail = st.columns(2)
        with col_succ:
            if st.button("⭕ 성공! (30포인트 획득)", use_container_width=True, key="eval_success"):
                st.session_state.player_scores[current_p] += 30
                st.session_state.message = f"[P{current_p+1}] 미션 성공! 선생님의 인정으로 30포인트를 획득했습니다."
                st.session_state.teacher_eval_pending = False
                st.session_state.current_turn = (current_p + 1) % st.session_state.num_players
                check_game_over()
                st.rerun()
        with col_fail:
            if st.button("❌ 실패 (10포인트 차감)", use_container_width=True, key="eval_fail"):
                st.session_state.player_scores[current_p] -= 10
                st.session_state.message = f"[P{current_p+1}] 미션 실패! 10포인트가 차감되었습니다."
                st.session_state.teacher_eval_pending = False
                st.session_state.current_turn = (current_p + 1) % st.session_state.num_players
                check_game_over()
                st.rerun()

    # [3] 퀴즈 폼
    if st.session_state.current_quiz is not None:
        st.warning(f"[P{current_p+1}] 이 구역을 소유하려면 아래 퀴즈를 맞혀야 합니다!")
        quiz = st.session_state.current_quiz

        st.write(f"**문제:** {quiz['q']}")
        with st.form(key="quiz_form"):
            user_answer = st.radio("정답 선택:", quiz['options'], index=None)
            submit_button = st.form_submit_button(label="정답 확인 및 턴 종료")

            if submit_button:
                if user_answer == quiz['answer']:
                    st.session_state.player_scores[current_p] += 15
                    st.session_state.owned_spaces[st.session_state.player_positions[current_p]] = current_p
                    st.session_state.message = (
                        f"정답입니다! 15포인트를 획득하고 "
                        f"{board[st.session_state.player_positions[current_p]]['name']}을(를) 점령했습니다."
                    )
                else:
                    st.session_state.player_scores[current_p] -= 5
                    st.session_state.message = (
                        f"오답입니다. 올바른 정답은 '{quiz['answer']}' 입니다. 5포인트를 잃었습니다."
                    )
                st.session_state.current_quiz = None
                st.session_state.current_turn = (current_p + 1) % st.session_state.num_players
                check_game_over()
                st.rerun()
