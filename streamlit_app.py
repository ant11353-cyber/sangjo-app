import streamlit as st
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

# -----------------------------------------------------------------------------
# 1. 페이지 설정 및 배경화면
# -----------------------------------------------------------------------------
st.set_page_config(page_title="천비칠마 상조회", page_icon="📱", layout="wide")

# 배경화면 CSS
background_url = "https://images.unsplash.com/photo-1497366216548-37526070297c?q=80&w=1920&auto=format&fit=crop"

st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("{background_url}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}
    .block-container {{
        background-color: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 2rem;
        margin-top: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }}
    </style>
    """,
    unsafe_allow_html=True
)

st.title("📱 천비칠마 상조회 통합 관리")
st.write("원하시는 메뉴의 문을 열어주세요.")

# -----------------------------------------------------------------------------
# 2. 데이터 불러오기 및 공통 계산 함수
# -----------------------------------------------------------------------------
@st.cache_data(ttl=60)
def load_data(sheet_name):
    try:
        url = st.secrets["connections"]["sheet_url"]
        # 구글 시트 주소에서 ID 추출
        if "/d/" in url:
            sheet_id = url.split("/d/")[1].split("/")[0]
            csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
            return pd.read_csv(csv_url)
        else:
            return pd.DataFrame()
    except Exception:
        return pd.DataFrame()

def get_dues_calc_info():
    today = datetime.now()
    # 기준월: 앱 실행일이 속한 달의 전달
    ref_date = today - relativedelta(months=1)
    
    # 2020년 2월부터 기준월까지의 개월 수 계산
    start_date = datetime(2020, 2, 1)
    diff = relativedelta(ref_date, start_date)
    months_passed = diff.years * 12 + diff.months
    
    if months_passed < 0: months_passed = 0
        
    return ref_date, months_passed

# -----------------------------------------------------------------------------
# 3. 메뉴 선택 (3개의 문)
# -----------------------------------------------------------------------------
if 'menu' not in st.session_state:
    st.session_state['menu'] = 'home'

# 홈 화면
if st.session_state['menu'] == 'home':
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("📊 전체 현황을 봅니다.")
        if st.button("🚪 회원 전체 현황", use_container_width=True):
            st.session_state['menu'] = 'all_status'
            st.rerun()

    with col2:
        st.warning("🔒 개인 정보를 확인합니다.")
        if st.button("🚪 회원 개인 현황", use_container_width=True):
            st.session_state['menu'] = 'personal_status'
            st.rerun()

    with col3:
        st.success("📜 회칙을 확인합니다.")
        if st.button("🚪 회칙", use_container_width=True):
            st.session_state['menu'] = 'rules'
            st.rerun()

def go_home():
    st.divider()
    if st.button("🏠 홈으로 돌아가기"):
        st.session_state['menu'] = 'home'
        st.rerun()

# -----------------------------------------------------------------------------
# 4. [기능 1] 회원 개인 현황 (비밀번호 체크)
# -----------------------------------------------------------------------------
if st.session_state['menu'] == 'personal_status':
    st.header("🔒 회원 개인 현황")
    st.write("개인 정보를 보호하기 위해 비밀번호를 입력해주세요.")
    
    password_input = st.text_input("비밀번호 4자리를 입력하세요", type="password")
    
    if password_input:
        df_members = load_data("members")
        df_ledger = load_data("ledger")
        
        # 비밀번호 매칭
        # 비밀번호가 숫자일 수도 있으므로 문자로 변환해서 비교
        user_info = df_members[df_members['비밀번호'].astype(str) == str(password_input)]
        
        if not user_info.empty:
            user = user_info.iloc[0]
            user_name = user['성명']
            
            st.success(f"환영합니다, {user_name} ({user['직책']})님!")
            
            # --- 계산 로직 ---
            ref_date,
