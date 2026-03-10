"""
Servicio de datos SNIES: carga de Excel Instituciones y Programas, filtros y KPIs.
No modifica archivos; solo lectura y transformación en memoria.
"""
from pathlib import Path

import pandas as pd

# Resolver carpeta SNIES probando varias rutas (según desde dónde se ejecute la app)
_APP_ROOT = Path(__file__).resolve().parent.parent  # streamlit_app
_CWD = Path.cwd().resolve()


def _find_snies_dir() -> Path:
    """Primera ruta donde exista data/raw/snies/Instituciones.xlsx."""
    _file = Path(__file__).resolve()
    candidates = [
        _APP_ROOT.parent.parent / "data" / "raw" / "snies",   # streamlit_app -> frontend -> men-data-platform
        _file.parent.parent.parent.parent / "data" / "raw" / "snies",  # services -> streamlit_app -> frontend -> men-data-platform
        _APP_ROOT.parent / "data" / "raw" / "snies",         # frontend/data/raw/snies
        _CWD / "data" / "raw" / "snies",                      # cwd = raíz del repo
    ]
    for p in candidates:
        try:
            p = p.resolve()
            if (p / "Instituciones.xlsx").is_file():
                return p
        except (OSError, RuntimeError):
            continue
    # Por defecto: asumir raíz del repo = parent.parent de streamlit_app
    return _APP_ROOT.parent.parent / "data" / "raw" / "snies"


SNIES_DIR = _find_snies_dir()
PATH_INSTITUCIONES = SNIES_DIR / "Instituciones.xlsx"
PATH_PROGRAMAS = SNIES_DIR / "Programas.xlsx"


def get_snies_paths_for_debug() -> tuple[Path, Path, Path]:
    """Devuelve (SNIES_DIR, PATH_INSTITUCIONES, PATH_PROGRAMAS) para mensajes de error."""
    return SNIES_DIR, PATH_INSTITUCIONES, PATH_PROGRAMAS


def _normalize_col(s: str) -> str:
    """Normaliza nombre de columna para acceso estable."""
    if not isinstance(s, str):
        return str(s)
    return s.strip()


def load_instituciones() -> pd.DataFrame:
    """Carga Instituciones.xlsx y normaliza nombres de columnas."""
    if not PATH_INSTITUCIONES.is_file():
        return pd.DataFrame()
    df = pd.read_excel(PATH_INSTITUCIONES)
    df.columns = [_normalize_col(c) for c in df.columns]
    # Tipos: evitar errores en filtros
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].astype(str).replace("nan", "").str.strip()
    return df


def load_programas() -> pd.DataFrame:
    """Carga Programas.xlsx y normaliza nombres de columnas."""
    if not PATH_PROGRAMAS.is_file():
        return pd.DataFrame()
    df = pd.read_excel(PATH_PROGRAMAS)
    df.columns = [_normalize_col(c) for c in df.columns]
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].astype(str).replace("nan", "").str.strip()
    return df


def get_summary_stats(
    instituciones: pd.DataFrame | None = None,
    programas: pd.DataFrame | None = None,
) -> dict:
    """
    Calcula KPIs para la sección Resumen.
    Acepta DataFrames ya cargados para no leer dos veces.
    """
    if instituciones is None:
        instituciones = load_instituciones()
    if programas is None:
        programas = load_programas()

    def safe_unique(series, drop_na=True):
        if series is None or len(series) == 0:
            return 0
        s = series.dropna() if drop_na else series
        return s.nunique()

    # Columnas esperadas (por si el Excel cambia de nombre)
    col_inst = instituciones.columns
    col_dpto_inst = "DEPARTAMENTO_DOMICILIO" if "DEPARTAMENTO_DOMICILIO" in col_inst else None
    col_acreditada = "ACREDITADA_ALTA_CALIDAD" if "ACREDITADA_ALTA_CALIDAD" in col_inst else None
    col_dpto_prog = "DEPARTAMENTO_OFERTA_PROGRAMA" if "DEPARTAMENTO_OFERTA_PROGRAMA" in programas.columns else None

    total_instituciones = len(instituciones)
    total_programas = len(programas)
    deptos_instituciones = safe_unique(instituciones[col_dpto_inst]) if col_dpto_inst else 0
    deptos_programas = safe_unique(programas[col_dpto_prog]) if col_dpto_prog else 0

    instituciones_acreditadas = 0
    if col_acreditada and col_acreditada in instituciones.columns:
        acr = instituciones[col_acreditada].astype(str).str.upper().str.strip()
        instituciones_acreditadas = int(acr.isin(("SÍ", "SI", "S", "YES", "1", "TRUE", "ACREDITADA")).sum())

    return {
        "total_instituciones": total_instituciones,
        "total_programas": total_programas,
        "total_departamentos_instituciones": deptos_instituciones,
        "total_departamentos_programas": deptos_programas,
        "instituciones_acreditadas_alta_calidad": instituciones_acreditadas,
    }


