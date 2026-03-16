"""
Workspace de verificación de hojas de vida para Gestión CONACES.

Panel izquierdo: controles y verificación.
Panel derecho: visor de PDF demo (EJEMPLO DE BBDD.pdf).
"""
import base64
from pathlib import Path
from urllib.parse import quote

import streamlit as st
import streamlit.components.v1 as components

from services.conaces_history_service import (
    build_master_conaces,
    normalize_document_value,
)


@st.cache_data(ttl=300)
def _get_master():
    return build_master_conaces()


def _get_project_root() -> Path:
    # streamlit_app/components/conaces -> components -> streamlit_app -> frontend -> men-data-platform
    here = Path(__file__).resolve()
    return here.parent.parent.parent.parent.parent


def _render_pdf_panel() -> None:
    """
    Panel derecho de PDF:
    - visor embebido
    - botón de descarga
    - opción para abrir en pestaña nueva (local)
    """
    project_root = _get_project_root()
    pdf_path = project_root / "data" / "raw" / "gconases" / "EJEMPLO DE BBDD.pdf"

    if not pdf_path.is_file():
        st.warning(
            "No se encontró el archivo de ejemplo `EJEMPLO DE BBDD.pdf` en `data/raw/gconases/`. "
            "Cuando esté disponible, se mostrará aquí el visor de hoja de vida."
        )
        return

    file_size_kb = pdf_path.stat().st_size / 1024

    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
    b64_pdf = base64.b64encode(pdf_bytes).decode("utf-8")
    pdf_display = f'''
    <iframe
        src="data:application/pdf;base64,{b64_pdf}"
        width="100%"
        height="800px"
        style="border:none;"
        type="application/pdf">
    </iframe>
    '''
    components.html(pdf_display, height=820, scrolling=True)

    st.caption(
        f"Archivo: `EJEMPLO DE BBDD.pdf` — tamaño aproximado: {file_size_kb:,.1f} KB"
    )

    # Mensaje informativo y opciones alternativas
    st.info(
        "Si el visor embebido es bloqueado por el navegador, use **Descargar PDF** o **Abrir PDF en otra pestaña**."
    )

    # Botón de descarga directa
    st.download_button(
        "Descargar PDF de ejemplo",
        data=pdf_bytes,
        file_name="EJEMPLO_DE_BBDD.pdf",
        mime="application/pdf",
        key="hv_pdf_download",
    )

    # En local, ofrecer un enlace file:// para abrir en una pestaña nueva.
    # Codificamos espacios y caracteres especiales para que el enlace sea clicable.
    file_url = "file://" + quote(str(pdf_path))
    st.markdown(f"[Abrir PDF en una pestaña nueva]({file_url})", unsafe_allow_html=False)


def render_verificacion_workspace() -> None:
    """Vista principal de Verificación de hojas de vida."""
    st.subheader("Verificación de hojas de vida — Gestión CONACES")

    col_left, col_right = st.columns([1, 2], gap="large")

    with col_left:
        st.markdown("### Panel de verificación")
        doc_in = st.text_input("Número de cédula / documento", placeholder="Ej: 12345678", key="hv_doc_query")
        buscar = st.button("Buscar en histórico", type="primary", key="hv_buscar")

        df_master = _get_master()
        doc = normalize_document_value(doc_in)

        if buscar:
            if not doc:
                st.warning("Ingrese un documento válido para iniciar la verificación.")
            elif df_master is None or df_master.empty:
                st.warning("No hay información histórica disponible para verificación en este momento.")
            elif "documento" not in df_master.columns:
                st.warning("La información histórica no contiene la columna `documento`.")
            else:
                df_doc = df_master[
                    df_master["documento"].fillna("").astype(str).str.strip() == doc
                ].copy()
                if df_doc.empty:
                    st.info("No se encontraron registros históricos para este documento.")
                else:
                    st.success(f"Se encontró al menos un proceso histórico para el documento {doc}.")
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
                    cols_show = [c for c in cols_show if c in df_doc.columns]
                    st.markdown("**Resumen del proceso histórico**")
                    st.dataframe(df_doc[cols_show].head(5), use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown("### Validación documental")
        doc_pres = st.radio(
            "Documento de identidad presentado",
            options=["Sí", "No"],
            key="hv_doc_presentado",
            horizontal=True,
        )
        sop_acad = st.radio(
            "Soportes académicos",
            options=["Sí", "No"],
            key="hv_soportes_acad",
            horizontal=True,
        )
        sop_exp = st.radio(
            "Soportes de experiencia",
            options=["Sí", "No"],
            key="hv_soportes_exp",
            horizontal=True,
        )
        hv_legible = st.radio(
            "Hoja de vida legible/completa",
            options=["Sí", "No"],
            key="hv_legible",
            horizontal=True,
        )

        st.markdown("### Criterios de evaluación")
        st.caption("Primera versión manual; en el futuro se integrarán reglas automáticas.")

        st.markdown("### Observaciones")
        obs = st.text_area("Observaciones del evaluador", key="hv_observaciones", height=120)

        st.markdown("### Resultado preliminar")
        concepto = st.selectbox(
            "Concepto preliminar",
            options=["", "Cumple", "No cumple", "Requiere revisión"],
            key="hv_concepto",
        )

        # Botón de guardar (sin persistencia todavía, solo placeholder de flujo)
        st.button("Registrar verificación (no persiste aún)", key="hv_guardar")

    with col_right:
        st.markdown("### Hoja de vida (PDF demo)")
        _render_pdf_panel()

