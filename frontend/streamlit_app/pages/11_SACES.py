"""
SACES: placeholder del módulo de analítica sobre procesos de aseguramiento de la calidad.
Sin datos reales integrados; página institucional en preparación.
"""
import streamlit as st

from components.footer import render_footer
from components.header import render_header
from config.theme import get_global_css

PAGE_TITLE = "SACES"
PAGE_ICON = "📋"

st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout="wide")
st.markdown(get_global_css(), unsafe_allow_html=True)

render_header(logo_path=None)

st.title(f"{PAGE_ICON} {PAGE_TITLE}")
st.markdown("Sistema de Aseguramiento de la Calidad de la Educación Superior.")
st.divider()

st.info(
    "**Módulo en preparación.** Esta sección integrará próximamente analítica sobre procesos "
    "de aseguramiento de la calidad de la educación superior."
)
st.markdown(
    """
    En esta espacio se dispondrá de consultas y reportes asociados a SACES, en línea con la 
    plataforma de gestión y analítica de datos de la Subdirección de Aseguramiento de la Calidad.
    """
)

render_footer()
