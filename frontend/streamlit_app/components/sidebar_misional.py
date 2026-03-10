"""
Menú lateral interno para módulos misionales (Dashboard, Consultas, Actividades, Reportes, Indicadores).
Mismo patrón visual que sidebar_governance: radio, estilo ligero, sin páginas globales.
"""
import streamlit as st

from config.misional_sections import MISIONAL_SECTIONS
from config.theme import get_module_submenu_css


def render_sidebar_misional(
    *,
    module_id: str,
    module_title: str,
    current_section: str,
    session_state_key: str,
) -> None:
    """
    Muestra en el sidebar un expander con las 5 secciones estándar del módulo misional.
    module_id: identificador único (ej. "registro") para la key del radio.
    module_title: título que se muestra en el expander (ej. "Registro Calificado").
    current_section: sección activa (dashboard, consultas, etc.).
    session_state_key: clave de session_state donde se guarda la sección (ej. "registro_section").
    """
    radio_key = f"{module_id}_nav_radio"
    with st.sidebar:
        st.markdown(get_module_submenu_css(), unsafe_allow_html=True)
        with st.expander(f"**{module_title}** — Secciones", expanded=True):
            st.markdown(
                '<div class="men-module-submenu-marker" style="display:none" aria-hidden="true"></div>',
                unsafe_allow_html=True,
            )
            options = [s[0] for s in MISIONAL_SECTIONS]
            labels = {s[0]: f"{s[2]}  {s[1]}" for s in MISIONAL_SECTIONS}
            idx = next(
                (i for i, s in enumerate(MISIONAL_SECTIONS) if s[0] == (current_section or "dashboard")),
                0,
            )
            st.radio(
                label="Secciones",
                options=options,
                format_func=labels.get,
                index=idx,
                key=radio_key,
                label_visibility="collapsed",
            )
