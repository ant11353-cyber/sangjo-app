import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from dateutil.relativedelta import relativedelta
import base64

# -----------------------------------------------------------------------------
# 1. 페이지 설정
# -----------------------------------------------------------------------------
st.set_page_config(page_title="천비칠마 상조회", page_icon="🐴", layout="wide")

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
# 2. 공통 함수
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
    months_passed = (today.year - start_date.year) * 12 + (today.month - start_date.month)+1
    if months_passed < 0: months_passed = 0
    return today, months_passed

# -----------------------------------------------------------------------------
# 3. Plotly 차트 함수들
# -----------------------------------------------------------------------------

PLOTLY_LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#e0e0e0', family='Pretendard, sans-serif'),
    margin=dict(l=10, r=10, t=40, b=10),
)

def make_gauge_chart(paid, total, title="납부율"):
    """납부율 게이지 차트"""
    rate = min(round((paid / total) * 100, 1) if total > 0 else 0, 100)
    
    if rate >= 100:
        bar_color = "#4CAF50"
        steps_color = [
            {'range': [0, 60], 'color': 'rgba(255,82,82,0.15)'},
            {'range': [60, 85], 'color': 'rgba(255,193,7,0.15)'},
            {'range': [85, 100], 'color': 'rgba(76,175,80,0.15)'},
        ]
    elif rate >= 85:
        bar_color = "#66BB6A"
        steps_color = [
            {'range': [0, 60], 'color': 'rgba(255,82,82,0.15)'},
            {'range': [60, 85], 'color': 'rgba(255,193,7,0.15)'},
            {'range': [85, 100], 'color': 'rgba(76,175,80,0.15)'},
        ]
    elif rate >= 60:
        bar_color = "#FFC107"
        steps_color = [
            {'range': [0, 60], 'color': 'rgba(255,82,82,0.15)'},
            {'range': [60, 85], 'color': 'rgba(255,193,7,0.25)'},
            {'range': [85, 100], 'color': 'rgba(76,175,80,0.15)'},
        ]
    else:
        bar_color = "#FF5252"
        steps_color = [
            {'range': [0, 60], 'color': 'rgba(255,82,82,0.25)'},
            {'range': [60, 85], 'color': 'rgba(255,193,7,0.15)'},
            {'range': [85, 100], 'color': 'rgba(76,175,80,0.15)'},
        ]

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=rate,
        number={'suffix': '%', 'font': {'size': 36, 'color': bar_color}},
        delta={'reference': 100, 'suffix': '%', 'font': {'size': 14}},
        title={'text': title, 'font': {'size': 14, 'color': '#b0b0b0'}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': '#555'},
            'bar': {'color': bar_color, 'thickness': 0.25},
            'bgcolor': 'rgba(0,0,0,0)',
            'borderwidth': 0,
            'steps': steps_color,
            'threshold': {
                'line': {'color': '#ffffff', 'width': 2},
                'thickness': 0.75,
                'value': 100
            }
        }
    ))
    fig.update_layout(**PLOTLY_LAYOUT, height=220)
    return fig

def make_donut_chart(labels, values, title="자산 구성"):
    """자산 구성 도넛 차트"""
    colors = ['#4CAF50', '#EF5350', '#4FC3F7', '#FF8A65', '#CE93D8', '#F48FB1']
    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.55,
        marker=dict(colors=colors[:len(labels)], line=dict(color='rgba(0,0,0,0.3)', width=2)),
        textinfo='label+percent',
        textfont=dict(size=12, color='#e0e0e0'),
        hovertemplate='<b>%{label}</b><br>%{value:,.0f}원<br>%{percent}<extra></extra>',
    ))
    fig.update_layout(
        **PLOTLY_LAYOUT,
        height=300,
        title=dict(text=title, font=dict(size=14, color='#b0b0b0'), x=0.5),
        legend=dict(
            orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5,
            font=dict(color='#e0e0e0', size=11)
        ),
        showlegend=True,
    )
    return fig

def make_payment_bar_chart(df_analysis):
    """회원별 납부 현황 가로 막대 차트"""
    df_plot = df_analysis[df_analysis['회원명'] != '합계'].copy()
    df_plot['납부율'] = (df_plot['B.납부한금액'] / df_plot['A.납부할금액'] * 100).clip(0, 100)
    df_plot = df_plot.sort_values('납부율', ascending=True)

    colors = ['#FF5252' if r < 60 else ('#FFC107' if r < 100 else '#4CAF50') for r in df_plot['납부율']]

    fig = go.Figure(go.Bar(
        y=df_plot['회원명'],
        x=df_plot['납부율'],
        orientation='h',
        marker=dict(color=colors, line=dict(color='rgba(0,0,0,0.2)', width=1)),
        text=[f"{r:.1f}%" for r in df_plot['납부율']],
        textposition='outside',
        textfont=dict(color='#e0e0e0', size=12),
        hovertemplate='<b>%{y}</b><br>납부율: %{x:.1f}%<extra></extra>',
    ))
    fig.add_vline(x=100, line_dash="dash", line_color="rgba(255,255,255,0.3)", line_width=1)
    fig.update_layout(
        **PLOTLY_LAYOUT,
        height=max(250, len(df_plot) * 40 + 60),
        title=dict(text="회원별 납부율", font=dict(size=14, color='#b0b0b0'), x=0.5),
        xaxis=dict(range=[0, 120], ticksuffix='%', gridcolor='rgba(255,255,255,0.07)'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.07)'),
    )
    return fig

