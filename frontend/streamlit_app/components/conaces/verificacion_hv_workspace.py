"""
Workspace de verificación de hojas de vida para Gestión CONACES.

Panel izquierdo: controles y verificación.
Panel derecho: visor de PDF demo (EJEMPLO DE BBDD.pdf).
"""
import base64
from pathlib import Path
from urllib.parse import quote
from typing import List, Tuple

import streamlit as st
import streamlit.components.v1 as components

from services.conaces_history_service import (
    build_master_conaces,
    normalize_document_value,
)

SALAS_CONACES = [
    "Educación",
    "Artes y Humanidades",
    "Ciencias Sociales, Periodismo e Información",
    "Administración de Empresas y Derecho",
    "Ciencias Naturales, Matemáticas y Estadística",
    "TIC",
    "Ingeniería, Industria y Construcción",
    "Agropecuaria, Silvicultura, Pesca y Veterinaria",
    "Salud y Bienestar",
    "Técnicos Profesionales y Tecnológicos",
    "Trámites Institucionales",
]


def validar_estudios(sala: str, data: dict) -> Tuple[bool, str]:
    """
    Valida el bloque de Estudios según reglas normativas por sala.

    Retorna: (cumple, mensaje explicativo)
    """
    sala_norm = (sala or "").strip().upper()

    titulo_exterior = bool(data.get("titulo_exterior"))
    convalidado = bool(data.get("convalidado"))
    if titulo_exterior and not convalidado:
        return False, "No cumple: título del exterior sin convalidación."

    profesional = bool(data.get("profesional"))
    maestria = bool(data.get("maestria"))
    doctorado = bool(data.get("doctorado"))
    especialidad_medica = bool(data.get("especialidad_medica"))
    tecnico = bool(data.get("tecnico"))
    tecnologo = bool(data.get("tecnologo"))
    certificados = bool(data.get("certificados"))
    duracion_certificados = float(data.get("duracion_certificados") or 0)
    profesional_en_educacion = bool(data.get("profesional_en_educacion"))
    posgrado_en_educacion = bool(data.get("posgrado_en_educacion"))

    has_posgrado = maestria or doctorado

    # SALA EDUCACIÓN
    if sala_norm in ("EDUCACIÓN", "EDUCACION"):
        ok = profesional_en_educacion and posgrado_en_educacion
        return (
            ok,
            "Cumple: título profesional y posgrado en el campo de educación."
            if ok
            else "No cumple: requiere título profesional y posgrado en el campo de educación.",
        )

    # SALA SALUD Y BIENESTAR
    if sala_norm == "SALUD Y BIENESTAR":
        ok = profesional and (has_posgrado or especialidad_medica)
        return (
            ok,
            "Cumple: profesional y (maestría, doctorado o especialidad médica)."
            if ok
            else "No cumple: requiere profesional y (maestría, doctorado o especialidad médica).",
        )

    # SALA TÉCNICOS Y TECNOLÓGICOS
    if sala_norm in ("TÉCNICOS PROFESIONALES Y TECNOLÓGICOS", "TECNICOS PROFESIONALES Y TECNOLOGICOS"):
        ok = (tecnico or tecnologo) and (has_posgrado or (certificados and duracion_certificados >= 5))
        return (
            ok,
            "Cumple: (técnico o tecnólogo) y (maestría/doctorado o certificados >= 5 años)."
            if ok
            else "No cumple: requiere (técnico o tecnólogo) y (maestría/doctorado o certificados >= 5 años).",
        )

    # TODAS LAS DEMÁS SALAS
    ok = profesional and has_posgrado
    return (
        ok,
        "Cumple: profesional y (maestría o doctorado)." if ok else "No cumple: requiere profesional y (maestría o doctorado).",
    )


