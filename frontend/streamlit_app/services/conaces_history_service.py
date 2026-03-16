"""
Servicio de datos histórico para Gestión CONACES.

Lee los Excel de `data/raw/gconases/` por fase y construye un maestro
consolidado por aspirante (documento), pensado para dashboards y consultas.
"""
from pathlib import Path
from typing import Dict, Iterable, List

import pandas as pd

# Raíz del repo: streamlit_app/services -> streamlit_app -> frontend -> men-data-platform
_APP_ROOT = Path(__file__).resolve().parent.parent
_PROJECT_ROOT = _APP_ROOT.parent.parent
GCONACES_DIR = _PROJECT_ROOT / "data" / "raw" / "gconases"

def normalize_document_value(value: str) -> str:
    """Normaliza un valor de documento ingresado por el usuario."""
    if value is None:
        return ""
    s = str(value).strip()
    s = s.replace("\u00a0", " ")
    s = s.strip()
    s = s.replace(".0", "") if s.endswith(".0") else s
    return s


def _clean_document_series(series: pd.Series) -> pd.Series:
    """Normaliza identificaciones para que sean comparables entre fases."""
    s = series.astype(str).str.strip()
    # Quitar sufijo `.0` típico de Excel en números
    s = s.str.replace(r"\.0$", "", regex=True)
    # Normalizar vacíos
    s = s.replace({"nan": ""})
    return s


def build_traza_conaces() -> pd.DataFrame:
    """
    Construye tabla larga de trazabilidad por fase/archivo (una fila por documento por fase).
    Se usa para consultas históricas.
    """
    fases = [
        ("F1", "01-21112025 - PUBLICACIÓN.xlsx", load_fase_1),
        ("F2", "02-02122025 - PUBLICACIÓN.xlsx", load_fase_2),
        ("F3", "03-15122025 - CORRECCIÓN.xlsx", load_fase_3),
        ("F4", "04-24122025 - PUBLICACIÓN.xlsx", load_fase_4),
        ("F5", "05-30122025 - PUBLICACIÓN.xlsx", load_fase_5),
    ]
    parts: List[pd.DataFrame] = []
    for fase, filename, loader in fases:
        df = loader()
        if df is None or df.empty:
            continue
        df = df.copy()
        df["fase"] = fase
        df["archivo_origen"] = filename
        # Garantizar documento limpio
        if "documento" in df.columns:
            df["documento"] = _clean_document_series(df["documento"])
        parts.append(df)
    if not parts:
        return pd.DataFrame()
    traza = pd.concat(parts, ignore_index=True)
    # Orden de columnas preferido
    cols_pref = [
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
        "fase",
        "archivo_origen",
    ]
    cols_exist = [c for c in cols_pref if c in traza.columns]
    rest = [c for c in traza.columns if c not in cols_exist]
    return traza[cols_exist + rest]


def _load_first_nonempty_sheet(path: Path) -> pd.DataFrame:
    """
    Lee el primer sheet no vacío del Excel.
    Si falla o no existe, devuelve DataFrame vacío.
    """
    if not path.is_file():
        return pd.DataFrame()
    try:
        xls = pd.ExcelFile(path)
        for sheet_name in xls.sheet_names:
            df = xls.parse(sheet_name)
            if not df.empty:
                return df
        return pd.DataFrame()
    except Exception:
        return pd.DataFrame()