def make_expense_pie_chart(labels, values):
    """지출 구성 파이 차트"""
    colors = ['#EF5350', '#FF7043', '#FFA726', '#42A5F5']
    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        marker=dict(colors=colors[:len(labels)], line=dict(color='rgba(0,0,0,0.3)', width=2)),
        textinfo='label+percent',
        textfont=dict(size=12, color='#ffffff'),
        hovertemplate='<b>%{label}</b><br>%{value:,.0f}원<br>%{percent}<extra></extra>',
        pull=[0.05] * len(labels),
    ))
    fig.update_layout(
        **PLOTLY_LAYOUT,
        height=300,
        title=dict(text="지출 구성", font=dict(size=14, color='#b0b0b0'), x=0.5),
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5,
                    font=dict(color='#e0e0e0', size=11)),
    )
    return fig

def make_interest_timeline(principal, current):
    """원금 vs 평가액 비교 막대"""
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name='원금', x=['적금 현황'], y=[principal],
        marker_color='#42A5F5',
        text=[f"{format_comma(principal)}원"], textposition='outside',
        textfont=dict(color='#e0e0e0'),
    ))
    fig.add_trace(go.Bar(
        name='평가액', x=['적금 현황'], y=[current],
        marker_color='#66BB6A',
        text=[f"{format_comma(current)}원"], textposition='outside',
        textfont=dict(color='#e0e0e0'),
    ))
    fig.update_layout(
        **PLOTLY_LAYOUT,
        height=280,
        barmode='group',
        title=dict(text="원금 vs 평가액", font=dict(size=14, color='#b0b0b0'), x=0.5),
        yaxis=dict(gridcolor='rgba(255,255,255,0.07)'),
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5,
                    font=dict(color='#e0e0e0')),
        bargap=0.3, bargroupgap=0.1,
    )
    return fig

