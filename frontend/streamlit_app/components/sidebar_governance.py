"""
Menú lateral del módulo Gobierno de Datos.
Menú de opciones (st.radio), no botones; navegación por estado.
Reutilizable para otros módulos con subsecciones.
"""
import streamlit as st

from config.theme import get_module_submenu_css

# (id_vista, etiqueta, icono) — orden de las secciones del módulo
INTERNAL_VIEWS = [
    ("hub", "Gobierno de Datos", "🧭"),
    ("catalogo", "Catálogo de Datos", "📋"),
    ("calidad", "Calidad de Datos", "✅"),
    ("linaje", "Linaje", "🔄"),
    ("metadatos", "Metadatos", "📐"),
]


def render_sidebar_governance(
    *,
    current_view: str,
    session_state_key: str = "governance_view",
) -> None:
    """
    Muestra en el sidebar un expander con las secciones del módulo como menú (radio).
    Al cambiar la opción, Streamlit hace rerun; la vista se sincroniza al inicio de la página.
    """
    with st.sidebar:
        st.markdown(get_module_submenu_css(), unsafe_allow_html=True)
        with st.expander("**Gobierno de Datos** — Secciones", expanded=True):
            st.markdown(
                '<div class="men-module-submenu-marker" style="display:none" aria-hidden="true"></div>',
                unsafe_allow_html=True,
            )
            options = [v[0] for v in INTERNAL_VIEWS]
            labels = {v[0]: f"{v[2]}  {v[1]}" for v in INTERNAL_VIEWS}
            idx = next(
                (i for i, v in enumerate(INTERNAL_VIEWS) if v[0] == (current_view or "hub")),
                0,
            )
            st.radio(
                label="Secciones",
                options=options,
                format_func=labels.get,
                index=idx,
                key="gov_nav_radio",
                label_visibility="collapsed",
            )