def filter_instituciones(
    df: pd.DataFrame,
    nombre: str = "",
    departamento: str = "",
    municipio: str = "",
    sector: str = "",
    caracter_academico: str = "",
    estado: str = "",
    acreditada: str = "",
) -> pd.DataFrame:
    """Aplica filtros sobre el DataFrame de instituciones (por contenido de texto)."""
    out = df.copy()
    col = out.columns

    def apply_text_filter(column_name: str, value: str):
        if not value or column_name not in col:
            return
        nonlocal out
        v = value.strip().upper()
        if not v:
            return
        ser = out[column_name].astype(str).str.upper()
        out = out[ser.str.contains(v, na=False)]

    apply_text_filter("NOMBRE_INSTITUCIÓN", nombre)
    apply_text_filter("DEPARTAMENTO_DOMICILIO", departamento)
    apply_text_filter("MUNICIPIO_DOMICILIO", municipio)
    apply_text_filter("SECTOR", sector)
    apply_text_filter("CARÁCTER_ACADÉMICO", caracter_academico)
    apply_text_filter("ESTADO", estado)
    if acreditada and "ACREDITADA_ALTA_CALIDAD" in col:
        v = acreditada.strip().upper()
        if v:
            ser = out["ACREDITADA_ALTA_CALIDAD"].astype(str).str.upper()
            if v in ("SÍ", "SI", "S", "1", "TRUE", "ACREDITADA"):
                out = out[ser.isin(("SÍ", "SI", "S", "YES", "1", "TRUE", "ACREDITADA"))]
            elif v in ("NO", "N", "0", "FALSE"):
                out = out[~ser.isin(("SÍ", "SI", "S", "YES", "1", "TRUE", "ACREDITADA"))]
    return out


def filter_programas(
    df: pd.DataFrame,
    nombre_programa: str = "",
    nombre_institucion: str = "",
    departamento: str = "",
    municipio: str = "",
    area_conocimiento: str = "",
    nucleo_conocimiento: str = "",
    nivel_formacion: str = "",
    modalidad: str = "",
    estado_programa: str = "",
) -> pd.DataFrame:
    """Aplica filtros sobre el DataFrame de programas."""
    out = df.copy()
    col = out.columns

    def apply_text_filter(column_name: str, value: str):
        if not value or column_name not in col:
            return
        nonlocal out
        v = value.strip().upper()
        if not v:
            return
        ser = out[column_name].astype(str).str.upper()
        out = out[ser.str.contains(v, na=False)]

    apply_text_filter("NOMBRE_DEL_PROGRAMA", nombre_programa)
    apply_text_filter("NOMBRE_INSTITUCIÓN", nombre_institucion)
    apply_text_filter("DEPARTAMENTO_OFERTA_PROGRAMA", departamento)
    apply_text_filter("MUNICIPIO_OFERTA_PROGRAMA", municipio)
    apply_text_filter("ÁREA_DE_CONOCIMIENTO", area_conocimiento)
    apply_text_filter("NÚCLEO_BÁSICO_DEL_CONOCIMIENTO", nucleo_conocimiento)
    apply_text_filter("NIVEL_DE_FORMACIÓN", nivel_formacion)
    apply_text_filter("MODALIDAD", modalidad)
    apply_text_filter("ESTADO_PROGRAMA", estado_programa)
    return out


def get_programas_por_institucion(programas_df: pd.DataFrame, codigo_institucion: str) -> pd.DataFrame:
    """Devuelve programas asociados a una institución por CÓDIGO_INSTITUCIÓN."""
    if not codigo_institucion or "CÓDIGO_INSTITUCIÓN" not in programas_df.columns:
        return programas_df.head(0)
    cod = str(codigo_institucion).strip()
    return programas_df[programas_df["CÓDIGO_INSTITUCIÓN"].astype(str).str.strip() == cod].copy()


# --- Agregaciones para la sección Reportes ---

def _safe_value_counts(series, name_col="nombre", count_col="cantidad"):
    """Conteo por valores; devuelve DataFrame con nombre_col y count_col."""
    if series is None or len(series) == 0:
        return pd.DataFrame(columns=[name_col, count_col])
    s = series.astype(str).replace("nan", "").str.strip()
    s = s[s != ""]
    counts = s.value_counts().reset_index()
    counts.columns = [name_col, count_col]
    return counts.sort_values(count_col, ascending=False)


