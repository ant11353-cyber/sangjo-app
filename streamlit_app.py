import streamlit as st
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
import base64

# -----------------------------------------------------------------------------
# 1. 초기 설정 (페이지 제목 등)
# -----------------------------------------------------------------------------
st.set_page_config(page_title="천비칠마 상조회", page_icon="📱", layout="wide")

# 세션 상태 초기화 (메뉴 기억하기)
if 'menu' not in st.session_state:
    st.session_state['menu'] = 'home'

# -----------------------------------------------------------------------------
# 2. 디자인 및 배경화면 제어 함수 (핵심 수정 부분!)
# -----------------------------------------------------------------------------
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_style(current_menu):
    """메뉴 상태에 따라 배경화면을 다르게 설정하는 함수"""
    
    # 공통 스타일 (버튼, 박스 등)
    common_style = """
    <style>
    /* 상세 페이지용 흰색 박스 스타일 */
    .content-box {{
        background-color: #ffffff;
        border-radius: 15px;
        padding: 30px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        margin-top: 20px;
        margin-bottom: 20px;
        max-width: 1200px;
        margin-left: auto;
        margin-right: auto;
    }}
    /* 버튼 기본 스타일 */
    .stButton > button {{
        width: 100%;
        height: 4rem;
        border-radius: 8px;
        font-size: 1.2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }}
    </style>
    """
    st.markdown(common_style, unsafe_allow_html=True)

    # [CASE 1] 홈 화면일 때 -> 배경화면 이미지 사용
    if current_menu == 'home':
        try:
            bin_str = get_base64_of_bin_file('bg.png')
            home_style = f"""
            <style>
            .stApp {{
                background-image: url("data:image/png;base64,{bin_str}");
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
                background-attachment: fixed;
            }}
            /* 홈 화면에서는 상단 여백 제거 및 컨테이너 투명화 */
            .block-container {{
                background-color: transparent; 
                padding-top: 0rem;
                padding-left: 2rem;
                max-width: 100%;
            }}
            /* 홈 화면 버튼: 배경에 잘 보이게 반투명 검정 */
            .stButton > button {{
                background-color: rgba(0, 0, 0, 0.6); 
                color: #f0f0f0;
                border: 1px solid rgba(255, 255, 255, 0.3);
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.5);
            }}
            .stButton > button:hover {{
                background-color: rgba(0, 0, 0, 0.9);
                color: #ffcc00;
                border-color: #ffcc00;
                transform: scale(1.02);
            }}
            </style>
            """
            st.markdown(home_style, unsafe_allow_html=True)
        except FileNotFoundError:
            st.error("배경화면 파일(bg.png)을 찾을 수 없습니다.")

    # [CASE 2] 상세 메뉴일 때 -> 깔끔한 회색 배경 사용
    else:
        detail_style = """
        <style>
        .stApp {{
            background-image: none !important;
            background-color: #f0f2f6; /* 눈이 편한 밝은 회색 */
        }}
        /* 상세 화면 버튼: 깔끔한 흰색/파란색 스타일 */
        .stButton > button {{
            background-color: #ffffff;
            color: #31333F;
            border: 1px solid #d6d6d8;
        }}
        .stButton > button:hover {{
            border-color: #ff4b4b;
            color: #ff4b4b;
        }}
        </style>
        """
        st.markdown(detail_style, unsafe_allow_html=True)

# 현재 메뉴 상태에 맞춰 스타일 적용 실행
set_style(st.session_state['menu'])

# -----------------------------------------------------------------------------
# 3. 데이터 불러오기 및 계산 함수
# -----------------------------------------------------------------------------
@st.cache_data(ttl=60)
def load_data(sheet_name):
    try:
        url = st.secrets["connections"]["sheet_url"]
        if "/d/" in url:
            sheet_id = url.split("/d/")[1].split("/")[0]
            csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
            return pd.read_csv(csv_url, dtype=str)
        else:
            return pd.DataFrame()
    except Exception:
        return pd.DataFrame()

def safe_int(value):
    try:
        return int(str(value).replace(',', '').replace(' ', ''))
    except:
        return 0

def get_dues_calc_info():
    today = datetime.now()
    ref_date = today - relativedelta(months=1)
    start_date = datetime(2020, 2, 1)
    diff = relativedelta(ref_date, start_date)
    months_passed = diff.years * 12 + diff.months
    if months_passed < 0: months_passed = 0
    return ref_date, months_passed

