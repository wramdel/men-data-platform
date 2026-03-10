"""
Bloque de KPIs reutilizable para el módulo Gobierno de Datos.
"""
import streamlit as st


def render_kpi_metrics(metrics: list[dict], columns_count: int = 4) -> None:
    """
    Muestra métricas en columnas.
    metrics: lista de dicts con 'label', 'value' y opcional 'icon'.
    """
    cols = st.columns(columns_count)
    for idx, m in enumerate(metrics):
        with cols[idx % columns_count]:
            icon = m.get("icon", "")
            st.metric(
                label=f"{icon} {m['label']}" if icon else m["label"],
                value=m["value"],
            )
