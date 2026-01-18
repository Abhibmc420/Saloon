
import streamlit as st

st.title("My Streamlit App")
if st.button("Click me"):
    st.session_state.count = st.session_state.get("count", 0) + 1
    st.write(f"Clicked {st.session_state.count} times")
