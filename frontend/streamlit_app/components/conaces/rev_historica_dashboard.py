"""
Dashboard de revisión histórica para Gestión CONACES.

Usa el maestro consolidado por documento de conaces_history_service.
"""
import pandas as pd
import streamlit as st

from components.kpi_metrics import render_kpi_metrics
from components.conaces.rev_historica_consultas import render_rev_historica_consultas
from services.conaces_history_service import build_master_conaces


@st.cache_data(ttl=300)
def _get_master():
    """Obtiene el maestro consolidado de CONACES (cacheado)."""
    return build_master_conaces()


def render_rev_historica_dashboard() -> None:
    """Renderiza Rev. histórica (Dashboard + Consultas)."""
    tab_dash, tab_cons = st.tabs(["Dashboard", "Consultas"])

    with tab_cons:
        render_rev_historica_consultas()

    with tab_dash:
        _render_dashboard()


def _render_dashboard() -> None:
    """Dashboard histórico (KPIs, embudo, distribuciones)."""
    df = _get_master()

    st.subheader("Revisión histórica — Gestión CONACES")
    if df.empty:
        st.warning(
            "No se encontraron datos consolidados de CONACES. "
            "Verifique que existan los archivos en `data/raw/gconases/` y que el mapeo de columnas sea correcto."
        )
        return

    # KPIs sobre documento único (una fila por aspirante en el maestro)
    total_inscritos = df["documento"].nunique(dropna=True)

    estado = df.get("estado_inscripcion")
    if estado is not None:
        estado_str = estado.fillna("").astype(str)
        estado_upper = estado_str.str.upper().str.strip()
        mask_no_cumple = estado_upper.str.contains("NO CUMPLE", na=False)
        mask_cumple = estado_upper.str.contains("CUMPLE", na=False) & ~mask_no_cumple
        cumple = int(mask_cumple.sum())
        no_cumple = int(mask_no_cumple.sum())
    else:
        estado_upper = None
        cumple = 0
        no_cumple = 0

    # Evaluados en fase 3: tienen puntaje o resultado de fase 3
    puntaje_f3 = df["puntaje_fase_3"] if "puntaje_fase_3" in df.columns else None
    resultado_f3 = df["resultado_fase_3"] if "resultado_fase_3" in df.columns else None
    mask_f3 = None
    if puntaje_f3 is not None:
        mask_f3 = puntaje_f3.notna()
    if resultado_f3 is not None:
        res_f3_str = resultado_f3.fillna("").astype(str).str.strip()
        mask_res = res_f3_str != ""
        mask_f3 = mask_res if mask_f3 is None else (mask_f3 | mask_res)
    evaluados_fase3 = int(mask_f3.sum()) if mask_f3 is not None else 0

    resultado_final = df.get("resultado_final")
    if resultado_final is not None:
        res_fin_str = resultado_final.fillna("").astype(str).str.strip()
        mask_res_final = res_fin_str != ""
        con_resultado_final = int(mask_res_final.sum())
    else:
        con_resultado_final = 0

    kpis = [
        {"label": "Total inscritos (documentos únicos)", "value": total_inscritos, "icon": "🧑‍🎓"},
        {"label": "Cumple requisitos", "value": cumple, "icon": "✅"},
        {"label": "No cumple requisitos", "value": no_cumple, "icon": "⚠️"},
        {"label": "Evaluados en fase 3", "value": evaluados_fase3, "icon": "📊"},
        {"label": "Con resultado final", "value": con_resultado_final, "icon": "🏁"},
    ]
    render_kpi_metrics(kpis, columns_count=5)

    # Validación visual de posibles duplicados por documento
    if "documento" in df.columns and df["documento"].duplicated().any():
        st.warning(
            "Se encontraron documentos duplicados en el maestro consolidado. "
            "Revise la configuración de las fases o la limpieza de datos."
        )

    st.markdown("---")
    st.markdown("**Embudo del proceso**")
    funnel_data = [
        {"Etapa": "Inscritos", "Cantidad": total_inscritos},
        {"Etapa": "Cumple requisitos", "Cantidad": cumple},
        {"Etapa": "Evaluados fase 3", "Cantidad": evaluados_fase3},
        {"Etapa": "Con resultado final", "Cantidad": con_resultado_final},
    ]
    funnel_df = pd.DataFrame(funnel_data)
    st.dataframe(funnel_df, use_container_width=True, hide_index=True)
    st.bar_chart(funnel_df.set_index("Etapa"))

    st.markdown("---")
    st.markdown("**Distribución por sala**")
    if "sala" in df.columns:
        salas = df["sala"].fillna("").astype(str).str.strip()
        salas = salas[salas != ""]
        sala_counts = salas.value_counts().reset_index()
        sala_counts.columns = ["Sala", "Cantidad"]
        st.dataframe(sala_counts, use_container_width=True, hide_index=True)
        if not sala_counts.empty:
            st.bar_chart(sala_counts.set_index("Sala"))
    else:
        st.caption("No hay información de salas disponible.")

    st.markdown("---")
    st.markdown("**Distribución por estado de inscripción**")
    if estado_upper is not None:
        estado_clean = estado_upper.replace("NAN", "").replace("", pd.NA)
        estado_clean = estado_clean.dropna()
        estado_counts = estado_clean.value_counts().reset_index()
        estado_counts.columns = ["Estado inscripción", "Cantidad"]
        st.dataframe(estado_counts, use_container_width=True, hide_index=True)
        if not estado_counts.empty:
            st.bar_chart(estado_counts.set_index("Estado inscripción"))
    else:
        st.caption("No hay información de estado de inscripción disponible.")

    st.markdown("---")
    st.markdown("**Muestra de registros consolidados**")
    cols_relevantes = [
        "documento",
        "convocatoria",
        "sala",
        "estado_inscripcion",
        "puntaje_fase_3",
        "resultado_fase_3",
        "puntaje_final",
        "resultado_final",
    ]
    cols_existentes = [c for c in cols_relevantes if c in df.columns]
    if cols_existentes:
        st.dataframe(df[cols_existentes].head(300), use_container_width=True, hide_index=True)
    else:
        st.dataframe(df.head(300), use_container_width=True, hide_index=True)

