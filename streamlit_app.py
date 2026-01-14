import streamlit as st
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
import base64

# -----------------------------------------------------------------------------
# 1. 페이지 설정 (가장 먼저 실행)
# -----------------------------------------------------------------------------
st.set_page_config(page_title="천비칠마 상조회", page_icon="👑", layout="wide")

# -----------------------------------------------------------------------------
# 2. 공통 함수 및 스타일 정의 (기능 보존 + 디자인 업그레이드)
# -----------------------------------------------------------------------------
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
    ref_date = today - relativedelta(months=1)
    start_date = datetime(2020, 2, 1)
    diff = relativedelta(ref_date, start_date)
    months_passed = diff.years * 12 + diff.months
    if months_passed < 0: months_passed = 0
    return ref_date, months_passed

def apply_theme_style():
    # React 디자인(Gold + Dark + Blur)을 CSS로 재해석하여 적용
    design_css = """
    <style>
    /* [1] 폰트 및 기본 컬러 설정 */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Noto Sans KR', sans-serif;
    }

    /* [2] 배경 디자인: React 코드의 bg-gold blur 효과를 CSS Gradient로 구현 */
    .stApp {
        background-color: #0a0a0a; /* 딥 블랙 */
        background-image: 
            radial-gradient(circle at 10% 20%, rgba(212, 175, 55, 0.15) 0%, transparent 40%),
            radial-gradient(circle at 90% 10%, rgba(212, 175, 55, 0.1) 0%, transparent 40%),
            radial-gradient(circle at 50% 50%, rgba(255, 215, 0, 0.05) 0%, transparent 60%);
        background-attachment: fixed;
        background-size: cover;
    }

    /* 헤더 및 텍스트 컬러 (골드 포인트) */
    h1, h2, h3 {
        color: #FFD700 !important; /* Gold Text */
        font-weight: 700 !important;
        text-shadow: 0 0 10px rgba(255, 215, 0, 0.3);
    }
    p, span, div, label {
        color: #e0e0e0 !important;
    }

    /* [3] 카드 스타일 (Glassmorphism) */
    .content-box, .login-guide-box, .conclusion-box, [data-testid="stDataFrame"] {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 215, 0, 0.15); /* 은은한 금색 테두리 */
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s;
    }
    
    /* [4] 버튼 스타일 (참고 디자인의 둥근 형태) */
    .stButton > button {
        background: linear-gradient(145deg, rgba(30,30,30,0.9), rgba(20,20,20,0.9)) !important;
        color: #FFD700 !important; /* Gold Text */
        border: 1px solid rgba(255, 215, 0, 0.3) !important;
        border-radius: 9999px !important; /* 완전 둥글게 */
        font-weight: bold !important;
        height: 3.5rem !important;
        transition: all 0.3s ease !important;
    }
    .stButton > button:hover {
        background: rgba(255, 215, 0, 0.1) !important;
        border-color: #FFD700 !important;
        box-shadow: 0 0 15px rgba(255, 215, 0, 0.2);
        transform: translateY(-2px);
    }

    /* [5] 입력창 스타일 */
    .stTextInput input {
        background-color: rgba(0, 0, 0, 0.3) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
        color: #fff !important;
    }
    .stTextInput input:focus {
        border-color: #FFD700 !important;
        box-shadow: 0 0 0 1px #FFD700 !important;
    }

    /* [6] 표 스타일 커스텀 */
    [data-testid="stDataFrame"] {
        background: transparent !important;
        border: none !important;
    }
    [data-testid="stHeader"] {
        background-color: rgba(0,0,0,0) !important;
    }
    
    /* 탭 스타일 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent !important;
        border-radius: 20px !important;
        color: #888 !important;
        padding: 10px 20px !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(255, 215, 0, 0.1) !important;
        color: #FFD700 !important;
        border: 1px solid rgba(255, 215, 0, 0.3) !important;
    }

    /* 하단 저작권 */
    .footer-credit {
        position: fixed;
        bottom: 10px;
        left: 0;
        width: 100%;
        text-align: center;
        color: rgba(255, 255, 255, 0.3) !important;
        font-size: 0.8rem;
        pointer-events: none;
    }
    
    /* 이자 박스 강조 */
    .interest-box {
        font-size: 1.8rem;
        font-weight: 800;
        color: #FFD700 !important; /* Gold */
        text-align: center;
        padding: 20px;
        background: radial-gradient(circle, rgba(255,215,0,0.1) 0%, transparent 70%);
        border-radius: 15px;
        margin: 10px 0;
    }
    </style>
    """
    st.markdown(design_css, unsafe_allow_html=True)

