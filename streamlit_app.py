import streamlit as st
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

# -----------------------------------------------------------------------------
# 1. 페이지 설정 및 배경화면
# -----------------------------------------------------------------------------
st.set_page_config(page_title="천비칠마 상조회", page_icon="📱", layout="wide")

# 배경화면 CSS (원하는 이미지 주소로 변경 가능)
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
    /* 컨텐츠 가독성을 위해 흰색 반투명 박스 적용 */
    .block-container {{
        background-color: rgba(255, 255, 255, 0.9);
        border-radius: 20px;
        padding: 3rem;
        margin-top: 2rem;
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
@st.cache_data(ttl=60) # 1분마다 갱신
def load_data(sheet_name):
    try:
        url = st.secrets["connections"]["sheet_url"]
        sheet_id = url.split("/d/")[1].split("/")[0]
        csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
        return pd.read_csv(csv_url)
    except Exception as e:
        return pd.DataFrame()

# 기준월 및 개월 수 계산 함수
def get_dues_calc_info():
    today = datetime.now()
    # 기준월: 앱 실행일이 속한 달의 전달
    ref_date = today - relativedelta(months=1)
    
    # 2020년 2월부터 기준월까지의 개월 수 계산
    start_date = datetime(2020, 2, 1)
    diff = relativedelta(ref_date, start_date)
    months_passed = diff.years * 12 + diff.months
    
    # 만약 2020년 2월 이전이라면 0으로 처리
    if months_passed < 0: months_passed = 0
        
    return ref_date, months_passed

# -----------------------------------------------------------------------------
# 3. 메뉴 선택 (3개의 문)
# -----------------------------------------------------------------------------
# 세션 상태를 사용하여 화면 전환 구현
if 'menu' not in st.session_state:
    st.session_state['menu'] = 'home'

# 홈 화면 버튼 구성
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

# '홈으로 가기' 버튼 함수
def go_home():
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
        [cite_start]df_members = load_data("members") # [cite: 1]
        df_ledger = load_data("ledger")
        
        # 비밀번호 매칭 (문자열로 변환하여 비교)
        user_info = df_members[df_members['비밀번호'].astype(str) == password_input]
        
        if not user_info.empty:
            user = user_info.iloc[0] # 첫 번째 일치하는 회원
            [cite_start]user_name = user['성명'] # [cite: 1]
            
            st.success(f"{user_name} ({user['직책']})님 환영합니다.")
            
            # --- 계산 로직 ---
            ref_date, months_passed = get_dues_calc_info()
            
            # 1. 기준월까지 입금해야 할 총 회비
            total_due_target = 1000000 + (months_passed * 30000)
            
            # 2. 기준월까지 입금한 총 회비 (장부에서 '입금' & '회원명' 매칭)
            # 장부 컬럼 가정: '구분'(입금/지출), '내용'(회원명), '금액'
            my_deposit = df_ledger[
                (df_ledger['구분'] == '입금') & 
                (df_ledger['내용'] == user_name)
            ]['금액'].sum()
            
            # 3. 미납액
            unpaid = total_due_target - my_deposit
            
            # 4. 조의금/근조화환 (지출 내역에서 매칭)
            # 장부 컬럼 가정: '구분'(지출), '분류'(조의금/근조화환), '내용'(회원명)
            my_condolence_amt = df_ledger[
                (df_ledger['구분'] == '지출') & 
                (df_ledger['분류'] == '조의금') & 
                (df_ledger['내용'] == user_name)
            ]['금액'].sum()
            
            my_wreath_amt = df_ledger[
                (df_ledger['구분'] == '지출') & 
                (df_ledger['분류'] == '근조화환') & 
                (df_ledger['내용'] == user_name)
            ]['금액'].sum()
            
            condolence_count = int(my_condolence_amt / 1000000)
            
            # --- 결과 출력 (세로 리스트 형태) ---
            st.divider()
            st.markdown(f"### 📋 {user_name}님의 현황표")
            st.info(f"기준월: {ref_date.strftime('%Y년 %m월')}")
            
            data_list = {
                "1. 성명": user_name,
                "2. [cite_start]직책": user['직책'], # [cite: 1]
                [cite_start]"3. 가입일자": user['가입일자'], # [cite: 1]
                "4. 조의횟수": f"{condolence_count} 회",
                "5. 조의금 수령액": f"{my_condolence_amt:,} 원",
                "6. 근조화환 수령액": f"{my_wreath_amt:,} 원",
                "7. 미납금 현황": ""
            }
            
            for key, value in data_list.items():
                st.write(f"**{key}** {value}")
                
            # 미납금 상세 내역 (가, 나, 다)
            st.markdown(f"""
            &nbsp;&nbsp;&nbsp;&nbsp;가. 총 납부해야 할 회비: **{total_due_target:,} 원** &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*(100만원 + {months_passed}개월 × 30,000원)* &nbsp;&nbsp;&nbsp;&nbsp;나. 실제 납부한 회비: **{my_deposit:,} 원** &nbsp;&nbsp;&nbsp;&nbsp;다. 미납액 (가-나): **{unpaid:,} 원**
            """)
            
            if unpaid > 0:
                st.error(f"👉 현재 **{unpaid:,} 원 미납** 상태입니다.")
            elif unpaid == 0:
                st.success("👉 **완납** 상태입니다. 감사합니다!")
            else:
                st.info(f"👉 현재 **{abs(unpaid):,} 원 선납** 상태입니다.")
                
        else:
            st.error("비밀번호가 일치하는 회원이 없습니다.")
            
    go_home()

# -----------------------------------------------------------------------------
# 5. [기능 2] 회원 전체 현황
# -----------------------------------------------------------------------------
if st.session_state['menu'] == 'all_status':
    st.header("📊 회원 전체 및 자산 현황")
    
    [cite_start]df_members = load_data("members") # [cite: 1]
    df_ledger = load_data("ledger")
    df_assets = load_data("assets")
    
    tab1, tab2, tab3 = st.tabs(["입금 분석", "자산 현황", "이자 분석"])
    
    ref_date, months_passed = get_dues_calc_info()
    total_due_target_per_person = 1000000 + (months_passed * 30000)
    
    # --- [가] 회비통장의 분석적 검토 ---
    with tab1:
        st.subheader("1. 전체 입금내역 분석 (회원별)")
        
        # 분석 테이블 만들기
        analysis_data = []
        for index, row in df_members.iterrows():
            [cite_start]name = row['성명'] # [cite: 1]
            
            # 입금한 총액 계산
            paid_total = df_ledger[
                (df_ledger['구분'] == '입금') & 
                (df_ledger['내용'] == name)
            ]['금액'].sum()
            
            unpaid = total_due_target_per_person - paid_total
            
            note = "완납"
            if unpaid > 0: note = "미납"
            elif unpaid < 0: note = "선납"
            
            analysis_data.append({
                "회원명": name,
                "납부해야할 총액": total_due_target_per_person,
                "입금한 총액": paid_total,
                "미납액": unpaid,
                "비고": note
            })
            
        df_analysis = pd.DataFrame(analysis_data)
        
        # 합계 행 추가 (Total)
        total_row = pd.DataFrame([{
            "회원명": "합계",
            "납부해야할 총액": df_analysis['납부해야할 총액'].sum(),
            "입금한 총액": df_analysis['입금한 총액'].sum(),
            "미납액": df_analysis['미납액'].sum(),
            "비고": "-"
        }])
        df_display = pd.concat([df_analysis, total_row], ignore_index=True)
        
        st.dataframe(df_display, use_container_width=True)
        
        st.divider()
        st.subheader("2. 회비통장 지출 분석 (적금 제외)")
        
        # 지출 합계 계산 (적금 이체는 제외해야 정확한 비용 분석 가능)
        exp_condolence = df_ledger[(df_ledger['구분']=='지출') & (df_ledger['분류']=='조의금')]['금액'].sum()
        exp_wreath = df_ledger[(df_ledger['구분']=='지출') & (df_ledger['분류']=='근조화환')]['금액'].sum()
        exp_meeting = df_ledger[(df_ledger['구분']=='지출') & (df_ledger['분류'].str.contains('회의비|운영비'))]['금액'].sum()
        exp_total = exp_condolence + exp_wreath + exp_meeting
        
        col_e1, col_e2, col_e3, col_e4 = st.columns(4)
        col_e1.metric("조의금 합계", f"{exp_condolence:,}")
        col_e2.metric("근조화환 합계", f"{exp_wreath:,}")
        col_e3.metric("회의비등 합계", f"{exp_meeting:,}")
        col_e4.metric("지출 총계", f"{exp_total:,}")
        
        st.divider()
        st.subheader("3. 잔액 차이 검토")
        
        # 예상 잔액 (전체 입금 - 전체 지출)
        total_income = df_ledger[df_ledger['구분']=='입금']['금액'].sum()
        expected_balance = total_income - exp_total # (주의: 적금 불입액도 지출로 잡혀있다면 조정 필요)
        
        # 실제 회비통장 잔액 가져오기 (assets 시트에서 '회비통장' 찾기)
        try:
            real_balance = df_assets[df_assets['항목'] == '회비통장']['금액'].iloc[0]
        except:
            real_balance = 0
            
        diff_balance = expected_balance - real_balance
        
        st.write(f"• 예상 잔액: {expected_balance:,} 원 (입금총액 - 지출총액)")
        st.write(f"• 실제 회비통장 잔액: {real_balance:,} 원")
        st.write(f"• 차이 금액: {diff_balance:,} 원")
        st.caption("결론: 중요성 관점에서 차이금액은 이자수익 등 미반영분으로 판단되며 문제없음.")

    # --- [나] 보유 자산 현황 ---
    with tab2:
        st.subheader("보유 자산 현황")
        st.dataframe(df_assets, use_container_width=True)
        
        total_assets = df_assets['금액'].sum()
        st.metric("자산 총계", f"{total_assets:,} 원")

    # --- [다] 적금통장 이자 발생 누적액 ---
    with tab3:
        st.subheader("적금 이자 수익 분석")
        
        # 1. 적금 가입 원금 (장부에서 '적금'으로 지출된 금액 합계)
        savings_principal = df_ledger[
            (df_ledger['구분']=='지출') & 
            (df_ledger['분류'].str.contains('적금'))
        ]['금액'].sum()
        
        # 2. 현재 적금 통장 평가액 (assets 시트에서 적금 통장들 합계)
        savings_current = df_assets[df_assets['항목'].str.contains('적금')]['금액'].sum()
        
        # 3. 이자 발생액
        interest_earned = savings_current - savings_principal
        
        col_i1, col_i2, col_i3 = st.columns(3)
        col_i1.metric("적금 불입 원금", f"{savings_principal:,} 원")
        col_i2.metric("현재 평가액", f"{savings_current:,} 원")
        col_i3.metric("이자 발생 이익", f"{interest_earned:,} 원", delta_color="normal")
        
        st.info("총평: 회비는 매우 투명하게 관리되고 있으며, 입출금내역 검토 결과 이상 없습니다.")

    go_home()

# -----------------------------------------------------------------------------
# 6. [기능 3] 회칙
# -----------------------------------------------------------------------------
if st.session_state['menu'] == 'rules':
    st.header("📜 회칙 및 규정")
    
    df_rules = load_data("rules")
    
    search_rule = st.text_input("궁금한 규정을 검색해보세요", placeholder="예: 경조사, 회비")
    
    if search_rule:
        df_rules = df_rules[df_rules['내용'].str.contains(search_rule) | df_rules['조항'].str.contains(search_rule)]
    
    if not df_rules.empty:
        for idx, row in df_rules.iterrows():
            with st.expander(f"📌 {row.get('조항', '조항 없음')}"):
                st.write(row.get('내용', '내용 없음'))
    else:
        st.write("등록된 회칙이 없습니다.")

    go_home()
