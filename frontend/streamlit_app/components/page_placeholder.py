"""
Placeholder reutilizable para páginas en construcción.
Inyecta tema institucional y mensaje consistente sin lógica de negocio.
"""
import streamlit as st

from components.footer import render_footer
from config.theme import get_global_css


def render_page_placeholder(module_title: str) -> None:
    """
    Página genérica "en construcción" con identidad institucional.
    module_title: nombre del módulo (ej. "Registro Calificado").
    """
    st.markdown(get_global_css(), unsafe_allow_html=True)
    st.markdown(
        '<div style="padding-top: 1.75rem; margin-bottom: 0;"></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<p style="margin-top:0; margin-bottom:1rem; font-size:0.9rem; color: var(--men-text-muted);">'
        f'<strong>MEN</strong> — {module_title}</p>',
        unsafe_allow_html=True,
    )
    st.title(module_title)
    st.write("Módulo en construcción.")
    st.info(
        f"Aquí se visualizarán funciones, indicadores y servicios asociados a {module_title}."
    )
    render_footer()
