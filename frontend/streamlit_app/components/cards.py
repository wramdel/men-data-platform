import streamlit as st


def render_module_card(title: str, icon: str) -> None:
    """
    Card de módulo con acento institucional (borde y hover).
    Navegación por el menú lateral; sin acción de clic en la card.
    """
    st.markdown(
        f"""
        <div class="men-module-card">
            <div class="men-card-icon">{icon}</div>
            <div class="men-card-title">{title}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )