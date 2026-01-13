# 📱 천비칠마 상조회 통합 관리 시스템 (v2.0)

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Google Sheets](https://img.shields.io/badge/Google%20Sheets-34A853?style=for-the-badge&logo=google-sheets&logoColor=white)

**"투명하고 편리한 상조회 관리를 위한 모바일 최적화 웹 애플리케이션"**

기존 엑셀로 관리되던 상조회 장부를 모바일 앱으로 변환하여, 모든 회원이 언제 어디서나 자금 흐름과 본인의 납부 현황을 투명하게 확인할 수 있도록 개발되었습니다.

---

## 🚀 주요 기능 (Key Features)

### 1. 🏠 홈 (Dashboard)
- **Deep Dark 디자인:** 천비칠마(天飛七馬) 배경 이미지와 조화를 이루는 고급스러운 다크 모드 적용.
- **Glassmorphism UI:** 반투명한 유리 효과를 적용한 버튼과 박스로 세련된 시각적 경험 제공.
- **모바일 최적화:** 휴대폰 화면 크기에 맞춰 버튼 크기와 레이아웃이 자동 조정되는 반응형 디자인.

### 2. 📊 회원 전체 현황 (Financial Status)
회 전체의 자금 흐름을 회계적으로 분석하여 투명하게 공개합니다.
- **분석적 검토:** (전체 입금액 - 전체 지출액)과 (실제 통장 잔액)을 비교하여 차액 검증.
- **자산 현황:** 실시간 통장 잔액 조회 (합계 행 자동 제외 로직 적용).
- **이자 분석:** 적금 원금(Ledger)과 현재 평가액(Asset)을 비교하여 이자 수익 자동 산출.
- **지출 상세:** 조의금, 근조화환, 회의비 등 항목별 지출 합계 자동 분류.

### 3. 🔒 회원 개인 현황 (My Status)
개인 프라이버시를 보호하며 본인의 정보를 조회합니다.
- **간편 로그인:** 이메일 아이디(ID)를 통한 본인 인증.
- **납부 내역:** 가입일 기준 납부해야 할 총액 vs 실제 납부액을 비교하여 **미납/완납/선납** 상태 표시.
- **수혜 내역:** 본인이 수령한 경조사비 및 화환 내역 조회.

### 4. 📜 회칙 및 규정 (Rules)
- 키워드 검색 기능을 포함한 회칙 뷰어 제공.

---

## 🛠️ 기술 스택 (Tech Stack)

* **Frontend & Backend:** Python, Streamlit
* **Database:** Google Spreadsheets (실시간 양방향 연동)
* **Data Processing:** Pandas (데이터 전처리, 공백 제거, 콤마 포맷팅)
* **Deployment:** Streamlit Cloud

---

## 📝 개발 히스토리 (Development History)

**개발 기간:** 2026.01.12 ~ 2026.01.13  
**개발자:** GS Kim

#### **Phase 1: 데이터 연동 및 로직 구현**
* 구글 스프레드시트(`members`, `ledger`, `assets`, `rules`)와 API 연동 성공.
* 회비 자동 계산 알고리즘 구현 (기준일 2020.02.01 기반 경과 개월 수 산정).
* 장부의 텍스트('입금', '출금', '조의금' 등)를 인식하여 자금 흐름을 자동 분류하는 로직 개발.

#### **Phase 2: 사용자 경험(UX) 고도화**
* **Navigation 개선:** 기존의 단순 화면 전환 방식에서 `st.navigation` & `st.Page` 구조로 변경하여 **휴대폰 '뒤로가기' 버튼 완벽 지원**.
* **홈 버튼 오류 해결:** 페이지 객체 기반의 라우팅으로 수정하여 앱 종료 없이 홈 화면 복귀 구현.

#### **Phase 3: 디자인 시스템 구축 (Dark & Mobile First)**
* **Dark Mode:** 눈의 피로를 줄이고 중후함을 주는 검회색(`#121212`) 배경 채택.
* **Responsive CSS:**
    * PC에서는 시원하고 큰 버튼 배치.
    * 모바일에서는 버튼 높이를 축소하고 여백을 제거하여 한 손 조작 편의성 증대.
* **Visual Elements:** 파비콘(Favicon) 적용 및 `bg.png`를 활용한 브랜드 아이덴티티 강화.

---

## © Copyright
**Copyright © 2026 GS Kim. All rights reserved.**
