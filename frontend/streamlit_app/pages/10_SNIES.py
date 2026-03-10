"""
SNIES: consulta sobre Instituciones y Programas (datos reales desde Excel).
Secciones: Resumen, Instituciones, Programas, Reportes. Opcional: programas por institución seleccionada.
"""
import streamlit as st

from components.footer import render_footer
from components.header import render_header
from components.kpi_metrics import render_kpi_metrics
from config.theme import get_global_css
from services.snies_service import (
    filter_instituciones,
    filter_programas,
    get_programas_por_institucion,
    get_snies_paths_for_debug,
    get_summary_stats,
    load_instituciones,
    load_programas,
    report_instituciones_acreditadas,
    report_instituciones_por_caracter_academico,
    report_instituciones_por_departamento,
    report_instituciones_por_sector,
    report_programas_por_area_conocimiento,
    report_programas_por_departamento,
    report_programas_por_institucion,
    report_programas_por_modalidad,
    report_programas_por_municipio,
    report_programas_por_nivel_formacion,
)

PAGE_TITLE = "SNIES"
PAGE_ICON = "📊"

# Columnas a mostrar (ajustar si el Excel no las trae)
COLS_INST = [
    "CÓDIGO_INSTITUCIÓN",
    "NOMBRE_INSTITUCIÓN",
    "ESTADO",
    "SECTOR",
    "CARÁCTER_ACADÉMICO",
    "DEPARTAMENTO_DOMICILIO",
    "MUNICIPIO_DOMICILIO",
    "PROGRAMAS_VIGENTES",
    "ACREDITADA_ALTA_CALIDAD",
]
COLS_PROG = [
    "CÓDIGO_SNIES_DEL_PROGRAMA",
    "NOMBRE_DEL_PROGRAMA",
    "NOMBRE_INSTITUCIÓN",
    "ESTADO_PROGRAMA",
    "ÁREA_DE_CONOCIMIENTO",
    "NIVEL_DE_FORMACIÓN",
    "MODALIDAD",
    "DEPARTAMENTO_OFERTA_PROGRAMA",
    "MUNICIPIO_OFERTA_PROGRAMA",
]


@st.cache_data(ttl=300)
def _cached_instituciones():
    return load_instituciones()


@st.cache_data(ttl=300)
def _cached_programas():
    return load_programas()


st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout="wide")
st.markdown(get_global_css(), unsafe_allow_html=True)

# Header simple (sin logo si no se pasa; esta página no usa layout del portal)
render_header(logo_path=None)

st.title(f"{PAGE_ICON} {PAGE_TITLE}")
st.markdown("Consulta institucional sobre instituciones de educación superior y programas (SNIES).")

# Carga una sola vez por sesión/cache
df_inst = _cached_instituciones()
df_prog = _cached_programas()

if df_inst.empty and df_prog.empty:
    snies_dir, path_inst, path_prog = get_snies_paths_for_debug()
    st.warning(
        "No se encontraron datos SNIES. Compruebe que existan los archivos Excel."
    )
    st.caption(f"Ruta usada: `{snies_dir.resolve()}`. Instituciones: existe={path_inst.is_file()}, Programas: existe={path_prog.is_file()}. "
               "Si acaba de corregir la ruta, reinicie Streamlit (Ctrl+C y volver a ejecutar) para limpiar la caché.")
    render_footer()
    st.stop()


def _render_report_table_chart(df, key_col: str, value_col: str, title: str, max_bars: int = 30):
    """Muestra tabla y gráfico de barras para un reporte agrupado."""
    if df is None or df.empty:
        st.caption(f"{title}: sin datos.")
        return
    st.markdown(f"**{title}**")
    st.dataframe(df, use_container_width=True, height=min(250, 50 + len(df) * 22))
    df_chart = df.head(max_bars).set_index(key_col)
    if not df_chart.empty:
        st.bar_chart(df_chart)


# Pestañas para que Reportes sea visible sin hacer scroll
tab_resumen, tab_instituciones, tab_programas, tab_reportes = st.tabs([
    "Resumen",
    "Instituciones",
    "Programas",
    "Reportes",
])

with tab_resumen:
    st.subheader("Resumen")
    stats = get_summary_stats(df_inst, df_prog)
    metrics = [
        {"label": "Total instituciones", "value": stats["total_instituciones"], "icon": "🏛️"},
        {"label": "Total programas", "value": stats["total_programas"], "icon": "📚"},
        {"label": "Departamentos (instituciones)", "value": stats["total_departamentos_instituciones"], "icon": "🗺️"},
        {"label": "Departamentos (programas)", "value": stats["total_departamentos_programas"], "icon": "📍"},
        {"label": "Instituciones acreditadas alta calidad", "value": stats["instituciones_acreditadas_alta_calidad"], "icon": "⭐"},
    ]
    render_kpi_metrics(metrics, columns_count=5)

with tab_instituciones:
    st.subheader("Instituciones")
    with st.expander("Filtros", expanded=False):
        c1, c2, c3 = st.columns(3)
        with c1:
            f_nombre_inst = st.text_input("Nombre institución", key="snies_f_nombre_inst")
            f_dpto_inst = st.text_input("Departamento", key="snies_f_dpto_inst")
            f_mun_inst = st.text_input("Municipio", key="snies_f_mun_inst")
        with c2:
            f_sector = st.text_input("Sector", key="snies_f_sector")
            f_caracter = st.text_input("Carácter académico", key="snies_f_caracter")
            f_estado_inst = st.text_input("Estado", key="snies_f_estado_inst")
        with c3:
            f_acreditada = st.selectbox("Acreditada alta calidad", ["", "Sí", "No"], key="snies_f_acreditada")

    df_inst_f = filter_instituciones(
        df_inst,
        nombre=f_nombre_inst,
        departamento=f_dpto_inst,
        municipio=f_mun_inst,
        sector=f_sector,
        caracter_academico=f_caracter,
        estado=f_estado_inst,
        acreditada=f_acreditada,
    )
    cols_inst_show = [c for c in COLS_INST if c in df_inst_f.columns]
    if cols_inst_show:
        st.caption(f"Mostrando {len(df_inst_f)} registro(s).")
        st.dataframe(df_inst_f[cols_inst_show], use_container_width=True, height=350)
    else:
        st.info("No hay columnas de instituciones disponibles para mostrar.")

