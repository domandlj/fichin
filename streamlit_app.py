import streamlit as st
from datetime import datetime, timedelta
from fichin import post_token
from streamlit_autorefresh import st_autorefresh

st.title("🪙 Fichin")

# 🧠 Session state init
for key in ["token", "expiry", "expander_open"]:
    if key not in st.session_state:
        st.session_state[key] = None if key != "expander_open" else True

# 🔁 Autorefresh if logged in
if st.session_state.token:
    st_autorefresh(interval=1000, key="token_timer")

# ⏳ Time remaining logic
remaining_text = ""
if st.session_state.token and st.session_state.expiry:
    now = datetime.now()
    remaining = st.session_state.expiry - now
    if remaining.total_seconds() <= 0:
        st.session_state.token = None
        st.session_state.expiry = None
        st.session_state.expander_open = True  # reopen if expired
        remaining_text = "❌ Token expired"
    else:
        minutes, seconds = divmod(int(remaining.total_seconds()), 60)
        remaining_text = f"{minutes:02d}:{seconds:02d}"

# 🧭 Manual expander toggle
col1, col2 = st.columns([1, 10])
with col1:
    if st.button("🔁 Toggle Login"):
        st.session_state.expander_open = not st.session_state.expander_open

# 🔐 Expander UI
expander_title = f"🔐 Sign In ({remaining_text})" if remaining_text else "🔐 Sign In"
if st.session_state.expander_open:
    with st.expander(expander_title, expanded=True):
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Sign In")

        if submitted:
            if username and password:
                st.session_state.token = post_token(username, password)
                st.session_state.expiry = datetime.now() + timedelta(minutes=10)
                st.session_state.expander_open = False
                st.success("Signed in successfully!")
                st.rerun()
            else:
                st.error("Please enter both username and password.")

# 💬 Token info
if st.session_state.token and st.session_state.expiry:
    now = datetime.now()
    remaining = st.session_state.expiry - now
    if remaining.total_seconds() <= 0:
        st.error("❌ Token expired.")
        st.session_state.token = None
        st.session_state.expiry = None
        st.session_state.expander_open = True
    else:
        st.code(st.session_state.token, language='text')
        minutes, seconds = divmod(int(remaining.total_seconds()), 60)
        time_left = f"{minutes:02d}:{seconds:02d}"
        if remaining.total_seconds() < 60:
            st.warning(f"⚠️ Less than a minute left: **{time_left}**")
        else:
            st.info(f"⏳ Token expires in **{time_left}**")
