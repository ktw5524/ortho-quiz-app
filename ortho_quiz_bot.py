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

# 문제를 파트별로 분류
questions_by_part = {part: [] for part in parts}
for q in questions:
    if "part" in q and q["part"] in questions_by_part:
        questions_by_part[q["part"].strip()].append(q)

# 상태 초기화 함수 (실제 재실행 없이 상태 초기화용)
def reset_quiz_state():
    st.session_state.selected_part = None
    st.session_state.quiz_list = []
    st.session_state.quiz_index = 0
    st.session_state.score = 0
    st.session_state.total = 0
    st.session_state.wrong_answers = []
    st.session_state.bookmarks = []

# 세션 상태 초기화
if "selected_part" not in st.session_state:
    reset_quiz_state()

# 앱 제목 표시 (두 줄로 분리, 가운데 정렬, 이탤릭 굵게)
st.markdown("""
    <h1 style='text-align: center; font-style: italic; font-weight: 700; color: #2E86C1; margin-bottom: 0;'>
        정형외과 국가고시
    </h1>
    <h1 style='text-align: center; font-style: italic; font-weight: 700; color: #2E86C1; margin-top: 0;'>
        문제은행
    </h1>
    <hr style='border: 1px solid #bbb;'>
    """, unsafe_allow_html=True)

# 탭 UI
quiz_tab, wrong_tab, bookmark_tab = st.tabs(["📋 퀴즈", "📒 오답노트", "⭐ 북마크"])

with quiz_tab:
    if not st.session_state.selected_part:
        st.subheader("💡 퀴즈 파트를 선택하세요:")
        selected = st.selectbox("정형외과 10개 파트 중 하나를 고르세요", parts)
        if st.button("🚀 퀴즈 시작"):
            st.session_state.selected_part = selected
            st.session_state.quiz_list = random.sample(
                questions_by_part[selected], 
                min(5, len(questions_by_part[selected]))
            )
            st.session_state.quiz_index = 0
            st.session_state.score = 0
            st.session_state.total = 0
            st.session_state.wrong_answers = []
            st.experimental_rerun()  # 스트림릿 1.21 이상부터 사용 가능, 아니라면 아래 코드 참조
    else:
        part = st.session_state.selected_part
        quiz_list = st.session_state.quiz_list
        index = st.session_state.quiz_index

        if index >= len(quiz_list):
            st.success(f"🎉 {part} 퀴즈 완료! 점수: {st.session_state.score} / {st.session_state.total}")
            if st.button("🔙 처음으로"):
                reset_quiz_state()
                st.experimental_rerun()
        else:
            question = quiz_list[index]
            st.markdown(f"<h4 style='color:#1F618D'>문제 {index+1}:</h4><p style='font-size:18px'>{question['question']}</p>", unsafe_allow_html=True)
            user_answer = st.radio("답을 선택하세요:", question["choices"], key=f"quiz_{index}")

            if st.button("✅ 답안 제출", key=f"submit_{index}"):
                st.session_state.total += 1
                if user_answer == question["answer"]:
                    st.success("🎉 정답입니다!")
                    st.session_state.score += 1
                else:
                    st.error(f"❌ 오답입니다. 정답은: {question['answer']}")
                    # 오답노트 저장은 버튼 따로 만들기로 설계 가능
                    st.session_state.wrong_answers.append({
                        "question": question["question"],
                        "your_answer": user_answer,
                        "correct_answer": question["answer"]
                    })

                # GPT 해설 요약 생성
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

                # 상세 보기별 해설 (있으면)
                if "detailed_explanations" in question:
                    with st.expander("📖 보기별 해설 전체 보기"):
                        for choice in question["choices"]:
                            detail = question["detailed_explanations"].get(choice, "설명 없음")
                            st.markdown(f"**📝 {choice}**: {detail}")

            # 북마크 버튼
            if st.button("🔖 이 문제 북마크하기", key=f"bookmark_{index}"):
                if question not in st.session_state.bookmarks:
                    st.session_state.bookmarks.append(question)
                    st.success("⭐ 북마크에 추가되었습니다.")

            # 다음 문제 버튼
            if st.button("➡️ 다음 문제", key=f"next_{index}"):
                st.session_state.quiz_index += 1
                st.experimental_rerun()

            st.markdown(f"""
                <hr style='border: 0.5px solid #ddd;'>
                <h5 style='color:#2C3E50;'>📊 현재 점수: <span style='color:#27AE60'>{st.session_state.score}</span> / {st.session_state.total}</h5>
            """, unsafe_allow_html=True)

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

# 📊 통계 요약 (하단 고정)
st.markdown("""
    <hr>
    <div style='text-align:center'>
        <b>총 푼 문제 수:</b> {total} &nbsp;&nbsp;
        <b>정답 수:</b> {score} &nbsp;&nbsp;
        <b>정답률:</b> {round(score/total*100, 1) if total else 0}%
    </div>
""".format(score=st.session_state.score, total=st.session_state.total), unsafe_allow_html=True)
