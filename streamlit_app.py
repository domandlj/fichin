import streamlit as st
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# Dummy post_token function for testing
def post_token(username, password):
    return f"token-for-{username}"

# Initialize session state
if 'token' not in st.session_state:
    st.session_state.token = None
    st.session_state.expiry = None

# Trigger auto-refresh every second if token exists
if st.session_state.token:
    st_autorefresh(interval=1000, key="refresh_timer")

def get_time_left_str():
    if st.session_state.expiry:
        remaining = st.session_state.expiry - datetime.now()
        if remaining.total_seconds() > 0:
            minutes, seconds = divmod(int(remaining.total_seconds()), 60)
            return f"{minutes:02d}:{seconds:02d}"
    return "--:--"

st.title("🎮 Fichin")

# Show sign-in header with live timer if token exists
if st.session_state.token:
    time_left = get_time_left_str()
    header_text = f"🔐 Sign In (expires in {time_left})"
else:
    header_text = "🔐 Sign In"

st.markdown(f"### {header_text}")

with st.expander("Sign-In Form", expanded=True):
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Sign In")

    if submitted:
        if username and password:
            st.session_state.token = post_token(username, password)
            st.session_state.expiry = datetime.now() + timedelta(minutes=10)
            st.success("Signed in successfully!")
        else:
            st.error("Please enter both username and password.")

    if st.session_state.token and st.session_state.expiry:
        st.code(st.session_state.token, language='text')
        remaining = st.session_state.expiry - datetime.now()
        if remaining.total_seconds() <= 0:
            st.error("❌ Token expired.")
            st.session_state.token = None
            st.session_state.expiry = None
        else:
            if remaining.total_seconds() < 60:
                st.warning(f"⚠️ Less than a minute left: **{get_time_left_str()}**")
            else:
                st.info(f"⏳ Token expires in **{get_time_left_str()}**")
