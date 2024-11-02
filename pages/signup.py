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


# 회원가입 페이지
def signup_page():
    st.title("회원가입")

    with st.form("signup_form"):
        user_id = st.text_input("아이디")
        password = st.text_input("비밀번호", type="password")
        name = st.text_input("이름")

        # 이름 입력 칸과 회원가입 버튼 사이에 동의 체크박스 추가
        agree_to_terms = st.checkbox("사이트의 정보를 이용함에 따라 발생할 수 있는 오류와 중요 정보에 대해서는 직접 확인할 책임이 있음을 동의합니다.")

        submit = st.form_submit_button("회원가입")

        if submit:
            if not agree_to_terms:
                st.error("회원가입을 진행하려면 동의 서약서에 체크해주세요.")
            elif user_id and password and name:
                db = get_db_connection()
                cursor = db.cursor()
                hashed_password = hash_password(password)
                try:
                    cursor.execute("INSERT INTO user (id, password, name) VALUES (%s, %s, %s)",
                                   (user_id, hashed_password, name))
                    db.commit()
                    st.success("회원가입이 완료되었습니다.")
                    switch_page("login")  # 회원가입 후 로그인 페이지로 이동
                finally:
                    cursor.close()
                db.close()
            else:
                st.error("모든 필드를 입력해주세요.")


if __name__ == "__main__":
    signup_page()
