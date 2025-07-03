import streamlit as st
import json
import random
import openai

# 페이지 설정
st.set_page_config(
    page_title="정형외과 국가고시 문제은행",
    page_icon="🦴",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 🔑 OpenAI API 키 설정 (본인의 키로 교체하세요)
openai.api_key = "YOUR_OPENAI_API_KEY"

# 📂 문제 로딩
with open("questions.json", "r", encoding="utf-8") as f:
    questions = json.load(f)

# 📚 파트 목록 정의
parts = [
    "견관절", "주관절", "수부", "고관절", "슬관절",
    "족부/발목", "척추", "소아", "종양", "기타"
]

# 문제를 파트별로 분류 (questions.json에 'part' 필드가 있어야 함)
questions_by_part = {part: [] for part in parts}
for q in questions:
    if "part" in q and q["part"] in questions_by_part:
        questions_by_part[q["part"].strip()].append(q)

# 🎯 Streamlit 앱 제목
st.markdown("""
    <h1 style='text-align: center; font-style: italic; font-weight: 700; color: #2E86C1; margin-bottom:0;'>
        정형외과 국가고시
    </h1>
    <h1 style='text-align: center; font-style: italic; font-weight: 700; color: #2E86C1; margin-top:0;'>
        문제은행
    </h1>
    <hr style='border: 1px solid #bbb;'>
    """, unsafe_allow_html=True)

# 📌 세션 상태 초기화
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

# 🔽 파트 선택 화면
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
        st.experimental_rerun()

else:
    part = st.session_state.selected_part
    quiz_list = st.session_state.quiz_list
    index = st.session_state.quiz_index

    if index >= len(quiz_list):
        st.success(f"🎉 {part} 퀴즈 완료! 점수: {st.session_state.score} / {st.session_state.total}")
        st.button("🔙 처음으로", on_click=lambda: st.session_state.update({"selected_part": None}))
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
                st.session_state.wrong_answers.append({
                    "question": question["question"],
                    "your_answer": user_answer,
                    "correct_answer": question["answer"]
                })

            # GPT 해설 요약 요청
            prompt = f"""
            다음은 정형외과 전문의 시험 문제입니다.
            질문: {question['question']}
            정답: {question['answer']}
            이 문제의 핵심 개념과 중요한 의학적 요점을 간단히 요약해서 설명해줘. 3줄 이내로 정리해줘.
            """
            with st.spinner("🧠 GPT 요약 해설 생성 중..."):
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "당신은 정형외과 전문의 국가고시 준비를 돕는 AI 튜터입니다."},
                        {"role": "user", "content": prompt}
                    ]
                )
                explanation = response['choices'][0]['message']['content']
                st.info(f"📘 요약 해설:\n\n{explanation}")

            # 보기별 해설 추가
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

            # 다음 문제로 이동
            if st.button("➡️ 다음 문제"):
                st.session_state.quiz_index += 1
                st.experimental_rerun()

    # 점수 표시
    st.markdown(f"""
        <hr style='border: 0.5px solid #ddd;'>
        <h5 style='color:#2C3E50;'>📊 현재 점수: <span style='color:#27AE60'>{st.session_state.score}</span> / {st.session_state.total}</h5>
    """, unsafe_allow_html=True)

    # 오답노트
    if st.session_state.wrong_answers:
        with st.expander("📒 오답노트 보기"):
            for i, wrong in enumerate(st.session_state.wrong_answers, 1):
                st.markdown(f"""
                    <div style='background-color:#FDEDEC; padding:10px; border-radius:8px; margin-bottom:10px;'>
                        <b>{i}. 문제:</b> {wrong['question']}<br>
                        <b>당신의 답:</b> {wrong['your_answer']}<br>
                        <b>정답:</b> {wrong['correct_answer']}
                    </div>
                """, unsafe_allow_html=True)

    # 북마크 보기
    if st.session_state.bookmarks:
        with st.expander("⭐ 북마크한 문제 보기"):
            for i, bm in enumerate(st.session_state.bookmarks, 1):
                st.markdown(f"""
                    <div style='background-color:#FEF9E7; padding:10px; border-radius:8px; margin-bottom:10px;'>
                        <b>{i}. 문제:</b> {bm['question']}<br>
                        <b>정답:</b> {bm['answer']}
                    </div>
                """, unsafe_allow_html=True)
