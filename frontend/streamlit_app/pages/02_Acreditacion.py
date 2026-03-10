"""
Módulo Acreditación: hub con secciones internas (Dashboard, Consultas, Actividades, Reportes, Indicadores).
"""
import streamlit as st

from components.footer import render_footer
from components.section_placeholders import (
    render_actividades_placeholder,
    render_consultas_placeholder,
    render_dashboard_placeholder,
    render_indicadores_placeholder,
    render_reportes_placeholder,
)
from components.sidebar_misional import render_sidebar_misional
from config.theme import get_global_css

MODULE_ID = "acreditacion"
MODULE_TITLE = "Acreditación"
SECTION_KEY = f"{MODULE_ID}_section"

st.set_page_config(page_title=MODULE_TITLE, page_icon="🏛️", layout="wide")

if SECTION_KEY not in st.session_state:
    st.session_state[SECTION_KEY] = "dashboard"
st.session_state[SECTION_KEY] = st.session_state.get(
    f"{MODULE_ID}_nav_radio", st.session_state[SECTION_KEY]
)

st.markdown(get_global_css(), unsafe_allow_html=True)
render_sidebar_misional(
    module_id=MODULE_ID,
    module_title=MODULE_TITLE,
    current_section=st.session_state[SECTION_KEY],
    session_state_key=SECTION_KEY,
)

current = st.session_state[SECTION_KEY]
if current == "dashboard":
    render_dashboard_placeholder(MODULE_ID, MODULE_TITLE)
elif current == "consultas":
    render_consultas_placeholder(MODULE_TITLE)
elif current == "actividades":
    render_actividades_placeholder(MODULE_TITLE)
elif current == "reportes":
    render_reportes_placeholder(MODULE_TITLE)
elif current == "indicadores":
    render_indicadores_placeholder(MODULE_ID, MODULE_TITLE)

render_footer()