with tab_programas:
    st.subheader("Programas")
    with st.expander("Filtros", expanded=False):
        p1, p2, p3 = st.columns(3)
        with p1:
            f_nombre_prog = st.text_input("Nombre del programa", key="snies_f_nombre_prog")
            f_inst_prog = st.text_input("Nombre institución", key="snies_f_inst_prog")
            f_dpto_prog = st.text_input("Departamento", key="snies_f_dpto_prog")
            f_mun_prog = st.text_input("Municipio", key="snies_f_mun_prog")
        with p2:
            f_area = st.text_input("Área de conocimiento", key="snies_f_area")
            f_nucleo = st.text_input("Núcleo básico del conocimiento", key="snies_f_nucleo")
        with p3:
            f_nivel = st.text_input("Nivel de formación", key="snies_f_nivel")
            f_modalidad = st.text_input("Modalidad", key="snies_f_modalidad")
            f_estado_prog = st.text_input("Estado del programa", key="snies_f_estado_prog")

    df_prog_f = filter_programas(
        df_prog,
        nombre_programa=f_nombre_prog,
        nombre_institucion=f_inst_prog,
        departamento=f_dpto_prog,
        municipio=f_mun_prog,
        area_conocimiento=f_area,
        nucleo_conocimiento=f_nucleo,
        nivel_formacion=f_nivel,
        modalidad=f_modalidad,
        estado_programa=f_estado_prog,
    )
    cols_prog_show = [c for c in COLS_PROG if c in df_prog_f.columns]
    if cols_prog_show:
        st.caption(f"Mostrando {len(df_prog_f)} registro(s).")
        st.dataframe(df_prog_f[cols_prog_show], use_container_width=True, height=350)
    else:
        st.info("No hay columnas de programas disponibles para mostrar.")

    st.subheader("Programas por institución")
    if not df_inst_f.empty and "CÓDIGO_INSTITUCIÓN" in df_inst_f.columns and "NOMBRE_INSTITUCIÓN" in df_inst_f.columns:
        opts = df_inst_f.set_index("CÓDIGO_INSTITUCIÓN")["NOMBRE_INSTITUCIÓN"].astype(str)
        opciones = ["— Seleccione una institución —"] + [f"{cod} — {nombre}" for cod, nombre in opts.items()]
        sel = st.selectbox("Ver programas de la institución", opciones, key="snies_sel_inst")
        if sel and sel != "— Seleccione una institución —":
            cod_sel = sel.split(" — ")[0].strip()
            df_detalle = get_programas_por_institucion(df_prog, cod_sel)
            cols_det = [c for c in COLS_PROG if c in df_detalle.columns]
            if not df_detalle.empty and cols_det:
                st.caption(f"{len(df_detalle)} programa(s) para esta institución.")
                st.dataframe(df_detalle[cols_det], use_container_width=True, height=300)
            else:
                st.caption("Sin programas registrados para esta institución.")
    else:
        st.caption("Aplique filtros en Instituciones para elegir una institución y ver sus programas.")

with tab_reportes:
    st.subheader("Reportes")
    st.caption("Agrupaciones y visualizaciones a partir de Instituciones y Programas (datos reales).")

    st.markdown("**Instituciones**")
    r1 = report_instituciones_por_departamento(df_inst)
    _render_report_table_chart(r1, "departamento", "cantidad", "Instituciones por departamento")

    r2 = report_instituciones_por_sector(df_inst)
    _render_report_table_chart(r2, "sector", "cantidad", "Instituciones por sector")

    r3 = report_instituciones_por_caracter_academico(df_inst)
    _render_report_table_chart(r3, "carácter_académico", "cantidad", "Instituciones por carácter académico")

    acr = report_instituciones_acreditadas(df_inst)
    st.markdown("**Instituciones acreditadas (alta calidad)**")
    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("Acreditadas", acr["acreditadas"])
    with col_b:
        st.metric("No acreditadas", acr["no_acreditadas"])

    st.markdown("---")
    st.markdown("**Programas**")
    r5 = report_programas_por_institucion(df_prog, top_n=40)
    _render_report_table_chart(r5, "institución", "cantidad", "Top instituciones por número de programas", max_bars=25)

    r6 = report_programas_por_departamento(df_prog)
    _render_report_table_chart(r6, "departamento", "cantidad", "Programas por departamento")

    r7 = report_programas_por_municipio(df_prog)
    _render_report_table_chart(r7, "municipio", "cantidad", "Programas por municipio")

    r8 = report_programas_por_area_conocimiento(df_prog)
    _render_report_table_chart(r8, "área_conocimiento", "cantidad", "Programas por área de conocimiento")

    r9 = report_programas_por_nivel_formacion(df_prog)
    _render_report_table_chart(r9, "nivel_formación", "cantidad", "Programas por nivel de formación")

    r10 = report_programas_por_modalidad(df_prog)
    _render_report_table_chart(r10, "modalidad", "cantidad", "Programas por modalidad")

render_footer()
