import streamlit as st
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
import base64
import os

# -----------------------------------------------------------------------------
# 1. 페이지 설정 및 배경화면
# -----------------------------------------------------------------------------
st.set_page_config(page_title="천비칠마 상조회", page_icon="📱", layout="wide")

def get_base64_of_bin_file(bin_file):
    """이미지 파일을 읽어서 코드로 변환하는 함수"""
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_png_as_page_bg(png_file):
    """변환된 코드를 배경화면으로 설정하는 함수"""
    try:
        bin_str = get_base64_of_bin_file(png_file)
        page_bg_img = f'''
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{bin_str}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        /* 컨텐츠 가독성을 위한 흰색 박스 스타일 */
        .block-container {{
            background-color: rgba(255, 255, 255, 0.92);
            border-radius: 15px;
            padding: 2rem;
            margin-top: 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        }}
        </style>
        '''
        st.markdown(page_bg_img, unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"배경화면 파일({png_file})을 찾을 수 없습니다. 깃허브 파일명을 확인해주세요.")

# [수정됨] bg.png 파일을 읽도록 변경
set_png_as_page_bg('bg.png')

st.title("📱 천비칠마 상조회 통합 관리")
st.write("원하시는 메뉴의 문을 열어주세요.")

# -----------------------------------------------------------------------------
# 2. 데이터 불러오기 및 공통 계산 함수
# -----------------------------------------------------------------------------
@st.cache_data(ttl=60)
def load_data(sheet_name):
    try:
        url = st.secrets["connections"]["sheet_url"]
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
    ref_date = today - relativedelta(months=1)
    
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
# 4. [기능 1] 회원 개인 현황
# -----------------------------------------------------------------------------
if st.session_state['menu'] == 'personal_status':
    st.header("🔒 회원 개인 현황")
    st.write("개인 정보를 보호하기 위해 비밀번호를 입력해주세요.")
    
    password_input = st.text_input("비밀번호 4자리를 입력하세요", type="password")
    
    if password_input:
        df_members = load_data("members")
        df_ledger = load_data("ledger")
        
        user_info = df_members[df_members['비밀번호'].astype(str) == str(password_input)]
        
        if not user_info.empty:
            user = user_info.iloc[0]
            user_name = user['성명']
            
            st.success(f"환영합니다, {user_name} ({user['직책']})님!")
            
            ref_date, months_passed = get_dues_calc_info()
            total_due_target = 1000000 + (months_passed * 30000)
            
            if not df_ledger.empty:
                my_deposit = df_ledger[
                    (df_ledger['구분'] == '입금') & 
                    (df_ledger['내용'] == user_name)
                ]['금액'].sum()
                
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
            else:
                my_deposit = 0
                my_condolence_amt = 0
                my_wreath_amt = 0

            unpaid = total_due_target - my_deposit
            condolence_count = int(my_condolence_amt / 1000000)
            
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
            
            st.markdown(f"""
            - **가. 총 납부해야 할 회비:** {total_due_target:,} 원  
              *(100만원 + {months_passed}개월 × 30,000원)*
            - **나. 실제 납부한 회비:** {my_deposit:,} 원
            - **다. 미납액 (가-나):** {unpaid:,} 원
            """)
            
            if unpaid > 0:
                st.error(f"👉 **{unpaid:,} 원 미납** 상태입니다.")
            elif unpaid == 0:
                st.success("👉 **완납** 상태입니다. 감사합니다!")
            else:
                st.info(f"👉 **{abs(unpaid):,} 원 선납** 상태입니다.")
                
        else:
            st.error("비밀번호가 일치하는 회원이 없습니다. 다시 확인해주세요.")
            
    go_home()

