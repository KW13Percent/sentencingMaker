import streamlit as st
import mysql.connector
import hashlib
from streamlit_extras.switch_page_button import switch_page  # switch_page 함수 사용


# MySQL 연결 설정
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="username",
        password="password",
        database="DBname"
    )


# 비밀번호 해시화 함수
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# 로그인 페이지
def login_page():
    st.title("로그인")

    with st.form("login_form"):
        user_id = st.text_input("아이디")
        password = st.text_input("비밀번호", type="password")
        submit = st.form_submit_button("로그인")

        if submit:
            db = get_db_connection()
            cursor = db.cursor(dictionary=True)
            hashed_password = hash_password(password)
            try:
                cursor.execute("SELECT * FROM user WHERE id=%s AND password=%s", (user_id, hashed_password))
                user = cursor.fetchone()  # 결과 읽기
                cursor.fetchall()  # 처리되지 않은 나머지 결과 읽기(오류 방지)

                if user:
                    st.session_state["user_id"] = user["userId"]
                    st.session_state["user_name"] = user["name"]
                    st.success(f"환영합니다, {user['name']}님!")
                    switch_page("case")  # 로그인 후 case 페이지로 이동
                else:
                    st.error("아이디 또는 비밀번호가 잘못되었습니다.")
            finally:
                cursor.close()
            db.close()

    # 회원가입으로 이동하는 버튼 추가
    if st.button("회원가입"):
        switch_page("signup")


if __name__ == "__main__":
    login_page()