def validar_experiencia(sala: str, data: dict) -> Tuple[bool, str, List[str]]:
    """
    Valida Experiencia por rutas/condiciones.

    Retorna: (cumple, mensaje_resumen, rutas_cumplidas)
    """
    sala_norm = (sala or "").strip().lower()

    # Fuente de verdad: rutas calculadas en la UI (r1..r7 o ti1..ti3)
    if sala_norm in ("trámites institucionales", "tramites institucionales"):
        ti1 = bool(data.get("ti1"))
        ti2 = bool(data.get("ti2"))
        ti3 = bool(data.get("ti3"))
        rutas = []
        if ti1:
            rutas.append("Ruta TI-1")
        if ti2:
            rutas.append("Ruta TI-2")
        if ti3:
            rutas.append("Ruta TI-3")
        cumple = len(rutas) >= 1
        msg = (
            "Cumple regla TI (al menos una condición verificada)."
            if cumple
            else "No cumple regla TI: no se verifican condiciones suficientes."
        )
        return cumple, msg, rutas

    r1 = bool(data.get("r1"))
    r2 = bool(data.get("r2"))
    r3 = bool(data.get("r3"))
    r4 = bool(data.get("r4"))
    r5 = bool(data.get("r5"))
    r6 = bool(data.get("r6"))
    r7 = bool(data.get("r7"))
    rutas = []
    for idx, ok in enumerate([r1, r2, r3, r4, r5, r6, r7], start=1):
        if ok:
            rutas.append(f"Ruta {idx}")

    cumple = len(rutas) >= 2
    msg = (
        f"Cumple: {len(rutas)} rutas verificadas (mínimo 2)."
        if cumple
        else f"No cumple: {len(rutas)} rutas verificadas (mínimo 2)."
    )
    return cumple, msg, rutas


@st.cache_data(ttl=300)
def _get_master():
    return build_master_conaces()


def _get_project_root() -> Path:
    # streamlit_app/components/conaces -> components -> streamlit_app -> frontend -> men-data-platform
    here = Path(__file__).resolve()
    return here.parent.parent.parent.parent.parent


@st.cache_data(ttl=300)
def _get_pdf_demo() -> Tuple[Path, bytes, str, float] | Tuple[None, None, None, None]:
    """Carga el PDF demo una vez y lo devuelve para reutilizarlo en visor/acciones."""
    project_root = _get_project_root()
    pdf_path = project_root / "data" / "raw" / "gconases" / "EJEMPLO DE BBDD.pdf"
    if not pdf_path.is_file():
        return None, None, None, None
    pdf_bytes = pdf_path.read_bytes()
    b64_pdf = base64.b64encode(pdf_bytes).decode("utf-8")
    file_size_kb = pdf_path.stat().st_size / 1024
    return pdf_path, pdf_bytes, b64_pdf, file_size_kb


def _render_open_pdf_button(b64_pdf: str) -> None:
    """Abre el PDF en otra pestaña usando Blob (sin file://)."""
    open_html = f"""
    <div style="margin-top:0.75rem;">
      <button
        onclick="(function() {{
          const b64 = '{b64_pdf}';
          const byteCharacters = atob(b64);
          const byteNumbers = new Array(byteCharacters.length);
          for (let i = 0; i < byteCharacters.length; i++) {{
            byteNumbers[i] = byteCharacters.charCodeAt(i);
          }}
          const byteArray = new Uint8Array(byteNumbers);
          const blob = new Blob([byteArray], {{type: 'application/pdf'}});
          const url = URL.createObjectURL(blob);
          window.open(url, '_blank');
          setTimeout(function() {{ URL.revokeObjectURL(url); }}, 60000);
        }})();"
        style="padding:0.65rem 0.9rem; border-radius:8px; border:1px solid rgba(0,0,0,0.15); background:#f3f4f6; cursor:pointer; display:inline-block;">
        Abrir PDF en otra ventana
      </button>
    </div>
    """
    components.html(open_html, height=90)


