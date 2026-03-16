"""
Vista de consultas históricas para Gestión CONACES (Rev. histórica).

Permite buscar por documento y mostrar:
- Procesos/convocatorias asociados (agrupados)
- Resumen maestro (build_master_conaces) por documento
- Trazabilidad por fases/archivos (build_traza_conaces) por documento y grupo
"""
import pandas as pd
import streamlit as st

from services.conaces_history_service import build_master_conaces, build_traza_conaces, normalize_document_value


@st.cache_data(ttl=300)
def _get_master():
    return build_master_conaces()


@st.cache_data(ttl=300)
def _get_traza():
    return build_traza_conaces()


def render_rev_historica_consultas() -> None:
    st.subheader("Consultas — Revisión histórica (CONACES)")
    doc_in = st.text_input("Número de cédula / documento", key="conaces_doc_query", placeholder="Ej: 12345678")
    doc = normalize_document_value(doc_in)

    if not doc:
        st.caption("Ingrese un documento para consultar el histórico.")
        return

    df_master = _get_master()
    df_traza = _get_traza()

    if df_traza.empty:
        st.warning("No hay trazabilidad disponible. Verifique los Excel en `data/raw/gconases/`.")
        return

    # Filtrar trazabilidad por documento (la traza es la fuente principal para saber si aparece o no)
    if "documento" not in df_traza.columns:
        st.warning("La trazabilidad no contiene la columna `documento`.")
        return

    df_doc = df_traza[df_traza["documento"] == doc].copy()
    if df_doc.empty:
        st.info("No se encontraron registros para ese documento en el histórico.")
        return

    # Preparar agrupación por proceso (convocatoria, sala) sin concatenar strings
    if "convocatoria" not in df_doc.columns:
        df_doc["convocatoria"] = ""
    if "sala" not in df_doc.columns:
        df_doc["sala"] = ""

    df_doc["_conv_key"] = df_doc["convocatoria"].fillna("").astype(str).str.strip()
    df_doc["_sala_key"] = df_doc["sala"].fillna("").astype(str).str.strip()
    df_doc["_conv_key"] = df_doc["_conv_key"].replace("", "SIN_CONVOCATORIA")
    df_doc["_sala_key"] = df_doc["_sala_key"].replace("", "SIN_SALA")

    grupos = list(pd.unique(list(zip(df_doc["_conv_key"], df_doc["_sala_key"]))))
    st.success(
        f"Se encontraron {len(df_doc)} registro(s) históricos y {len(grupos)} proceso(s)/grupo(s) "
        f"para el documento {doc}."
    )

    # Resumen maestro: una fila por documento (si existe)
    if df_master is None or df_master.empty or "documento" not in df_master.columns:
        df_master_doc = pd.DataFrame()
    else:
        df_master_doc = df_master[df_master["documento"].fillna("").astype(str).str.strip() == doc].copy()

    # Orden de fases más robusto (preparado para fase_orden si existiera)
    fase_order_map = {"F1": 1, "F2": 2, "F3": 3, "F4": 4, "F5": 5}

    for conv_key, sala_key in sorted(grupos, key=lambda t: (t[0], t[1])):
        df_g = df_doc[(df_doc["_conv_key"] == conv_key) & (df_doc["_sala_key"] == sala_key)].copy()

        title = (
            f"Proceso: {conv_key}" if conv_key and conv_key != "SIN_CONVOCATORIA" else "Proceso: (sin convocatoria)"
        )
        if sala_key and sala_key != "SIN_SALA":
            title = f"{title} — {sala_key}"

        with st.expander(title, expanded=True):
            st.markdown("**Resumen (maestro consolidado)**")
            if not df_master_doc.empty:
                # Intentar filtrar por convocatoria/sala; si queda vacío, caer al resumen del documento
                df_m_all = df_master_doc.copy()
                df_m = df_m_all.copy()
                if "convocatoria" in df_m.columns and conv_key and conv_key != "SIN_CONVOCATORIA":
                    df_m = df_m[df_m["convocatoria"].fillna("").astype(str).str.strip() == conv_key]
                if "sala" in df_m.columns and sala_key and sala_key != "SIN_SALA":
                    df_m = df_m[df_m["sala"].fillna("").astype(str).str.strip() == sala_key]
                if df_m.empty:
                    df_m = df_m_all

                cols_show = [
                    "documento",
                    "convocatoria",
                    "sala",
                    "estado_inscripcion",
                    "puntaje_fase_3",
                    "resultado_fase_3",
                    "puntaje_prueba",
                    "puntaje_entrevista",
                    "puntaje_final",
                    "resultado_final",
                ]
                cols_show = [c for c in cols_show if c in df_m.columns]
                st.dataframe(df_m[cols_show].head(5), use_container_width=True, hide_index=True)
            else:
                st.caption("No hay fila maestra disponible para este documento.")

            st.markdown("**Trazabilidad por fases / archivos**")
            cols_traza = [
                "fase",
                "archivo_origen",
                "convocatoria",
                "sala",
                "estado_inscripcion",
                "puntaje_fase_3",
                "resultado_fase_3",
                "puntaje_prueba",
                "puntaje_entrevista",
                "puntaje_final",
                "resultado_final",
            ]
            cols_traza = [c for c in cols_traza if c in df_g.columns]
            # Preparar orden robusto por fase
            if "fase" in df_g.columns:
                if "fase_orden" not in df_g.columns:
                    df_g = df_g.copy()
                    df_g["fase_orden"] = (
                        df_g["fase"].fillna("").astype(str).map(fase_order_map).fillna(999).astype(int)
                    )
                sort_cols = ["fase_orden", "fase", "archivo_origen"] if "archivo_origen" in df_g.columns else [
                    "fase_orden",
                    "fase",
                ]
            else:
                sort_cols = ["archivo_origen"] if "archivo_origen" in df_g.columns else []

            df_sorted = df_g.sort_values(sort_cols, ascending=True) if sort_cols else df_g
            st.dataframe(
                df_sorted[cols_traza],
                use_container_width=True,
                hide_index=True,
            )