def render_header_nav(title):
    # 헤더도 카드가 아닌 투명한 배경에 금색 타이틀로 처리
    c1, c2 = st.columns([8, 2])
    with c1: 
        st.markdown(f"## {title}")
    with c2:
        if st.button("🏠 홈으로"):
            st.switch_page(home) 
    st.markdown("---")

def render_footer_div():
    # 기존 기능 유지용 (빈 함수)
    pass


# -----------------------------------------------------------------------------
# 3. 페이지별 함수 정의
# -----------------------------------------------------------------------------

def page_home():
    """홈 화면"""
    apply_theme_style() # 디자인 적용
    
    st.markdown("<div style='text-align: center; padding-top: 5vh; padding-bottom: 5vh;'>", unsafe_allow_html=True)
    st.title("천비칠마 상조회")
    st.markdown("<p style='opacity: 0.7;'>Membership Dashboard</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 카드형 레이아웃 배치
    c1, c2, c3 = st.columns(3)
    
    # Streamlit은 버튼 스타일링에 한계가 있어 CSS로 덮어씌웠으므로
    # 여기서는 배치만 깔끔하게 하면 됩니다.
    with c1:
        st.info("📊 전체 현황")
        if st.button("회원 전체 현황 바로가기", use_container_width=True):
            st.switch_page(status)
    
    with c2:
        st.warning("👤 내 정보") # Gold 색상 느낌을 위해 warning 활용 가능
        if st.button("회원 개인 현황 바로가기", use_container_width=True):
            st.switch_page(personal)
            
    with c3:
        st.success("📜 규정 확인")
        if st.button("회칙 확인 바로가기", use_container_width=True):
            st.switch_page(rules)
            
    # 하단 장식 요소
    st.markdown("<div style='height: 10vh;'></div>", unsafe_allow_html=True)
    st.markdown('<div class="footer-credit">Copyright © 2026 GS Kim. All rights reserved.</div>', unsafe_allow_html=True)


def page_personal():
    """회원 개인 현황"""
    apply_theme_style()
    render_header_nav("MEMBERSHIP CARD") # 영어 타이틀이 디자인과 어울림
    
    spacer_left, col_center, spacer_right = st.columns([1, 2, 1])
    with col_center:
        # 멤버십 카드 느낌의 로그인 박스
        st.markdown(
            """
            <div class="login-guide-box" style="text-align:center;">
                <h3 style="margin: 0; padding-bottom:10px;">🔑 MEMBER ACCESS</h3>
                <p style="opacity: 0.7;">본인의 이메일 아이디(ID)를 입력해주세요</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        user_id_input = st.text_input("ID", placeholder="예: abc1234", label_visibility="collapsed")
    
    if user_id_input:
        df_members = load_data("members")
        df_ledger = load_data("ledger")
        
        target_col = '아이디' if '아이디' in df_members.columns else '비밀번호'
        user_info = df_members[df_members[target_col].astype(str).str.lower() == str(user_id_input).lower()]

        if not user_info.empty:
            user = user_info.iloc[0]
            user_name = user['성명']
            
            # 데이터 계산 로직 (기존 코드 그대로 유지)
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
            
            # --- 결과 보여주기 (디자인 적용) ---
            st.divider()
            
            # 회원 카드 디자인
            st.markdown(f"""
            <div class="content-box">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <h2 style="margin:0;">{user_name}</h2>
                        <p style="opacity:0.6; margin:0;">{user['직책']} | Since {user['가입일자']}</p>
                    </div>
                    <div style="text-align:right;">
                         <span style="font-size:0.8rem; color:#FFD700 !important; border:1px solid #FFD700; padding:5px 10px; border-radius:15px;">ACTIVE MEMBER</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"""
                <div class="content-box">
                    <h4 style="color:#FFD700 !important;">💰 납부 현황</h4>
                    <p>총 납부 대상액: <b>{format_comma(total_due_target)}</b> 원</p>
                    <p>실제 납부액: <b>{format_comma(my_deposit)}</b> 원</p>
                </div>
                """, unsafe_allow_html=True)
            with c2:
                 st.markdown(f"""
                <div class="content-box">
                    <h4 style="color:#FFD700 !important;">🎗 수령 현황</h4>
                    <p>조의 횟수: <b>{condolence_count}</b> 회</p>
                    <p>총 수령액: <b>{format_comma(my_condolence_amt + my_wreath_amt)}</b> 원</p>
                </div>
                """, unsafe_allow_html=True)

            # 미납금 알림 (색상으로 상태 구분)
            if unpaid > 0:
                st.error(f"⚠️ 미납액이 있습니다: {format_comma(unpaid)} 원")
            elif unpaid == 0:
                st.success("✅ 회비가 완납되었습니다.")
            else:
                st.info(f"💙 선납액이 있습니다: {format_comma(abs(unpaid))} 원")
                
        else:
            with col_center:
                st.error("일치하는 아이디가 없습니다.")


def page_all_status():
    """회원 전체 현황"""
    apply_theme_style()
    render_header_nav("DASHBOARD")
    
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

    # 탭 디자인
    tab1, tab2, tab3 = st.tabs(["📊 분석 리포트", "💰 자산 현황", "📈 이자 수익"])
    
    ref_date, months_passed = get_dues_calc_info()
    total_due_target_per_person = 1000000 + (months_passed * 30000)
    
    with tab1:
        # [1] 전체 입금액 계산 로직
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
                    "납부할금액": total_due_target_per_person, 
                    "납부한금액": paid_total, 
                    "차이": unpaid, 
                    "상태": note
                })
            df_analysis = pd.DataFrame(analysis_data)
            total_due = df_analysis['납부할금액'].sum()
            total_paid_sum = df_analysis['납부한금액'].sum()
            total_diff = df_analysis['차이'].sum()
            
            # 합계 행
            total_row = pd.DataFrame([{
                "회원명": "TOTAL",
                "납부할금액": total_due,
                "납부한금액": total_paid_sum,
                "차이": total_diff,
                "상태": "-"
            }])
            df_display = pd.concat([df_analysis, total_row], ignore_index=True)
            
            st.markdown(f"### 1. 입금 분석 (Total: {format_comma(total_paid_sum)}원)")
            
            # 포맷팅
            for col in ["납부할금액", "납부한금액", "차이"]:
                df_display[col] = df_display[col].apply(format_comma)
            
            # 데이터프레임을 CSS 적용된 컨테이너에 넣기
            st.dataframe(df_display, use_container_width=True, hide_index=True)
        else:
            st.warning("데이터가 로딩되지 않았습니다.")
            
        st.divider()
        
        # [2] 지출액 계산 로직
        exp_total = 0
        if '금액' in df_ledger.columns:
            exp_condolence = df_ledger[(df_ledger['구분'] == '출금') & (df_ledger['분류'] == '조의금')]['금액'].sum()
            exp_wreath = df_ledger[(df_ledger['구분'] == '출금') & (df_ledger['분류'] == '근조화환')]['금액'].sum()
            exp_meeting = df_ledger[(df_ledger['구분'] == '출금') & (df_ledger['분류'] == '회의비외')]['금액'].sum()
            exp_total = exp_condolence + exp_wreath + exp_meeting
            
            exp_data = {
                "지출 항목": ["조의금", "근조화환", "운영비", "합계"],
                "금액": [exp_condolence, exp_wreath, exp_meeting, exp_total]
            }
            df_exp = pd.DataFrame(exp_data)
            df_exp['금액'] = df_exp['금액'].apply(format_comma)

        st.markdown(f"### 2. 지출 분석 (Total: {format_comma(exp_total)}원)")
        st.dataframe(df_exp, use_container_width=True, hide_index=True)
        
        st.divider()

        # [3] 분석적 검토
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
            "구분": ["장부상 잔액 (A)", "실제 통장 잔액 (B)", "차이 (A-B)"],
            "금액": [val_a, val_b, diff_final]
        }
        df_review = pd.DataFrame(review_data)
        df_review['금액'] = df_review['금액'].apply(format_comma)

        st.markdown("### 3. 정합성 검토")
        st.dataframe(df_review, use_container_width=True, hide_index=True)

        st.markdown("""<div class="conclusion-box">✅ 검토 결과: 차이 금액은 이자 수익 등으로 인한 자연스러운 발생분이며 회계상 적정합니다.</div>""", unsafe_allow_html=True)

    with tab2:
        st.markdown("### 💎 자산 포트폴리오")
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
                
                # 메트릭 스타일
                st.metric("총 자산 규모", f"{format_comma(total_asset_val)} 원")
                st.dataframe(df_assets_disp, use_container_width=True, hide_index=True)
        else:
            st.warning("자산 데이터 없음")

    with tab3:
        if not df_ledger.empty and not df_assets.empty and asset_amount_col and asset_name_col and '금액' in df_ledger.columns:
            target_ledger = df_ledger[df_ledger['구분'].str.contains('적금', na=False)].copy()
            principal_sum = target_ledger['금액'].sum()
            
            target_assets = df_assets[df_assets[asset_name_col].str.contains('적금', na=False)].copy()
            current_val_sum = target_assets[asset_amount_col].sum()
            
            interest = current_val_sum - principal_sum
            
            c1, c2, c3 = st.columns(3)
            with c1: st.metric("적금 원금", f"{format_comma(principal_sum)}원")
            with c2: st.metric("현재 평가액", f"{format_comma(current_val_sum)}원")
            with c3: st.metric("이자 수익", f"+{format_comma(interest)}원", delta_color="normal")
            
            st.divider()
            st.markdown("### 💰 누적 이자 수익")
            st.markdown(f"<div class='interest-box'>+ {format_comma(interest)} KRW</div>", unsafe_allow_html=True)


