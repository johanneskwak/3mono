import streamlit as st
import random
import time

st.set_page_config(layout="wide", page_title="삼권분립 마블")

# --- [게임 설정 단계] ---
if 'game_started' not in st.session_state:
    st.session_state.game_started = False

if not st.session_state.game_started:
    st.title("삼권분립 마블 보드게임 - 게임 설정")
    st.write("플레이할 인원수를 선택하고 게임을 시작하세요.")
    
    num_players = st.number_input("플레이어 수 (1~5명)", min_value=1, max_value=5, value=4)
    
    if st.button("게임 시작", use_container_width=True):
        st.session_state.num_players = num_players
        st.session_state.player_positions = [0] * num_players
        st.session_state.player_scores = [50] * num_players
        st.session_state.owned_spaces = {}  # {칸 인덱스: 소유한 플레이어 인덱스}
        st.session_state.current_turn = 0   # 0부터 시작 (P1)
        st.session_state.current_quiz = None
        st.session_state.message = "게임이 시작되었습니다! P1의 차례입니다."
        st.session_state.last_dice = None
        st.session_state.game_started = True
        st.rerun()
    st.stop()  # 설정이 끝날 때까지 아래 코드는 실행하지 않음

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

quizzes = [
    {"q": "법률안을 제출할 수 있는 권한을 가진 곳은 국회의원과 또 어디일까요?", "options": ["대법원", "정부(행정부)", "헌법재판소", "경찰청"], "answer": "정부(행정부)"},
    {"q": "우리나라 행정부의 최고 책임자는 누구인가요?", "options": ["국무총리", "국회의장", "대법원장", "대통령"], "answer": "대통령"},
    {"q": "법관은 무엇에 따라 독립하여 심판할까요?", "options": ["대통령의 지시", "국민의 여론", "헌법과 법률, 그 양심", "국회의원의 의견"], "answer": "헌법과 법률, 그 양심"},
    {"q": "고위 공직자가 직무를 집행하면서 헌법을 위반했을 때, 파면을 결정하는 헌법재판소의 심판은?", "options": ["위헌 법률 심판", "탄핵 심판", "정당 해산 심판", "권한 쟁의 심판"], "answer": "탄핵 심판"},
    {"q": "국회에서 국가의 1년 예산안을 심의하고 확정하는 권한은 무엇에 해당할까요?", "options": ["입법에 관한 권한", "재정에 관한 권한", "국정 통제에 관한 권한", "사법에 관한 권한"], "answer": "재정에 관한 권한"},
    {"q": "법률이 헌법에 위반되는지 여부를 심판하여, 위반될 경우 법률의 효력을 상실시키는 곳은?", "options": ["대법원", "국회", "헌법재판소", "법무부"], "answer": "헌법재판소"},
    {"q": "1심 판결에 불복하여 2심 법원에 재판을 다시 청구하는 것을 무엇이라고 하나요?", "options": ["상고", "항소", "항고", "재심"], "answer": "항소"},
    {"q": "대통령 소속이지만 독립적인 지위를 가지며, 국가의 세금 사용을 검사하는 기관은?", "options": ["국세청", "국회", "감사원", "기획재정부"], "answer": "감사원"},
    {"q": "국회의원의 임기는 몇 년일까요?", "options": ["3년", "4년", "5년", "6년"], "answer": "4년"},
    {"q": "국민의 대표 기관인 국회에서 매년 정기적으로 국정 운영 전반에 관해 조사하고 잘못된 부분을 적발하는 활동은?", "options": ["위헌 법률 심판", "국정 감사", "조약 체결", "행정 심판"], "answer": "국정 감사"},
    {"q": "국회의원을 선출하는 방식 중, 정당의 득표율에 따라 의석을 나누어 주는 제도는 무엇인가요?", "options": ["지역구 선거", "비례 대표제", "다수결 원칙", "국민 투표"], "answer": "비례 대표제"},
    {"q": "우리나라 대통령의 임기는 몇 년이며, 연임(이어서 다시 하는 것)이 가능할까요?", "options": ["4년, 연임 가능", "5년, 단임제(불가능)", "5년, 연임 가능", "6년, 단임제(불가능)"], "answer": "5년, 단임제(불가능)"},
    {"q": "행정부의 주요 정책을 심의하는 최고 심의 기관으로, 대통령, 국무총리, 국무위원으로 구성된 회의는?", "options": ["국회 본회의", "대법원 전원합의체", "국무회의", "인사청문회"], "answer": "국무회의"},
    {"q": "대통령을 보좌하며, 대통령이 외국에 나가거나 일시적으로 일할 수 없을 때 권한을 대행하는 사람은?", "options": ["국회의장", "대법원장", "헌법재판소장", "국무총리"], "answer": "국무총리"},
    {"q": "우리나라 사법부의 최고 법원으로, 3심 재판을 담당하는 곳은 어디일까요?", "options": ["고등법원", "지방법원", "대법원", "헌법재판소"], "answer": "대법원"},
    {"q": "재판의 공정성을 위해 원칙적으로 한 사건에 대해 세 번까지 재판을 받을 수 있도록 하는 제도는?", "options": ["권력 분립", "위헌 법률 심판", "심급 제도(3심제)", "배심원제"], "answer": "심급 제도(3심제)"},
    {"q": "개인과 개인 사이의 권리나 이익에 관한 다툼을 해결하기 위한 재판은 무엇인가요?", "options": ["형사 재판", "행정 재판", "민사 재판", "헌법 재판"], "answer": "민사 재판"},
    {"q": "헌법재판소의 재판관은 총 몇 명으로 구성될까요?", "options": ["3명", "5명", "7명", "9명"], "answer": "9명"},
    {"q": "국가 기관의 공권력 행사나 불행사로 인해 국민의 기본권이 침해되었을 때, 이를 구제해 달라고 헌법재판소에 요청하는 심판은?", "options": ["탄핵 심판", "위헌 법률 심판", "헌법 소원 심판", "정당 해산 심판"], "answer": "헌법 소원 심판"},
    {"q": "국가 권력을 입법부, 행정부, 사법부로 나누어 서로 견제하고 균형을 이루게 하는 민주주의의 기본 원리는?", "options": ["국민 주권의 원리", "입헌주의의 원리", "복지 국가의 원리", "권력 분립의 원리"], "answer": "권력 분립의 원리"}
]