def _render_pdf_panel() -> None:
    """
    Panel derecho de PDF:
    - visor embebido
    - botón de descarga
    - opción para abrir en pestaña nueva (local)
    """
    pdf_path, pdf_bytes, b64_pdf, file_size_kb = _get_pdf_demo()
    if pdf_path is None:
        st.warning(
            "No se encontró el archivo de ejemplo `EJEMPLO DE BBDD.pdf` en `data/raw/gconases/`. "
            "Cuando esté disponible, se mostrará aquí el visor de hoja de vida."
        )
        return
    pdf_display = f'''
    <iframe
        src="data:application/pdf;base64,{b64_pdf}"
        width="100%"
        height="600px"
        style="border:none; border-radius: 8px;"
        type="application/pdf">
    </iframe>
    '''
    components.html(pdf_display, height=620, scrolling=True)

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

    # Botón de abrir queda en el panel izquierdo por UX.


def render_verificacion_workspace() -> None:
    """Vista principal de Verificación de hojas de vida."""
    st.subheader("Verificación de hojas de vida — Gestión CONACES")

    col_left, col_right = st.columns([2, 1], gap="large")

    with col_left:
        st.markdown("### Panel de verificación")
        doc_in = st.text_input("Número de cédula / documento", placeholder="Ej: 12345678", key="hv_doc_query")
        buscar = st.button("Buscar en histórico", type="primary", key="hv_buscar")

        # Acceso al PDF debajo del botón Buscar (sin depender de file://)
        _pdf_path, _pdf_bytes, _b64_pdf, _file_size_kb = _get_pdf_demo()
        if _pdf_path is not None and _b64_pdf:
            _render_open_pdf_button(_b64_pdf)

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

        st.markdown("---")
        st.markdown("### Selección de sala")
        sala = st.selectbox(
            "Sala (obligatorio)",
            options=[""] + SALAS_CONACES,
            key="hv_sala",
        )

        st.markdown("## 📘 Estudios")
        is_educacion = (sala or "").strip().lower() == "educación"
        c1, c2 = st.columns(2)
        with c1:
            # Para Sala Educación: ocultar checkboxes genéricos y mostrar solo validación específica
            profesional = False
            maestria = False
            doctorado = False
            especialidad_medica = False
            if not is_educacion:
                profesional = st.checkbox("Profesional", key="hv_est_profesional")
                maestria = st.checkbox("Maestría", key="hv_est_maestria")
                doctorado = st.checkbox("Doctorado", key="hv_est_doctorado")
                especialidad_medica = st.checkbox("Especialidad médica", key="hv_est_especialidad_medica")
            titulo_exterior = st.checkbox("Título exterior", key="hv_est_titulo_exterior")
            convalidado = False
            if titulo_exterior:
                convalidado = st.checkbox("Convalidado", key="hv_est_convalidado")

            profesional_en_educacion = False
            posgrado_en_educacion = False
            if is_educacion:
                st.markdown("**Educación — validación específica**")
                profesional_en_educacion = st.checkbox(
                    "Título profesional en el campo de educación",
                    key="hv_est_prof_en_educacion",
                )
                posgrado_en_educacion = st.checkbox(
                    "Posgrado en el campo de educación",
                    key="hv_est_posgrado_en_educacion",
                )
        with c2:
            tecnico = st.checkbox("Técnico", key="hv_est_tecnico")
            tecnologo = st.checkbox("Tecnólogo", key="hv_est_tecnologo")
            certificados = st.checkbox("Certificados", key="hv_est_certificados")
            duracion_certificados = st.number_input(
                "Duración certificados (años)",
                min_value=0.0,
                step=0.5,
                value=0.0,
                key="hv_est_duracion_certificados",
            )

        estudios_data = {
            "profesional": profesional,
            "maestria": maestria,
            "doctorado": doctorado,
            "especialidad_medica": especialidad_medica,
            "tecnico": tecnico,
            "tecnologo": tecnologo,
            "certificados": certificados,
            "duracion_certificados": duracion_certificados,
            "titulo_exterior": titulo_exterior,
            "convalidado": convalidado,
            "profesional_en_educacion": profesional_en_educacion,
            "posgrado_en_educacion": posgrado_en_educacion,
        }

        # UX: no evaluar hasta seleccionar sala
        cumple_estudios = False
        msg_estudios = ""
        estado_estudios = "—"

        if not sala:
            st.warning("Seleccione una sala para validar estudios.")
        else:
            cumple_estudios, msg_estudios = validar_estudios(sala, estudios_data)

            if not cumple_estudios:
                estado_estudios = "No cumple ❌"
                st.error(f"**Estudios:** No cumple. {msg_estudios}")
            else:
                # Cumple académico, pero en operación requiere soportes documentales
                if sop_acad == "No":
                    estado_estudios = "Requiere soporte documental ⚠️"
                    st.warning(
                        f"**Estudios:** Cumple requisitos académicos, pero falta soporte académico documental. {msg_estudios}"
                    )
                else:
                    estado_estudios = "Cumple ✅"
                    st.success(f"**Estudios:** Cumple. {msg_estudios}")

            if (sala or "").strip().lower() == "educación":
                st.caption("Para esta sala solo se consideran títulos en el campo de educación.")

        st.markdown("## 🧑‍🏫 Experiencia")

        # UX: no evaluar hasta seleccionar sala
        cumple_experiencia = False
        msg_experiencia = ""
        rutas_cumplidas: List[str] = []
        estado_experiencia = "—"

        if not sala:
            st.warning("Seleccione una sala para validar experiencia.")
        else:
            sala_norm = (sala or "").strip().lower()
            if sala_norm == "técnicos profesionales y tecnológicos":
                st.caption(
                    "Para esta sala, la experiencia profesoral y de dirección debe corresponder a programas técnicos profesionales, "
                    "tecnológicos o ciclos propedéuticos."
                )

            def _route_status(ok: bool) -> None:
                if ok:
                    st.success("Cumple")
                else:
                    st.caption("No cumple")

            # --- Rutas especiales para Trámites Institucionales ---
            if sala_norm in ("trámites institucionales", "tramites institucionales"):
                st.caption("Debe cumplir al menos 1 ruta.")
                st.markdown("### 🔹 Rutas especiales — Trámites Institucionales")

                st.markdown("### Ruta TI-1 — Rector/Vicerrector")
                anios_rector_vicerrector = st.number_input(
                    "Años Rector/Vicerrector",
                    min_value=0.0,
                    step=0.5,
                    value=0.0,
                    key="hv_exp_ti_anios_rector_vicerrector",
                )
                ti1 = anios_rector_vicerrector >= 4
                _route_status(ti1)
                st.divider()

                st.markdown("### Ruta TI-2 — Dirección / Planeación / Calidad / Financiero")
                anios_direccion_planeacion_calidad_financiero = st.number_input(
                    "Años en cargos Dirección/Planeación/Calidad/Financiero",
                    min_value=0.0,
                    step=0.5,
                    value=0.0,
                    key="hv_exp_ti_anios_dir_planeacion_calidad_fin",
                )
                ti2 = anios_direccion_planeacion_calidad_financiero >= 5
                _route_status(ti2)
                st.divider()

                st.markdown("### Ruta TI-3 — Combinación de cargos")
                ti3 = (anios_rector_vicerrector + anios_direccion_planeacion_calidad_financiero) >= 5
                _route_status(ti3)

                rutas_ui = []
                if ti1:
                    rutas_ui.append("Ruta TI-1")
                if ti2:
                    rutas_ui.append("Ruta TI-2")
                if ti3:
                    rutas_ui.append("Ruta TI-3")

                st.markdown(f"**Rutas cumplidas:** {len(rutas_ui)} de 3")
                if rutas_ui:
                    st.markdown("\n".join([f"- {r}" for r in rutas_ui]))

                experiencia_data = {"ti1": ti1, "ti2": ti2, "ti3": ti3}
            else:
                st.caption("Debe cumplir al menos 2 rutas.")
                # --- Rutas generales (7) ---
                st.markdown("### 🔹 Rutas de experiencia")

                st.markdown("### Ruta 1 — Docencia + Posgrado")
                c1, c2 = st.columns(2)
                with c1:
                    r1_anios_docencia_total = st.number_input(
                        "Años docencia total",
                        min_value=0.0,
                        step=0.5,
                        value=0.0,
                        key="hv_exp_r1_anios_docencia_total",
                    )
                with c2:
                    r1_anios_docencia_posgrado = st.number_input(
                        "Años docencia en posgrado",
                        min_value=0.0,
                        step=0.5,
                        value=0.0,
                        key="hv_exp_r1_anios_docencia_posgrado",
                    )
                r1 = (r1_anios_docencia_total >= 5) and (r1_anios_docencia_posgrado >= 2)
                _route_status(r1)
                st.divider()

                st.markdown("### Ruta 2 — Docencia + Investigación")
                c1, c2 = st.columns(2)
                with c1:
                    r2_anios_docencia_total = st.number_input(
                        "Años docencia total",
                        min_value=0.0,
                        step=0.5,
                        value=0.0,
                        key="hv_exp_r2_anios_docencia_total",
                    )
                with c2:
                    r2_experiencia_investigacion = st.checkbox(
                        "Experiencia en investigación",
                        key="hv_exp_r2_investigacion",
                    )
                r2 = (r2_anios_docencia_total >= 5) and bool(r2_experiencia_investigacion)
                _route_status(r2)
                st.divider()

                st.markdown("### Ruta 3 — Trámites")
                c1, c2 = st.columns(2)
                with c1:
                    r3_tramites_rc_o_institucionales = st.number_input(
                        "Trámites RC/institucionales (conteo)",
                        min_value=0,
                        step=1,
                        value=0,
                        key="hv_exp_r3_tramites_rc_inst",
                    )
                with c2:
                    r3_tramites_acreditacion = st.number_input(
                        "Trámites de acreditación (conteo)",
                        min_value=0,
                        step=1,
                        value=0,
                        key="hv_exp_r3_tramites_acreditacion",
                    )
                r3 = (int(r3_tramites_rc_o_institucionales) >= 4) or (int(r3_tramites_acreditacion) >= 2)
                _route_status(r3)
                st.divider()

                st.markdown("### Ruta 4 — Sala / Banco elegibles")
                c1, c2 = st.columns(2)
                with c1:
                    r4_anios_integrante_sala_conaces = st.number_input(
                        "Años como integrante de sala CONACES",
                        min_value=0.0,
                        step=0.5,
                        value=0.0,
                        key="hv_exp_r4_anios_integrante_sala",
                    )
                with c2:
                    r4_sesiones_banco_elegibles = st.number_input(
                        "Sesiones banco de elegibles (conteo)",
                        min_value=0,
                        step=1,
                        value=0,
                        key="hv_exp_r4_sesiones_banco",
                    )
                r4 = (r4_anios_integrante_sala_conaces >= 1) or (int(r4_sesiones_banco_elegibles) >= 4)
                _route_status(r4)
                st.divider()

                st.markdown("### Ruta 5 — Docencia + Ejercicio profesional")
                c1, c2 = st.columns(2)
                with c1:
                    r5_anios_docencia_total = st.number_input(
                        "Años docencia total",
                        min_value=0.0,
                        step=0.5,
                        value=0.0,
                        key="hv_exp_r5_anios_docencia_total",
                    )
                with c2:
                    r5_anios_ejercicio_profesional = st.number_input(
                        "Años de ejercicio profesional",
                        min_value=0.0,
                        step=0.5,
                        value=0.0,
                        key="hv_exp_r5_anios_ejercicio_prof",
                    )
                r5 = (r5_anios_docencia_total >= 3) and (r5_anios_ejercicio_profesional >= 5)
                _route_status(r5)
                st.divider()

                st.markdown("### Ruta 6 — Docencia + Dirección académica")
                c1, c2 = st.columns(2)
                with c1:
                    r6_anios_docencia_total = st.number_input(
                        "Años docencia total",
                        min_value=0.0,
                        step=0.5,
                        value=0.0,
                        key="hv_exp_r6_anios_docencia_total",
                    )
                with c2:
                    r6_anios_direccion_academica = st.number_input(
                        "Años de dirección académica",
                        min_value=0.0,
                        step=0.5,
                        value=0.0,
                        key="hv_exp_r6_anios_dir_acad",
                    )
                r6 = (r6_anios_docencia_total >= 3) and (r6_anios_direccion_academica >= 5)
                _route_status(r6)
                st.divider()

                st.markdown("### Ruta 7 — Diseño o gestión curricular")
                r7_anios_diseno_o_gestion_curricular = st.number_input(
                    "Años de diseño/gestión curricular",
                    min_value=0.0,
                    step=0.5,
                    value=0.0,
                    key="hv_exp_r7_anios_diseno_gestion",
                )
                r7 = r7_anios_diseno_o_gestion_curricular >= 5
                _route_status(r7)

                rutas_ui = [f"Ruta {i}" for i, ok in enumerate([r1, r2, r3, r4, r5, r6, r7], start=1) if ok]
                st.markdown(f"**Rutas cumplidas:** {len(rutas_ui)} de 7")
                if rutas_ui:
                    st.markdown("\n".join([f"- {r}" for r in rutas_ui]))

                # Fuente de verdad para el backend: booleanos por ruta visibles en la UI
                experiencia_data = {"r1": r1, "r2": r2, "r3": r3, "r4": r4, "r5": r5, "r6": r6, "r7": r7}

            cumple_experiencia, msg_experiencia, rutas_cumplidas = validar_experiencia(sala, experiencia_data)

            # Resultado final (manteniendo backend validar_experiencia)
            if not cumple_experiencia:
                estado_experiencia = "No cumple ❌"
                st.error(f"**Experiencia:** No cumple. {msg_experiencia}")
            else:
                if sop_exp == "No":
                    estado_experiencia = "Requiere soporte documental ⚠️"
                    st.warning(
                        f"**Experiencia:** Cumple requisitos, pero falta soporte documental de experiencia. {msg_experiencia}"
                    )
                else:
                    estado_experiencia = "Cumple ✅"
                    st.success(f"**Experiencia:** Cumple. {msg_experiencia}")

        st.markdown("## 🔬 Investigación")
        st.info("Este bloque será implementado en la siguiente fase.")
        investigacion_mock = st.selectbox(
            "Resultado de investigación (mock)",
            options=["", "Cumple", "No cumple", "No aplica", "Requiere revisión"],
            key="hv_inv_mock",
        )

        st.markdown("### Observaciones")
        obs = st.text_area("Observaciones del evaluador", key="hv_observaciones", height=120)

        st.markdown("### Resultado preliminar")
        st.markdown(f"**Estado de Estudios (automático):** {estado_estudios}")
        st.markdown(f"**Estado de Experiencia (automático):** {estado_experiencia}")
        st.caption("Nota: el resultado final dependerá también de Investigación.")
        concepto = st.selectbox(
            "Concepto preliminar",
            options=["", "Cumple", "No cumple", "Requiere revisión"],
            key="hv_concepto",
        )

        # Botón de guardar (sin persistencia todavía, solo placeholder de flujo)
        st.button("Registrar verificación (no persiste aún)", key="hv_guardar")

    with col_right:
        _render_pdf_panel()

