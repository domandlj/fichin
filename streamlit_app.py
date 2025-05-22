import streamlit as st
from datetime import datetime, timedelta
from fichin import post_token, mostrar_estado_cuenta, get_valores
import pandas as pd

# App title
st.title("🪙 Fichin")

# 🧠 Session state init
if 'token' not in st.session_state:
    st.session_state.token = None
    st.session_state.expiry = None


# 🚨 Manual refresh button
refresh_clicked = st.button("🗘 Check Token Info")

# ⏱️ Remaining time calculation (only when refreshed)
remaining_text = ""
if refresh_clicked and st.session_state.token and st.session_state.expiry:
    now = datetime.now()
    remaining = st.session_state.expiry - now
    if remaining.total_seconds() <= 0:
        st.session_state.token = None
        st.session_state.expiry = None
        remaining_text = "❌ Token expired"
    else:
        minutes, seconds = divmod(int(remaining.total_seconds()), 60)
        remaining_text = f"{minutes:02d}:{seconds:02d}"

# 🔐 Sign-In Section
expander_title = "🔐 Sign In"
with st.expander(expander_title, expanded=False):
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Sign In")
    
    if submitted:
        if username and password:
            st.session_state.token = post_token(username, password)["access_token"]
            st.session_state.expiry = datetime.now() + timedelta(minutes=10)
            st.success("Signed in successfully!")
            st.rerun()
        else:
            st.error("Please enter both username and password.")

# 💬 Token Info
if st.session_state.token and st.session_state.expiry:
    if refresh_clicked:
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
    else:
        st.info("Click 🔁 Refresh Token Info to check token status.")

# 📊 Estado Cuenta

def show_cuentas(df_cuentas):
    # 🎯 Resumen visual de saldos y títulos valorizados por cuenta
    col1, col2 = st.columns(2)

    with col1:
        cuenta_pesos = df_cuentas[df_cuentas["Moneda"] == "peso_Argentino"]
        if not cuenta_pesos.empty:
            st.metric(
                label="💵 Saldo en Pesos",
                value=f"${cuenta_pesos['Saldo'].values[0]:,.2f}"
            )
            st.metric(
                label="📈 Títulos Valorizados en Pesos",
                value=f"${cuenta_pesos['Títulos Valorizados'].values[0]:,.2f}"
            )

    with col2:
        cuenta_usd = df_cuentas[df_cuentas["Moneda"] == "dolar_Estadounidense"]
        if not cuenta_usd.empty:
            st.metric(
                label="💲 Saldo en USD",
                value=f"USD {cuenta_usd['Saldo'].values[0]:,.2f}"
            )
            st.metric(
                label="📉 Títulos Valorizados en USD",
                value=f"USD {cuenta_usd['Títulos Valorizados'].values[0]:,.2f}")
            



def mostrar_cartera(token: str):
    """
    Muestra la cartera de inversiones en ARS como una tabla con formato agradable y un gráfico de torta.
    """
    valores = get_valores(token)
    
    if not valores:
        st.warning("No hay valores en cartera.")
        return

    # Convertimos a DataFrame para trabajar más fácil
    df_valores = pd.DataFrame(valores)

    # Formateo
    df_valores["monto"] = df_valores["monto"].map(lambda x: round(x, 2))
    df_valores["peso (%)"] = df_valores["peso"].map(lambda x: round(x * 100, 2))
    df_valores.drop(columns=["peso"], inplace=True)

    # Ordenamos de mayor a menor participación
    df_valores.sort_values(by="monto", ascending=False, inplace=True)

    # Mostramos en dos columnas
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📋 Cartera de Inversiones en Pesos")
        st.dataframe(df_valores.rename(columns={
            "ticker": "Ticker",
            "monto": "Monto ($)",
            "peso (%)": "Peso (%)"
        }), use_container_width=True)

    with col2:
        st.subheader("📊 Distribución")
        st.plotly_chart(
            {
                "data": [
                    {
                        "type": "pie",
                        "labels": df_valores["ticker"],
                        "values": df_valores["monto"],
                        "hole": 0.4,
                        "textinfo": "label+percent"
                    }
                ],
                "layout": {"margin": {"l": 0, "r": 0, "b": 0, "t": 0}}
            },
            use_container_width=True
        )



if st.session_state.token:
    st.subheader("📊 Estado Cuenta")

    try:
        df_cuentas, df_saldos, df_estadisticas = mostrar_estado_cuenta(st.session_state.token)
        
        show_cuentas(df_cuentas)

        with st.expander("🔎 Resumen de Cuentas", expanded=False):
            st.dataframe(df_cuentas)

        with st.expander("📂 Detalle por Liquidación", expanded=False):
            st.dataframe(df_saldos)

        with st.expander("📈 Estadísticas", expanded=False):
            st.dataframe(df_estadisticas)

    except Exception as e:
        st.error(f"⚠️ No se pudo obtener el estado de cuenta: {e}")
    
    st.subheader("Cartera")
    mostrar_cartera(st.session_state.token)