def report_instituciones_por_departamento(instituciones: pd.DataFrame) -> pd.DataFrame:
    """Agrupa instituciones por DEPARTAMENTO_DOMICILIO. Columnas: departamento, cantidad."""
    col = "DEPARTAMENTO_DOMICILIO"
    if col not in instituciones.columns:
        return pd.DataFrame(columns=["departamento", "cantidad"])
    df = _safe_value_counts(instituciones[col], name_col="departamento", count_col="cantidad")
    return df


def report_instituciones_por_sector(instituciones: pd.DataFrame) -> pd.DataFrame:
    """Agrupa instituciones por SECTOR. Columnas: sector, cantidad."""
    col = "SECTOR"
    if col not in instituciones.columns:
        return pd.DataFrame(columns=["sector", "cantidad"])
    return _safe_value_counts(instituciones[col], name_col="sector", count_col="cantidad")


def report_instituciones_por_caracter_academico(instituciones: pd.DataFrame) -> pd.DataFrame:
    """Agrupa instituciones por CARÁCTER_ACADÉMICO. Columnas: carácter_académico, cantidad."""
    col = "CARÁCTER_ACADÉMICO"
    if col not in instituciones.columns:
        return pd.DataFrame(columns=["carácter_académico", "cantidad"])
    return _safe_value_counts(instituciones[col], name_col="carácter_académico", count_col="cantidad")


def report_instituciones_acreditadas(instituciones: pd.DataFrame) -> dict:
    """Resumen acreditadas / no acreditadas según ACREDITADA_ALTA_CALIDAD."""
    col = "ACREDITADA_ALTA_CALIDAD"
    if col not in instituciones.columns:
        return {"acreditadas": 0, "no_acreditadas": 0}
    acr = instituciones[col].astype(str).str.upper().str.strip()
    si_vals = ("SÍ", "SI", "S", "YES", "1", "TRUE", "ACREDITADA")
    acreditadas = int(acr.isin(si_vals).sum())
    no_acreditadas = len(instituciones) - acreditadas
    return {"acreditadas": acreditadas, "no_acreditadas": no_acreditadas}


def report_programas_por_institucion(programas: pd.DataFrame, top_n: int = 50) -> pd.DataFrame:
    """Top instituciones por número de programas. Columnas: institución o código, cantidad."""
    name_col = "NOMBRE_INSTITUCIÓN" if "NOMBRE_INSTITUCIÓN" in programas.columns else "CÓDIGO_INSTITUCIÓN"
    if name_col not in programas.columns:
        return pd.DataFrame(columns=["institución", "cantidad"])
    df = programas[name_col].astype(str).replace("nan", "").str.strip()
    df = df[df != ""]
    counts = df.value_counts().reset_index()
    counts.columns = ["institución", "cantidad"]
    return counts.head(top_n)


def report_programas_por_departamento(programas: pd.DataFrame) -> pd.DataFrame:
    """Agrupa programas por DEPARTAMENTO_OFERTA_PROGRAMA."""
    col = "DEPARTAMENTO_OFERTA_PROGRAMA"
    if col not in programas.columns:
        return pd.DataFrame(columns=["departamento", "cantidad"])
    return _safe_value_counts(programas[col], name_col="departamento", count_col="cantidad")


def report_programas_por_municipio(programas: pd.DataFrame) -> pd.DataFrame:
    """Agrupa programas por MUNICIPIO_OFERTA_PROGRAMA."""
    col = "MUNICIPIO_OFERTA_PROGRAMA"
    if col not in programas.columns:
        return pd.DataFrame(columns=["municipio", "cantidad"])
    return _safe_value_counts(programas[col], name_col="municipio", count_col="cantidad")


def report_programas_por_area_conocimiento(programas: pd.DataFrame) -> pd.DataFrame:
    """Agrupa programas por ÁREA_DE_CONOCIMIENTO."""
    col = "ÁREA_DE_CONOCIMIENTO"
    if col not in programas.columns:
        return pd.DataFrame(columns=["área_conocimiento", "cantidad"])
    return _safe_value_counts(programas[col], name_col="área_conocimiento", count_col="cantidad")


def report_programas_por_nivel_formacion(programas: pd.DataFrame) -> pd.DataFrame:
    """Agrupa programas por NIVEL_DE_FORMACIÓN."""
    col = "NIVEL_DE_FORMACIÓN"
    if col not in programas.columns:
        return pd.DataFrame(columns=["nivel_formación", "cantidad"])
    return _safe_value_counts(programas[col], name_col="nivel_formación", count_col="cantidad")


def report_programas_por_modalidad(programas: pd.DataFrame) -> pd.DataFrame:
    """Agrupa programas por MODALIDAD."""
    col = "MODALIDAD"
    if col not in programas.columns:
        return pd.DataFrame(columns=["modalidad", "cantidad"])
    return _safe_value_counts(programas[col], name_col="modalidad", count_col="cantidad")
