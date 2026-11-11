import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from dateutil.relativedelta import relativedelta
import base64
from html import escape
import streamlit.components.v1 as components

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
# 2. 색상 (먹과 한지)
# -----------------------------------------------------------------------------
INK      = "#14130f"   # 바탕
PAPER    = "#1d1b16"   # 카드
HANJI    = "#ece3cf"   # 글자
MUTED    = "#9f9684"   # 보조 글자
GOLD     = "#d8b86a"   # 빛바랜 금
CELADON  = "#8fb3a3"   # 청자 녹 (완납)
SEAL     = "#a63a2b"   # 낙관 적 (미납)
SEAL_LT  = "#d9826f"

# -----------------------------------------------------------------------------
# 3. 공통 함수
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
# 4. Plotly 차트
# -----------------------------------------------------------------------------
PLOTLY_LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color=HANJI, family='Noto Sans KR, sans-serif'),
    margin=dict(l=10, r=10, t=40, b=10),
    dragmode=False,  # 휴대폰에서 터치·드래그로 확대되지 않도록
)

def make_gauge_chart(paid, total, title="납부율"):
    rate = min(round((paid / total) * 100, 1) if total > 0 else 0, 100)
    bar_color = CELADON if rate >= 100 else (GOLD if rate >= 60 else SEAL_LT)
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=rate,
        number={'suffix': '%', 'font': {'size': 38, 'color': HANJI, 'family': 'Noto Serif KR, serif'}},
        title={'text': title, 'font': {'size': 13, 'color': MUTED}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': '#4a4639', 'tickfont': {'color': MUTED, 'size': 10}},
            'bar': {'color': bar_color, 'thickness': 0.28},
            'bgcolor': 'rgba(236,227,207,0.06)',
            'borderwidth': 0,
            'threshold': {'line': {'color': GOLD, 'width': 2}, 'thickness': 0.8, 'value': 100}
        }
    ))
    fig.update_layout(**PLOTLY_LAYOUT, height=220)
    return fig

def make_donut_chart(labels, values, title="구성"):
    colors = [CELADON, SEAL, GOLD, '#7f9bb3', '#b39a7f', '#a89fb3']
    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.62,
        marker=dict(colors=colors[:len(labels)], line=dict(color=INK, width=2)),
        textinfo='percent', textfont=dict(size=12, color=HANJI),
        hovertemplate='<b>%{label}</b><br>%{value:,.0f}원<br>%{percent}<extra></extra>',
    ))
    fig.update_layout(
        **PLOTLY_LAYOUT, height=300,
        title=dict(text=title, font=dict(size=13, color=MUTED), x=0.5),
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5, font=dict(color=HANJI, size=11)),
    )
    return fig

def make_payment_bar_chart(df_analysis):
    df_plot = df_analysis[df_analysis['회원명'] != '합계'].copy()
    df_plot['납부율'] = (df_plot['B.납부한금액'] / df_plot['A.납부할금액'] * 100).clip(0, 100)
    df_plot = df_plot.sort_values('납부율', ascending=True)
    colors = [CELADON if r >= 100 else (GOLD if r >= 60 else SEAL_LT) for r in df_plot['납부율']]
    fig = go.Figure(go.Bar(
        y=df_plot['회원명'], x=df_plot['납부율'], orientation='h',
        marker=dict(color=colors),
        text=[f"{r:.1f}%" for r in df_plot['납부율']], textposition='outside',
        textfont=dict(color=MUTED, size=11),
        hovertemplate='<b>%{y}</b><br>납부율: %{x:.1f}%<extra></extra>',
    ))
    fig.add_vline(x=100, line_dash="dot", line_color="rgba(216,184,106,0.5)", line_width=1)
    fig.update_layout(
        **PLOTLY_LAYOUT,
        height=max(250, len(df_plot) * 34 + 60),
        xaxis=dict(range=[0, 118], fixedrange=True, ticksuffix='%', gridcolor='rgba(236,227,207,0.06)', tickfont=dict(color=MUTED)),
        yaxis=dict(fixedrange=True, gridcolor='rgba(0,0,0,0)', tickfont=dict(color=HANJI, size=12)),
        bargap=0.35,
    )
    return fig

def make_expense_pie_chart(labels, values):
    return make_donut_chart(labels, values, "지출 구성")

def make_interest_timeline(principal, current):
    fig = go.Figure()
    fig.add_trace(go.Bar(name='원금', x=['적금'], y=[principal], marker_color='#7f9bb3',
                         text=[f"{format_comma(principal)}원"], textposition='outside', textfont=dict(color=HANJI)))
    fig.add_trace(go.Bar(name='평가액', x=['적금'], y=[current], marker_color=CELADON,
                         text=[f"{format_comma(current)}원"], textposition='outside', textfont=dict(color=HANJI)))
    fig.update_layout(
        **PLOTLY_LAYOUT, height=280, barmode='group',
        yaxis=dict(fixedrange=True, gridcolor='rgba(236,227,207,0.06)', tickfont=dict(color=MUTED)),
        xaxis=dict(fixedrange=True, tickfont=dict(color=HANJI)),
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5, font=dict(color=HANJI)),
        bargap=0.4, bargroupgap=0.1,
    )
    return fig

# -----------------------------------------------------------------------------
# 5. CSS
# -----------------------------------------------------------------------------
COMMON_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&family=Noto+Serif+KR:wght@500;700;900&display=swap');

.stApp, .stMarkdown, p, span, div, label {{
    color: {HANJI} !important;
    font-family: 'Noto Sans KR', sans-serif !important;
}}
h1, h2, h3, h4, .serif {{ font-family: 'Noto Serif KR', serif !important; }}