# -----------------------------------------------------------------------------
# 4. CSS 스타일 (애니메이션 포함)
# -----------------------------------------------------------------------------
COMMON_CSS = """
<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');

/* ── 기본 텍스트 ── */
.stApp, .stMarkdown, h1, h2, h3, h4, h5, h6, p, span, div {
    color: #e0e0e0 !important;
    font-family: 'Pretendard', -apple-system, sans-serif !important;
}

/* ── 페이지 진입 애니메이션 ── */
@keyframes fadeSlideUp {
    from { opacity: 0; transform: translateY(20px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes pulse-glow {
    0%, 100% { box-shadow: 0 0 0px rgba(255,204,0,0.3); }
    50%       { box-shadow: 0 0 20px rgba(255,204,0,0.6); }
}
@keyframes shimmer {
    0%   { background-position: -200% center; }
    100% { background-position: 200% center; }
}
@keyframes countUp {
    from { opacity: 0; transform: scale(0.8); }
    to   { opacity: 1; transform: scale(1); }
}

.fade-in {
    animation: fadeSlideUp 0.6s ease forwards;
}
.fade-in-delay-1 { animation: fadeSlideUp 0.6s ease 0.1s forwards; opacity:0; }
.fade-in-delay-2 { animation: fadeSlideUp 0.6s ease 0.2s forwards; opacity:0; }
.fade-in-delay-3 { animation: fadeSlideUp 0.6s ease 0.3s forwards; opacity:0; }

/* ── KPI 카드 ── */
.kpi-card {
    background: linear-gradient(135deg, rgba(30,30,30,0.9) 0%, rgba(20,20,20,0.95) 100%);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 20px;
    text-align: center;
    transition: transform 0.25s ease, border-color 0.25s ease;
    animation: fadeSlideUp 0.5s ease forwards;
    backdrop-filter: blur(10px);
}
.kpi-card:hover {
    transform: translateY(-4px);
    border-color: rgba(255,204,0,0.4);
}
.kpi-label {
    font-size: 0.82rem;
    color: #888 !important;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    margin-bottom: 8px;
}
.kpi-value {
    font-size: 1.6rem;
    font-weight: 700;
    color: #ffffff !important;
    animation: countUp 0.6s ease forwards;
}
.kpi-value.green  { color: #4CAF50 !important; }
.kpi-value.red    { color: #FF5252 !important; }
.kpi-value.yellow { color: #FFC107 !important; }
.kpi-value.gold   { color: #FFD700 !important; }

/* ── 버튼 ── */
.stButton > button {
    width: 100%;
    height: 4.5rem;
    border-radius: 50px;
    font-size: 1.15rem;
    font-weight: 600;
    transition: all 0.3s ease;
    margin-bottom: 12px;
    background: linear-gradient(135deg, rgba(35,35,35,0.9), rgba(20,20,20,0.95));
    color: #ffffff !important;
    border: 1px solid rgba(255,255,255,0.15);
    box-shadow: 0 4px 15px rgba(0,0,0,0.4);
    letter-spacing: 0.02em;
    position: relative;
    overflow: hidden;
}
.stButton > button::after {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.06) 50%, transparent 100%);
    background-size: 200% auto;
    animation: shimmer 3s linear infinite;
}
.stButton > button:hover {
    background: linear-gradient(135deg, rgba(60,60,60,0.95), rgba(40,40,40,0.99));
    border-color: #ffcc00;
    color: #ffcc00 !important;
    transform: scale(1.02);
    box-shadow: 0 6px 25px rgba(255,204,0,0.2), 0 0 0 1px rgba(255,204,0,0.3);
}

/* ── 섹션 헤더 ── */
.section-header {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 12px 0 8px 0;
    border-bottom: 1px solid rgba(255,255,255,0.08);
    margin-bottom: 16px;
}
.section-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: #ffffff !important;
    letter-spacing: -0.01em;
}
.section-badge {
    background: rgba(255,204,0,0.15);
    border: 1px solid rgba(255,204,0,0.3);
    color: #FFD700 !important;
    border-radius: 20px;
    padding: 2px 10px;
    font-size: 0.78rem;
    font-weight: 600;
}

/* ── 결론 박스 ── */
.conclusion-box {
    background: linear-gradient(135deg, rgba(0,0,0,0.5), rgba(20,20,20,0.6));
    border: 1px solid rgba(255,255,255,0.1);
    border-left: 3px solid #FFD700;
    padding: 18px 22px;
    border-radius: 12px;
    color: #f0f0f0 !important;
    font-weight: 500;
    font-size: 1.05rem;
    line-height: 1.7;
    margin-top: 12px;
    animation: fadeSlideUp 0.5s ease forwards;
}

/* ── 이자 강조 ── */
.interest-box {
    font-size: 2rem;
    font-weight: 800;
    color: #4CAF50 !important;
    text-align: center;
    padding: 20px;
    background: linear-gradient(135deg, rgba(76,175,80,0.1), rgba(76,175,80,0.05));
    border: 1px solid rgba(76,175,80,0.25);
    border-radius: 16px;
    animation: pulse-glow 2.5s ease infinite;
    letter-spacing: -0.02em;
}

/* ── 로그인 안내 박스 ── */
.login-guide-box {
    background: linear-gradient(135deg, rgba(30,30,30,0.9), rgba(20,20,20,0.95));
    padding: 24px;
    border-radius: 18px;
    text-align: center;
    box-shadow: 0 8px 32px rgba(0,0,0,0.5);
    margin-bottom: 24px;
    border: 1px solid rgba(255,255,255,0.08);
    animation: fadeSlideUp 0.5s ease forwards;
}
.highlight { color: #ffcc00 !important; font-weight: 700; }

/* ── 입력창 ── */
.stTextInput input {
    background: rgba(255,255,255,0.07) !important;
    color: #ffffff !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 12px !important;
    padding: 10px 14px !important;
    font-family: 'Pretendard', sans-serif !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
}
.stTextInput input:focus {
    border-color: rgba(255,204,0,0.5) !important;
    box-shadow: 0 0 0 2px rgba(255,204,0,0.15) !important;
}
.stTextInput label { color: #aaa !important; font-size: 0.88rem !important; }

/* ── 탭 스타일 ── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.03) !important;
    border-radius: 12px !important;
    padding: 4px !important;
    gap: 4px !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    color: #888 !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    padding: 8px 16px !important;
    transition: all 0.2s ease !important;
}
.stTabs [aria-selected="true"] {
    background: rgba(255,204,0,0.15) !important;
    color: #FFD700 !important;
    border-bottom: 2px solid #FFD700 !important;
}

/* ── 데이터프레임 ── */
[data-testid="stDataFrame"] {
    background: rgba(255,255,255,0.03);
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid rgba(255,255,255,0.06);
}
[data-testid="stDataFrame"] div[role="columnheader"] {
    background: rgba(255,204,0,0.08) !important;
    color: #FFD700 !important;
    font-weight: 700 !important;
    font-size: 0.82rem !important;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}
[data-testid="stDataFrame"] div[role="gridcell"] {
    color: #d0d0d0 !important;
    font-size: 0.9rem !important;
}

/* ── 구분선 ── */
hr { border-color: rgba(255,255,255,0.07) !important; }

/* ── Metric ── */
[data-testid="metric-container"] {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px;
    padding: 12px 16px !important;
}
[data-testid="stMetricLabel"] { color: #888 !important; font-size: 0.82rem !important; }
[data-testid="stMetricValue"] { color: #ffffff !important; font-weight: 700 !important; }

/* ── 모바일 최적화 ── */
@media only screen and (max-width: 600px) {
    .stButton > button {
        height: 3.5rem !important;
        font-size: 1rem !important;
        border-radius: 28px !important;
    }
    .block-container { padding-left: 1rem !important; padding-right: 1rem !important; }
    .kpi-value { font-size: 1.3rem !important; }
    .interest-box { font-size: 1.5rem !important; }
}

/* ── 푸터 ── */
.footer-credit {
    position: fixed;
    bottom: 10px;
    right: 10px;
    color: rgba(255,255,255,0.4) !important;
    font-size: 0.75rem;
    padding: 4px 12px;
    background: rgba(0,0,0,0.5);
    border-radius: 20px;
    z-index: 9999;
    backdrop-filter: blur(4px);
}
</style>
"""

