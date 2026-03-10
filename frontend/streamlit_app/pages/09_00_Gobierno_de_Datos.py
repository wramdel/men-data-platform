"""
Módulo Gobierno de Datos: una sola página con vistas internas (hub + Catálogo, Calidad, Linaje, Metadatos).
El sidebar global solo muestra "Gobierno de Datos"; los submódulos se eligen dentro de esta página.
"""
import streamlit as st

from components.footer import render_footer
from components.governance_module_header import render_governance_module_header
from components.kpi_metrics import render_kpi_metrics
from components.sidebar_governance import render_sidebar_governance
from components.source_selector import render_source_selector
from components.submodule_card import render_submodule_card
from config.theme import get_global_css
from governance_views import (
    render_calidad_view,
    render_catalogo_view,
    render_linaje_view,
    render_metadatos_view,
)
from services.governance_mock import get_hub_metrics, get_submodulos_hub

st.set_page_config(
    page_title="Gobierno de Datos",
    page_icon="🧭",
    layout="wide",
)

if "governance_view" not in st.session_state:
    st.session_state["governance_view"] = "hub"
# Sincronizar vista con el menú radio (el cambio de opción hace rerun automático)
st.session_state["governance_view"] = st.session_state.get(
    "gov_nav_radio", st.session_state["governance_view"]
)

st.markdown(get_global_css(), unsafe_allow_html=True)
render_sidebar_governance(current_view=st.session_state["governance_view"])

current = st.session_state["governance_view"]

if current == "hub":
    render_governance_module_header(
        title="Gobierno de Datos",
        subtitle="Gestión de la calidad, trazabilidad, catalogación y control de los activos de información de la plataforma.",
    )
    fuente = render_source_selector(key="hub_source", label="Fuente")
    metrics = get_hub_metrics(fuente)
    render_kpi_metrics(metrics, columns_count=4)
    st.markdown("---")
    st.markdown("**Capacidades**")
    submodulos = get_submodulos_hub()
    cols = st.columns(2)
    for idx, sm in enumerate(submodulos):
        with cols[idx % 2]:
            render_submodule_card(
                title=sm["title"],
                description=sm["description"],
                icon=sm["icon"],
                view_id=sm["view_id"],
                key=f"hub_{idx}",
            )
elif current == "catalogo":
    render_catalogo_view()
elif current == "calidad":
    render_calidad_view()
elif current == "linaje":
    render_linaje_view()
elif current == "metadatos":
    render_metadatos_view()

render_footer()
