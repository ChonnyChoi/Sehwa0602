import streamlit as st
import random

# 🎨 웹앱 페이지 설정
st.set_page_config(
    page_title="MBTI 직업 추천기 💼✨",
    page_icon="🧠",
    layout="wide",
)

# 🎉 타이틀
st.markdown("""
    <h1 style='text-align: center; color: #FF69B4;'>🌟 MBTI 기반 직업 추천기 💼</h1>
    <h4 style='text-align: center; color: #FFB6C1;'>당신의 성격에 딱 맞는 직업을 찾아보세요! 🚀</h4>
""", unsafe_allow_html=True)

# 🎯 MBTI 리스트
mbti_list = [
    "INTJ", "INTP", "ENTJ", "ENTP",
    "INFJ", "INFP", "ENFJ", "ENFP",
    "ISTJ", "ISFJ", "ESTJ", "ESFJ",
    "ISTP", "ISFP", "ESTP", "ESFP"
]

# 📘 MBTI 설명 + 직업 추천
mbti_info = {
    "INTJ": {
        "desc": "전략적인 계획자 🧠🔮",
        "jobs": ["데이터 사이언티스트", "전략 컨설턴트", "AI 엔지니어"]
    },
    "INFP": {
        "desc": "이상주의적 중재자 🌱💫",
        "jobs": ["작가 ✍️", "심리상담가 🧘", "UX 디자이너 🎨"]
    },
    "ENTP": {
        "desc": "창의적인 혁신가 ⚡️🎩",
        "jobs": ["창업가 🚀", "마케팅 디렉터 📣", "프로덕트 매니저 🧩"]
    },
    "ISFJ": {
        "desc": "따뜻한 수호자 🌼🛡️",
        "jobs": ["간호사 🏥", "교사 📚", "사회복지사 🤝"]
    },
    # 나머지 MBTI는 필요에 따라 추가 가능
}

# 🎛️ 사용자 입력: MBTI 선택
selected_mbti = st.selectbox("당신의 MBTI를 선택하세요! 💡", mbti_list)

if selected_mbti:
    info = mbti_info.get(selected_mbti, {
        "desc": "아직 준비 중인 MBTI입니다. 😅",
        "jobs": ["준비 중..."]
    })

    # 📦 추천 결과 박스
    st.markdown("---")
    st.markdown(f"<h2 style='color:#00CED1;'>{selected_mbti} - {info['desc']}</h2>", unsafe_allow_html=True)

    st.subheader("✨ 추천 직업 리스트:")
    for job in info['jobs']:
        st.markdown(f"- 🌟 **{job}**")

    st.markdown("---")

# 🎨 사이드바
st.sidebar.title("🔧 추가 기능")
st.sidebar.markdown("📎 [MBTI 테스트 하러 가기](https://www.16personalities.com/ko)")
st.sidebar.markdown("💌 개발자: [GitHub 프로필](https://github.com/yourprofile)")
st.sidebar.markdown("🖼️ 다양한 테마 추가 예정!")

# 🎆 하단 문구
st.markdown("<p style='text-align:center; color:gray;'>Made with ❤️ by 진로 AI</p>", unsafe_allow_html=True)