jail_events = [
    {"desc": "주차된 오토바이를 훔쳐 탔습니다. (절도죄 적용) 20포인트 차감.", "penalty": -20},
    {"desc": "편의점에서 몰래 음료수를 훔쳤습니다. (절도죄 적용) 15포인트 차감.", "penalty": -15},
    {"desc": "담배를 사기 위해 신분증의 숫자를 위조했습니다. (공문서위조죄 적용) 20포인트 차감.", "penalty": -20}
]

chance_events = [
    {"desc": "국정감사에서 날카로운 지적으로 훌륭한 활약을 보였습니다! 20포인트 획득.", "reward": 20},
    {"desc": "길에 떨어진 지갑을 찾아주어 모범 시민 표창을 받았습니다. 15포인트 획득.", "reward": 15},
    {"desc": "무단횡단을 하다 적발되어 과태료를 냅니다. 5포인트 차감.", "reward": -5}
]

# 플레이어 고유 색상 (빨강, 파랑, 초록, 주황, 보라)
player_colors = ["#e74c3c", "#3498db", "#2ecc71", "#e67e22", "#9b59b6"]
color_map = {
    "시작": "#ffe6e6", "입법부": "#ffcccc", "행정부": "#cce5ff", 
    "사법부": "#ccffcc", "독립기관": "#e6ccff", "찬스": "#fff2cc", "감옥": "#d9d9d9"
}

def get_tile_html(index):
    space = board[index]
    bg_color = color_map.get(space["type"], "#ffffff")
    
    # 해당 칸에 위치한 플레이어 마커 생성
    players_here = []
    for p_idx, pos in enumerate(st.session_state.player_positions):
        if pos == index:
            marker = f"<span style='display:inline-block; width:22px; height:22px; border-radius:50%; background-color:{player_colors[p_idx]}; color:white; font-size:12px; line-height:22px; text-align:center; margin:1px;'>P{p_idx+1}</span>"
            players_here.append(marker)
    player_marker = "".join(players_here)
    
    # 소유권 표시
    owner_marker = ""
    if index in st.session_state.owned_spaces:
        owner_idx = st.session_state.owned_spaces[index]
        owner_color = player_colors[owner_idx]
        owner_marker = f"<div style='color:{owner_color}; font-size:12px; font-weight:bold;'>[P{owner_idx+1} 소유]</div>"
        
    return f"""
    <div style="background-color: {bg_color}; border: 2px solid #555; border-radius: 8px; 
                padding: 8px; height: 130px; display: flex; flex-direction: column; 
                justify-content: space-between; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);">
        <div style="font-weight: bold; font-size: 13px; text-align: center; word-break: keep-all;">
            {space['name']}
        </div>
        <div style="text-align: center; min-height: 18px;">
            {owner_marker}
        </div>
        <div style="text-align: center; min-height: 25px;">
            {player_marker}
        </div>
    </div>
    """

# --- [상단 대시보드 (점수판)] ---
st.title("헌법 마블 보드게임")

score_cols = st.columns(st.session_state.num_players)
for i in range(st.session_state.num_players):
    with score_cols[i]:
        if i == st.session_state.current_turn:
            st.success(f"P{i+1} 점수: {st.session_state.player_scores[i]} (현재 차례)")
        else:
            st.info(f"P{i+1} 점수: {st.session_state.player_scores[i]}")

st.write("---")

# --- [보드판 및 중앙 컨트롤 렌더링] ---
board_layout = [
    [0,  1,  2,  3,  4],
    [15, -1, -1, -1, 5],
    [14, -1, -1, -1, 6],
    [13, -1, -1, -1, 7],
    [12, 11, 10,  9,  8]
]

current_p = st.session_state.current_turn