# -----------------------------------------------------------------------------
# 4. 화면 구성 (홈 화면)
# -----------------------------------------------------------------------------
if st.session_state['menu'] == 'home':
    # 왼쪽(메뉴) : 오른쪽(여백) = 1 : 4
    left_col, right_col = st.columns([1, 4])
    
    with left_col:
        # 화면 중간쯤에 오도록 빈 공간 추가
        st.markdown("<div style='height: 35vh;'></div>", unsafe_allow_html=True)
        
        if st.button("🚪 회원 전체 현황"):
            st.session_state['menu'] = 'all_status'
            st.rerun()
            
        st.write("") 
        
        if st.button("🚪 회원 개인 현황"):
            st.session_state['menu'] = 'personal_status'
            st.rerun()
            
        st.write("") 
        
        if st.button("🚪 회칙 확인"):
            st.session_state['menu'] = 'rules'
            st.rerun()

# -----------------------------------------------------------------------------
# 5. 화면 구성 (상세 페이지 공통 헤더/푸터)
# -----------------------------------------------------------------------------
def render_header(title):
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    c1, c2 = st.columns([8, 2])
    with c1:
        st.header(title)
    with c2:
        if st.button("🏠 홈으로"):
            st.session_state['menu'] = 'home'
            st.rerun()

def render_footer():
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 6. [기능 1] 회원 개인 현황
# -----------------------------------------------------------------------------
if st.session_state['menu'] == 'personal_status':
    render_header("🔒 회원 개인 현황")
    
    st.info("본인의 이메일 아이디를 입력해주세요.")
    user_id_input = st.text_input("아이디 입력 (예: hong)", placeholder="이메일 아이디를 입력하세요")
    
    if user_id_input:
        df_members = load_data("members")
        df_ledger = load_data("ledger")
        
        if '아이디' in df_members.columns:
            user_info = df_members[df_members['아이디'].str.lower() == user_id_input.lower()]
        else:
            user_info = df_members[df_members['비밀번호'].astype(str) == str(user_id_input)]

        if not user_info.empty:
            user = user_info.iloc[0]
            user_name = user['성명']
            
            st.success(f"환영합니다, {user_name} ({user['직책']})님!")
            
            ref_date, months_passed = get_dues_calc_info()
            total_due_target = 1000000 + (months_passed * 30000)
            
            my_deposit = 0; my_condolence_amt = 0; my_wreath_amt = 0
            
            if not df_ledger.empty:
                df_ledger['금액'] = df_ledger['금액'].apply(safe_int)
                my_deposit = df_ledger[(df_ledger['구분'] == '입금') & (df_ledger['내용'] == user_name)]['금액'].sum()
                my_condolence_amt = df_ledger[(df_ledger['구분'] == '지출') & (df_ledger['분류'] == '조의금') & (df_ledger['내용'] == user_name)]['금액'].sum()
                my_wreath_amt = df_ledger[(df_ledger['구분'] == '지출') & (df_ledger['분류'] == '근조화환') & (df_ledger['내용'] == user_name)]['금액'].sum()

            unpaid = total_due_target - my_deposit
            condolence_count = int(my_condolence_amt / 1000000) if my_condolence_amt > 0 else 0
            
            st.divider()
            st.subheader(f"📋 {user_name}님의 현황표")
            st.caption(f"기준월: {ref_date.strftime('%Y년 %m월')}")
            
            col_list1, col_list2 = st.columns(2)
            with col_list1:
                st.write(f"**1. 성명:** {user_name}")
                st.write(f"**2. 직책:** {user['직책']}")
                st.write(f"**3. 가입일자:** {user['가입일자']}")
            with col_list2:
                st.write(f"**4. 조의횟수:** {condolence_count} 회")
                st.write(f"**5. 조의금 수령액:** {my_condolence_amt:,} 원")
                st.write(f"**6. 근조화환 수령액:** {my_wreath_amt:,} 원")
            
            st.write("---")
            st.write("**7. 미납금 현황**")
            st.markdown(f"- **총 납부해야 할 회비:** {total_due_target:,} 원")
            st.markdown(f"- **실제 납부한 회비:** {my_deposit:,} 원")
            
            if unpaid > 0:
                st.error(f"👉 **미납액: {unpaid:,} 원**")
            elif unpaid == 0:
                st.success("👉 **완납** 상태입니다.")
            else:
                st.info(f"👉 **선납액: {abs(unpaid):,} 원**")
        else:
            st.error("일치하는 아이디가 없습니다.")
    
    render_footer()

