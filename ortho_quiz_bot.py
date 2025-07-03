import streamlit as st
import json
import random
import openai
from datetime import datetime
import os

# ----------------- 파일 저장/불러기 함수 -----------------
def load_data(filename):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_data(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ----------------- 초기 데이터 불러오기 -----------------
if "wrong_answers" not in st.session_state:
    st.session_state.wrong_answers = load_data("wrong_answers.json")
if "bookmarks" not in st.session_state:
    st.session_state.bookmarks = load_data("bookmarks.json")

# ----------------- 기본 세션 상태 초기화 -----------------
if "selected_part" not in st.session_state:
    st.session_state.selected_part = None
if "quiz_list" not in st.session_state:
    st.session_state.quiz_list = []
if "quiz_index" not in st.session_state:
    st.session_state.quiz_index = 0
if "score" not in st.session_state:
    st.session_state.score = 0
if "total" not in st.session_state:
    st.session_state.total = 0

# ----------------- OpenAI & 문제 로딩 -----------------
openai.api_key = "YOUR_OPENAI_API_KEY"

with open("questions.json", "r", encoding="utf-8") as f:
    questions = json.load(f)

parts = [
    "견관절", "주관절", "수부", "고관절", "슬관절",
    "족부/발목", "척추", "소아", "종양", "기타"
]

questions_by_part = {part: [] for part in parts}
for q in questions:
    if "part" in q and q["part"] in questions_by_part:
        questions_by_part[q["part"].strip()].append(q)

# ----------------- UI 타이틀 -----------------
st.set_page_config(page_title="정형외과 국가고시 문제은행", layout="centered")
st.markdown("""
    <h1 style='text-align: center; font-style: italic; font-weight: 700; color: #2E86C1;'>
        정형외과 국가고시 문제은행
    </h1>
    <hr style='border: 1px solid #bbb;'>
    """, unsafe_allow_html=True)

# ----------------- 메인 화면 or 퀴즈 화면 분기 -----------------
if not st.session_state.selected_part:
    st.subheader("💡 퀴즈 파트를 선택하세요:")
    selected = st.selectbox("정형외과 10개 파트 중 하나를 고르세요", parts)
    if st.button("🚀 퀴즈 시작"):
        st.session_state.selected_part = selected
        st.session_state.quiz_list = random.sample(questions_by_part[selected], min(5, len(questions_by_part[selected])))
        st.session_state.quiz_index = 0
        st.session_state.score = 0
        st.session_state.total = 0
        st.experimental_rerun()

    tabs = st.tabs(["📒 오답노트", "⭐ 북마크"])

    with tabs[0]:
        st.write("최근 저장된 오답노트:")
        if st.session_state.wrong_answers:
            for item in reversed(st.session_state.wrong_answers):
                st.markdown(f"""
                <div style='background:#FDEDEC; padding:10px; border-radius:8px; margin-bottom:10px;'>
                <b>문제:</b> {item['question']}<br>
                <b>내 답:</b> {item['your_answer']}<br>
                <b>정답:</b> {item['correct_answer']}<br>
                <small style='color:gray;'>저장 시간: {item['saved_at']}</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("오답노트에 저장된 문제가 없습니다.")

        if st.button("💾 오답노트 저장하기"):
            save_data("wrong_answers.json", st.session_state.wrong_answers)
            st.success("오답노트가 저장되었습니다.")

    with tabs[1]:
        st.write("최근 저장된 북마크:")
        if st.session_state.bookmarks:
            for item in reversed(st.session_state.bookmarks):
                st.markdown(f"""
                <div style='background:#FEF9E7; padding:10px; border-radius:8px; margin-bottom:10px;'>
                <b>문제:</b> {item['question']}<br>
                <b>정답:</b> {item['answer']}<br>
                <small style='color:gray;'>저장 시간: {item['saved_at']}</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("북마크에 저장된 문제가 없습니다.")

        if st.button("💾 북마크 저장하기"):
            save_data("bookmarks.json", st.session_state.bookmarks)
            st.success("북마크가 저장되었습니다.")

else:
    part = st.session_state.selected_part
    quiz_list = st.session_state.quiz_list
    index = st.session_state.quiz_index

    if index >= len(quiz_list):
        st.success(f"🎉 {part} 퀴즈 완료! 점수: {st.session_state.score} / {st.session_state.total}")
        if st.button("🔙 처음으로"):
            st.session_state.selected_part = None
            st.experimental_rerun()
    else:
        question = quiz_list[index]

        st.markdown(f"<h4 style='color:#1F618D'>문제 {index+1}:</h4><p style='font-size:18px'>{question['question']}</p>", unsafe_allow_html=True)
        user_answer = st.radio("답을 선택하세요:", question["choices"], key=question['question'])

        if st.button("✅ 답안 제출"):
            st.session_state.total += 1
            if user_answer == question["answer"]:
                st.success("🎉 정답입니다!")
                st.session_state.score += 1
            else:
                st.error(f"❌ 오답입니다. 정답은: {question['answer']}")

            st.markdown(f"**정답:** {question['answer']}")

            prompt = f"""
            다음은 정형외과 전문의 시험 문제입니다.
            질문: {question['question']}
            정답: {question['answer']}
            이 문제의 핵심 개념과 중요한 의학적 요점을 2~3줄로 간단히 요약해줘.
            """
            with st.spinner("🧠 해설 생성 중..."):
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "당신은 정형외과 전문의 국가고시 준비를 돕는 AI 튜터입니다."},
                        {"role": "user", "content": prompt}
                    ]
                )
                explanation_short = response['choices'][0]['message']['content']
                st.markdown(f"📘 간단 해설:\n\n{explanation_short}")

            with st.expander("📖 자세한 해설 보기"):
                st.markdown(question.get("explanation", "상세 해설이 없습니다."))

            col1, col2 = st.columns(2)
            with col1:
                if st.button("📒 오답노트에 저장"):
                    if user_answer != question["answer"]:
                        saved = {
                            "question": question["question"],
                            "your_answer": user_answer,
                            "correct_answer": question["answer"],
                            "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        st.session_state.wrong_answers.append(saved)
                        st.success("오답노트에 저장되었습니다.")
                    else:
                        st.info("정답인 문제는 오답노트에 저장되지 않습니다.")

            with col2:
                if st.button("⭐ 북마크 저장"):
                    saved = {
                        "question": question["question"],
                        "answer": question["answer"],
                        "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    if saved not in st.session_state.bookmarks:
                        st.session_state.bookmarks.append(saved)
                        st.success("북마크에 저장되었습니다.")
                    else:
                        st.info("이미 북마크에 저장된 문제입니다.")

            if st.button("➡️ 다음 문제"):
                st.session_state.quiz_index += 1
                st.experimental_rerun()

    st.markdown(f"""
        <hr style='border: 0.5px solid #ddd;'>
        <h5 style='color:#2C3E50;'>📊 현재 점수: <span style='color:#27AE60'>{st.session_state.score}</span> / {st.session_state.total}</h5>
    """, unsafe_allow_html=True)
