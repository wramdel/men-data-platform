"""
Selector de fuente (Todas / SNIES / SACES) reutilizable en el módulo Gobierno de Datos.
"""
import streamlit as st

from services.governance_mock import FUENTES


def render_source_selector(
    key: str = "governance_source",
    label: str = "Fuente",
) -> str:
    """
    Muestra un selectbox con Todas, SNIES, SACES.
    Retorna el valor seleccionado (string).
    """
    selected = st.selectbox(
        label,
        options=FUENTES,
        key=key,
        index=0,
    )
    return selected