# -----------------------------------------------------------------------------
# 7. [기능 2] 회원 전체 현황
# -----------------------------------------------------------------------------
if st.session_state['menu'] == 'all_status':
    render_header("📊 회원 전체 및 자산 현황")
    
    df_members = load_data("members")
    df_ledger = load_data("ledger")
    df_assets = load_data("assets")
    
    if not df_ledger.empty: df_ledger['금액'] = df_ledger['금액'].apply(safe_int)
    if not df_assets.empty: df_assets['금액'] = df_assets['금액'].apply(safe_int)
    
    tab1, tab2, tab3 = st.tabs(["입금 분석", "자산 현황", "이자 분석"])
    ref_date, months_passed = get_dues_calc_info()
    total_due_target_per_person = 1000000 + (months_passed * 30000)
    
    with tab1:
        st.subheader("1. 전체 입금내역 분석")
        if not df_members.empty and not df_ledger.empty:
            analysis_data = []
            for index, row in df_members.iterrows():
                name = row['성명']
                paid_total = df_ledger[(df_ledger['구분'] == '입금') & (df_ledger['내용'] == name)]['금액'].sum()
                unpaid = total_due_target_per_person - paid_total
                note = "미납" if unpaid > 0 else ("선납" if unpaid < 0 else "완납")
                analysis_data.append({"회원명": name, "납부대상액": total_due_target_per_person, "납부한금액": paid_total, "차액": unpaid, "상태": note})
            
            df_analysis = pd.DataFrame(analysis_data)
            st.dataframe(df_analysis, use_container_width=True, hide_index=True)
            
            st.divider()
            st.subheader("2. 지출 및 잔액 분석")
            exp_condolence = df_ledger[(df_ledger['구분']=='지출') & (df_ledger['분류']=='조의금')]['금액'].sum()
            exp_wreath = df_ledger[(df_ledger['구분']=='지출') & (df_ledger['분류']=='근조화환')]['금액'].sum()
            exp_meeting = df_ledger[(df_ledger['구분']=='지출') & (~df_ledger['분류'].isin(['조의금', '근조화환'])) & (~df_ledger['분류'].str.contains('적금'))]['금액'].sum()
            exp_total = exp_condolence + exp_wreath + exp_meeting
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("조의금", f"{exp_condolence:,}")
            c2.metric("근조화환", f"{exp_wreath:,}")
            c3.metric("운영비", f"{exp_meeting:,}")
            c4.metric("지출합계", f"{exp_total:,}")
            
            total_income = df_ledger[df_ledger['구분']=='입금']['금액'].sum()
            exp_savings = df_ledger[(df_ledger['구분']=='지출') & (df_ledger['분류'].str.contains('적금'))]['금액'].sum()
            expected_balance = total_income - (exp_total + exp_savings)
            try: real_balance = df_assets[df_assets['항목'] == '회비통장']['금액'].iloc[0]
            except: real_balance = 0
            
            st.info(f"💰 통장 잔액 차이: {expected_balance - real_balance:,} 원 (이자수익 등)")
        else:
            st.warning("데이터 로딩 중...")

    with tab2:
        st.subheader("보유 자산")
        if not df_assets.empty:
            st.dataframe(df_assets, use_container_width=True, hide_index=True)
            st.metric("총 자산", f"{df_assets['금액'].sum():,} 원")

    with tab3:
        st.subheader("적금 수익")
        if not df_ledger.empty and not df_assets.empty:
            savings_principal = df_ledger[(df_ledger['구분']=='지출') & (df_ledger['분류'].str.contains('적금'))]['금액'].sum()
            savings_current = df_assets[df_assets['항목'].str.contains('적금')]['금액'].sum()
            st.metric("이자 수익", f"{savings_current - savings_principal:,} 원")

    render_footer()

# -----------------------------------------------------------------------------
# 8. [기능 3] 회칙
# -----------------------------------------------------------------------------
if st.session_state['menu'] == 'rules':
    render_header("📜 회칙 및 규정")
    
    df_rules = load_data("rules")
    search_rule = st.text_input("규정 검색", placeholder="검색어를 입력하세요")
    
    if not df_rules.empty:
        if search_rule:
            df_rules = df_rules[df_rules['내용'].str.contains(search_rule) | df_rules['조항'].str.contains(search_rule)]
        for idx, row in df_rules.iterrows():
            with st.expander(f"📌 {row.get('조항', '-')}"):
                st.write(row.get('내용', '-'))
    
    render_footer()