@keyframes fadeSlideUp {{
    from {{ opacity: 0; transform: translateY(14px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}
.fade-in {{ animation: fadeSlideUp 0.6s ease forwards; }}

/* ── 헤더 ── */
.page-head {{
    display: flex; align-items: flex-end; gap: 16px;
    padding: 6px 0 16px 0; margin-bottom: 18px;
    border-bottom: 1px solid rgba(216,184,106,0.35);
}}
.seal {{
    flex: none; width: 42px; height: 42px; background: {SEAL};
    display: flex; align-items: center; justify-content: center;
    font-family: 'Noto Serif KR', serif !important; font-size: 13px; font-weight: 700;
    color: #f3ead8 !important; letter-spacing: 1px;
}}
.page-eyebrow {{ font-size: 11px; letter-spacing: 4px; color: {MUTED} !important; margin-bottom: 4px; }}
.page-title {{ font-family: 'Noto Serif KR', serif !important; font-size: 1.7rem; font-weight: 700; line-height: 1.1; margin: 0; }}

/* ── KPI 카드 ── */
.kpi-card {{
    background: {PAPER};
    border: 1px solid rgba(236,227,207,0.10);
    border-top: 2px solid rgba(216,184,106,0.6);
    padding: 20px 22px 16px 22px;
    animation: fadeSlideUp 0.5s ease forwards;
    margin-bottom: 12px;
    container-type: inline-size;
}}
.kpi-card.red   {{ border-top-color: rgba(166,58,43,0.8); }}
.kpi-card.green {{ border-top-color: rgba(143,179,163,0.7); }}
.kpi-label {{ font-size: 0.72rem; letter-spacing: 3px; color: {MUTED} !important; margin-bottom: 10px; }}
.kpi-value {{
    font-family: 'Noto Serif KR', serif !important;
    font-size: clamp(0.95rem, 10cqi, 1.9rem); font-weight: 700; line-height: 1; color: {HANJI} !important;
    white-space: nowrap;
}}
.kpi-value.green  {{ color: {CELADON} !important; }}
.kpi-value.red    {{ color: {SEAL_LT} !important; }}
.kpi-value.yellow {{ color: {GOLD} !important; }}
.kpi-value.gold   {{ color: {GOLD} !important; }}
.kpi-unit {{ font-size: 0.45em; color: {MUTED} !important; margin-left: 3px; }}

/* ── 버튼 ── */
.stButton > button {{
    width: 100%; height: 3.6rem;
    border-radius: 0;
    font-family: 'Noto Serif KR', serif !important;
    font-size: 1.05rem; font-weight: 700;
    background: rgba(20,19,15,0.78);
    color: {HANJI} !important;
    border: 1px solid rgba(216,184,106,0.45);
    transition: all 0.25s ease;
    margin-bottom: 10px;
}}
.stButton > button:hover {{
    background: rgba(216,184,106,0.12);
    border-color: {GOLD};
    color: {GOLD} !important;
}}

/* ── 섹션 헤더 ── */
.section-header {{
    display: flex; align-items: baseline; justify-content: space-between; gap: 10px;
    padding: 10px 0 10px 0; border-bottom: 1px solid rgba(236,227,207,0.12); margin-bottom: 14px;
}}
.section-title {{ font-family: 'Noto Serif KR', serif !important; font-size: 1.1rem; font-weight: 700; }}
.section-badge {{ font-size: 0.8rem; color: {MUTED} !important; }}
.section-badge b {{ font-family: 'Noto Serif KR', serif !important; color: {GOLD} !important; }}

/* ── 결론 박스 ── */
.conclusion-box {{
    display: flex; gap: 14px; align-items: flex-start;
    background: rgba(166,58,43,0.08);
    border: 1px solid rgba(166,58,43,0.3);
    padding: 16px 20px; margin-top: 12px;
    font-family: 'Noto Serif KR', serif !important;
    font-size: 0.98rem; line-height: 1.75;
    animation: fadeSlideUp 0.5s ease forwards;
}}
.conclusion-box .seal {{ width: 30px; height: 30px; font-size: 11px; }}

/* ── 이자 강조 ── */
.interest-box {{
    text-align: center; padding: 22px;
    background: {PAPER};
    border: 1px solid rgba(143,179,163,0.35);
}}
.interest-box .lbl {{ font-size: 0.72rem; letter-spacing: 3px; color: {MUTED} !important; margin-bottom: 8px; }}
.interest-box .val {{ font-family: 'Noto Serif KR', serif !important; font-size: clamp(1.2rem, 8vw, 2rem); white-space: nowrap; font-weight: 700; color: {CELADON} !important; }}

/* ── 로그인 안내 ── */
.login-guide-box {{
    background: {PAPER};
    border: 1px solid rgba(216,184,106,0.35);
    padding: 22px; text-align: center; margin-bottom: 18px;
    animation: fadeSlideUp 0.5s ease forwards;
}}
.highlight {{ color: {GOLD} !important; font-weight: 700; }}

/* ── 환영 배너 ── */
.welcome {{
    display: flex; align-items: center; justify-content: space-between;
    background: {PAPER}; border: 1px solid rgba(216,184,106,0.35);
    padding: 16px 20px; margin: 10px 0 18px 0;
    animation: fadeSlideUp 0.5s ease forwards;
}}
.welcome .name {{ font-family: 'Noto Serif KR', serif !important; font-size: 1.25rem; font-weight: 700; }}
.welcome .role {{ font-size: 0.85rem; color: {GOLD} !important; font-weight: 500; margin-left: 6px; }}
.welcome .sub {{ font-size: 0.78rem; color: {MUTED} !important; margin-top: 2px; }}

/* ── 입력창 ── */
.stTextInput input {{
    background: {PAPER} !important;
    color: {HANJI} !important;
    border: 1px solid rgba(236,227,207,0.18) !important;
    border-radius: 0 !important;
    padding: 10px 14px !important;
}}
.stTextInput input:focus {{ border-color: {GOLD} !important; box-shadow: none !important; }}

/* ── 탭 ── */
.stTabs [data-baseweb="tab-list"] {{ background: transparent !important; gap: 4px !important; border-bottom: 1px solid rgba(236,227,207,0.12) !important; }}
.stTabs [data-baseweb="tab"] {{
    font-family: 'Noto Serif KR', serif !important; font-weight: 700 !important;
    color: {MUTED} !important; padding: 10px 20px !important; border-radius: 0 !important;
}}
.stTabs [aria-selected="true"] {{ color: {HANJI} !important; border-bottom: 2px solid {GOLD} !important; }}
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] {{ display: none !important; }}

/* ── 데이터프레임 ── */
[data-testid="stDataFrame"] {{ background: {PAPER}; border: 1px solid rgba(236,227,207,0.10); }}
[data-testid="stDataFrame"] div[role="columnheader"] {{
    background: rgba(216,184,106,0.06) !important;
    color: {MUTED} !important; font-size: 0.74rem !important; letter-spacing: 2px;
}}
[data-testid="stDataFrame"] div[role="gridcell"] {{ color: {HANJI} !important; font-size: 0.88rem !important; }}

[data-testid="metric-container"] {{ background: {PAPER}; border: 1px solid rgba(236,227,207,0.10); padding: 12px 16px !important; }}
[data-testid="stMetricLabel"] {{ color: {MUTED} !important; font-size: 0.75rem !important; letter-spacing: 2px; }}
[data-testid="stMetricValue"] {{ font-family: 'Noto Serif KR', serif !important; color: {HANJI} !important; font-weight: 700 !important; }}

hr {{ border-color: rgba(236,227,207,0.10) !important; }}

/* ── 정돈 표 (A안) ── */
.ga-tbl-wrap {{ overflow-x: auto; margin-bottom: 8px; }}
.ga-tbl {{ width: 100%; border-collapse: collapse; font-variant-numeric: tabular-nums; font-size: 0.88rem; }}
.ga-tbl th {{
    font-weight: 400; font-size: 0.72rem; letter-spacing: 1px; color: {MUTED} !important; text-align: left;
    padding: 9px 8px; background: rgba(216,184,106,0.07); border-bottom: 1px solid rgba(216,184,106,0.35); white-space: nowrap;
}}
.ga-tbl td {{ padding: 10px 8px; border-bottom: 1px solid rgba(236,227,207,0.06); white-space: nowrap; }}
.ga-tbl th, .ga-tbl td {{ border-left: none !important; border-right: none !important; }}
.ga-tbl .n {{ text-align: right; }}
.ga-tbl tr.total td {{ border-top: 1px solid rgba(216,184,106,0.55); border-bottom: 0; font-family: 'Noto Serif KR', serif !important; font-weight: 700; }}
.ga-tbl td.hl {{ outline: 1px solid {GOLD}; outline-offset: -3px; color: {GOLD} !important; }}
.dim {{ color: {MUTED} !important; }}
.badge {{ display: inline-block; padding: 1px 8px; font-size: 0.72rem; font-weight: 500; border: 1px solid transparent; }}
.badge.ok  {{ color: {CELADON} !important; background: rgba(143,179,163,0.12); border-color: rgba(143,179,163,0.35); }}
.badge.pre {{ color: {GOLD} !important; background: rgba(216,184,106,0.10); border-color: rgba(216,184,106,0.35); }}
.badge.due {{ color: {SEAL_LT} !important; background: rgba(166,58,43,0.16); border-color: rgba(166,58,43,0.5); }}

/* ── 납부율 요약 (A안) ── */
.ga-hero {{
    display: grid; grid-template-columns: auto 1fr; gap: 20px; align-items: center;
    background: {PAPER}; border-top: 2px solid {GOLD}; padding: 18px 20px; margin: 8px 0 16px 0;
}}
.ga-donut {{ position: relative; width: 128px; height: 128px; }}
.ga-donut svg {{ width: 128px; height: 128px; transform: rotate(-90deg); }}
.ga-donut .c {{ position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; }}
.ga-donut b {{ font-family: 'Noto Serif KR', serif !important; font-size: 1.7rem; line-height: 1; }}
.ga-donut small {{ font-size: 0.68rem; color: {MUTED} !important; margin-top: 4px; letter-spacing: 1px; }}
.ga-stats {{ display: flex; flex-direction: column; gap: 8px; min-width: 0; container-type: inline-size; }}
.ga-stat {{ display: flex; justify-content: space-between; gap: 8px; font-size: clamp(0.7rem, 6.5cqi, 0.88rem); white-space: nowrap; color: {MUTED} !important; border-bottom: 1px solid rgba(236,227,207,0.06); padding-bottom: 7px; }}
.ga-stat:last-child {{ border-bottom: 0; padding-bottom: 0; }}
.ga-stat b {{ font-family: 'Noto Serif KR', serif !important; font-weight: 700; color: {HANJI} !important; }}
.ga-stat b.warn {{ color: {SEAL_LT} !important; }}

/* ── 분석적 검토 목록 (A안) ── */
.ga-review {{ background: {PAPER}; padding: 16px 18px; display: flex; flex-direction: column; gap: 9px; container-type: inline-size; }}
.ga-row {{ display: flex; justify-content: space-between; gap: 8px; font-size: clamp(0.72rem, 4.4cqi, 0.9rem); white-space: nowrap; color: {MUTED} !important; }}
.ga-row b {{ font-family: 'Noto Serif KR', serif !important; font-variant-numeric: tabular-nums; color: {HANJI} !important; }}
.ga-row.sum {{ border-top: 1px solid rgba(216,184,106,0.4); padding-top: 9px; color: {HANJI} !important; }}
.ga-row.sum b {{ color: {GOLD} !important; font-size: 1.22em; }}
.ga-row.sub {{ padding-left: 14px; font-size: clamp(0.68rem, 4.1cqi, 0.84rem); }}

/* ── 회칙 ── */
.rule-card {{
    background: {PAPER}; border: 1px solid rgba(236,227,207,0.10);
    padding: 14px 18px; margin-bottom: 10px; animation: fadeSlideUp 0.5s ease forwards;
}}
.rule-head {{ font-family: 'Noto Serif KR', serif !important; font-weight: 700; color: {GOLD} !important; margin-bottom: 6px; }}
.rule-body {{ font-size: 0.9rem; line-height: 1.7; }}

/* ── 홈 ── */
.home-brand {{ display: flex; flex-direction: column; gap: 6px; margin-bottom: 26px; }}
.home-brand .eyebrow {{ font-size: 11px; letter-spacing: 4px; color: {MUTED} !important; }}
.home-brand .title {{ font-family: 'Noto Serif KR', serif !important; font-size: 1.9rem; font-weight: 700; line-height: 1.2; }}
.home-brand .rule {{ width: 36px; height: 1px; background: {GOLD}; margin-top: 6px; }}
.home-brand .sub {{ font-size: 12px; color: {MUTED} !important; }}

/* ── 모바일 ── */
@media only screen and (max-width: 600px) {{
    .stButton > button {{ height: 3.2rem !important; font-size: 0.95rem !important; }}
    .block-container {{ padding-left: 1rem !important; padding-right: 1rem !important; }}
    .kpi-value {{ font-size: clamp(0.9rem, 10cqi, 1.4rem) !important; }}
    .page-title {{ font-size: 1.35rem; }}
}}

.footer-credit {{
    position: fixed; top: 14px; left: 14px;
    color: rgba(236,227,207,0.45) !important; font-size: 0.72rem; letter-spacing: 1px;
    padding: 4px 10px; background: rgba(20,19,15,0.6); z-index: 1000000;
}}
</style>
"""

def apply_theme_style(page_type="sub"):
    st.markdown(COMMON_CSS, unsafe_allow_html=True)
    if page_type == 'home':
        bin_str = get_base64_of_bin_file('bg.jpg') or get_base64_of_bin_file('bg.png')
        # 영상 파일 없이 CSS만으로 움직임 (용량·데이터 사용량 증가 없음)
        st.markdown(f"""
        <style>
        .stApp {{ background: {INK} !important; isolation: isolate; }}
        .stApp::before {{
            content: ""; position: fixed; inset: -4%; z-index: -3; pointer-events: none;
            background: url("data:image/jpeg;base64,{bin_str}") 46% 40% / cover no-repeat;
            animation: homeReveal 2.8s ease-out both, homeDrift 38s ease-in-out 2.8s infinite alternate;
        }}
        .stApp::after {{
            content: ""; position: fixed; inset: 0; z-index: -2; pointer-events: none;
            background: linear-gradient(90deg, rgba(20,19,15,0.88) 0%, rgba(20,19,15,0.55) 45%, rgba(20,19,15,0.25) 100%);
        }}
        .home-mist {{
            position: fixed; inset: -20% -40%; z-index: -1; pointer-events: none; opacity: 0.55; mix-blend-mode: screen;
            background:
                radial-gradient(40% 18% at 20% 30%, rgba(236,227,207,0.10), transparent 70%),
                radial-gradient(35% 14% at 70% 20%, rgba(236,227,207,0.08), transparent 70%),
                radial-gradient(45% 20% at 50% 75%, rgba(236,227,207,0.06), transparent 70%);
            animation: homeMist 46s linear infinite;
        }}
        .home-flash {{
            position: fixed; inset: 0; z-index: -1; pointer-events: none; opacity: 0;
            background:
                radial-gradient(60% 50% at 75% 15%, rgba(236,227,207,0.55), transparent 70%),
                radial-gradient(90% 70% at 70% 20%, rgba(200,210,230,0.18), transparent 75%);
            animation: homeFlash 9s 3s infinite;
        }}
        .block-container {{ padding-top: 0rem; }}
        .home-brand .eyebrow {{ display: flex; align-items: center; gap: 10px; animation: homeUp 0.8s ease-out 1.1s both; }}
        .home-seal {{
            width: 30px; height: 30px; background: {SEAL}; color: #f3ead8 !important; display: flex; align-items: center; justify-content: center;
            font-family: 'Noto Serif KR', serif !important; font-size: 10px; font-weight: 700; letter-spacing: 0;
            animation: homeStamp 0.5s cubic-bezier(.2,1.6,.4,1) 2.4s both;
        }}
        .home-brand .title span {{ display: inline-block; animation: homeInk 1s ease-out both; }}
        .home-brand .rule {{ transform-origin: left; animation: homeLine 0.9s ease-out 2s both; }}
        .home-brand .sub {{ animation: homeUp 0.8s ease-out 2.2s both; }}
        .st-key-btn_status, .st-key-btn_personal, .st-key-btn_rules, .st-key-btn_history {{ animation: homeUp 0.7s ease-out both; }}
        .st-key-btn_status {{ animation-delay: 2.5s; }}
        .st-key-btn_personal {{ animation-delay: 2.62s; }}
        .st-key-btn_rules {{ animation-delay: 2.74s; }}
        .st-key-btn_history {{ animation-delay: 2.86s; }}
        @keyframes homeReveal {{ from {{ filter: blur(14px) grayscale(1) brightness(.25); transform: scale(1.10); }} to {{ filter: none; transform: scale(1.04); }} }}
        @keyframes homeDrift {{ from {{ transform: scale(1.04) translate(0,0); }} to {{ transform: scale(1.12) translate(-2.5%,-1.5%); }} }}
        @keyframes homeMist {{ from {{ transform: translateX(0); }} to {{ transform: translateX(-25%); }} }}
        @keyframes homeFlash {{ 0%,100% {{ opacity: 0; }} 1% {{ opacity: 1; }} 2% {{ opacity: .25; }} 3.5% {{ opacity: .95; }} 5% {{ opacity: .4; }} 7% {{ opacity: 0; }} }}
        @keyframes homeInk {{ from {{ opacity: 0; filter: blur(8px); transform: translateY(6px); }} to {{ opacity: 1; filter: none; transform: none; }} }}
        @keyframes homeLine {{ from {{ transform: scaleX(0); }} to {{ transform: scaleX(1); }} }}
        @keyframes homeUp {{ from {{ opacity: 0; transform: translateY(12px); }} to {{ opacity: 1; transform: none; }} }}
        @keyframes homeStamp {{ from {{ opacity: 0; transform: scale(1.8) rotate(-8deg); }} to {{ opacity: 1; transform: rotate(-4deg); }} }}
        @media only screen and (max-width: 640px) {{
            .stApp::after {{ background: linear-gradient(180deg, rgba(20,19,15,0.35) 0%, rgba(20,19,15,0.75) 55%, rgba(20,19,15,0.92) 100%); }}
        }}
        @media (prefers-reduced-motion: reduce) {{
            .stApp::before, .home-mist, .home-flash, .home-brand *, .st-key-btn_status, .st-key-btn_personal, .st-key-btn_rules, .st-key-btn_history {{ animation: none !important; }}
        }}
        </style>
        <div class="home-mist"></div><div class="home-flash"></div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"<style>.stApp {{ background: {INK} !important; }}</style>", unsafe_allow_html=True)

def render_header_nav(title, eyebrow="천비칠마 상조회", seal_text="相助"):
    c1, c2 = st.columns([8, 2])
    with c1:
        st.markdown(f"""
        <div class="page-head fade-in">
            <div class="seal">{seal_text}</div>
            <div>
                <div class="page-eyebrow">{eyebrow}</div>
                <h2 class="page-title">{title}</h2>
            </div>
        </div>""", unsafe_allow_html=True)
    with c2:
        if st.button("홈", key="nav_home"):
            st.switch_page(home)

def kpi_card(label, value, color_class="", unit=""):
    unit_html = f'<span class="kpi-unit">{unit}</span>' if unit else ""
    return f"""
    <div class="kpi-card {color_class}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value {color_class}">{value}{unit_html}</div>
    </div>"""

def html_table(headers, rows, num_cols=(), total=None, hl_col=None):
    # st.dataframe 대신 먹과 한지 톤 표. 값은 호출하는 쪽에서 포맷·escape 해서 넘김
    def td(i, v, tag='td', extra=''):
        c = (('n ' if i in num_cols else '') + extra).strip()
        return f'<{tag} class="{c}">{v}</{tag}>' if c else f'<{tag}>{v}</{tag}>'
    head = ''.join(td(i, h, 'th') for i, h in enumerate(headers))
    body = ''.join('<tr>' + ''.join(td(i, v) for i, v in enumerate(r)) + '</tr>' for r in rows)
    if total:
        body += '<tr class="total">' + ''.join(td(i, v, extra='hl' if i == hl_col else '') for i, v in enumerate(total)) + '</tr>'
    return f'<div class="ga-tbl-wrap"><table class="ga-tbl"><tr>{head}</tr>{body}</table></div>'

def signed_diff(d):
    # 납부액 - 기준금액: 부족분만 강조하고 0·초과분은 흐리게
    if d < 0: return f'−{format_comma(-d)}'
    return f'<span class="dim">{"+" + format_comma(d) if d > 0 else "0"}</span>'

def status_badge(s):
    return f'<span class="badge {dict(완납="ok", 선납="pre", 미납="due").get(s, "")}">{s}</span>'

def rate_hero(rate, total_members, complete_count, unpaid_count, unpaid_sum):
    circ = 2 * 3.14159265 * 56
    dash = circ * min(max(rate, 0), 100) / 100
    warn = ' class="warn"' if unpaid_count > 0 else ''
    return (f'<div class="ga-hero"><div class="ga-donut">'
            f'<svg viewBox="0 0 128 128"><circle cx="64" cy="64" r="56" fill="none" stroke="rgba(236,227,207,0.08)" stroke-width="11"/>'
            f'<circle cx="64" cy="64" r="56" fill="none" stroke="{CELADON}" stroke-width="11" stroke-dasharray="{dash:.2f} {circ:.2f}"/></svg>'
            f'<div class="c"><b>{rate:.1f}%</b><small>전체 납부율</small></div></div>'
            f'<div class="ga-stats">'
            f'<div class="ga-stat">전체 회원 <b>{total_members}명</b></div>'
            f'<div class="ga-stat">완납·선납 <b>{complete_count}명</b></div>'
            f'<div class="ga-stat">미납 <b{warn}>{unpaid_count}명</b></div>'
            f'<div class="ga-stat">미납 잔액 <b{warn}>{format_comma(unpaid_sum)}원</b></div>'
            f'</div></div>')

def section_header(title, badge=""):
    badge_html = f'<span class="section-badge">{badge}</span>' if badge else ""
    st.markdown(f"""
    <div class="section-header fade-in">
        <span class="section-title">{title}</span>
        {badge_html}
    </div>""", unsafe_allow_html=True)

def conclusion(text, seal_text="檢"):
    st.markdown(f"""
    <div class="conclusion-box">
        <div class="seal">{seal_text}</div>
        <div>{text}</div>
    </div>""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 6. 페이지
# -----------------------------------------------------------------------------

def page_home():
    apply_theme_style("home")

    left_col, right_col = st.columns([1.3, 4])
    with left_col:
        st.markdown("<div style='height: 18vh;'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div class="home-brand">
            <div class="eyebrow"><span class="home-seal">相助</span>SINCE 2020</div>
            <div class="title"><span style="animation-delay:1.3s">천</span><span style="animation-delay:1.42s">비</span><span style="animation-delay:1.54s">칠</span><span style="animation-delay:1.66s">마</span><br><span style="animation-delay:1.78s">상</span><span style="animation-delay:1.9s">조</span><span style="animation-delay:2.02s">회</span></div>
            <div class="rule"></div>
            <div class="sub">투명한 회비 장부</div>
        </div>""", unsafe_allow_html=True)
        if st.button("一 · 회원 전체 현황", key="btn_status"):
            st.switch_page(status)
        if st.button("二 · 회원 개인 현황", key="btn_personal"):
            st.switch_page(personal)
        if st.button("三 · 회칙 확인", key="btn_rules"):
            st.switch_page(rules)
        if st.button("四 · 탈회등 회원", key="btn_history"):
            st.switch_page(history)

    st.markdown('<div class="footer-credit">© 2026 GS Kim. All rights reserved.</div>', unsafe_allow_html=True)


def parse_date(value):
    # 시트 날짜가 "2023-05-31", "2023.05.31", "2023. 5. 31" 등 어떤 형식이어도 읽히도록
    s = str(value).strip().rstrip('.').replace('. ', '-').replace('.', '-')
    d = pd.to_datetime(s, errors='coerce')
    return None if pd.isna(d) else d.to_pydatetime()

def is_hist_member(df_members):
    # members 시트에 탈회일자가 적힌 회원 = 이력회원
    if '탈회일자' not in df_members.columns:
        return pd.Series(False, index=df_members.index)
    return df_members['탈회일자'].apply(parse_date).notna()

def render_member_detail(user_name, role, join_date, df_ledger, end_date=None):
    today_date, months_passed = get_dues_calc_info()
    ref_month = today_date - relativedelta(months=1)
    # 이력회원: 탈회일자가 속한 달까지만 회비 부과 (경과월수 공식은 동일)
    if end_date is not None and end_date < today_date:
        months_passed = max((end_date.year - 2020) * 12 + (end_date.month - 2) + 1, 0)
        ref_month = end_date
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

    st.markdown(f"""
    <div class="welcome">
        <div>
            <div style="font-size:0.78rem; color:#9f9684 !important;">환영합니다</div>
            <div><span class="name">{user_name}</span><span class="role">{role}</span></div>
            <div class="sub">가입일자 {join_date}{' · 탈회일자 ' + end_date.strftime('%Y-%m-%d') if end_date else ''}</div>
        </div>
        <div class="seal">{str(user_name)[0]}</div>
    </div>""", unsafe_allow_html=True)

    k1, k2, k3, k4 = st.columns(4)
    status_color = "green" if unpaid <= 0 else ("yellow" if pay_rate >= 60 else "red")
    with k1: st.markdown(kpi_card("납부할 금액", format_comma(total_due_target), "", "원"), unsafe_allow_html=True)
    with k2: st.markdown(kpi_card("납부한 금액", format_comma(my_deposit), "green" if my_deposit >= total_due_target else "yellow", "원"), unsafe_allow_html=True)
    with k3: st.markdown(kpi_card("미납 / 선납", format_comma(abs(unpaid)), status_color, "원"), unsafe_allow_html=True)
    with k4: st.markdown(kpi_card("조의 횟수", condolence_count, "gold", "회"), unsafe_allow_html=True)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    col_gauge, col_info = st.columns([1, 1])
    with col_gauge:
        section_header("나의 납부율")
        st.plotly_chart(make_gauge_chart(my_deposit, total_due_target, ""), use_container_width=True, config={'displayModeBar': False})

    with col_info:
        section_header("수령 내역")
        rec1, rec2 = st.columns(2)
        with rec1: st.markdown(kpi_card("조의금 수령", format_comma(my_condolence_amt), "gold", "원"), unsafe_allow_html=True)
        with rec2: st.markdown(kpi_card("근조화환 수령", format_comma(my_wreath_amt), "gold", "원"), unsafe_allow_html=True)

        status_txt = '완납' if unpaid == 0 else ('선납 ' + format_comma(abs(unpaid)) + '원' if unpaid < 0 else '미납 ' + format_comma(abs(unpaid)) + '원')
        st.markdown(f"""
        <div style="background:{PAPER}; border:1px solid rgba(236,227,207,0.10); padding:14px 18px; font-size:0.85rem; line-height:1.9;">
            <div style="display:flex; justify-content:space-between;"><span style="color:#9f9684 !important;">기준월</span><span class="serif">{ref_month.strftime('%Y년 %m월')}</span></div>
            <div style="display:flex; justify-content:space-between;"><span style="color:#9f9684 !important;">납부율</span><span class="serif">{pay_rate:.1f}%</span></div>
            <div style="display:flex; justify-content:space-between;"><span style="color:#9f9684 !important;">상태</span><span class="serif">{status_txt}</span></div>
        </div>
        """, unsafe_allow_html=True)


def page_personal():
    apply_theme_style("sub")
    render_header_nav("회원 개인 현황")

    spacer_left, col_center, spacer_right = st.columns([1, 2, 1])
    with col_center:
        st.markdown("""
        <div class="login-guide-box">
            <div class="serif" style="font-size:1.05rem; font-weight:700; margin-bottom:8px;">아이디 확인</div>
            <p style="font-size:0.95rem; line-height:1.6; margin-bottom:4px;">본인의 이메일 아이디 중 <b>아이디만</b> 입력해주세요.</p>
            <p style="font-size:0.85rem; color:#9f9684 !important; margin:0;">(예: "abc123@nate.com" → <b class="highlight">abc123</b>)</p>
        </div>
        """, unsafe_allow_html=True)
        user_id_input = st.text_input("아이디 입력", placeholder="아이디를 입력하세요", label_visibility="collapsed")

    if user_id_input:
        df_members = load_data("members")
        df_ledger = load_data("ledger")

        target_col = '아이디' if '아이디' in df_members.columns else '비밀번호'
        user_info = df_members[df_members[target_col].astype(str).str.lower() == str(user_id_input).lower()]
        user_info = user_info[~is_hist_member(user_info)]

        if not user_info.empty:
            user = user_info.iloc[0]
            user_name = user['성명']

            render_member_detail(user_name, user['직책'], user['가입일자'], df_ledger)
        else:
            with col_center:
                st.error("일치하는 아이디가 없습니다. 다시 확인해주세요.")


def page_all_status():
    apply_theme_style("sub")
    render_header_nav("회원 전체 현황")

    df_members = load_data("members")
    df_ledger  = load_data("ledger")
    df_assets  = load_data("assets")

    if not df_members.empty:
        df_members = df_members[~is_hist_member(df_members)]

    if not df_ledger.empty:
        for col in ['구분', '분류']:
            if col in df_ledger.columns: df_ledger[col] = df_ledger[col].astype(str).str.strip()
        if '금액' in df_ledger.columns: df_ledger['금액'] = df_ledger['금액'].apply(safe_int)

    asset_name_col = None; asset_amount_col = None
    if not df_assets.empty:
        for col in ['항목', '자산명', '자산', '계좌명', '구분', '내용', 'Asset']:
            if col in df_assets.columns: asset_name_col = col; break
        for col in ['금액', '잔액', '평가액', '자산금액', 'Amount']:
            if col in df_assets.columns: asset_amount_col = col; break
        if asset_amount_col: df_assets[asset_amount_col] = df_assets[asset_amount_col].apply(safe_int)

    _, months_passed = get_dues_calc_info()
    total_due_per_person = 100000 + (months_passed * 30000)

    tab1, tab2, tab3 = st.tabs(["분석적 검토", "자산 현황", "이자 분석"])

    # ──────────────── TAB 1 ────────────────
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

        if not df_analysis.empty:
            total_members  = len(df_analysis)
            complete_count = (df_analysis['상태'].isin(['완납', '선납'])).sum()
            unpaid_count   = (df_analysis['상태'] == '미납').sum()
            overall_rate   = (total_paid_sum / (total_due_per_person * total_members) * 100) if total_members > 0 else 0
            unpaid_sum     = df_analysis['차이금액(=A-B)'].clip(lower=0).sum()

            st.markdown(rate_hero(overall_rate, total_members, complete_count, unpaid_count, unpaid_sum), unsafe_allow_html=True)

            section_header("회원별 납부율", f"납부 합계 <b>{format_comma(total_paid_sum)}원</b>")
            st.plotly_chart(make_payment_bar_chart(df_analysis), use_container_width=True, config={'displayModeBar': False})

        st.divider()

        section_header("一. 회원별 납부 현황", f"기준 <b>{format_comma(total_due_per_person)}원</b>/인")
        if not df_analysis.empty:
            member_rows = [[escape(str(r['회원명'])), format_comma(r['B.납부한금액']),
                            signed_diff(r['B.납부한금액'] - r['A.납부할금액']), status_badge(r['상태'])]
                           for _, r in df_analysis.iterrows()]
            total_diff = total_paid_sum - df_analysis['A.납부할금액'].sum()
            st.markdown(html_table(['회원', '납부액', '차이', '상태'], member_rows, num_cols=(1, 2),
                                   total=['합계', format_comma(total_paid_sum), signed_diff(total_diff), ''], hl_col=1),
                        unsafe_allow_html=True)

        st.divider()

        exp_total = 0
        if '금액' in df_ledger.columns:
            exp_c = df_ledger[(df_ledger['구분'] == '출금') & (df_ledger['분류'] == '상조금')]['금액'].sum()
            exp_w = df_ledger[(df_ledger['구분'] == '출금') & (df_ledger['분류'] == '근조화환')]['금액'].sum()
            exp_m = df_ledger[(df_ledger['구분'] == '출금') & (df_ledger['분류'] == '회의비외')]['금액'].sum()
            exp_s = df_ledger[(df_ledger['구분'] == '출금') & (df_ledger['분류'] == '적금')]['금액'].sum()
            exp_total = exp_c + exp_w + exp_m + exp_s

            col_exp_table, col_exp_chart = st.columns([3, 2])
            with col_exp_table:
                section_header("二. 회비통장 지출액", f"합계 <b>{format_comma(exp_total)}원</b>")
                exp_rows = [["조의금", "건당 100만원", format_comma(exp_c)],
                            ["근조화환", "건당 10만원", format_comma(exp_w)],
                            ["회의비 등", "식대 · 소모품", format_comma(exp_m)],
                            ["적금", "적금 원금", format_comma(exp_s)]]
                st.markdown(html_table(['지출 항목', '내용', '금액'], exp_rows, num_cols=(2,),
                                       total=['합계', '', format_comma(exp_total)], hl_col=2), unsafe_allow_html=True)
            with col_exp_chart:
                section_header("지출 구성")
                labels = ['조의금', '근조화환', '회의비 등', '적금']
                values = [exp_c, exp_w, exp_m, exp_s]
                valid = [(l, v) for l, v in zip(labels, values) if v > 0]
                if valid:
                    lv, vv = zip(*valid)
                    st.plotly_chart(make_expense_pie_chart(list(lv), list(vv)), use_container_width=True, config={'displayModeBar': False})

        df_meet = load_data("meetings")
        if not df_meet.empty:
            section_header("※ 최근 모임 내역")
            if '금액' in df_meet.columns:
                df_meet['금액'] = df_meet['금액'].apply(lambda v: format_comma(safe_int(v)) if str(v).strip() not in ('', 'nan') else '')
            df_meet = df_meet.fillna('')
            meet_cols = list(df_meet.columns)
            meet_rows = [[escape(str(v)) for v in r] for r in df_meet.values.tolist()]
            st.markdown(html_table([escape(str(c)) for c in meet_cols], meet_rows,
                                   num_cols=tuple(i for i, c in enumerate(meet_cols) if c == '금액')), unsafe_allow_html=True)

        st.divider()

        real_balance = 0
        if asset_amount_col and asset_name_col:
            try:
                mask = df_assets[asset_name_col].str.contains('회비통장', na=False)
                if mask.any(): real_balance = df_assets[mask][asset_amount_col].iloc[0]
            except: pass

        # 이력회원 입출금은 history 탭에 따로 적으므로, 장부상 잔액에 넣지 않고 차이 내역에서 따로 보여줌
        hist_net = 0
        df_hist = load_data("history")
        if not df_hist.empty and '금액' in df_hist.columns and '구분' in df_hist.columns:
            hist_gubun = df_hist['구분'].astype(str).str.strip()
            hist_amt = df_hist['금액'].apply(safe_int)
            hist_net = hist_amt[hist_gubun == '입금'].sum() - hist_amt[hist_gubun == '출금'].sum()
        val_a = total_paid_sum - exp_total
        diff_final = real_balance - val_a
        diff_other = diff_final - hist_net

        section_header("三. 분석적 검토", f"차이 <b>{format_comma(diff_final)}원</b>")
        st.markdown(
            f'<div class="ga-review">'
            f'<div class="ga-row">실제 통장 잔액 <b>{format_comma(real_balance)}원</b></div>'
            f'<div class="ga-row">장부상 잔액 <b>{format_comma(val_a)}원</b></div>'
            f'<div class="ga-row sum">차이 <b>{format_comma(diff_final)}원</b></div>'
            f'<div class="ga-row sub">└ 탈회등 회원 수입 <b>{format_comma(hist_net)}원</b></div>'
            f'<div class="ga-row sub">└ 기타 (이자 등) <b>{format_comma(diff_other)}원</b></div>'
            f'</div>', unsafe_allow_html=True)
        conclusion("차이금액은 회비통장 이자수익 미반영분으로, 중요성 관점에서 회계상 문제 없음.")

    # ──────────────── TAB 2 ────────────────
    with tab2:
        if not df_assets.empty and asset_amount_col and asset_name_col:
            mask_total = ~df_assets[asset_name_col].astype(str).str.contains('합계', na=False)
            df_valid = df_assets[mask_total]
            total_asset = df_valid[asset_amount_col].sum()

            section_header("보유 자산 현황", f"총 <b>{format_comma(total_asset)}원</b>")
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
                    st.plotly_chart(make_donut_chart(labels, values, ""), use_container_width=True, config={'displayModeBar': False})
        else:
            st.warning("자산 데이터를 불러오지 못했습니다.")

    # ──────────────── TAB 3 ────────────────
    with tab3:
        if not df_ledger.empty and not df_assets.empty and asset_amount_col and asset_name_col and '금액' in df_ledger.columns:
            target_ledger = df_ledger[df_ledger['분류'] == '적금'].copy()
            principal_sum = target_ledger['금액'].sum()
            target_assets = df_assets[df_assets[asset_name_col].str.contains('적금', na=False)].copy()
            current_val_sum = target_assets[asset_amount_col].sum()
            interest = current_val_sum - principal_sum

            p1, p2, p3 = st.columns(3)
            with p1: st.markdown(kpi_card("적금 원금", format_comma(principal_sum), "", "원"), unsafe_allow_html=True)
            with p2: st.markdown(kpi_card("현재 평가액", format_comma(current_val_sum), "green", "원"), unsafe_allow_html=True)
            with p3: st.markdown(kpi_card("누적 이자", format_comma(interest), "gold", "원"), unsafe_allow_html=True)

            st.markdown(f"""
            <div class="interest-box fade-in">
                <div class="lbl">누적 이자 발생액</div>
                <div class="val">{format_comma(interest)} 원</div>
            </div>""", unsafe_allow_html=True)
            st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

            col_chart2, col_tbl2 = st.columns([1, 1])
            with col_chart2:
                section_header("원금 · 평가액 비교")
                st.plotly_chart(make_interest_timeline(principal_sum, current_val_sum), use_container_width=True, config={'displayModeBar': False})
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
            conclusion("회비는 매우 투명하게 관리되고 있으며, 설명 불가한 입출금 내역 無.<br>이자 수익이 꾸준히 누적되어 매우 건실한 상태로 평가됨.", "評")


def page_rules():
    apply_theme_style("sub")
    render_header_nav("회칙 및 규정", seal_text="會則")
    df_rules = load_data("rules")
    search_rule = st.text_input("규정 검색", placeholder="검색어를 입력하세요")

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
            <div class="rule-card">
                <div class="rule-head">{header_text}</div>
                <div class="rule-body">{row.get('내용', '-')}</div>
            </div>""", unsafe_allow_html=True)
    else:
        st.info("회칙 데이터를 불러오는 중입니다.")


def page_history():
    apply_theme_style("sub")
    render_header_nav("탈회등 회원", seal_text="脫會")

    df = load_data("history")
    if df.empty or '금액' not in df.columns:
        st.warning("탈회등 회원 데이터를 불러오지 못했습니다.")
        return

    for col in ['구분', '내용', '분류']:
        if col in df.columns: df[col] = df[col].astype(str).str.strip()
    df['금액'] = df['금액'].apply(safe_int)

    dep = df[df['구분'] == '입금'].groupby('내용')['금액'].sum()
    wd  = df[df['구분'] == '출금'].groupby('내용')['금액'].sum()
    df_sum = pd.concat([dep.rename('입금 합계'), wd.rename('출금 합계')], axis=1).fillna(0).astype(int)
    df_sum['차액(입금-출금)'] = df_sum['입금 합계'] - df_sum['출금 합계']
    df_sum.index.name = '회원명'
    df_sum = df_sum.reset_index()

    total_in  = df_sum['입금 합계'].sum()
    total_out = df_sum['출금 합계'].sum()

    k1, k2, k3, k4 = st.columns(4)
    with k1: st.markdown(kpi_card("탈회등 회원", len(df_sum), "", "명"), unsafe_allow_html=True)
    with k2: st.markdown(kpi_card("입금 합계", format_comma(total_in), "green", "원"), unsafe_allow_html=True)
    with k3: st.markdown(kpi_card("출금 합계", format_comma(total_out), "red", "원"), unsafe_allow_html=True)
    with k4: st.markdown(kpi_card("차액", format_comma(total_in - total_out), "gold", "원"), unsafe_allow_html=True)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    section_header("一. 회원별 입출금")
    df_disp = pd.concat([df_sum, pd.DataFrame([{
        '회원명': '합계', '입금 합계': total_in, '출금 합계': total_out, '차액(입금-출금)': total_in - total_out
    }])], ignore_index=True)
    for c in ['입금 합계', '출금 합계', '차액(입금-출금)']:
        df_disp[c] = df_disp[c].apply(format_comma)
    event = st.dataframe(df_disp, use_container_width=True, hide_index=True,
                         on_select="rerun", selection_mode="single-row")
    st.caption("회원 행 맨 왼쪽 칸을 눌러 선택하면 아래에 개인 현황이 표시됩니다.")

    rows = event.selection.rows
    if rows and df_disp.loc[rows[0], '회원명'] != '합계':
        sel_name = df_disp.loc[rows[0], '회원명']
        df_members = load_data("members")
        role, join_date, end_date = '탈회등 회원', '-', None
        if not df_members.empty and '성명' in df_members.columns:
            m = df_members[df_members['성명'] == sel_name]
            if not m.empty:
                role, join_date = m.iloc[0].get('직책', role), m.iloc[0].get('가입일자', join_date)
                end_date = parse_date(m.iloc[0].get('탈회일자', ''))
        st.divider()
        if end_date is None:
            st.warning("members 시트에 탈회일자가 없어 오늘 기준으로 계산했습니다.")
        render_member_detail(sel_name, role, join_date, df, end_date)

# -----------------------------------------------------------------------------
# 7. 네비게이션
# -----------------------------------------------------------------------------
home     = st.Page(page_home,       title="홈",        url_path="home",     default=True)
status   = st.Page(page_all_status, title="회원전체현황", url_path="status")
personal = st.Page(page_personal,   title="회원개인현황", url_path="personal")
rules    = st.Page(page_rules,      title="회칙",       url_path="rules")
history  = st.Page(page_history,    title="탈회등 회원", url_path="history")

pg = st.navigation([home, status, personal, rules, history], position="hidden")

BGM_URL = "https://cdn.jsdelivr.net/gh/ant11353-cyber/sangjo-app@main/bgm.mp3"

def bgm_player(volume=1.0):
    # Streamlit은 페이지를 옮길 때마다 화면을 새로 그림 → 오디오를 앱 바깥(브라우저 화면)에 한 번만 붙여야 끊기지 않음
    # 휴대폰은 자동재생을 막으므로 첫 터치 때 재생 시작
    components.html(f"""
<script>
const doc = window.parent.document;
if (!doc.getElementById('bgm')) {{
  const a = doc.createElement('audio');
  a.id = 'bgm'; a.src = '{BGM_URL}'; a.loop = true; a.volume = {volume};
  doc.body.appendChild(a);
  const btn = doc.createElement('div');
  btn.textContent = '♪';
  btn.style.cssText = 'position:fixed;bottom:16px;right:16px;z-index:1000001;width:34px;height:34px;background:#a63a2b;color:#f3ead8;display:flex;align-items:center;justify-content:center;font-family:"Noto Serif KR",serif;font-size:14px;cursor:pointer;opacity:.85;';
  doc.body.appendChild(btn);
  const setLabel = () => {{ btn.textContent = a.paused ? '消' : '♪'; btn.style.opacity = a.paused ? '.45' : '.85'; }};
  a.addEventListener('play', setLabel); a.addEventListener('pause', setLabel);
  a.play().catch(() => {{}});
  let started = false;
  const firstTap = (e) => {{
    if (started || e.target === btn) return;
    started = true; a.play().catch(() => {{}});
  }};
  doc.addEventListener('click', firstTap, true);
  doc.addEventListener('touchend', firstTap, true);
  btn.addEventListener('click', () => {{ started = true; a.paused ? a.play() : a.pause(); }});
}}
</script>""", height=0)

bgm_player()
pg.run()
