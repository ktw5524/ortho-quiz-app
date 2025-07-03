import streamlit as st
import json
import os

# 페이지 설정
st.set_page_config(page_title="정형외과 국가고시 문제은행", layout="wide")

# 문제 불러오기 함수
@st.cache_data
def load_questions():
    path = "question.json"  # 같은 디렉토리에 있는 경우
    # path = "data/question.json"  # 폴더에 있을 경우 이 경로 사용
    if not os.path.exists(path):
        st.error(f"{path} 파일이 존재하지 않습니다.")
        return []

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("questions", [])

# 문제 불러오기
questions = load_questions()

# 제목
st.title("📘 정형외과 전문의 국가고시 문제은행")

if not questions:
    st.warning("문제 데이터가 없습니다. 'question.json' 파일을 확인해주세요.")
else:
    for idx, q in enumerate(questions):
        st.markdown(f"### ❓ 문제 {idx + 1}")
        st.write(q["question"])

        # 보기 선택
        user_choice = st.radio(
            "선택지",
            options=q["options"],
            key=f"radio_{idx}"
        )

        # 정답 확인 버튼
        if st.button("정답 확인", key=f"btn_{idx}"):
            correct_idx = q["answer"]
            correct_option = q["options"][correct_idx]

            if user_choice == correct_option:
                st.success(f"정답입니다! ✅ ({correct_option})")
            else:
                st.error(f"틀렸습니다. ❌ 정답은: {correct_option}")

            # 해설 보기
            with st.expander("📖 해설 보기"):
                st.markdown(f"**전체 해설**: {q['explanation']['전체해설']}")
                st.markdown("**선지별 해설**:")
                for i, opt in enumerate(q["options"]):
                    detail = q['explanation']['선지해설'].get(str(i + 1), "")
                    st.markdown(f"- **{i + 1}. {opt}** — {detail}")

        st.divider()
