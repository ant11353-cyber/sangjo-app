import streamlit as st
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
import base64

# -----------------------------------------------------------------------------
# 1. 페이지 설정 및 디자인
# -----------------------------------------------------------------------------
st.set_page_config(page_title="천비칠마 상조회", page_icon="📱", layout="wide")

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_style(current_menu):
    common_style = """
    <style>
    /* 컨텐츠 박스 */
    .content-box {
        background-color: transparent;
        padding: 20px 0px;
        margin-bottom: 20px;
    }
    
    /* 버튼 스타일 */
    .stButton > button {
        width: 100%;
        height: 5rem;
        border-radius: 50px;
        font-size: 1.3rem;
        font-weight: 600;
        transition: all 0.3s ease;
        margin-bottom: 10px;
    }
    
    /* 표 내용 가운데 정렬 */
    [data-testid="stDataFrame"] .stDataFrame {
        width: 100%;
    }
    [data-testid="stDataFrame"] div[role="columnheader"] {
        display: flex;
        justify-content: center;
        text-align: center;
    }
    [data-testid="stDataFrame"] div[role="gridcell"] {
        display: flex;
        justify-content: center;
        text-align: center;
    }
    
    /* 결론 박스 스타일 */
    .conclusion-box {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.3);
        padding: 20px;
        border-radius: 10px;
        color: inherit;
        font-weight: bold;
        font-size: 1.1rem;
        text-align: center;
        margin-top: 10px;
    }
    
    /* 섹션 제목 강조 스타일 (금액 부분 색상 변경 등 가능) */
    .highlight-sum {
        color: #ff4b4b; /* 스트림릿 기본 붉은색 계열 */
        font-weight: bold;
    }
    </style>
    """
    st.markdown(common_style, unsafe_allow_html=True)

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
            .block-container {{
                background-color: transparent; 
                padding-top: 0rem;
                padding-left: 2rem;
                max-width: 100%;
            }}
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
                transform: scale(1.05);
            }}
            </style>
            """
            st.markdown(home_style, unsafe_allow_html=True)
        except FileNotFoundError:
            st.error("배경화면 파일(bg.png)을 찾을 수 없습니다.")
    else:
        detail_style = """
        <style>
        .stApp {
            background-image: none !important;
        }
        .stButton > button {
            background-color: #ffffff;
            color: #31333F;
            border: 1px solid #d6d6d8;
        }
        .stButton > button:hover {
            border-color: #ff4b4b;
            color: #ff4b4b;
        }
        </style>
        """
        st.markdown(detail_style, unsafe_allow_html=True)

if 'menu' not in st.session_state:
    st.session_state['menu'] = 'home'

set_style(st.session_state['menu'])

# -----------------------------------------------------------------------------
# 2. 데이터 불러오기 및 계산 함수
# -----------------------------------------------------------------------------
@st.cache_data(ttl=60)
def load_data(sheet_name):
    try:
        url = st.secrets["connections"]["sheet_url"]
        if "/d/" in url:
            sheet_id = url.split("/d/")[1].split("/")[0]
            csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
            df = pd.read_csv(csv_url, dtype=str)
            df.columns = df.columns.str.strip()
            return df
        else:
            return pd.DataFrame()
    except Exception:
        return pd.DataFrame()

def safe_int(value):
    try:
        return int(str(value).replace(',', '').replace(' ', ''))
    except:
        return 0

def format_comma(val):
    try:
        return f"{int(val):,}"
    except:
        return val

def get_dues_calc_info():
    today = datetime.now()
    ref_date = today - relativedelta(months=1)
    start_date = datetime(2020, 2, 1)
    diff = relativedelta(ref_date, start_date)
    months_passed = diff.years * 12 + diff.months
    if months_passed < 0: months_passed = 0
    return ref_date, months_passed

# -----------------------------------------------------------------------------
# 3. 화면 구성 (홈 화면)
# -----------------------------------------------------------------------------
if st.session_state['menu'] == 'home':
    left_col, right_col = st.columns([1, 4])
    with left_col:
        st.markdown("<div style='height: 30vh;'></div>", unsafe_allow_html=True)
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

def render_header(title):
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    c1, c2 = st.columns([8, 2])
    with c1: st.header(title)
    with c2:
        if st.button("🏠 홈으로"):
            st.session_state['menu'] = 'home'
            st.rerun()

def render_footer():
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 4. 기능: 회원 개인 현황
# -----------------------------------------------------------------------------
if st.session_state['menu'] == 'personal_status':
    render_header("🔒 회원 개인 현황")
    st.info("본인의 이메일 아이디를 입력해주세요.")
    user_id_input = st.text_input("아이디 입력 (예: hong)", placeholder="이메일 아이디를 입력하세요")
    
    if user_id_input:
        df_members = load_data("members")
        df_ledger = load_data("ledger")
        
        target_col = '아이디' if '아이디' in df_members.columns else '비밀번호'
        user_info = df_members[df_members[target_col].astype(str).str.lower() == str(user_id_input).lower()]

        if not user_info.empty:
            user = user_info.iloc[0]
            user_name = user['성명']
            st.success(f"환영합니다, {user_name} ({user['직책']})님!")
            
            ref_date, months_passed = get_dues_calc_info()
            total_due_target = 1000000 + (months_passed * 30000)
            
            my_deposit = 0; my_condolence_amt = 0; my_wreath_amt = 0
            if not df_ledger.empty:
                if '금액' in df_ledger.columns:
                    df_ledger['금액'] = df_ledger['금액'].apply(safe_int)
                    my_deposit = df_ledger[(df_ledger['구분'] == '입금') & (df_ledger['내용'] == user_name)]['금액'].sum()
                    my_condolence_amt = df_ledger[(df_ledger['구분'] == '출금') & (df_ledger['분류'] == '조의금') & (df_ledger['내용'] == user_name)]['금액'].sum()
                    my_wreath_amt = df_ledger[(df_ledger['구분'] == '출금') & (df_ledger['분류'] == '근조화환') & (df_ledger['내용'] == user_name)]['금액'].sum()

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
                st.write(f"**5. 조의금 수령액:** {format_comma(my_condolence_amt)} 원")
                st.write(f"**6. 근조화환 수령액:** {format_comma(my_wreath_amt)} 원")
            
            st.write("---")
            st.write("**7. 미납금 현황**")
            st.markdown(f"- **총 납부해야 할 회비:** {format_comma(total_due_target)} 원")
            st.markdown(f"- **실제 납부한 회비:** {format_comma(my_deposit)} 원")
            
            if unpaid > 0: st.error(f"👉 **미납액: {format_comma(unpaid)} 원**")
            elif unpaid == 0: st.success("👉 **완납** 상태입니다.")
            else: st.info(f"👉 **선납액: {format_comma(abs(unpaid))} 원**")
        else:
            st.error("일치하는 아이디가 없습니다.")
    render_footer()

# -----------------------------------------------------------------------------
# 5. 기능: 회원 전체 현황
# -----------------------------------------------------------------------------
if st.session_state['menu'] == 'all_status':
    render_header("📊 회원전체현황")
    
    df_members = load_data("members")
    df_ledger = load_data("ledger")
    df_assets = load_data("assets")
    
    # 전처리
    if not df_ledger.empty:
        if '구분' in df_ledger.columns: df_ledger['구분'] = df_ledger['구분'].astype(str).str.strip()
        if '분류' in df_ledger.columns: df_ledger['분류'] = df_ledger['분류'].astype(str).str.strip()
        if '금액' in df_ledger.columns: df_ledger['금액'] = df_ledger['금액'].apply(safe_int)

    asset_name_col = None; asset_amount_col = None
    if not df_assets.empty:
        for col in ['항목', '자산명', '자산', '계좌명', '구분', '내용', 'Asset']:
            if col in df_assets.columns: asset_name_col = col; break
        for col in ['금액', '잔액', '평가액', '자산금액', 'Amount']:
            if col in df_assets.columns: asset_amount_col = col; break
        if asset_amount_col:
            df_assets[asset_amount_col] = df_assets[asset_amount_col].apply(safe_int)

    tab1, tab2, tab3 = st.tabs(["분석적검토", "자산 현황", "이자 분석"])
    ref_date, months_passed = get_dues_calc_info()
    total_due_target_per_person = 1000000 + (months_passed * 30000)
    
    with tab1:
        # [계산 1] 전체 입금액 계산 (먼저 수행)
        total_paid_sum = 0
        df_display = pd.DataFrame()
        
        if not df_members.empty and not df_ledger.empty:
            analysis_data = []
            for index, row in df_members.iterrows():
                name = row['성명']
                paid_total = 0
                if '금액' in df_ledger.columns:
                    paid_total = df_ledger[(df_ledger['구분'] == '입금') & (df_ledger['내용'] == name)]['금액'].sum()
                
                unpaid = total_due_target_per_person - paid_total
                note = "미납" if unpaid > 0 else ("선납" if unpaid < 0 else "완납")
                
                analysis_data.append({
                    "회원명": name, 
                    "A.납부할금액": total_due_target_per_person, 
                    "B.납부한금액": paid_total, 
                    "차이금액(=A-B)": unpaid, 
                    "상태": note
                })
            
            df_analysis = pd.DataFrame(analysis_data)
            
            total_due = df_analysis['A.납부할금액'].sum()
            total_paid_sum = df_analysis['B.납부한금액'].sum() # 여기서 구한 값이 제목에 들어감
            total_diff = df_analysis['차이금액(=A-B)'].sum()
            
            total_row = pd.DataFrame([{
                "회원명": "합계",
                "A.납부할금액": total_due,
                "B.납부한금액": total_paid_sum,
                "차이금액(=A-B)": total_diff,
                "상태": "-"
            }])
            df_display = pd.concat([df_analysis, total_row], ignore_index=True)
            
            # [출력 1] 제목 옆에 금액 표시
            st.subheader(f"1. 전체 입금내역 분석 : {format_comma(total_paid_sum)} 원")
            
            cols_to_comma = ["A.납부할금액", "B.납부한금액", "차이금액(=A-B)"]
            for col in cols_to_comma:
                df_display[col] = df_display[col].apply(format_comma)
            
            st.dataframe(df_display, use_container_width=True, hide_index=True)
        else:
            st.subheader("1. 전체 입금내역 분석")
            st.warning("데이터가 없습니다.")
            
        st.divider()
        
        # [계산 2] 지출액 계산
        exp_total = 0
        df_exp = pd.DataFrame()
        
        if '금액' in df_ledger.columns:
            exp_condolence = df_ledger[(df_ledger['구분'] == '출금') & (df_ledger['분류'] == '조의금')]['금액'].sum()
            exp_wreath = df_ledger[(df_ledger['구분'] == '출금') & (df_ledger['분류'] == '근조화환')]['금액'].sum()
            exp_meeting = df_ledger[(df_ledger['구분'] == '출금') & (df_ledger['분류'] == '회의비외')]['금액'].sum()
            
            exp_total = exp_condolence + exp_wreath + exp_meeting # 합계
            
            exp_data = {
                "지출 항목": ["(1) 조의금", "(2) 근조화환", "(3) 회의비등", "(4) 합계"],
                "내용 설명": [
                    "조의건당 1백만원",
                    "조의건당 1십만원",
                    "상조기 및 모임식대, 각종소포품 등",
                    "=(1)+(2)+(3)"
                ],
                "금액": [exp_condolence, exp_wreath, exp_meeting, exp_total]
            }
            df_exp = pd.DataFrame(exp_data)
            df_exp['금액'] = df_exp['금액'].apply(format_comma)

        # [출력 2] 제목 옆에 금액 표시
        st.subheader(f"2. 회비통장지출액 : {format_comma(exp_total)} 원")
        if not df_exp.empty:
            st.dataframe(df_exp, use_container_width=True, hide_index=True)
        
        st.divider()

        # [계산 3] 분석적 검토
        real_balance = 0
        if asset_amount_col and asset_name_col:
            try: 
                mask = df_assets[asset_name_col].str.contains('회비통장', na=False)
                if mask.any(): real_balance = df_assets[mask][asset_amount_col].iloc[0]
            except: pass
        
        val_a = total_paid_sum - exp_total
        val_b = real_balance
        diff_final = val_a - val_b
        
        review_data = {
            "구분": ["A. 장부상 잔액", "B. 실제 통장 잔액", "차이 (A-B)"],
            "산출 근거": [
                "전체 입금액 합계 - 회비통장 지출 총계",
                "자산(assets) 시트의 회비통장 잔액",
                "이자수익 및 적금불입액 등 차이"
            ],
            "금액": [val_a, val_b, diff_final]
        }
        df_review = pd.DataFrame(review_data)
        df_review['금액'] = df_review['금액'].apply(format_comma)

        # [출력 3] 제목 옆에 차이 금액 표시
        st.subheader(f"3. 분석적검토 (차이: {format_comma(diff_final)} 원)")
        st.dataframe(df_review, use_container_width=True, hide_index=True)

        st.divider()

        # 4. 결론
        st.subheader("4. 결론")
        st.markdown(
            """
            <div class="conclusion-box">
            차이금액은 회비통장의 이자수익 등 미반영으로 차이 발생분으로 중요성관점에서 문제없음
            </div>
            """, 
            unsafe_allow_html=True
        )

    with tab2:
        st.subheader("보유 자산")
        if not df_assets.empty and asset_amount_col:
            total_asset_val = df_assets[asset_amount_col].sum()
            df_assets_disp = df_assets.copy()
            df_assets_disp[asset_amount_col] = df_assets_disp[asset_amount_col].apply(format_comma)
            
            st.dataframe(df_assets_disp, use_container_width=True, hide_index=True)
            st.metric("총 자산", f"{format_comma(total_asset_val)} 원")
        else:
            st.warning("자산 데이터를 불러오지 못했습니다.")

    with tab3:
        st.subheader("적금 수익")
        if not df_ledger.empty and not df_assets.empty and asset_amount_col and asset_name_col and '금액' in df_ledger.columns:
            savings_principal = df_ledger[(df_ledger['구분']=='출금') & (df_ledger['분류'].str.contains('적금'))]['금액'].sum()
            mask = df_assets[asset_name_col].str.contains('적금', na=False)
            savings_current = df_assets[mask][asset_amount_col].sum()
            st.metric("이자 수익", f"{format_comma(savings_current - savings_principal)} 원")

    render_footer()

# -----------------------------------------------------------------------------
# 6. 기능: 회칙
# -----------------------------------------------------------------------------
if st.session_state['menu'] == 'rules':
    render_header("📜 회칙 및 규정")
    df_rules = load_data("rules")
    search_rule = st.text_input("규정 검색", placeholder="검색어를 입력하세요")
    
    if not df_rules.empty:
        if search_rule:
            df_rules = df_rules[df_rules['내용'].str.contains(search_rule) | df_rules['조항'].str.contains(search_rule)]
        
        for idx, row in df_rules.iterrows():
            article = row.get('조항', '')
            title = row.get('제목', row.get('항목', ''))
            
            if title and str(title).lower() != 'nan':
                header_text = f"{article}({title})"
            else:
                header_text = article
            
            st.markdown(f"<div class='rule-header'>{header_text}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='rule-content'>{row.get('내용', '-')}</div>", unsafe_allow_html=True)
            st.divider()
            
    render_footer()
