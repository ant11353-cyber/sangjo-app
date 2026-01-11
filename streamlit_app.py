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
            ref_date, months_passed = get_dues_calc_info()
            
            # 1. 기준월까지 입금해야 할 총 회비
            total_due_target = 1000000 + (months_passed * 30000)
            
            # 2. 기준월까지 입금한 총 회비
            if not df_ledger.empty:
                my_deposit = df_ledger[
                    (df_ledger['구분'] == '입금') & 
                    (df_ledger['내용'] == user_name)
                ]['금액'].sum()
                
                # 조의금/근조화환 수령액
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

            # 3. 미납액
            unpaid = total_due_target - my_deposit
            condolence_count = int(my_condolence_amt / 1000000)
            
            # --- 결과 출력 ---
            st.divider()
            st.subheader(f"📋 {user_name}님의 현황표")
            st.caption(f"기준월: {ref_date.strftime('%Y년 %m월')}")
            
            # 보기 좋게 리스트업
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
            
            # 미납금 상세 내역
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
    
    # --- [가] 회비통장의 분석적 검토 ---
    with tab1:
        st.subheader("1. 전체 입금내역 분석 (회원별)")
        
        if not df_members.empty and not df_ledger.empty:
            analysis_data = []
            for index, row in df_members.iterrows():
                name = row['성명']
                
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
            
            # 합계 행
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
            # 회의비 등 (조의금, 근조화환, 적금이 아닌 모든 지출)
            exp_meeting = df_ledger[
                (df_ledger['구분']=='지출') & 
                (~df_ledger['분류'].isin(['
