"""
Módulo Gestión Conaces: hub con secciones internas (Dashboard, Consultas, Actividades, Reportes, Indicadores).

Se integra Rev. histórica como contenido del Dashboard y Verificación de hojas de vida
como contenido de la sección Consultas, usando el menú lateral estándar de secciones.
"""
import streamlit as st

from components.conaces.rev_historica_dashboard import render_rev_historica_dashboard
from components.conaces.verificacion_hv_workspace import render_verificacion_workspace
from components.footer import render_footer
from components.section_placeholders import (
    render_actividades_placeholder,
    render_indicadores_placeholder,
    render_reportes_placeholder,
)
from components.sidebar_misional import render_sidebar_misional
from config.theme import get_global_css

MODULE_ID = "conaces"
MODULE_TITLE = "Gestión Conaces"
SECTION_KEY = f"{MODULE_ID}_section"

st.set_page_config(page_title=MODULE_TITLE, page_icon="📋", layout="wide")

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
    # Dashboard = Rev. histórica
    render_rev_historica_dashboard()
elif current == "consultas":
    # Consultas = Verificación de hojas de vida (workspace funcional)
    render_verificacion_workspace()
elif current == "actividades":
    render_actividades_placeholder(MODULE_TITLE)
elif current == "reportes":
    render_reportes_placeholder(MODULE_TITLE)
elif current == "indicadores":
    render_indicadores_placeholder(MODULE_ID, MODULE_TITLE)

render_footer()
