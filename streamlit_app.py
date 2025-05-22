import streamlit as st
from datetime import datetime, timedelta
from fichin import post_token
from streamlit_autorefresh import st_autorefresh

# App title
st.title("🎮 Fichin")

# Initialize session state
if 'token' not in st.session_state:
    st.session_state.token = None
    st.session_state.expiry = None

# Refresh every 1 second if a token exists
if st.session_state.token:
    st_autorefresh(interval=1000, key="token_timer")

# Dynamic expander title
expander_title = "🔐 Sign In"
if st.session_state.expiry:
    expiry_time = st.session_state.expiry.strftime("%H:%M:%S")
    expander_title += f" (Token expires at {expiry_time})"

# Foldable Sign-In Section
with st.expander(expander_title, expanded=True):
    # Login form
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

    # Token display + countdown
    if st.session_state.token and st.session_state.expiry:
        st.code(st.session_state.token, language='text')
        now = datetime.now()
        remaining = st.session_state.expiry - now

        if remaining.total_seconds() <= 0:
            st.error("❌ Token expired.")
            st.session_state.token = None
            st.session_state.expiry = None
        else:
            # Calculate remaining time with ceil to avoid 00:00 when 0.9 seconds left
            remaining_seconds = int(remaining.total_seconds()) + 1
            minutes, seconds = divmod(remaining_seconds, 60)
            time_left = f"{minutes:02d}:{seconds:02d}"
            
            if remaining_seconds <= 60:
                st.warning(f"⚠️ Token expires in: **{seconds} seconds**")
            else:
                st.info(f"⏳ Token expires in: **{time_left}**")