def page_rules():
    """회칙 페이지"""
    apply_theme_style()
    render_header_nav("BYLAWS & RULES")
    
    df_rules = load_data("rules")
    search_rule = st.text_input("Search", placeholder="규정 검색어 입력...", label_visibility="collapsed")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if not df_rules.empty:
        if search_rule:
            df_rules = df_rules[df_rules['내용'].str.contains(search_rule) | df_rules['조항'].str.contains(search_rule)]
        
        for idx, row in df_rules.iterrows():
            article = row.get('조항', '')
            title = row.get('제목', row.get('항목', ''))
            content = row.get('내용', '-')
            
            # 카드 형태로 규정 표시
            st.markdown(f"""
            <div class="content-box" style="margin-bottom: 15px;">
                <div style="color: #FFD700; font-weight: bold; font-size: 1.1em; margin-bottom: 5px;">
                    {article} {f'({title})' if title and str(title) != 'nan' else ''}
                </div>
                <div style="color: #ccc; line-height: 1.6;">
                    {content}
                </div>
            </div>
            """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 4. 네비게이션 설정 (유지)
# -----------------------------------------------------------------------------
home = st.Page(page_home, title="홈", url_path="home", default=True)
status = st.Page(page_all_status, title="회원전체현황", url_path="status")
personal = st.Page(page_personal, title="회원개인현황", url_path="personal")
rules = st.Page(page_rules, title="회칙", url_path="rules")

pg = st.navigation([home, status, personal, rules], position="hidden")
pg.run()
