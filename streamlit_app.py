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

# Force refresh every second when token exists
if st.session_state.token:
    st_autorefresh(interval=1000, key="fichin_refresh", limit=None)

# Dynamic expander title
def get_title():
    if st.session_state.expiry:
        remaining = st.session_state.expiry - datetime.now()
        if remaining.total_seconds() > 0:
            expiry_time = st.session_state.expiry.strftime("%H:%M:%S")
            return f"🔐 Signed In (Expires at {expiry_time})"
    return "🔐 Sign In"

# Foldable section
with st.expander(get_title(), expanded=True):
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

    # Token display and countdown
    if st.session_state.token and st.session_state.expiry:
        st.code(st.session_state.token, language='text')
        now = datetime.now()
        remaining = st.session_state.expiry - now

        if remaining.total_seconds() <= 0:
            st.error("❌ Token expired.")
            st.session_state.token = None
            st.session_state.expiry = None
        else:
            # Real-time countdown calculation
            total_seconds = int(remaining.total_seconds())
            mins, secs = divmod(total_seconds, 60)
            timer = f"{mins:02d}:{secs:02d}"
            
            if total_seconds > 60:
                st.info(f"⏳ Time remaining: **{timer}**")
            else:
                st.warning(f"⚠️ **{secs} seconds** remaining")

# Force UI update by re-rendering the expander
st.experimental_rerun()