for r_idx, row in enumerate(board_layout):
    cols = st.columns(5)
    for c_idx, cell_index in enumerate(row):
        with cols[c_idx]:
            if cell_index != -1:
                st.markdown(get_tile_html(cell_index), unsafe_allow_html=True)
            else:
                # 보드판 정중앙 (주사위 굴리기 영역)
                if r_idx == 2 and c_idx == 2:
                    st.markdown(f"<h3 style='text-align:center; color:{player_colors[current_p]};'>P{current_p+1} 차례</h3>", unsafe_allow_html=True)
                    
                    dice_placeholder = st.empty()
                    if st.session_state.last_dice:
                        dice_placeholder.markdown(f"<h1 style='text-align:center; font-size: 40px;'>주사위: {st.session_state.last_dice}</h1>", unsafe_allow_html=True)
                    else:
                        dice_placeholder.markdown(f"<h1 style='text-align:center; font-size: 40px; opacity: 0.3;'>주사위: ?</h1>", unsafe_allow_html=True)
                    
                    if st.session_state.current_quiz is None:
                        if st.button("주사위 굴리기", use_container_width=True):
                            for _ in range(10):
                                dice_placeholder.markdown(f"<h1 style='text-align:center; font-size: 40px;'>주사위: {random.randint(1,6)}</h1>", unsafe_allow_html=True)
                                time.sleep(0.05)
                            
                            dice_roll = random.randint(1, 6)
                            st.session_state.last_dice = dice_roll
                            dice_placeholder.markdown(f"<h1 style='text-align:center; font-size: 40px; color: #d32f2f;'>주사위: {dice_roll}</h1>", unsafe_allow_html=True)
                            time.sleep(0.4)
                            
                            old_pos = st.session_state.player_positions[current_p]
                            new_pos = old_pos + dice_roll
                            
                            if new_pos >= len(board):
                                new_pos = new_pos % len(board)
                                st.session_state.player_scores[current_p] += 20
                                st.session_state.message = f"[P{current_p+1}] 출발선을 통과하여 월급 20점을 받았습니다!"
                            else:
                                st.session_state.message = f"[P{current_p+1}] {board[new_pos]['name']}에 도착했습니다."
                                
                            st.session_state.player_positions[current_p] = new_pos
                            current_space = board[new_pos]
                            turn_ends_now = True
                            
                            # 도착한 칸의 이벤트 처리 로직
                            if current_space['type'] == "감옥":
                                event = random.choice(jail_events)
                                st.session_state.player_scores[current_p] += event['penalty']
                                st.session_state.message += f"<br>경찰서: {event['desc']}"
                                
                            elif current_space['type'] == "찬스":
                                event = random.choice(chance_events)
                                st.session_state.player_scores[current_p] += event['reward']
                                st.session_state.message += f"<br>황금열쇠: {event['desc']}"
                                
                            elif current_space['type'] not in ["시작", "감옥", "찬스"]:
                                if new_pos in st.session_state.owned_spaces:
                                    owner = st.session_state.owned_spaces[new_pos]
                                    if owner == current_p:
                                        st.session_state.message += "<br>이미 점령한 나의 구역입니다. 안전하게 휴식합니다."
                                    else:
                                        st.session_state.message += f"<br>앗! P{owner+1}의 구역입니다. 통행료 5포인트를 지불합니다."
                                        st.session_state.player_scores[current_p] -= 5
                                        st.session_state.player_scores[owner] += 5
                                else:
                                    st.session_state.current_quiz = random.choice(quizzes)
                                    turn_ends_now = False # 퀴즈를 풀어야 턴이 넘어감
                                    
                            if turn_ends_now:
                                st.session_state.current_turn = (current_p + 1) % st.session_state.num_players
                                
                            st.rerun()

st.write("---")

# --- [상태창 및 퀴즈 폼] ---
st.markdown(f"<div style='padding: 15px; background-color: #f8f9fa; border-left: 5px solid #ccc; font-size: 16px;'>{st.session_state.message}</div>", unsafe_allow_html=True)
st.write("")

if st.session_state.current_quiz is not None:
    st.warning(f"[P{current_p+1}] 이 구역을 소유하려면 아래 퀴즈를 맞혀야 합니다!")
    quiz = st.session_state.current_quiz
    
    with st.container():
        st.write(f"**문제:** {quiz['q']}")
        with st.form(key="quiz_form"):
            user_answer = st.radio("정답 선택:", quiz['options'], index=None)
            submit_button = st.form_submit_button(label="정답 확인 및 턴 종료")
            
            if submit_button:
                if user_answer == quiz['answer']:
                    st.session_state.player_scores[current_p] += 15
                    st.session_state.owned_spaces[st.session_state.player_positions[current_p]] = current_p
                    st.session_state.message = f"정답입니다! 15포인트를 획득하고 {board[st.session_state.player_positions[current_p]]['name']}을(를) 점령했습니다."
                else:
                    st.session_state.player_scores[current_p] -= 5
                    st.session_state.message = f"오답입니다. 올바른 정답은 '{quiz['answer']}' 입니다. 5포인트를 잃었습니다."
                    
                st.session_state.current_quiz = None
                st.session_state.current_turn = (current_p + 1) % st.session_state.num_players
                st.rerun()
