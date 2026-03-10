"""
Encabezado reutilizable para páginas del módulo Gobierno de Datos.
La página debe inyectar get_global_css() antes de llamar a este componente.
"""
import streamlit as st


def render_governance_module_header(title: str, subtitle: str) -> None:
    """Muestra título y subtítulo de página del módulo con estilo institucional."""
    st.markdown(
        '<div style="padding-top: 1rem; margin-bottom: 0.5rem;"></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<p style="margin:0 0 0.25rem 0; font-size:0.9rem; color: var(--men-text-muted);">'
        f'<strong>MEN</strong> — Gobierno de Datos</p>',
        unsafe_allow_html=True,
    )
    st.title(title)
    st.caption(subtitle)