def apply_theme_style(page_type="sub"):
    st.markdown(COMMON_CSS, unsafe_allow_html=True)

    if page_type == 'home':
        bin_str = get_base64_of_bin_file('bg.jpg') or get_base64_of_bin_file('bg.png')
        bg_css = f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpeg;base64,{bin_str}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        .block-container {{ padding-top: 0rem; }}
        /* 홈 버튼 영역 글래스모피즘 */
        .home-btn-wrap {{
            background: rgba(0,0,0,0.35);
            backdrop-filter: blur(12px);
            border-radius: 24px;
            padding: 24px 16px;
            border: 1px solid rgba(255,255,255,0.1);
        }}
        </style>
        """
        st.markdown(bg_css, unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(160deg, #0d0d0d 0%, #141414 50%, #111111 100%) !important;
        }
        </style>""", unsafe_allow_html=True)

def render_header_nav(title):
    c1, c2 = st.columns([8, 2])
    with c1:
        st.markdown(f"""
        <div class="fade-in" style="padding: 8px 0 4px 0;">
            <h2 style="margin:0; font-size:1.4rem; font-weight:800; letter-spacing:-0.02em;">{title}</h2>
        </div>""", unsafe_allow_html=True)
    with c2:
        if st.button("🏠 홈", key="nav_home"):
            st.switch_page(home)
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

def kpi_card(label, value, color_class="", delay=0):
    """KPI 카드 HTML 컴포넌트"""
    return f"""
    <div class="kpi-card fade-in-delay-{delay}" style="animation-delay:{delay*0.1}s;">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value {color_class}">{value}</div>
    </div>"""

