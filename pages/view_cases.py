import streamlit as st
import mysql.connector
from streamlit_extras.switch_page_button import switch_page  # switch_page 함수 사용

# MySQL 연결 설정
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="username",
        password="password",
        database="DBname"
    )

# 이전 Case 기록 보기 페이지
def view_cases_page():
    if "user_id" not in st.session_state:
        st.warning("로그인이 필요합니다.")
        switch_page("login")
        return

    # 로그아웃 버튼을 맨 위에 추가
    if st.button("로그아웃"):
        st.session_state.clear()  # 세션 상태 초기화
        switch_page("login")  # 로그아웃 후 login 페이지로 이동
        return

    st.title("이전 사건 기록")

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM `case` WHERE userId=%s", (st.session_state["user_id"],))
        cases = cursor.fetchall()
    finally:
        cursor.close()
    db.close()

    if cases:
        for case in cases:
            # 사건 정보를 토글 형식으로 표시
            with st.expander(f"Case: {case['caseDetail']}"):
                # 내용 섹션
                st.markdown("### 내용")
                st.write(case['caseDetail'])
                st.divider()  # 섹션 구분선

                # 유사한 Case 섹션
                st.markdown("### 유사 판결문")
                cnt = 1
                similar_case_split = case['similarCase'].split()
                for i in similar_case_split:
                    st.write(f"유사 판결문 {cnt}: {i}")
                    cnt += 1
                st.divider()  # 섹션 구분선

                # 결과 섹션
                st.markdown("### 결과")
                st.write(case['result'])
    else:
        st.write("저장된 case가 없습니다.")

    # Case 입력 페이지로 돌아가는 버튼 추가
    if st.button("사건 입력 페이지로 돌아가기"):
        switch_page("case")

if __name__ == "__main__":
    view_cases_page()
