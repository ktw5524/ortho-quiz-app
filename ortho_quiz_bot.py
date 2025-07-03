import streamlit as st
import json
import random

# 페이지 설정
st.set_page_config(
    page_title="정형외과 국가고시 문제은행",
    page_icon="🦴",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 문제 로딩
with open("questions.json", "r", encoding="utf-8") as f:
    questions = json.load(f)

# 파트 목록 정의
parts = [
    "견관절", "주관절", "수부", "고관절", "슬관절",
    "족부/발목", "척추", "소아", "종양", "기타"
]

# 문제를 파트별로 분류
questions_by_part = {part: [] for part in parts}
for q in questions:
    if "part" in q and q["part"] in questions_by_part:
        questions_by_part[q["part"].strip()].append(q)

# 세션 상태 초기화
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
if "wrong_answers" not in st.session_state:
    st.session_state.wrong_answers = []
if "bookmarks" not in st.session_state:
    st.session_state.bookmarks = []

# 앱 제목 표시
st.markdown("""
    <h1 style='text-align: center; font-style: italic; font-weight: 700; color: #2E86C1; margin-bottom:0;'>
        정형외과 국가고시
    </h1>
    <h1 style='text-align: center; font-style: italic; font-weight: 700; color: #2E86C1; margin-top:0;'>
        문제은행
    </h1>
    <hr style='border: 1px solid #bbb;'>
    """, unsafe_allow_html=True)

quiz_tab, wrong_tab, bookmark_tab = st.tabs(["📋 퀴즈", "📒 오답노트", "⭐ 북마크"])

with quiz_tab:
    if not st.session_state.selected_part:
        st.subheader("💡 퀴즈 파트를 선택하세요:")
        selected = st.selectbox("정형외과 10개 파트 중 하나를 고르세요", parts)
        if st.button("🚀 퀴즈 시작"):
            st.session_state.selected_part = selected
            st.session_state.quiz_list = random.sample(questions_by_part[selected], min(5, len(questions_by_part[selected])))
            st.session_state.quiz_index = 0
            st.session_state.score = 0
            st.session_state.total = 0
            st.session_state.wrong_answers = []
            st.experimental_rerun()  # 만약 오류 나면 아래 설명 참고

    else:
        index = st.session_state.quiz_index
        quiz_list = st.session_state.quiz_list

        if index >= len(quiz_list):
            st.success(f"🎉 {st.session_state.selected_part} 퀴즈 완료! 점수: {st.session_state.score} / {st.session_state.total}")
            if st.button("🔙 처음으로"):
                st.session_state.selected_part = None
                st.session_state.quiz_list = []
                st.session_state.quiz_index = 0
                st.session_state.score = 0
                st.session_state.total = 0
                st.session_state.wrong_answers = []
                st.experimental_rerun()
        else:
            question = quiz_list[index]
            st.markdown(f"<h4 style='color:#1F618D'>문제 {index + 1}:</h4><p style='font-size:18px'>{question['question']}</p>", unsafe_allow_html=True)
            user_answer = st.radio("답을 선택하세요:", question["choices"], key=question['question'])

            if st.button("✅ 답안 제출"):
                st.session_state.total += 1
                if user_answer == question["answer"]:
                    st.success("🎉 정답입니다!")
                    st.session_state.score += 1
                else:
                    st.error(f"❌ 오답입니다. 정답은: {question['answer']}")
                    st.session_state.wrong_answers.append({
                        "question": question["question"],
                        "your_answer": user_answer,
                        "correct_answer": question["answer"]
                    })

                # 저장된 간단 해설 출력 (question에 summary_explanation 필드가 있다고 가정)
                if "summary_explanation" in question:
                    st.info(f"📘 해설 요약:\n\n{question['summary_explanation']}")

                # 상세 해설(보기별 해설)
                if "detailed_explanations" in question:
                    with st.expander("📖 보기별 해설 전체 보기"):
                        for choice in question["choices"]:
                            explanation = question["detailed_explanations"].get(choice, "설명 없음")
                            st.markdown(f"**📝 {choice}**: {explanation}")

                # 북마크 버튼
                if st.button("🔖 이 문제 북마크하기"):
                    if question not in st.session_state.bookmarks:
                        st.session_state.bookmarks.append(question)
                        st.success("⭐ 북마크에 추가되었습니다.")

                if st.button("➡️ 다음 문제"):
                    st.session_state.quiz_index += 1
                    st.experimental_rerun()

            st.markdown(f"""
                <hr style='border: 0.5px solid #ddd;'>
                <h5 style='color:#2C3E50;'>📊 현재 점수: <span style='color:#27AE60'>{st.session_state.score}</span> / {st.session_state.total}</h5>
            """, unsafe_allow_html=True)

# 오답노트 탭
with wrong_tab:
    if st.session_state.wrong_answers:
        for i, wrong in enumerate(reversed(st.session_state.wrong_answers), 1):
            with st.container():
                st.markdown(f"""
                    <div style='background-color:#FDEDEC; padding:10px; border-radius:8px; margin-bottom:10px;'>
                        <b>{i}. 문제:</b> {wrong['question']}<br>
                        <b>당신의 답:</b> {wrong['your_answer']}<br>
                        <b>정답:</b> {wrong['correct_answer']}<br>
                        <i>저장됨: 최근</i>
                    </div>
                """, unsafe_allow_html=True)
                if st.button(f"❌ 오답노트에서 삭제하기 #{i}", key=f"remove_wrong_{i}"):
                    st.session_state.wrong_answers.remove(wrong)
                    st.experimental_rerun()
    else:
        st.info("❗ 아직 오답노트가 없습니다.")

# 북마크 탭
with bookmark_tab:
    if st.session_state.bookmarks:
        for i, bm in enumerate(reversed(st.session_state.bookmarks), 1):
            with st.container():
                st.markdown(f"""
                    <div style='background-color:#FEF9E7; padding:10px; border-radius:8px; margin-bottom:10px;'>
                        <b>{i}. 문제:</b> {bm['question']}<br>
                        <b>정답:</b> {bm['answer']}<br>
                        <i>저장됨: 최근</i>
                    </div>
                """, unsafe_allow_html=True)
                if st.button(f"❌ 북마크 해제하기 #{i}", key=f"remove_bookmark_{i}"):
                    st.session_state.bookmarks.remove(bm)
                    st.experimental_rerun()
    else:
        st.info("⭐ 북마크된 문제가 없습니다.")

# 하단 통계 표시
st.markdown(f"""
    <hr>
    <div style='text-align:center'>
        <b>총 푼 문제 수:</b> {st.session_state.total} &nbsp;&nbsp;
        <b>정답 수:</b> {st.session_state.score} &nbsp;&nbsp;
        <b>정답률:</b> {round(st.session_state.score / st.session_state.total * 100, 1) if st.session_state.total else 0}%
    </div>
""", unsafe_allow_html=True)