def section_header(title, badge=""):
    badge_html = f'<span class="section-badge">{badge}</span>' if badge else ""
    st.markdown(f"""
    <div class="section-header fade-in">
        <span class="section-title">{title}</span>
        {badge_html}
    </div>""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 5. 페이지별 함수
# -----------------------------------------------------------------------------

def page_home():
    apply_theme_style("home")

    left_col, right_col = st.columns([1.2, 4])
    with left_col:
        st.markdown("<div style='height: 28vh;'></div>", unsafe_allow_html=True)
        if st.button("📊 회원 전체 현황", key="btn_status"):
            st.switch_page(status)
        if st.button("👤 회원 개인 현황", key="btn_personal"):
            st.switch_page(personal)
        if st.button("📜 회칙 확인", key="btn_rules"):
            st.switch_page(rules)

    st.markdown('<div class="footer-credit">© 2026 GS Kim. All rights reserved.</div>', unsafe_allow_html=True)


def page_personal():
    apply_theme_style("sub")
    render_header_nav("🔒 회원 개인 현황")

    spacer_left, col_center, spacer_right = st.columns([1, 2, 1])
    with col_center:
        st.markdown("""
        <div class="login-guide-box">
            <h3 style="margin-top:0; color:#FFD700 !important; font-size:1.1rem;">🔑 아이디 확인</h3>
            <p style="font-size:1rem; line-height:1.6; margin-bottom:6px;">
                본인의 이메일 아이디 중 <b>아이디만</b> 입력해주세요.
            </p>
            <p style="font-size:0.88rem; color:#999 !important;">
                (예: "abc123@nate.com" → <b class="highlight">abc123</b>)
            </p>
        </div>
        """, unsafe_allow_html=True)
        user_id_input = st.text_input("아이디 입력", placeholder="아이디를 입력하세요", label_visibility="collapsed")

    if user_id_input:
        df_members = load_data("members")
        df_ledger = load_data("ledger")

        target_col = '아이디' if '아이디' in df_members.columns else '비밀번호'
        user_info = df_members[df_members[target_col].astype(str).str.lower() == str(user_id_input).lower()]

        if not user_info.empty:
            user = user_info.iloc[0]
            user_name = user['성명']

            today_date, months_passed = get_dues_calc_info()
            total_due_target = 100000 + (months_passed * 30000)

            my_deposit = 0; my_condolence_amt = 0; my_wreath_amt = 0
            if not df_ledger.empty and '금액' in df_ledger.columns:
                df_ledger['금액'] = df_ledger['금액'].apply(safe_int)
                my_deposit = df_ledger[(df_ledger['구분'] == '입금') & (df_ledger['내용'] == user_name)]['금액'].sum()
                my_condolence_amt = df_ledger[(df_ledger['구분'] == '출금') & (df_ledger['분류'] == '상조금') & (df_ledger['내용'] == user_name)]['금액'].sum()
                my_wreath_amt = df_ledger[(df_ledger['구분'] == '출금') & (df_ledger['분류'] == '근조화환') & (df_ledger['내용'] == user_name)]['금액'].sum()

            unpaid = total_due_target - my_deposit
            condolence_count = int(my_condolence_amt / 1000000) if my_condolence_amt > 0 else 0
            pay_rate = min((my_deposit / total_due_target * 100) if total_due_target > 0 else 0, 100)

            # ── 환영 배너 ──
            st.markdown(f"""
            <div class="fade-in" style="
                background: linear-gradient(135deg, rgba(255,204,0,0.1), rgba(255,204,0,0.05));
                border: 1px solid rgba(255,204,0,0.25);
                border-radius: 16px; padding: 16px 20px; margin: 12px 0 20px 0;
                display: flex; align-items: center; gap: 12px;">
                <span style="font-size:1.8rem;">👋</span>
                <div>
                    <div style="font-size:1.15rem; font-weight:700; color:#FFD700 !important;">
                        환영합니다, {user_name} ({user['직책']})님!
                    </div>
                    <div style="font-size:0.82rem; color:#888 !important; margin-top:2px;">
                        가입일자: {user['가입일자']}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # ── KPI 카드 4개 ──
            k1, k2, k3, k4 = st.columns(4)
            status_color = "green" if unpaid <= 0 else ("yellow" if pay_rate >= 60 else "red")
            status_icon  = "✅" if unpaid <= 0 else ("⚠️" if pay_rate >= 60 else "🔴")
            with k1: st.markdown(kpi_card("납부해야 할 금액", f"{format_comma(total_due_target)}원", "", 1), unsafe_allow_html=True)
            with k2: st.markdown(kpi_card("납부한 금액", f"{format_comma(my_deposit)}원", "green" if my_deposit >= total_due_target else "yellow", 2), unsafe_allow_html=True)
            with k3: st.markdown(kpi_card("미납 / 선납", f"{format_comma(abs(unpaid))}원", status_color, 3), unsafe_allow_html=True)
            with k4: st.markdown(kpi_card("조의 횟수", f"{condolence_count}회", "gold", 4), unsafe_allow_html=True)

            st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

            # ── 납부율 게이지 차트 ──
            col_gauge, col_info = st.columns([1, 1])
            with col_gauge:
                section_header("📈 납부율 현황")
                fig_gauge = make_gauge_chart(my_deposit, total_due_target, f"{user_name}님의 납부율")
                st.plotly_chart(fig_gauge, use_container_width=True, config={'displayModeBar': False})

            with col_info:
                section_header("💳 수령 내역")
                st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
                rec1, rec2 = st.columns(2)
                with rec1:
                    st.markdown(kpi_card("조의금 수령", f"{format_comma(my_condolence_amt)}원", "gold", 1), unsafe_allow_html=True)
                with rec2:
                    st.markdown(kpi_card("근조화환 수령", f"{format_comma(my_wreath_amt)}원", "gold", 2), unsafe_allow_html=True)

                st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
                prev_month = today_date - relativedelta(months=1)
                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.07);
                     border-radius: 12px; padding: 14px 18px; font-size: 0.85rem; color: #888 !important; line-height: 1.8;">
                    📅 기준월: <b style="color:#ccc!important;">{prev_month.strftime('%Y년 %m월')}</b><br>
                    📌 납부율: <b style="color:{'#4CAF50' if pay_rate >= 100 else ('#FFC107' if pay_rate >= 60 else '#FF5252')} !important;">
                        {pay_rate:.1f}%</b><br>
                    {status_icon} 상태: <b style="color:#fff!important;">
                        {'완납' if unpaid == 0 else ('선납 ' + format_comma(abs(unpaid)) + '원' if unpaid < 0 else '미납 ' + format_comma(abs(unpaid)) + '원')}
                    </b>
                </div>
                """, unsafe_allow_html=True)

        else:
            with col_center:
                st.error("일치하는 아이디가 없습니다. 다시 확인해주세요.")


def page_all_status():
    apply_theme_style("sub")
    render_header_nav("📊 회원 전체 현황")

    df_members = load_data("members")
    df_ledger  = load_data("ledger")
    df_assets  = load_data("assets")

    if not df_ledger.empty:
        for col in ['구분', '분류']:
            if col in df_ledger.columns: df_ledger[col] = df_ledger[col].astype(str).str.strip()
        if '금액' in df_ledger.columns: df_ledger['금액'] = df_ledger['금액'].apply(safe_int)

    # 자산 컬럼 자동 탐지
    asset_name_col = None; asset_amount_col = None
    if not df_assets.empty:
        for col in ['항목', '자산명', '자산', '계좌명', '구분', '내용', 'Asset']:
            if col in df_assets.columns: asset_name_col = col; break
        for col in ['금액', '잔액', '평가액', '자산금액', 'Amount']:
            if col in df_assets.columns: asset_amount_col = col; break
        if asset_amount_col: df_assets[asset_amount_col] = df_assets[asset_amount_col].apply(safe_int)

    _, months_passed = get_dues_calc_info()
    total_due_per_person = 100000 + (months_passed * 30000)

    tab1, tab2, tab3 = st.tabs(["📋 분석적 검토", "🏦 자산 현황", "📈 이자 분석"])

    # ──────────────── TAB 1: 분석적 검토 ────────────────
    with tab1:
        total_paid_sum = 0
        df_analysis = pd.DataFrame()

        if not df_members.empty and not df_ledger.empty:
            rows = []
            for _, row in df_members.iterrows():
                name = row['성명']
                paid = df_ledger[(df_ledger['구분'] == '입금') & (df_ledger['내용'] == name)]['금액'].sum() if '금액' in df_ledger.columns else 0
                unpaid = total_due_per_person - paid
                rows.append({
                    "회원명": name,
                    "A.납부할금액": total_due_per_person,
                    "B.납부한금액": paid,
                    "차이금액(=A-B)": unpaid,
                    "상태": "미납" if unpaid > 0 else ("선납" if unpaid < 0 else "완납"),
                })
            df_analysis = pd.DataFrame(rows)
            total_paid_sum = df_analysis['B.납부한금액'].sum()
            total_diff     = df_analysis['차이금액(=A-B)'].sum()

        # ── 상단 KPI 요약 ──
        if not df_analysis.empty:
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            k1, k2, k3, k4 = st.columns(4)
            total_members   = len(df_analysis)
            complete_count = (df_analysis['상태'].isin(['완납', '선납'])).sum()
            unpaid_count    = (df_analysis['상태'] == '미납').sum()
            overall_rate    = (total_paid_sum / (total_due_per_person * total_members) * 100) if total_members > 0 else 0

            with k1: st.markdown(kpi_card("전체 회원", f"{total_members}명", ""), unsafe_allow_html=True)
            with k2: st.markdown(kpi_card("완납 회원", f"{complete_count}명", "green"), unsafe_allow_html=True)
            with k3: st.markdown(kpi_card("미납 회원", f"{unpaid_count}명", "red" if unpaid_count > 0 else "green"), unsafe_allow_html=True)
            with k4: st.markdown(kpi_card("전체 납부율", f"{overall_rate:.1f}%", "green" if overall_rate >= 90 else "yellow"), unsafe_allow_html=True)

            st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

        # ── 차트: 회원별 납부율 + 전체 입금 파이 ──
        if not df_analysis.empty:
            col_bar, col_pie = st.columns([3, 2])
            with col_bar:
                section_header("회원별 납부율", f"합계 {format_comma(total_paid_sum)}원")
                fig_bar = make_payment_bar_chart(df_analysis)
                st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False})

            with col_pie:
                section_header("납부 현황 구성")
                paid_total_sum   = df_analysis['B.납부한금액'].sum()
                unpaid_total_sum = df_analysis['차이금액(=A-B)'].clip(lower=0).sum()
                if paid_total_sum + unpaid_total_sum > 0:
                    fig_pie = make_donut_chart(
                        ['납부완료', '미납잔액'],
                        [paid_total_sum, unpaid_total_sum],
                        "전체 납부 현황"
                    )
                    st.plotly_chart(fig_pie, use_container_width=True, config={'displayModeBar': False})

        st.divider()

        # ── 상세 테이블 ──
        section_header("1. 전체 입금 내역 분석")
        if not df_analysis.empty:
            total_row = pd.DataFrame([{
                "회원명": "합계",
                "A.납부할금액": df_analysis['A.납부할금액'].sum(),
                "B.납부한금액": total_paid_sum,
                "차이금액(=A-B)": df_analysis['차이금액(=A-B)'].sum(),
                "상태": "-"
            }])
            df_disp = pd.concat([df_analysis, total_row], ignore_index=True)
            for col in ["A.납부할금액", "B.납부한금액", "차이금액(=A-B)"]:
                df_disp[col] = df_disp[col].apply(format_comma)
            st.dataframe(df_disp, use_container_width=True, hide_index=True)

        st.divider()

        # ── 지출 분석 ──
        exp_total = 0
        if '금액' in df_ledger.columns:
            exp_c = df_ledger[(df_ledger['구분'] == '출금') & (df_ledger['분류'] == '상조금')]['금액'].sum()
            exp_w = df_ledger[(df_ledger['구분'] == '출금') & (df_ledger['분류'] == '근조화환')]['금액'].sum()
            exp_m = df_ledger[(df_ledger['구분'] == '출금') & (df_ledger['분류'] == '회의비외')]['금액'].sum()
            exp_s = df_ledger[(df_ledger['구분'] == '출금') & (df_ledger['분류'] == '적금')]['금액'].sum()
            exp_total = exp_c + exp_w + exp_m + exp_s

            col_exp_table, col_exp_chart = st.columns([3, 2])
            with col_exp_table:
                section_header("2. 회비통장 지출액 분석", f"합계 {format_comma(exp_total)}원")
                df_exp = pd.DataFrame({
                    "지출 항목": ["(1) 조의금", "(2) 근조화환", "(3) 회의비등", "(4) 적금", "합계"],
                    "금액": [format_comma(x) for x in [exp_c, exp_w, exp_m, exp_s, exp_total]],
                    "내용": ["건당 100만원", "건당 10만원", "식대/소모품", "적금원금", ""]
                })
                st.dataframe(df_exp, use_container_width=True, hide_index=True)

            with col_exp_chart:
                section_header("지출 구성")
                labels = ['조의금', '근조화환', '회의비등', '적금']
                values = [exp_c, exp_w, exp_m, exp_s]
                valid = [(l, v) for l, v in zip(labels, values) if v > 0]
                if valid:
                    lv, vv = zip(*valid)
                    st.plotly_chart(make_expense_pie_chart(list(lv), list(vv)),
                                    use_container_width=True, config={'displayModeBar': False})

        st.divider()

        # ── 분석적 검토 ──
        real_balance = 0
        if asset_amount_col and asset_name_col:
            try:
                mask = df_assets[asset_name_col].str.contains('회비통장', na=False)
                if mask.any(): real_balance = df_assets[mask][asset_amount_col].iloc[0]
            except: pass

        val_a = total_paid_sum - exp_total
        diff_final = real_balance - val_a

        section_header("3. 분석적 검토", f"차이: {format_comma(diff_final)}원")
        r1, r2, r3 = st.columns(3)
        with r1: st.markdown(kpi_card("실제 통장 잔액", f"{format_comma(real_balance)}원", "green"), unsafe_allow_html=True)
        with r2: st.markdown(kpi_card("장부상 잔액", f"{format_comma(val_a)}원", "yellow"), unsafe_allow_html=True)
        with r3: st.markdown(kpi_card("차이 (이자 등)", f"{format_comma(diff_final)}원", "gold"), unsafe_allow_html=True)

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div class="conclusion-box">
            💡 차이금액은 회비통장 이자수익 미반영분으로, 중요성 관점에서 회계상 문제 없음
        </div>""", unsafe_allow_html=True)

    # ──────────────── TAB 2: 자산 현황 ────────────────
    with tab2:
        if not df_assets.empty and asset_amount_col and asset_name_col:
            mask_total = ~df_assets[asset_name_col].astype(str).str.contains('합계', na=False)
            df_valid = df_assets[mask_total]
            total_asset = df_valid[asset_amount_col].sum()

            section_header("보유 자산 현황", f"총 {format_comma(total_asset)}원")

            col_tbl, col_chart = st.columns([3, 2])
            with col_tbl:
                df_disp = df_assets.copy()
                df_disp[asset_amount_col] = df_disp[asset_amount_col].apply(format_comma)
                df_disp = df_disp.astype(str).replace({'None': '', 'nan': '', '0': '', '0.0': ''}, regex=False)
                st.dataframe(df_disp, use_container_width=True, hide_index=True)
                st.metric("총 자산", f"{format_comma(total_asset)} 원")

            with col_chart:
                section_header("자산 구성")
                labels = df_valid[asset_name_col].tolist()
                values = df_valid[asset_amount_col].tolist()
                if labels and values:
                    st.plotly_chart(make_donut_chart(labels, values, "자산 구성"),
                                    use_container_width=True, config={'displayModeBar': False})
        else:
            st.warning("자산 데이터를 불러오지 못했습니다.")

    # ──────────────── TAB 3: 이자 분석 ────────────────
    with tab3:
        if not df_ledger.empty and not df_assets.empty and asset_amount_col and asset_name_col and '금액' in df_ledger.columns:
            target_ledger = df_ledger[df_ledger['분류'] == '적금'].copy()
            principal_sum = target_ledger['금액'].sum()

            target_assets = df_assets[df_assets[asset_name_col].str.contains('적금', na=False)].copy()
            current_val_sum = target_assets[asset_amount_col].sum()
            interest = current_val_sum - principal_sum

            # KPI 카드 3개
            p1, p2, p3 = st.columns(3)
            with p1: st.markdown(kpi_card("📥 적금 원금", f"{format_comma(principal_sum)}원", ""), unsafe_allow_html=True)
            with p2: st.markdown(kpi_card("💰 현재 평가액", f"{format_comma(current_val_sum)}원", "green"), unsafe_allow_html=True)
            with p3: st.markdown(kpi_card("🌱 누적 이자", f"{format_comma(interest)}원", "gold"), unsafe_allow_html=True)

            st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

            # 이자 강조 박스
            st.markdown(f"""
            <div class="interest-box fade-in">
                💰 누적 이자 발생액 &nbsp; {format_comma(interest)} 원
            </div>""", unsafe_allow_html=True)

            st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

            # 원금 vs 평가액 차트
            col_chart2, col_tbl2 = st.columns([1, 1])
            with col_chart2:
                section_header("원금 vs 평가액 비교")
                fig_bar2 = make_interest_timeline(principal_sum, current_val_sum)
                st.plotly_chart(fig_bar2, use_container_width=True, config={'displayModeBar': False})

            with col_tbl2:
                section_header("적금 통장 상세")
                bank_col = next((c for c in ['은행', 'Bank', '금융기관', '은행명'] if c in df_assets.columns), None)
                df_s = pd.DataFrame({
                    '구분': target_assets[asset_name_col].values,
                    '은행': target_assets[bank_col].values if bank_col else ['-'] * len(target_assets),
                    '잔액(원)': [format_comma(v) for v in target_assets[asset_amount_col].values],
                })
                st.dataframe(df_s, use_container_width=True, hide_index=True)

            st.divider()
            st.markdown("""
            <div class="conclusion-box">
                🏆 회비는 매우 투명하게 관리되고 있으며, 설명 불가한 입출금 내역 無. <br>
                이자 수익이 꾸준히 누적되어 매우 건실한 상태로 평가됨.
            </div>""", unsafe_allow_html=True)


