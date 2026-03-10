"""
Vistas placeholder para las secciones estándar de módulos misionales.
Contenido alineado con los tres ejes: información rápida, consolidación y seguimiento a funcionarios.
"""
import streamlit as st
import pandas as pd

from components.kpi_metrics import render_kpi_metrics
from services.misional_mock import (
    get_actividades_placeholder,
    get_consultas_results_placeholder,
    get_dashboard_kpis,
    get_indicadores_avance_por_responsable,
    get_indicadores_distribucion_estado,
    get_indicadores_seguimiento_kpis,
    get_reportes_placeholder,
)


def _section_header(module_title: str, section_title: str, subtitle: str) -> None:
    """Encabezado común: línea MEN — Módulo, título de sección y descripción."""
    st.markdown(
        f'<p style="margin:0 0 0.25rem 0; font-size:0.9rem; color: var(--men-text-muted);">'
        f"<strong>MEN</strong> — {module_title}</p>",
        unsafe_allow_html=True,
    )
    st.title(section_title)
    st.caption(subtitle)


def render_dashboard_placeholder(module_id: str, module_title: str) -> None:
    """Dashboard: visión ejecutiva rápida — volumen de casos, estados y alertas."""
    _section_header(
        module_title,
        "Dashboard",
        "Visión ejecutiva rápida: volumen de casos, estados generales y alertas del proceso.",
    )
    kpis = get_dashboard_kpis(module_id)
    render_kpi_metrics(kpis, columns_count=4)
    st.markdown("---")
    st.markdown("**Resumen del módulo**")
    st.info("Gráficos y resúmenes visuales del proceso. (Placeholder — información rápida para consulta y toma de decisiones.)")


def render_consultas_placeholder(module_title: str) -> None:
    """Consultas: exploración y búsqueda de información."""
    _section_header(
        module_title,
        "Consultas",
        "Explore y busque información: instituciones, programas, trámites, expedientes. Filtre por estado o período.",
    )
    with st.expander("**Filtros de búsqueda**", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            st.date_input("Fecha desde", key="consultas_fecha_desde")
            st.selectbox("Estado", ["Todos", "En trámite", "En revisión", "Completado"], key="consultas_estado")
        with c2:
            st.date_input("Fecha hasta", key="consultas_fecha_hasta")
            st.text_input("Expediente / Referencia", key="consultas_ref")
        st.text_input("Institución o programa", key="consultas_institucion")
        st.button("Buscar", key="consultas_buscar")
    st.markdown("**Resultados**")
    rows = get_consultas_results_placeholder()
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def render_actividades_placeholder(module_title: str) -> None:
    """Actividades: gestión operativa y seguimiento del trabajo diario por responsable."""
    _section_header(
        module_title,
        "Actividades",
        "Gestión operativa y seguimiento del trabajo diario: tareas pendientes, en curso, vencidas y responsables asignados.",
    )
    items = get_actividades_placeholder()
    df = pd.DataFrame(items)
    df = df.rename(columns={
        "responsable": "Responsable",
        "actividad": "Actividad",
        "fecha_limite": "Fecha límite",
        "estado": "Estado",
        "prioridad": "Prioridad",
    })
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.caption("Lista operativa de tareas asignadas a funcionarios. (Placeholder — seguimiento a funcionarios.)")


def render_reportes_placeholder(module_title: str) -> None:
    """Reportes: salida formal y consolidada del módulo."""
    _section_header(
        module_title,
        "Reportes",
        "Salida formal y consolidada: reportes exportables, listados, históricos, por responsable o por estado.",
    )
    reportes = get_reportes_placeholder()
    st.dataframe(pd.DataFrame(reportes), use_container_width=True, hide_index=True)
    st.caption("(Placeholder: en producción se habilitará la descarga o visualización.)")


def render_indicadores_placeholder(module_id: str, module_title: str) -> None:
    """Indicadores: seguimiento a funcionarios con tareas asignadas, carga y desempeño operativo."""
    _section_header(
        module_title,
        "Indicadores",
        "Seguimiento a funcionarios con tareas asignadas: carga de trabajo, desempeño operativo, tiempos de atención y avance por responsable.",
    )
    kpis = get_indicadores_seguimiento_kpis(module_id)
    render_kpi_metrics(kpis, columns_count=3)
    st.markdown("---")
    st.markdown("**Avance por responsable**")
    avance = get_indicadores_avance_por_responsable()
    st.dataframe(pd.DataFrame(avance), use_container_width=True, hide_index=True)
    st.markdown("**Distribución de actividades por estado**")
    dist = get_indicadores_distribucion_estado()
    st.dataframe(pd.DataFrame(dist), use_container_width=True, hide_index=True)
    st.caption("Herramienta de seguimiento de gestión y de funcionarios involucrados en el proceso.")
