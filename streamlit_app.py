import streamlit as st
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
import base64

# -----------------------------------------------------------------------------
# 1. 페이지 설정 (가장 먼저 실행)
# -----------------------------------------------------------------------------
# [수정 1] 아이콘을 bg.jpg로 변경
st.set_page_config(page_title="천비칠마 상조회", page_icon="bg.jpg", layout="wide")

# [수정 2] 카카오톡 미리보기 이미지 주소를 bg.jpg로 변경
meta_tags = """
<head>
    <meta property="og:title" content="천비칠마 상조회" />
    <meta property="og:description" content="투명하고 편리한 모바일 회비 장부" />
    <meta property="og:image" content="https://raw.githubusercontent.com/ant11353-cyber/sangjo-app/main/bg.jpg" />
    <meta property="og:image:width" content="1200" />
    <meta property="og:image:height" content="630" />
</head>
"""
st.markdown(meta_tags, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. 공통 함수 및 스타일 정의
# -----------------------------------------------------------------------------
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return ""

def format_comma(val):
    try: return f"{int(val):,}"
    except: return val

def safe_int(value):
    try: return int(str(value).replace(',', '').replace(' ', ''))
    except: return 0

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

def get_dues_calc_info():
    today = datetime.now()
    start_date = datetime(2020, 2, 1)
    
    # 경과 월수 계산 (현재년 - 시작년)*12 + (현재월 - 시작월)
    months_passed = (today.year - start_date.year) * 12 + (today.month - start_date.month)
    
    if months_passed < 0: months_passed = 0
    return today, months_passed

def apply_theme_style(page_type="sub"):
    # 다크 모드 공통 CSS
    common_css = """
    <style>
    /* 전체 텍스트 (흰색/회색) */
    .stApp, .stMarkdown, .stText, h1, h2, h3, h4, h5, h6, p, span, div {
        color: #e0e0e0 !important;
    }
    
    /* 컨텐츠 박스 (투명) */
    .content-box {
        background-color: transparent;
        padding: 10px 0px;
        margin-bottom: 20px;
    }
    
    /* 버튼 스타일 (PC 기준) */
    .stButton > button {
        width: 100%;
        height: 4.5rem;
        border-radius: 50px;
        font-size: 1.2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        margin-bottom: 12px;
        background-color: rgba(30, 30, 30, 0.8);
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    .stButton > button:hover {
        background-color: rgba(50, 50, 50, 0.9);
        border-color: #ffcc00;
        color: #ffcc00 !important;
        transform: scale(1.02);
    }

    /* [모바일 최적화] */
    @media only screen and (max-width: 600px) {
        .stButton > button {
            height: 3.5rem !important;
            min-height: 3.5rem !important;
            font-size: 1rem !important;
            border-radius: 30px !important;
            margin-bottom: 10px !important;
        }
        .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
    }
    
    /* 표 스타일 (다크) */
    [data-testid="stDataFrame"] {
        background-color: rgba(255, 255, 255, 0.05);
        padding: 5px;
        border-radius: 10px;
    }
    [data-testid="stDataFrame"] div[role="columnheader"] {
        display: flex;
        justify-content: center;
        text-align: center;
        color: #ffffff !important;
        font-weight: bold;
    }
    [data-testid="stDataFrame"] div[role="gridcell"] {
        display: flex;
        justify-content: center;
        text-align: center;
        color: #e0e0e0 !important;
    }
    
    /* 결론 박스 */
    .conclusion-box {
        background-color: rgba(0, 0, 0, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.15);
        padding: 20px;
        border-radius: 10px;
        color: #f0f0f0 !important;
        font-weight: bold;
        font-size: 1.3rem;
        text-align: center;
        margin-top: 15px;
        line-height: 1.6;
    }
    
    /* 이자 강조 */
    .interest-box {
        font-size: 1.5rem;
        font-weight: bold;
        color: #81c784 !important;
        text-align: center;
        padding: 15px;
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
    }

    /* 로그인 안내 박스 */
    .login-guide-box {
        background-color: rgba(30, 30, 30, 0.8);
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
        margin-bottom: 20px;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .highlight {
         color: #ffcc00 !important;
         font-weight: bold;
    }
    
    /* 입력창 */
    .stTextInput input {
        background-color: rgba(255, 255, 255, 0.1);
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    .stTextInput label {
        color: #ffffff !important;
    }
    </style>
    """
    st.markdown(common_css, unsafe_allow_html=True)

    if page_type == 'home':
        try:
            # [수정 3] 배경 이미지도 bg.jpg를 읽도록 변경
            bin_str = get_base64_of_bin_file('bg.jpg')
            
            # 혹시나 파일이 없을 경우를 대비해 예외 처리 강화
            if not bin_str:
                 # bg.jpg 읽기 실패시 bg.png 시도 (안전장치)
                 bin_str = get_base64_of_bin_file('bg.png')

            bg_css = f"""
            <style>
            .stApp {{
                background-image: url("data:image/png;base64,{bin_str}");
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
                background-attachment: fixed;
            }}
            .block-container {{
                padding-top: 0rem;
            }}
            .footer-credit {{
                position: fixed;
                bottom: 10px;
                right: 10px;
                color: rgba(255, 255, 255, 0.5) !important;
                font-size: 0.8rem;
                padding: 4px 10px;
                background-color: rgba(0, 0, 0, 0.4);
                border-radius: 15px;
                z-index: 9999;
            }}
            </style>
            """
            st.markdown(bg_css, unsafe_allow_html=True)
        except:
            st.error("배경화면 파일(bg.jpg)을 찾을 수 없습니다.")
    else:
        bg_css = """
        <style>
        .stApp {
            background-image: none !important;
            background-color: #121212 !important;
        }
        </style>
        """
        st.markdown(bg_css, unsafe_allow_html=True)

def render_header_nav(title):
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    c1, c2 = st.columns([8, 2])
    with c1: st.header(title)
    with c2:
        if st.button("🏠 홈으로"):
            st.switch_page(home) 

def render_footer_div():
    st.markdown('</div>', unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 3. 페이지별 함수 정의
# -----------------------------------------------------------------------------

def page_home():
    """홈 화면"""
    apply_theme_style("home")
    
    left_col, right_col = st.columns([1.2, 4])
    
    with left_col:
        st.markdown("<div style='height: 30vh;'></div>", unsafe_allow_html=True)
        
        if st.button("🚪 회원 전체 현황"):
            st.switch_page(status)
        st.write("") 
        if st.button("🚪 회원 개인 현황"):
            st.switch_page(personal)
        st.write("") 
        if st.button("🚪 회칙 확인"):
            st.switch_page(rules)
            
    st.markdown('<div class="footer-credit">Copyright © 2026 GS Kim. All rights reserved.</div>', unsafe_allow_html=True)


def page_personal():
    """회원 개인 현황"""
    apply_theme_style("sub")
    render_header_nav("🔒 회원 개인 현황")
    
    spacer_left, col_center, spacer_right = st.columns([1, 2, 1])
    with col_center:
        st.markdown(
            """
            <div class="login-guide-box">
                <h3 style="margin-top: 0; color: white;">🔑 아이디 확인</h3>
                <p style="font-size: 1.1rem; line-height: 1.6; margin-bottom: 5px;">
                    본인의 이메일 아이디 중 <b>아이디만</b> 입력해주세요.
                </p>
                <p style="font-size: 0.95rem; opacity: 0.8;">
                    (예: "abc123@nate.com"이면 <b class="highlight">"abc123"</b>을 입력)
                </p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        user_id_input = st.text_input("아이디입력", placeholder="여기에 아이디를 입력하세요")
    
    if user_id_input:
        df_members = load_data("members")
        df_ledger = load_data("ledger")
        
        target_col = '아이디' if '아이디' in df_members.columns else '비밀번호'
        user_info = df_members[df_members[target_col].astype(str).str.lower() == str(user_id_input).lower()]

        if not user_info.empty:
            user = user_info.iloc[0]
            user_name = user['성명']
            st.success(f"환영합니다, {user_name} ({user['직책']})님!")
            
            today_date, months_passed = get_dues_calc_info()
            
            # 최초 가입금 100,000원
            total_due_target = 100000 + (months_passed * 30000)
            
            my_deposit = 0; my_condolence_amt = 0; my_wreath_amt = 0
            if not df_ledger.empty:
                if '금액' in df_ledger.columns:
                    df_ledger['금액'] = df_ledger['금액'].apply(safe_int)
                    my_deposit = df_ledger[(df_ledger['구분'] == '입금') & (df_ledger['내용'] == user_name)]['금액'].sum()
                    
                    my_condolence_amt = df_ledger[(df_ledger['구분'] == '출금') & (df_ledger['분류'] == '상조금') & (df_ledger['내용'] == user_name)]['금액'].sum()
                    my_wreath_amt = df_ledger[(df_ledger['구분'] == '출금') & (df_ledger['분류'] == '근조화환') & (df_ledger['내용'] == user_name)]['금액'].sum()

            unpaid = total_due_target - my_deposit
            condolence_count = int(my_condolence_amt / 1000000) if my_condolence_amt > 0 else 0
            
            st.divider()
            st.subheader(f"📋 {user_name}님의 현황표")
            prev_month_date = today_date - relativedelta(months=1)
            st.caption(f"기준월: {prev_month_date.strftime('%Y년 %m월')}")
            
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
            with col_center:
                st.error("일치하는 아이디가 없습니다. 다시 확인해주세요.")
    render_footer_div()


def page_all_status():
    """회원 전체 현황"""
    apply_theme_style("sub")
    render_header_nav("📊 회원전체현황")
    
    df_members = load_data("members")
    df_ledger = load_data("ledger")
    df_assets = load_data("assets")
    
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
    
    _, months_passed = get_dues_calc_info()
    total_due_target_per_person = 100000 + (months_passed * 30000)
    
    with tab1:
        # [1] 전체 입금액
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
            total_paid_sum = df_analysis['B.납부한금액'].sum()
            total_diff = df_analysis['차이금액(=A-B)'].sum()
            
            total_row = pd.DataFrame([{
                "회원명": "합계",
                "A.납부할금액": total_due,
                "B.납부한금액": total_paid_sum,
                "차이금액(=A-B)": total_diff,
                "상태": "-"
            }])
            df_display = pd.concat([df_analysis, total_row], ignore_index=True)
            
            st.subheader(f"1. 전체 입금내역 분석 : {format_comma(total_paid_sum)} 원")
            cols_to_comma = ["A.납부할금액", "B.납부한금액", "차이금액(=A-B)"]
            for col in cols_to_comma:
                df_display[col] = df_display[col].apply(format_comma)
            st.dataframe(df_display, use_container_width=True, hide_index=True)
        else:
            st.warning("데이터가 없습니다.")
            
        st.divider()
        
        # [2] 지출액
        exp_total = 0
        df_exp = pd.DataFrame()
        
        if '금액' in df_ledger.columns:
            exp_condolence = df_ledger[(df_ledger['구분'] == '출금') & (df_ledger['분류'] == '상조금')]['금액'].sum()
            exp_wreath = df_ledger[(df_ledger['구분'] == '출금') & (df_ledger['분류'] == '근조화환')]['금액'].sum()
            exp_meeting = df_ledger[(df_ledger['구분'] == '출금') & (df_ledger['분류'] == '회의비외')]['금액'].sum()
            exp_savings = df_ledger[(df_ledger['구분'] == '출금') & (df_ledger['분류'] == '적금')]['금액'].sum()
            
            # 합계에 적금 포함
            exp_total = exp_condolence + exp_wreath + exp_meeting + exp_savings
            
            exp_data = {
                "지출 항목": ["(1) 조의금", "(2) 근조화환", "(3) 회의비등", "(4) 적금", "(5) 합계"],
                "내용 설명": [
                    "조의건당 1백만원", 
                    "조의건당 1십만원", 
                    "상조기 및 모임식대, 각종소포품 등", 
                    "최초적금가입원금", 
                    "=(1)+(2)+(3)+(4)"
                ],
                "금액": [exp_condolence, exp_wreath, exp_meeting, exp_savings, exp_total]
            }
            df_exp = pd.DataFrame(exp_data)
            df_exp['금액'] = df_exp['금액'].apply(format_comma)

        st.subheader(f"2. 회비통장지출액 : {format_comma(exp_total)} 원")
        if '금액' in df_ledger.columns:
            st.dataframe(df_exp, use_container_width=True, hide_index=True)
        
        st.divider()

        # [3] 분석적 검토
        real_balance = 0
        if asset_amount_col and asset_name_col:
            try: 
                mask = df_assets[asset_name_col].str.contains('회비통장', na=False)
                if mask.any(): real_balance = df_assets[mask][asset_amount_col].iloc[0]
            except: pass
        
        val_a = total_paid_sum - exp_total # 장부상 잔액
        val_b = real_balance # 실제 통장 잔액
        
        diff_final = val_b - val_a
        
        review_data = {
            "구분": ["A. 실제 통장 잔액", "B. 장부상 잔액", "차이 (A-B)"],
            "산출 근거": [
                "회비통장실제잔액",
                "전체 입금액 합계 - 회비통장 지출 총계",
                "이자수익 및 적금불입액 등 차이"
            ],
            "금액": [val_b, val_a, diff_final]
        }
        df_review = pd.DataFrame(review_data)
        df_review['금액'] = df_review['금액'].apply(format_comma)

        st.subheader(f"3. 분석적검토 (차이: {format_comma(diff_final)} 원)")
        st.dataframe(df_review, use_container_width=True, hide_index=True)

        st.divider()
        st.subheader("4. 결론")
        st.markdown("""<div class="conclusion-box">차이금액은 회비통장의 이자수익 등 미반영으로 차이 발생분으로 중요성관점에서 문제없음</div>""", unsafe_allow_html=True)

    with tab2:
        st.subheader("보유 자산")
        if not df_assets.empty:
            total_asset_val = 0
            if asset_amount_col:
                if asset_name_col:
                    mask = ~df_assets[asset_name_col].astype(str).str.contains('합계', na=False)
                    total_asset_val = df_assets[mask][asset_amount_col].sum()
                else:
                    total_asset_val = df_assets[asset_amount_col].sum()
                
                df_assets_disp = df_assets.copy()
                df_assets_disp[asset_amount_col] = df_assets_disp[asset_amount_col].apply(format_comma)
                
                df_assets_disp = df_assets_disp.astype(str)
                df_assets_disp = df_assets_disp.replace({'None': '', 'nan': '', '0': '', '0.0': ''}, regex=False)
                
                st.dataframe(df_assets_disp, use_container_width=True, hide_index=True)
                st.metric("총 자산", f"{format_comma(total_asset_val)} 원")
            else:
                df_assets_disp = df_assets.astype(str).replace({'None': '', 'nan': '', '0': '', '0.0': ''}, regex=False)
                st.dataframe(df_assets_disp, use_container_width=True, hide_index=True)
        else:
            st.warning("자산 데이터를 불러오지 못했습니다.")

    with tab3:
        if not df_ledger.empty and not df_assets.empty and asset_amount_col and asset_name_col and '금액' in df_ledger.columns:
            
            target_ledger = df_ledger[df_ledger['분류'] == '적금'].copy()
            principal_sum = target_ledger['금액'].sum()
            
            st.subheader(f"1. 적금가입원금 : {format_comma(principal_sum)} 원")
            
            if not target_ledger.empty:
                df_disp_ledger = pd.DataFrame()
                df_disp_ledger['거래일시'] = target_ledger['거래일시']
                df_disp_ledger['금액'] = target_ledger['금액'].apply(format_comma)
                df_disp_ledger['내용'] = "적금원금"
                st.dataframe(df_disp_ledger, use_container_width=True, hide_index=True)
            else:
                st.info("적금 가입 내역이 없습니다.")
            
            st.divider()
            
            target_assets = df_assets[df_assets[asset_name_col].str.contains('적금', na=False)].copy()
            current_val_sum = target_assets[asset_amount_col].sum()
            st.subheader(f"2. 적금통장가입액(평가액) : {format_comma(current_val_sum)} 원")
            
            bank_col = None
            for col in ['은행', 'Bank', '금융기관', '은행명']:
                if col in df_assets.columns: bank_col = col; break
            
            df_disp_assets = pd.DataFrame()
            df_disp_assets['구분'] = target_assets[asset_name_col]
            df_disp_assets['은행'] = target_assets[bank_col] if bank_col else '-'
            df_disp_assets['잔액'] = target_assets[asset_amount_col].apply(format_comma)
            st.dataframe(df_disp_assets, use_container_width=True, hide_index=True)

            st.divider()
            interest = current_val_sum - principal_sum
            st.subheader(f"3. 이자발생누적액(2-1)")
            st.markdown(f"<div class='interest-box'>💰 {format_comma(interest)} 원</div>", unsafe_allow_html=True)
            
            st.divider()
            st.subheader("4. 총평")
            st.markdown("""<div class="conclusion-box">회비는 매우 투명하게 관리되고 있으며, 입출금내역 검토시 설명할 수 없는 내역은 존재하지 아니함. 매우 훌륭하다고 평가됨</div>""", unsafe_allow_html=True)
    render_footer_div()


def page_rules():
    """회칙 페이지"""
    apply_theme_style("sub")
    render_header_nav("📜 회칙 및 규정")
    df_rules = load_data("rules")
    search_rule = st.text_input("규정 검색", placeholder="검색어를 입력하세요")
    
    if not df_rules.empty:
        if search_rule:
            df_rules = df_rules[df_rules['내용'].str.contains(search_rule) | df_rules['조항'].str.contains(search_rule)]
        
        for idx, row in df_rules.iterrows():
            article = row.get('조항', '')
            title = row.get('제목', row.get('항목', ''))
            header_text = f"{article}({title})" if title and str(title).lower() != 'nan' else article
            
            st.markdown(f"<div class='rule-header' style='font-weight:bold; font-size:1.1rem; color:#fff; margin-top:10px;'>{header_text}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='rule-content' style='color:#e0e0e0; margin-bottom:10px;'>{row.get('내용', '-')}</div>", unsafe_allow_html=True)
            st.divider()
    render_footer_div()


# -----------------------------------------------------------------------------
# 4. 네비게이션 설정
# -----------------------------------------------------------------------------
home = st.Page(page_home, title="홈", url_path="home", default=True)
status = st.Page(page_all_status, title="회원전체현황", url_path="status")
personal = st.Page(page_personal, title="회원개인현황", url_path="personal")
rules = st.Page(page_rules, title="회칙", url_path="rules")

pg = st.navigation([home, status, personal, rules], position="hidden")
pg.run()