def _standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Limpia espacios en nombres de columnas."""
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    return df


def _build_phase_df(
    path: Path,
    fase: str,
    col_map: Dict[str, str],
    extra_keep: Iterable[str] | None = None,
) -> pd.DataFrame:
    """
    Crea un DataFrame estándar para una fase.

    col_map: {nombre_columna_real: nombre_estandar}
    extra_keep: columnas reales adicionales a conservar con su nombre original (trazabilidad).
    """
    df_raw = _load_first_nonempty_sheet(path)
    if df_raw.empty:
        return pd.DataFrame(
            columns=[
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
                "fase",
            ]
        )

    df_raw = _standardize_columns(df_raw)

    # Documentación del mapeo de columnas reales -> estándar.
    # Ejemplo (ajustar a los nombres reales de los archivos):
    #   "NÚMERO_DOCUMENTO" -> "documento"
    #   "CONVOCATORIA"     -> "convocatoria"
    #   "SALA_CONACES"     -> "sala"
    #   "ESTADO_INSCRIP"   -> "estado_inscripcion"

    data: Dict[str, pd.Series] = {}
    matched_any = False
    for real_col, std_col in col_map.items():
        if real_col in df_raw.columns:
            data[std_col] = df_raw[real_col]
            matched_any = True
        else:
            # Columna no presente en esta fase
            # Rellenamos más adelante solo si hay al menos una coincidencia.
            data[std_col] = pd.Series([pd.NA] * len(df_raw))

    # Si ninguna columna real coincidió con el mapeo, devolvemos un DataFrame vacío
    # con el esquema estándar para evitar errores de construcción.
    if not matched_any:
        return pd.DataFrame(
            columns=list(col_map.values())
            + [
                "fase",
            ]
        )

    df = pd.DataFrame(data)

    # Normalizar documento
    if "documento" in df.columns:
        df["documento"] = _clean_document_series(df["documento"])

    # Añadir columnas extra (para trazabilidad si se desean exponer después)
    extra_keep = list(extra_keep or [])
    for col in extra_keep:
        if col in df_raw.columns and col not in df.columns:
            df[col] = df_raw[col]

    df["fase"] = fase

    # Resolver múltiples filas por documento dentro de la fase:
    # priorizar registros con más campos no nulos.
    if "documento" in df.columns:
        non_null_counts = df.notna().sum(axis=1)
        df = df.assign(_nn=non_null_counts)
        df = (
            df.sort_values("_nn", ascending=False)
            .drop_duplicates(subset=["documento"], keep="first")
            .drop(columns=["_nn"])
        )

    return df


# --- Carga por fase --------------------------------------------------------


def load_fase_1() -> pd.DataFrame:
    """
    Fase 1: publicación inicial de inscritos.

    Archivo: 01-21112025 - PUBLICACIÓN.xlsx

    Columnas reales relevantes (según insumo del usuario):
    - "Convocatoria"                  -> convocatoria
    - "Número de Documento Inscrito"  -> documento
    - "Estado"                        -> estado_inscripcion
    - "Sala"                          -> sala
    """
    path = GCONACES_DIR / "01-21112025 - PUBLICACIÓN.xlsx"
    col_map_f1: Dict[str, str] = {
        "Número de Documento Inscrito": "documento",
        "Convocatoria": "convocatoria",
        "Sala": "sala",
        "Estado": "estado_inscripcion",
        # Sin información de fases ni resultados en este archivo
        "": "puntaje_fase_3",
        " ": "resultado_fase_3",
        "  ": "puntaje_prueba",
        "   ": "puntaje_entrevista",
        "    ": "puntaje_final",
        "     ": "resultado_final",
    }
    return _build_phase_df(path, fase="F1", col_map=col_map_f1)


def load_fase_2() -> pd.DataFrame:
    """
    Fase 2: segunda publicación / ajustes.

    Archivo: 02-02122025 - PUBLICACIÓN.xlsx

    Columnas reales relevantes (según insumo del usuario):
    - "Convocatoria"                  -> convocatoria
    - "Número de Documento Inscrito"  -> documento
    - "Estado"                        -> estado_inscripcion
    - "Sala"                          -> sala
    """
    path = GCONACES_DIR / "02-02122025 - PUBLICACIÓN.xlsx"
    col_map_f2: Dict[str, str] = {
        "Número de Documento Inscrito": "documento",
        "Convocatoria": "convocatoria",
        "Sala": "sala",
        "Estado": "estado_inscripcion",
        # Sin resultados de fases en este archivo
        "": "puntaje_fase_3",
        " ": "resultado_fase_3",
        "  ": "puntaje_prueba",
        "   ": "puntaje_entrevista",
        "    ": "puntaje_final",
        "     ": "resultado_final",
    }
    return _build_phase_df(path, fase="F2", col_map=col_map_f2)


def load_fase_3() -> pd.DataFrame:
    """
    Fase 3: corrección.

    Archivo: 03-15122025 - CORRECCIÓN.xlsx

    Columnas reales relevantes:
    - "No. Cédula"  -> documento
    - "Puntaje"     -> puntaje_fase_3
    - "Resultado"   -> resultado_fase_3
    """
    path = GCONACES_DIR / "03-15122025 - CORRECCIÓN.xlsx"
    col_map_f3: Dict[str, str] = {
        "No. Cédula": "documento",
        "Puntaje": "puntaje_fase_3",
        "Resultado": "resultado_fase_3",
        # El resto se deja vacío / NaN para esta fase
        "": "convocatoria",
        " ": "sala",
        "  ": "estado_inscripcion",
        "   ": "puntaje_prueba",
        "    ": "puntaje_entrevista",
        "     ": "puntaje_final",
        "      ": "resultado_final",
    }
    return _build_phase_df(path, fase="F3", col_map=col_map_f3)


def load_fase_4() -> pd.DataFrame:
    """
    Fase 4: publicación siguiente.

    Archivo: 04-24122025 - PUBLICACIÓN.xlsx

    Columnas reales relevantes:
    - "Identificación aspirante"            -> documento
    - "Sala"                                -> sala
    - "Puntaje Prueba de Conocimiento"      -> puntaje_prueba
    - "Ponderación Prueba 75%"              -> (se puede ignorar o usar auxiliar)
    - "Puntaje Entrevista"                  -> puntaje_entrevista
    - "Ponderación Entrevista 25%"          -> (auxiliar)
    - "Puntaje Final 100%"                  -> puntaje_final
    - "Resultado Final"                     -> resultado_final
    """
    path = GCONACES_DIR / "04-24122025 - PUBLICACIÓN.xlsx"
    col_map_f4: Dict[str, str] = {
        "Identificación aspirante": "documento",
        "Sala": "sala",
        "Puntaje Prueba de Conocimiento": "puntaje_prueba",
        "Puntaje Entrevista": "puntaje_entrevista",
        "Puntaje Final 100%": "puntaje_final",
        "Resultado Final": "resultado_final",
        # Sin datos de estos campos en esta fase
        "": "convocatoria",
        " ": "estado_inscripcion",
        "  ": "puntaje_fase_3",
        "   ": "resultado_fase_3",
    }
    return _build_phase_df(path, fase="F4", col_map=col_map_f4)


def load_fase_5() -> pd.DataFrame:
    """
    Fase 5: publicación final.

    Archivo: 05-30122025 - PUBLICACIÓN.xlsx

    Columnas reales relevantes:
    - "Identificación"            -> documento
    - "Sala"                      -> sala
    - "Puntaje Final 100%"        -> puntaje_final
    - "Resultado Final"           -> resultado_final
    """
    path = GCONACES_DIR / "05-30122025 - PUBLICACIÓN.xlsx"
    col_map_f5: Dict[str, str] = {
        "Identificación": "documento",
        "Sala": "sala",
        "Puntaje Final 100%": "puntaje_final",
        "Resultado Final": "resultado_final",
        # Sin datos de estos campos en esta fase
        "": "convocatoria",
        " ": "estado_inscripcion",
        "  ": "puntaje_fase_3",
        "   ": "resultado_fase_3",
        "    ": "puntaje_prueba",
        "     ": "puntaje_entrevista",
    }
    return _build_phase_df(path, fase="F5", col_map=col_map_f5)


def _merge_phases_by_document(phases: List[pd.DataFrame]) -> pd.DataFrame:
    """
    Consolida por documento:
    - Fase 1 se toma como base (inscritos).
    - Fases siguientes enriquecen usando el documento como llave.
    - Para cada campo, se respetan los valores existentes y solo se rellenan NaN
      con información posterior.
    """
    if not phases:
        return pd.DataFrame()

    base = phases[0]
    if base.empty:
        return pd.DataFrame()

    if "documento" not in base.columns:
        return pd.DataFrame()

    base = base.set_index("documento")

    for phase in phases[1:]:
        if phase is None or phase.empty or "documento" not in phase.columns:
            continue
        p = phase.set_index("documento")
        # Alinear índices
        p = p.loc[~p.index.isna()]
        # Para cada columna de la fase (excepto 'fase', que no se mezcla)
        for col in p.columns:
            if col == "fase":
                continue
            if col not in base.columns:
                base[col] = p[col]
            else:
                # Mantener valor existente; rellenar NaN con datos de la fase
                base[col] = base[col].where(~base[col].isna(), p[col])

    base = base.reset_index()
    # Asegurar columnas mínimas en el maestro
    cols_min = [
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
    for c in cols_min:
        if c not in base.columns:
            base[c] = pd.NA
    return base[cols_min]


def build_master_conaces() -> pd.DataFrame:
    """
    Devuelve un DataFrame maestro con una fila por aspirante (documento).

    Estrategia:
    - Fase 1 define el universo de inscritos.
    - Fases 2–5 aportan información adicional (estados, puntajes, resultados).
    - Si una fase no tiene un campo, se deja como NaN.
    """
    f1 = load_fase_1()
    f2 = load_fase_2()
    f3 = load_fase_3()
    f4 = load_fase_4()
    f5 = load_fase_5()
    phases = [f1, f2, f3, f4, f5]
    return _merge_phases_by_document(phases)

