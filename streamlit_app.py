import streamlit as st
from datetime import datetime, timedelta
from fichin import post_token
from streamlit_autorefresh import st_autorefresh
import math  # Added for proper ceiling calculation

# App title
st.title("🎮 Fichin")

# Initialize session state
if 'token' not in st.session_state:
    st.session_state.token = None
    st.session_state.expiry = None

# Refresh every 1 second if a token exists
if st.session_state.token:
    st_autorefresh(interval=1000, key="token_timer")

# Foldable Sign-In Section
def get_expander_title():
    if st.session_state.expiry:
        expiry_time = st.session_state.expiry.strftime("%H:%M:%S")
        return f"🔐 Sign In (Token expires at {expiry_time})"
    return "🔐 Sign In"

with st.expander(get_expander_title(), expanded=True):
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
            # Corrected countdown calculation using math.ceil
            remaining_seconds = math.ceil(remaining.total_seconds())
            minutes, seconds = divmod(remaining_seconds, 60)
            
            if remaining_seconds > 60:
                time_left = f"{minutes:02d}:{seconds:02d}"
                st.info(f"⏳ Token expires in: **{time_left}**")
            else:
                st.warning(f"⚠️ Token expires in: **{seconds} seconds**")