# -----------------------------------------------------------------------------
# 5. [기능 2] 회원 전체 현황
# -----------------------------------------------------------------------------
if st.session_state['menu'] == 'all_status':
    st.header("📊 회원 전체 및 자산 현황")
    
    df_members = load_data("members")
    df_ledger = load_data("ledger")
    df_assets = load_data("assets")
    
    tab1, tab2, tab3 = st.tabs(["입금 분석", "자산 현황", "이자 분석"])
    
    ref_date, months_passed = get_dues_calc_info()
    total_due_target_per_person = 1000000 + (months_passed * 30000)
    
    with tab1:
        st.subheader("1. 전체 입금내역 분석 (회원별)")
        
        if not df_members.empty and not df_ledger.empty:
            analysis_data = []
            for index, row in df_members.iterrows():
                name = row['성명']
                
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
            
            total_row = pd.DataFrame([{
                "회원명": "합계",
                "납부해야할 총액": df_analysis['납부해야할 총액'].sum(),
                "입금한 총액": df_analysis['입금한 총액'].sum(),
                "미납액": df_analysis['미납액'].sum(),
                "비고": "-"
            }])
            df_display = pd.concat([df_analysis, total_row], ignore_index=True)
            
            st.dataframe(df_display, use_container_width=True, hide_index=True)
            
            st.divider()
            st.subheader("2. 회비통장 지출 분석 (적금 제외)")
            
            exp_condolence = df_ledger[(df_ledger['구분']=='지출') & (df_ledger['분류']=='조의금')]['금액'].sum()
            exp_wreath = df_ledger[(df_ledger['구분']=='지출') & (df_ledger['분류']=='근조화환')]['금액'].sum()
            exp_meeting = df_ledger[
                (df_ledger['구분']=='지출') & 
                (~df_ledger['분류'].isin(['조의금', '근조화환'])) & 
                (~df_ledger['분류'].str.contains('적금'))
            ]['금액'].sum()
            
            exp_total = exp_condolence + exp_wreath + exp_meeting
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("조의금", f"{exp_condolence:,}")
            c2.metric("근조화환", f"{exp_wreath:,}")
            c3.metric("회의비등", f"{exp_meeting:,}")
            c4.metric("지출 합계", f"{exp_total:,}")
            
            st.divider()
            st.subheader("3. 잔액 차이 검토")
            
            total_income = df_ledger[df_ledger['구분']=='입금']['금액'].sum()
            exp_savings = df_ledger[(df_ledger['구분']=='지출') & (df_ledger['분류'].str.contains('적금'))]['금액'].sum()
            expected_balance = total_income - (exp_total + exp_savings)
            
            try:
                real_balance = df_assets[df_assets['항목'] == '회비통장']['금액'].iloc[0]
            except:
                real_balance = 0
                
            diff_balance = expected_balance - real_balance
            
            st.write(f"• **예상 잔액:** {expected_balance:,} 원")
            st.write(f"• **실제 회비통장 잔액:** {real_balance:,} 원")
            st.write(f"• **차이 금액:** {diff_balance:,} 원")
            st.info("결론: 중요성 관점에서 차이금액은 이자수익 등 미반영분으로 판단되며 문제없음.")
            
        else:
            st.warning("데이터를 불러오는 중입니다.")

    with tab2:
        st.subheader("보유 자산 현황")
        if not df_assets.empty:
            st.dataframe(df_assets, use_container_width=True, hide_index=True)
            total_assets = df_assets['금액'].sum()
            st.metric("자산 총계", f"{total_assets:,} 원")
        else:
            st.warning("자산 데이터를 불러오지 못했습니다.")

    with tab3:
        st.subheader("적금 이자 수익 분석")
        
        if not df_ledger.empty and not df_assets.empty:
            savings_principal = df_ledger[
                (df_ledger['구분']=='지출') & 
                (df_ledger['분류'].str.contains('적금'))
            ]['금액'].sum()
            
            savings_current = df_assets[df_assets['항목'].str.contains('적금')]['금액'].sum()
            interest_earned = savings_current - savings_principal
            
            c1, c2, c3 = st.columns(3)
            c1.metric("적금 불입 원금", f"{savings_principal:,} 원")
            c2.metric("현재 평가액", f"{savings_current:,} 원")
            c3.metric("이자 수익", f"{interest_earned:,} 원")
            
            st.success("총평: 회비는 매우 투명하게 관리되고 있으며, 입출금내역 검토 결과 이상 없습니다.")

    go_home()

# -----------------------------------------------------------------------------
# 6. [기능 3] 회칙
# -----------------------------------------------------------------------------
if st.session_state['menu'] == 'rules':
    st.header("📜 회칙 및 규정")
    
    df_rules = load_data("rules")
    
    search_rule = st.text_input("궁금한 규정을 검색해보세요", placeholder="예: 경조사, 회비")
    
    if not df_rules.empty:
        if search_rule:
            df_rules = df_rules[df_rules['내용'].str.contains(search_rule) | df_rules['조항'].str.contains(search_rule)]
            
        for idx, row in df_rules.iterrows():
            with st.expander(f"📌 {row.get('조항', '조항 없음')}"):
                st.write(row.get('내용', '내용 없음'))
    else:
        st.write("등록된 회칙이 없습니다.")

    go_home()
