"""
Router principal de la plataforma.
Control de acceso: si no hay sesión se muestra login; si hay sesión, el portal con navegación.
"""
from pathlib import Path

import streamlit as st

from auth.auth_service import is_authenticated
from auth.login_page import render_login_page
from components.footer import render_footer
from components.header import render_header
from components.layout import render_module_group
from config.navigation import MODULE_GROUPS
from config.theme import get_global_css

st.set_page_config(
    page_title="MEN - Plataforma de Gestión y Analítica de Datos",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(get_global_css(), unsafe_allow_html=True)

if not is_authenticated():
    render_login_page()
    st.stop()

# Cerrar sesión desde el enlace del footer (?logout=1)
if st.query_params.get("logout"):
    from auth.auth_service import logout

    logout()
    if "logout" in st.query_params:
        del st.query_params["logout"]  # deja la URL limpia (solo /) para el login
    st.rerun()

# Logo: buscar en assets (logo_MEN.png, logo.png, etc.)
assets_dir = Path(__file__).parent / "assets"
logo_path = None
for name in ("logo_MEN.png", "logo.png", "logo.svg", "logo.jpg"):
    p = assets_dir / name
    if p.is_file():
        logo_path = str(p)
        break


def home_page():
    """Portal principal: header, grupos de módulos y footer (con usuario y Cerrar sesión)."""
    render_header(logo_path=logo_path)
    for group_name, group in MODULE_GROUPS.items():
        render_module_group(group_name, group["modules"], columns_count=group["columns"])
    render_footer()


# Páginas visibles en el menú global
home = st.Page(home_page, title="Portal", icon="🏠", default=True)

registro = st.Page("pages/01_Registro_Calificado.py", title="Registro Calificado", icon="📘")
acreditacion = st.Page("pages/02_Acreditacion.py", title="Acreditación", icon="🏛️")
convalidaciones = st.Page("pages/03_Convalidaciones.py", title="Convalidaciones", icon="🌍")
pares = st.Page("pages/04_Pares_Academicos.py", title="Pares Académicos", icon="👥")
transversal = st.Page("pages/05_Area_Transversal.py", title="Área Transversal", icon="🔄")
subdireccion = st.Page("pages/06_Subdireccion.py", title="Subdirección", icon="📊")
conaces = st.Page("pages/07_Gestion_Conaces.py", title="Gestión Conaces", icon="📋")
normatividad = st.Page("pages/08_Normatividad.py", title="Normatividad", icon="📜")

gobierno = st.Page("pages/09_00_Gobierno_de_Datos.py", title="Gobierno de Datos", icon="🧭")

# Catálogo, Calidad, Linaje y Metadatos son vistas internas del módulo (no páginas globales).
pages = {
    "Portal": [home],
    "Módulos Misionales": [
        registro,
        acreditacion,
        convalidaciones,
        pares,
        transversal,
        subdireccion,
        conaces,
        normatividad,
    ],
    "Capacidades Estratégicas": [gobierno],
}

pg = st.navigation(pages, position="sidebar", expanded=True)
pg.run()
