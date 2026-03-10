"""
Vistas internas del módulo Gobierno de Datos (Catálogo, Calidad, Linaje, Metadatos).
Se usan desde la página única 09_00; no son páginas globales del sidebar.
"""
import streamlit as st
import pandas as pd

from components.governance_module_header import render_governance_module_header
from components.source_selector import render_source_selector
from services.governance_mock import get_catalogo, get_calidad, get_linaje, get_metadatos


def render_catalogo_view(key_prefix: str = "catalogo") -> None:
    render_governance_module_header(
        title="Catálogo de Datos",
        subtitle="Inventario de datasets disponibles, su origen y su uso.",
    )
    fuente = render_source_selector(key=f"{key_prefix}_source", label="Fuente")
    datos = get_catalogo(fuente)
    if datos:
        df = pd.DataFrame(datos)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No hay datasets para la fuente seleccionada.")


def render_calidad_view(key_prefix: str = "calidad") -> None:
    render_governance_module_header(
        title="Calidad de Datos",
        subtitle="Monitoreo de consistencia, completitud y confiabilidad de los activos de información.",
    )
    fuente = render_source_selector(key=f"{key_prefix}_source", label="Fuente")
    datos = get_calidad(fuente)
    if datos:
        df = pd.DataFrame(datos)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No hay reglas de calidad para la fuente seleccionada.")


def render_linaje_view(key_prefix: str = "linaje") -> None:
    render_governance_module_header(
        title="Linaje",
        subtitle="Seguimiento del recorrido de los datos desde el origen hasta reportes o dashboards.",
    )
    fuente = render_source_selector(key=f"{key_prefix}_source", label="Fuente")
    nodos = get_linaje(fuente)
    cols = st.columns(len(nodos))
    for idx, nodo in enumerate(nodos):
        with cols[idx]:
            st.markdown(
                f"""
                <div style="
                    border: 1px solid var(--men-card-border);
                    border-left: 4px solid var(--men-primary);
                    border-radius: 8px;
                    padding: 1rem;
                    text-align: center;
                    background: rgba(255,255,255,0.02);
                ">
                    <div style="font-size: 0.75rem; color: var(--men-text-muted); margin-bottom: 0.25rem;">{nodo["etapa"]}</div>
                    <div style="font-weight: 700;">{nodo["nombre"]}</div>
                    <div style="font-size: 0.85rem; margin-top: 0.25rem;">{nodo["descripcion"]}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    if len(nodos) > 1:
        st.caption("Flujo de datos: de izquierda a derecha.")


def render_metadatos_view(key_prefix: str = "metadatos") -> None:
    render_governance_module_header(
        title="Metadatos",
        subtitle="Definiciones técnicas y de contexto de los activos de información.",
    )
    fuente = render_source_selector(key=f"{key_prefix}_source", label="Fuente")
    datos = get_metadatos(fuente)
    if datos:
        df = pd.DataFrame(datos)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No hay metadatos para la fuente seleccionada.")
