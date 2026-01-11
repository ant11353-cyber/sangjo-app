import streamlit as st
import pandas as pd

# 1. 페이지 설정 (아이콘과 제목)
st.set_page_config(page_title="우리 모임", page_icon="📱", layout="wide")

st.title("📱 우리 모임 통합 관리")
st.write("언제 어디서나 간편하게 확인하세요!")

# 2. 데이터 불러오기 함수
def load_data(sheet_name):
    try:
        url = st.secrets["connections"]["sheet_url"]
        sheet_id = url.split("/d/")[1].split("/")[0]
        csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
        return pd.read_csv(csv_url)
    except Exception as e:
        return pd.DataFrame()

# 3. 탭 구성
tab1, tab2, tab3, tab4 = st.tabs(["👥 회원찾기", "💰 회계장부", "🏢 자산", "📜 회칙"])

# --- 탭 1: 회원 명부 (검색 기능 + 카드 뷰) ---
with tab1:
    st.header("회원 연락처 찾기")
    df_members = load_data("members")
    
    if not df_members.empty:
        # 상단 통계
        st.metric("총 회원 수", f"{len(df_members)}명")
        
        # 🔍 검색창 만들기
        search_name = st.text_input("이름으로 검색해보세요", placeholder="예: 홍길동")
        
        # 검색 기능 적용
        if search_name:
            df_members = df_members[df_members['이름'].astype(str).str.contains(search_name)]
        
        st.divider() # 구분선
        
        # 📱 스마트폰처럼 '카드' 형태로 보여주기
        for idx, row in df_members.iterrows():
            # 이름과 직책을 제목으로 표시
            with st.expander(f"👤 {row['이름']} ({row.get('직책', '회원')})"):
                # 펼치면 상세 정보 보임
                st.write(f"📞 **전화번호:** {row.get('전화번호', '-')}")
                st.write(f"📅 **가입일:** {row.get('가입일', '-')}")
                # 필요한 항목이 더 있다면 여기에 추가: st.write(f"주소: {row.get('주소', '-')}")

    else:
        st.warning("데이터를 불러오지 못했습니다. 탭 이름(members)을 확인하세요.")

# --- 탭 2: 회계 장부 (표 형태) ---
with tab2:
    st.header("회비 입출금 내역")
    df_ledger = load_data("ledger")
    if not df_ledger.empty:
        st.info("💡 오른쪽 위 돋보기 아이콘을 누르면 표 내용을 검색할 수 있습니다.")
        st.dataframe(df_ledger, use_container_width=True, hide_index=True)

# --- 탭 3: 자산 현황 ---
with tab3:
    st.header("모임 자산 목록")
    df_assets = load_data("assets")
    if not df_assets.empty:
        st.dataframe(df_assets, use_container_width=True, hide_index=True)

# --- 탭 4: 회칙 ---
with tab4:
    st.header("회칙 및 규정")
    df_rules = load_data("rules")
    if not df_rules.empty:
        # 회칙은 줄글이 많으므로 표보다는 리스트로 보여주기
        for idx, row in df_rules.iterrows():
            st.markdown(f"**{row.get('조항', '-')}**")
            st.write(row.get('내용', '-'))
            st.divider()
