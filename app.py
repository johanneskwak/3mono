import streamlit as st
import random

# 초기 상태 설정
if 'position' not in st.session_state:
    st.session_state.position = 0
if 'score' not in st.session_state:
    st.session_state.score = 50
if 'owned_spaces' not in st.session_state:
    st.session_state.owned_spaces = []
if 'current_quiz' not in st.session_state:
    st.session_state.current_quiz = None
if 'message' not in st.session_state:
    st.session_state.message = "주사위를 굴려 게임을 시작하세요."

# 보드판 구역 설정
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

# 중3 사회 헌법과 국가기관 퀴즈 데이터
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

# 형법 위반 이벤트 (1단원 연계)
jail_events = [
    {"desc": "주차된 오토바이를 훔쳐 탔습니다. (절도죄 적용) 합의금 및 벌금으로 20포인트 차감.", "penalty": -20},
    {"desc": "편의점에서 몰래 음료수를 훔쳤습니다. (절도죄 적용) 15포인트 차감.", "penalty": -15},
    {"desc": "담배를 사기 위해 신분증의 숫자를 위조했습니다. (공문서위조죄 적용) 20포인트 차감.", "penalty": -20},
    {"desc": "화가 나서 다른 사람의 물건을 일부러 부수었습니다. (손괴죄 적용) 15포인트 차감.", "penalty": -15},
    {"desc": "친구와 싸우다 주먹을 휘둘러 다치게 했습니다. (상해죄 적용) 20포인트 차감.", "penalty": -20}
]

# 황금열쇠 이벤트
chance_events = [
    {"desc": "국정감사에서 날카로운 지적으로 훌륭한 활약을 보였습니다! 20포인트 획득.", "reward": 20},
    {"desc": "길에 떨어진 지갑을 찾아주어 모범 시민 표창을 받았습니다. 15포인트 획득.", "reward": 15},
    {"desc": "선거일에 투표를 완료하여 민주주의 발전에 기여했습니다. 10포인트 획득.", "reward": 10},
    {"desc": "무단횡단을 하다 적발되어 과태료를 냅니다. 5포인트 차감.", "reward": -5}
]

st.title("헌법 마블 게임")
st.subheader("국가기관 구역을 차지하고 민주주의 포인트를 모아보세요")

col1, col2 = st.columns(2)
with col1:
    st.info(f"현재 위치: {board[st.session_state.position]['name']}")
with col2:
    st.success(f"내 포인트: {st.session_state.score} 점")

st.write(st.session_state.message)

board_display = ""
for i, space in enumerate(board):
    if i == st.session_state.position:
        board_display += f"[{space['name']}(현재)] - "
    elif i in st.session_state.owned_spaces:
        board_display += f"[{space['name']}(내 구역)] - "
    else:
        board_display += f"{space['name']} - "
st.write("보드판 진행 상황: " + board_display[:-3])

st.write("---")

if st.session_state.current_quiz is None:
    if st.button("주사위 굴리기", use_container_width=True):
        dice_roll = random.randint(1, 6)
        new_position = st.session_state.position + dice_roll
        
        if new_position >= len(board):
            new_position = new_position % len(board)
            st.session_state.score += 20
            st.session_state.message = f"주사위 {dice_roll}이 나왔습니다. 출발선을 통과하여 월급 20점을 받았습니다!"
        else:
            st.session_state.message = f"주사위 {dice_roll}이 나왔습니다. {board[new_position]['name']}에 도착했습니다."
            
        st.session_state.position = new_position
        current_space = board[new_position]
        
        # 칸 종류별 이벤트 처리
        if current_space['type'] == "감옥":
            event = random.choice(jail_events)
            st.session_state.score += event['penalty']
            st.session_state.message += f"\n\n경찰서에 도착했습니다! {event['desc']}"
            
        elif current_space['type'] == "찬스":
            event = random.choice(chance_events)
            st.session_state.score += event['reward']
            st.session_state.message += f"\n\n황금열쇠를 뽑았습니다! {event['desc']}"
            
        elif current_space['type'] not in ["시작", "감옥", "찬스"] and new_position not in st.session_state.owned_spaces:
            st.session_state.current_quiz = random.choice(quizzes)
            
        elif new_position in st.session_state.owned_spaces:
            st.session_state.message += "\n\n이미 점령한 나의 구역입니다. 편안하게 휴식합니다."
            
        st.rerun()

# 퀴즈 풀기 로직
if st.session_state.current_quiz is not None:
    st.warning("이 구역을 차지하려면 퀴즈를 풀어야 합니다.")
    quiz = st.session_state.current_quiz
    
    st.write(f"문제: {quiz['q']}")
    
    with st.form(key="quiz_form"):
        user_answer = st.radio("정답을 선택하세요:", quiz['options'], index=None)
        submit_button = st.form_submit_button(label="정답 확인 및 구역 획득")
        
        if submit_button:
            if user_answer == quiz['answer']:
                st.session_state.score += 15
                st.session_state.owned_spaces.append(st.session_state.position)
                st.session_state.message = "정답입니다! 15포인트를 획득하고 이 기관을 내 구역으로 만들었습니다."
            else:
                st.session_state.score -= 5
                st.session_state.message = f"오답입니다. 올바른 정답은 '{quiz['answer']}' 입니다. 5포인트를 잃었습니다."
                
            st.session_state.current_quiz = None
            st.rerun()