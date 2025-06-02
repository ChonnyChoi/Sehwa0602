import streamlit as st
import random

st.title("🎲 행운의 숫자 맞추기 게임 🍀")

if 'target' not in st.session_state:
    st.session_state.target = random.randint(1, 10)
    st.session_state.attempts = 0

guess = st.number_input("1부터 10까지 숫자를 입력하세요!", min_value=1, max_value=10, step=1)

if st.button("맞춰보기!"):
    st.session_state.attempts += 1
    if guess == st.session_state.target:
        st.success(f"🎉 축하합니다! {guess}가 맞는 숫자에요! {st.session_state.attempts}번 만에 맞추셨네요!")
        if st.button("다시하기"):
            st.session_state.target = random.randint(1, 10)
            st.session_state.attempts = 0
    elif guess < st.session_state.target:
        st.warning("좀 더 큰 숫자에요! 🔼")
    else:
        st.warning("좀 더 작은 숫자에요! 🔽")

st.write(f"시도 횟수: {st.session_state.attempts}")
