import streamlit as st
import pandas as pd

# 1. 페이지 설정
st.set_page_config(page_title="우리 모임", page_icon="📱", layout="wide")

# --- CSS 스타일 적용 ---
# 사이드바 버튼을 타원형으로 만들고 크기를 키우는 CSS입니다.
st.markdown(
    """
    <style>
    /* 사이드바 버튼 스타일 */
    section[data-testid="stSidebar"] .stButton button {
        width: 100%;                /* 너비는 사이드바에 맞춤 */
        border-radius: 50px;        /* 둥근 모서리 (타원형) */
        padding: 25px 0;            /* 위아래 여백을 줘서 높이를 키움 */
        font-size: 22px;            /* 글자 크기 확대 */
        font-weight: bold;          /* 글자 굵게 */
        margin-bottom: 20px;        /* 버튼 사이 간격 */
        background-color: #5a99d8;  /* 버튼 배경색 (파란색 계열) */
        color: white;               /* 글자색 (흰색) */
        border: none;               /* 테두리 없음 */
        box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2); /* 그림자 효과 */
        transition: 0.3s;           /* 부드러운 효과 */
    }

    /* 마우스를 올렸을 때 버튼 스타일 */
    section[data-testid="stSidebar"] .stButton button:hover {
        background-color: #4a89c8;  /* 배경색 약간 진하게 */
        box-shadow: 0 8px 16px 0 rgba(0,0,0,0.2); /* 그림자 진하게 */
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("📱 우리 모임 통합 관리")

# (이하 데이터 로딩 및 탭 구성 코드는 동일합니다)
# ...
