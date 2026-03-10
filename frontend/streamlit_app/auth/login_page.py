"""
Pantalla de login institucional. Puerta de entrada al sistema.
"""
import streamlit as st

from auth.auth_service import login
from config.theme import get_global_css


def render_login_page() -> None:
    """
    Muestra la pantalla de login. Si el usuario envía credenciales correctas,
    hace rerun para que Home.py muestre el portal.
    """
    st.markdown(get_global_css(), unsafe_allow_html=True)

    st.markdown(
        """
        <div style="text-align: center; margin-bottom: 2rem;">
            <p style="font-size: 1.5rem; font-weight: 700; color: var(--men-primary); margin: 0;">
                Ministerio de Educación Nacional
            </p>
            <p style="font-size: 1.1rem; color: var(--men-text-muted); margin: 0.5rem 0 0 0;">
                Plataforma de Gestión y Analítica de Datos
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Guardar credenciales en el momento del clic (on_click corre cuando los inputs ya están en session_state)
    if "login_attempt" not in st.session_state:
        st.session_state.login_attempt = None

    def capture_and_login():
        u = (st.session_state.get("login_username") or "").strip().lower()
        p = (st.session_state.get("login_password") or "").strip()
        st.session_state.login_attempt = ("ok", u, p) if (u and p) else ("empty", u, p)

    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("**Iniciar sesión**")
            st.text_input("Usuario", key="login_username", placeholder="Nombre de usuario")
            st.text_input("Contraseña", type="password", key="login_password", placeholder="Contraseña")
            st.button("Ingresar", key="login_btn", on_click=capture_and_login)

            attempt = st.session_state.get("login_attempt")
            if attempt is not None:
                st.session_state.login_attempt = None  # consumir para no repetir
                status, u, p = attempt
                if status == "empty":
                    st.error("Ingrese usuario y contraseña.")
                elif login(u, p):
                    st.success("Bienvenido. Redirigiendo al portal...")
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos. Intente de nuevo.")

    st.markdown(
        """
        <div style="text-align: center; margin-top: 3rem; font-size: 0.85rem; color: var(--men-text-muted);">
            Subdirección de Aseguramiento de la Calidad
        </div>
        """,
        unsafe_allow_html=True,
    )