def page_rules():
    apply_theme_style("sub")
    render_header_nav("📜 회칙 및 규정")
    df_rules = load_data("rules")
    search_rule = st.text_input("🔍 규정 검색", placeholder="검색어를 입력하세요")

    if not df_rules.empty:
        if search_rule:
            df_rules = df_rules[
                df_rules['내용'].str.contains(search_rule, na=False) |
                df_rules['조항'].str.contains(search_rule, na=False)
            ]
        for _, row in df_rules.iterrows():
            article = row.get('조항', '')
            title   = row.get('제목', row.get('항목', ''))
            header_text = f"{article} ({title})" if title and str(title).lower() != 'nan' else article
            st.markdown(f"""
            <div class="fade-in" style="
                background: rgba(255,255,255,0.03);
                border: 1px solid rgba(255,255,255,0.07);
                border-left: 3px solid rgba(255,204,0,0.5);
                border-radius: 10px;
                padding: 14px 18px;
                margin-bottom: 10px;">
                <div style="font-weight:700; font-size:1rem; color:#FFD700 !important; margin-bottom:6px;">
                    {header_text}
                </div>
                <div style="color:#d0d0d0 !important; font-size:0.9rem; line-height:1.7;">
                    {row.get('내용', '-')}
                </div>
            </div>""", unsafe_allow_html=True)
    else:
        st.info("회칙 데이터를 불러오는 중입니다.")

# -----------------------------------------------------------------------------
# 6. 네비게이션
# -----------------------------------------------------------------------------
home     = st.Page(page_home,       title="홈",        url_path="home",     default=True)
status   = st.Page(page_all_status, title="회원전체현황", url_path="status")
personal = st.Page(page_personal,   title="회원개인현황", url_path="personal")
rules    = st.Page(page_rules,      title="회칙",       url_path="rules")

pg = st.navigation([home, status, personal, rules], position="hidden")
pg.run()
