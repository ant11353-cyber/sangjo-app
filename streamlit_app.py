import streamlit as st
import pandas as pd

# 1. 페이지 제목 설정
st.set_page_config(page_title="우리 모임 관리", layout="wide")
st.title("📂 우리 모임 통합 관리 시스템")

# 2. 데이터 불러오기 함수 (구글 시트 연결)
# secrets에 저장된 주소를 가져와서 엑셀처럼 읽어옵니다.
def load_data(sheet_name):
    try:
        # secrets에서 주소 가져오기
        url = st.secrets["connections"]["sheet_url"]
        # 구글 시트 ID 추출해서 CSV 변환 주소로 변경
        sheet_id = url.split("/d/")[1].split("/")[0]
        csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
        
        # 데이터 읽기
        df = pd.read_csv(csv_url)
        return df
    except Exception as e:
        st.error(f"데이터를 불러오는데 실패했습니다: {e}")
        return pd.DataFrame()

# 3. 화면 구성 (탭 만들기)
tab1, tab2, tab3, tab4 = st.tabs(["📋 회원명부", "💰 회계장부", "🏢 자산현황", "📜 회칙"])

# 탭 1: 회원명부
with tab1:
    st.header("회원 명단")
    df_members = load_data("members") # 탭 이름: members
    st.dataframe(df_members, use_container_width=True)

# 탭 2: 회계장부
with tab2:
    st.header("회비 입출금 내역")
    df_ledger = load_data("ledger") # 탭 이름: ledger
    st.dataframe(df_ledger, use_container_width=True)

# 탭 3: 자산현황
with tab3:
    st.header("모임 자산 목록")
    df_assets = load_data("assets") # 탭 이름: assets
    st.dataframe(df_assets, use_container_width=True)

# 탭 4: 회칙
with tab4:
    st.header("회칙 및 규정")
    df_rules = load_data("rules") # 탭 이름: rules
    st.dataframe(df_rules, use_container_width=True)
