import streamlit as st
import json
from sqlalchemy import create_engine, text

# OpenAI API 키 설정
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

# PostgreSQL 연결
DATABASE_URL = st.secrets["DATABASE_URL"]
engine = create_engine(DATABASE_URL)

# Streamlit 앱 시작
st.title("학생의 인공지능 사용 내역(교사용)")

# 비밀번호 입력
password = st.text_input("비밀번호를 입력하세요", type="password")

def fetch_records():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT id, number, name, time FROM qna ORDER BY time DESC"))
            records = [{"id": row.id, "number": row.number, "name": row.name, "time": row.time} for row in result]
        return records
    except Exception as e:
        st.error(f"PostgreSQL 오류: {e}")
        return []

def fetch_record_by_id(record_id):
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT chat FROM qna WHERE id = :id"), {"id": record_id})
            row = result.fetchone()
            if row:
                chat = row.chat
                if isinstance(chat, str):
                    chat = json.loads(chat)
                return chat
            return None
    except Exception as e:
        st.error(f"PostgreSQL 오류: {e}")
        return None

if password == st.secrets["PASSWORD"]:
    records = fetch_records()

    if records:
        record_options = [
            f"{record['number']} ({record['name']}) - {record['time']}" for record in records
        ]
        selected_record = st.selectbox("내역을 선택하세요:", record_options)

        selected_record_id = records[record_options.index(selected_record)]["id"]

        chat = fetch_record_by_id(selected_record_id)
        if chat:
            st.write("### 학생의 대화 기록")
            for message in chat:
                if message["role"] == "user":
                    st.write(f"**You:** {message['content']}")
                elif message["role"] == "assistant":
                    st.write(f"**수학여행 도우미:** {message['content']}")
        else:
            st.warning("선택된 레코드에 대화 기록이 없습니다.")
    else:
        st.warning("PostgreSQL에 저장된 내역이 없습니다.")
else:
    st.error("비밀번호가 틀렸습니다.")
