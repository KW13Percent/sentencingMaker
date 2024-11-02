import streamlit as st
from streamlit_extras.switch_page_button import switch_page  # switch_page 함수 사용


# 초기 메인 페이지
def main():
    st.title("법률 정보 제공 웹 서비스")
    st.write("로그인 또는 회원가입을 통해 법률 서비스를 이용하세요.")

    # 로그인 버튼
    if st.button("로그인"):
        switch_page("login")

    # 회원가입 버튼
    if st.button("회원가입"):
        switch_page("signup")


if __name__ == "__main__":
    main()
