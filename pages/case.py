import streamlit as st
import mysql.connector
import requests
import re
import numpy as np
import pandas as pd
import openai
import json
from streamlit_extras.switch_page_button import switch_page  # switch_page 함수 사용
from krwordrank.word import KRWordRank
from konlpy.tag import Okt
from bs4 import BeautifulSoup as bs
from datetime import datetime as dt
import requests
import xml.etree.ElementTree as ET

# OpenAI API 설정
openai.api_key = 'openai - api 키값'

# Fine-tuned 모델 ID 설정

MODEL_ID = 'gpt 모델 ID'


# MySQL 연결 설정
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="username",
        password="password",
        database="DBname"
    )


# Fine-tuned GPT 모델 API 호출 함수
def get_finetuned_gpt_response(user_input):
    try:
        response_for_finetuning = openai.ChatCompletion.create(
            model=MODEL_ID,
            messages=[
                {"role": "system", "content": "You are a judge."},
                {"role": "user", "content": user_input},
            ],
            max_tokens=3000,
            n=1,
            stop=None,
            temperature=0.6
        )
        return response_for_finetuning['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"Error: {str(e)}"


# 필터 리스트 설정
filter1 = ["절도", "성폭력", "초범", "침입", "재산권", "성기", "무고", "자살", "흉기", "미성년",
    "혈중", "살인", "간음", "보복", "도박", "감금", "살해", "어린", "사체", "도난", "사기죄", "성범죄",
           "학대", "폭발", "가출", "유흥", "성범", "알콜", "싸움", "알코올", "착취", "폭로", "초등학",
           "성행위", "해킹", "알코", "중상", "질식", "테러", "밀고", "성욕", "음란물", "밀수", "스토",
           "학살", "경범죄", "강제추", "괴롭", "암페타민", "절도죄", "외도", "윤락", "명예훼손", "난동",
           "뺑소", "성희롱", "섹스", "타살", "준강간", "명예훼손죄", "위증죄", "무면허운", "모욕죄", "채무",
           "불법", "강제", "고의", "상속", "유서", "폭력", "부채", "이혼", "강도",
    "음주", "강간", "몰래", "청소년", "성폭", "탈세", "강압", "필로폰", "구타", "소프트웨어",
    "사칭", "성희", "성관계", "대마", "성매매", "채무불이행", "음주운전", "횡령죄", "무면허", "납치",
    "무면허운전", "불륜", "친고죄", "성추행", "간접강", "음주운", "강제추행", "초범", "강원랜드", "병역법",
    "특수강", "성폭행", "피싱", "총격", "협박죄", "강간죄", "상속법", "성행", "횡령", "김영란", "불법행"]
filter2_file_path = 'C:/Users/SUHUN/OneDrive/Desktop/13percent/streamlit_exercise/filter_list.csv'

filter2 = []
with open(filter2_file_path, 'r', encoding="cp949") as file:
    for row in file:
        filter2.append(row.strip())
filter2 = [word for word in filter2 if word not in filter1]

# 키워드 추출 함수
okt = Okt()


def split_noun_sentences(text):
    sentences = text.replace(". ", ".")
    sentences = re.sub(r'([^\n\s\.\?!]+[^\n\.\?!]*[\.\?!])', r'\1\n', sentences).strip().split("\n")
    result = []
    for sentence in sentences:
        if len(sentence) == 0:
            continue
        sentence_pos = okt.pos(sentence, stem=True)
        nouns = [word for word, pos in sentence_pos if pos == 'Noun']
        if len(nouns) == 1:
            continue
        result.append(' '.join(nouns) + '.')
    return result


# 유사 판례 조회 함수
def get_similar_judgement(text):
    min_count = 1
    max_length = 10
    beta = 0.85
    max_iter = 20
    key_word = []
    result = []

    wordrank_extractor = KRWordRank(min_count=min_count, max_length=max_length)
    texts = split_noun_sentences(text)
    keywords, rank, graph = wordrank_extractor.extract(texts, beta, max_iter)
    for word, score in keywords.items():
        key_word.append(word)

    filter1_keyword = [word for word in key_word if word in filter1]
    filter2_keyword = [word for word in key_word if word in filter2]

    if filter1_keyword and filter2_keyword:
        file_path = 'C:/Users/SUHUN/OneDrive/Desktop/13percent/streamlit_exercise/key_word.csv'
        data = pd.read_csv(file_path, sep=',', header=None, names=['일련번호', '키워드'], encoding='cp949')
        data['키워드'] = data['키워드'].astype(str)
        data['키워드 수'] = data['키워드'].apply(lambda x: sum(keyword in x for keyword in filter1_keyword))
        cases_with_keywords = data[data['키워드 수'] > 0]
        cases_with_keywords['키워드 수'] = cases_with_keywords['키워드'].apply(
            lambda x: sum(keyword in x for keyword in filter2_keyword))
        cases_with_keywords = cases_with_keywords[cases_with_keywords['키워드 수'] > 0]
        top_cases = cases_with_keywords.sort_values(by='키워드 수', ascending=False).head(3)

        for index, row in top_cases.iterrows():
            url = f"http://www.law.go.kr/DRF/lawService.do?OC=dnruruf&target=prec&ID={row['일련번호']}&type=XML"
            response = requests.get(url)
            contents = response.text
            root = ET.fromstring(contents)
            case_name = root.find("사건명").text
            case_number = root.find("사건번호").text
            base_url = "https://www.law.go.kr/판례/"
            clean_text = f"{base_url}{case_name}"
            result.append(clean_text)
            st.write(clean_text)

        result2 = ' '.join(result)
        return result2


# Case 입력 및 출력 페이지
def case_page():
    if "user_id" not in st.session_state:
        st.warning("로그인이 필요합니다.")
        switch_page("login")
        return

    # 로그아웃 버튼 추가
    if st.button("로그아웃"):
        st.session_state.clear()  # 세션 상태 초기화
        switch_page("main")  # 로그아웃 후 main.py로 이동
        return

    st.title("Case 입력 및 출력")

    # 사건 정보 입력 부분 (텍스트 영역을 사용하여 크기를 자동으로 조정)
    case_detail = st.text_area("사건 정보에 대해 입력하시오:", height=100)
    case_detail += "이 사건에 대해 판결문을 작성해주세요"
    case_detail += "범죄 사실, 법령의 적용, 증거의 요지, 양형의 이유, 형량을 맞춰주세요."
    # 결과 출력하기 버튼 추가 (텍스트 입력 후 엔터 대신 버튼으로 제출 가능)
    # if st.button("결과 출력하기"):
    #     if case_detail:
    #         response_for_finetuning = get_finetuned_gpt_response(case_detail)
    #         st.write("#### 결과")
    #         st.write(response_for_finetuning)
    #
    #         st.write("#### 유사 판례 ")
    #         similar_case = get_similar_judgement(case_detail)
    #
    #
    #         if case_detail:
    #             db = get_db_connection()
    #             cursor = db.cursor()
    #             try:
    #                 cursor.execute(
    #                     "INSERT INTO `case` (userId, caseDetail, similarCase, result) VALUES (%s, %s, %s, %s)",
    #                     (st.session_state["user_id"], case_detail, similar_case, response_for_finetuning)
    #                 )
    #                 db.commit()
    #                 st.success("Case가 저장되었습니다.")
    #             finally:
    #                 cursor.close()
    #             db.close()
    if st.button("결과 출력하기"):
        if case_detail:
            response_for_finetuning = get_finetuned_gpt_response(case_detail)
            st.write("#### 결과")
            st.write(response_for_finetuning)

            st.write("#### 유사 판례 ")
            similar_case = get_similar_judgement(case_detail)

            if similar_case is not None:  # None이 아닌 경우에만 실행
                db = get_db_connection()
                cursor = db.cursor()
                try:
                    cursor.execute(
                        "INSERT INTO `case` (userId, caseDetail, similarCase, result) VALUES (%s, %s, %s, %s)",
                        (st.session_state["user_id"], case_detail, similar_case, response_for_finetuning)
                    )
                    db.commit()
                    st.success("Case가 저장되었습니다.")
                finally:
                    cursor.close()
                db.close()
            else:
                st.warning("유사 판례를 불러올 수 없습니다.")

    # 이전 case 기록 보기 버튼을 누르면 페이지 전환 후 바로 return
    if st.button("이전 case 기록 보기"):
        switch_page("view_cases")
        return  # 버튼을 눌렀을 때 현재 함수를 종료


if __name__ == "__main__":
    case_page()
