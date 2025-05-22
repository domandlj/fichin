import streamlit as st
from datetime import datetime, timedelta
from fichin import post_token
from streamlit_autorefresh import st_autorefresh

# App title
st.title("🪙 Fichin")

# Initialize session state
if 'token' not in st.session_state:
    st.session_state.token = None
    st.session_state.expiry = None
    

# Initialize expander state
if "expander_open" not in st.session_state:
    st.session_state.expander_open = True

# 🔁 Refresh every second if token exists
if st.session_state.token:
    st_autorefresh(interval=1000, key="token_timer")

# Calculate remaining time
remaining_text = ""
if st.session_state.token and st.session_state.expiry:
    now = datetime.now()
    remaining = st.session_state.expiry - now
    if remaining.total_seconds() <= 0:
        st.session_state.token = None
        st.session_state.expiry = None
        remaining_text = "❌ Token expired"
    else:
        minutes, seconds = divmod(int(remaining.total_seconds()), 60)
        remaining_text = f"{minutes:02d}:{seconds:02d}"

# 🔐 Sign-In Section (form only inside expander)
expander_title = f"🔐 Sign In ({remaining_text})" if remaining_text else "🔐 Sign In"


with st.expander(expander_title, expanded=st.session_state.expander_open):
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Sign In")
    st.session_state.expander_open = True

    if submitted:
        if username and password:
            st.session_state.token = post_token(username, password)
            st.session_state.expiry = datetime.now() + timedelta(minutes=10)
            st.session_state.expander_open = False  # 👈 Collapse it after login
            st.success("Signed in successfully!")
            st.rerun()
        else:
            st.error("Please enter both username and password.")

# 💬 Token Info (outside expander)
if st.session_state.token and st.session_state.expiry:
    now = datetime.now()
    remaining = st.session_state.expiry - now

    if remaining.total_seconds() <= 0:
        st.error("❌ Token expired.")
        st.session_state.token = None
        st.session_state.expiry = None
    else:
        st.code(st.session_state.token, language='text')
        minutes, seconds = divmod(int(remaining.total_seconds()), 60)
        time_left = f"{minutes:02d}:{seconds:02d}"
        if remaining.total_seconds() < 60:
            st.warning(f"⚠️ Less than a minute left: **{time_left}**")
        else:
            st.info(f"⏳ Token expires in **{time_left}**")
