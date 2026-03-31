"""
Reglas del bloque Experiencia (CONACES), sin dependencias de UI.

Dos modos en validar_experiencia:
- Si vienen booleanos r1..r7 / ti1..ti3 (como arma Streamlit hoy), se respetan.
- Si faltan esas claves, se calculan rutas desde los campos numéricos con los helpers.
"""
from __future__ import annotations

from typing import Callable, List, Tuple


def _get_float(data: dict, *keys: str, default: float = 0.0) -> float:
    """Primer valor numérico disponible entre varias claves posibles (UI vs. pruebas)."""
    for k in keys:
        if k not in data or data[k] is None:
            continue
        try:
            return float(data[k])
        except (TypeError, ValueError):
            return default
    return default


def _get_int(data: dict, *keys: str, default: int = 0) -> int:
    return int(_get_float(data, *keys, default=float(default)))


def _truthy(data: dict, *keys: str) -> bool:
    for k in keys:
        if k in data and data[k]:
            return True
    return False


# --- Rutas generales (cálculo desde datos crudos) ---


def _cumple_ruta_1(data: dict) -> bool:
    """Docencia total >= 5 y docencia posgrado >= 2."""
    dt = _get_float(data, "r1_anios_docencia_total")
    dp = _get_float(data, "r1_anios_docencia_posgrado")
    return dt >= 5 and dp >= 2


def _cumple_ruta_2(data: dict) -> bool:
    """Docencia total >= 5 y experiencia en investigación."""
    dt = _get_float(data, "r2_anios_docencia_total")
    inv = _truthy(data, "r2_experiencia_investigacion", "experiencia_investigacion")
    return dt >= 5 and inv


def _cumple_ruta_3(data: dict) -> bool:
    """Trámites RC/institucionales >= 4 o trámites de acreditación >= 2."""
    rc = _get_int(
        data,
        "r3_tramites_rc_o_institucionales",
        "tramites_rc_o_institucionales",
    )
    ac = _get_int(
        data,
        "r3_tramites_acreditacion",
        "tramites_acreditacion",
    )
    return rc >= 4 or ac >= 2


def _cumple_ruta_4(data: dict) -> bool:
    """Integrante sala CONACES >= 1 año o sesiones banco elegibles >= 4."""
    anios = _get_float(
        data,
        "r4_anios_integrante_sala_conaces",
        "anios_integrante_sala_conaces",
    )
    ses = _get_int(
        data,
        "r4_sesiones_banco_elegibles",
        "sesiones_banco_elegibles",
    )
    return anios >= 1 or ses >= 4


def _cumple_ruta_5(data: dict) -> bool:
    """Docencia total >= 3 y ejercicio profesional >= 5 años."""
    dt = _get_float(data, "r5_anios_docencia_total")
    ej = _get_float(data, "r5_anios_ejercicio_profesional", "anios_ejercicio_profesional")
    return dt >= 3 and ej >= 5


def _cumple_ruta_6(data: dict) -> bool:
    """Docencia total >= 3 y dirección académica >= 5 años."""
    dt = _get_float(data, "r6_anios_docencia_total")
    da = _get_float(data, "r6_anios_direccion_academica", "anios_direccion_academica")
    return dt >= 3 and da >= 5


def _cumple_ruta_7(data: dict) -> bool:
    """Diseño o gestión curricular >= 5 años."""
    return _get_float(
        data,
        "r7_anios_diseno_o_gestion_curricular",
        "anios_diseno_o_gestion_curricular",
    ) >= 5


RUTAS_GENERALES_CALCULO: Tuple[Callable[[dict], bool], ...] = (
    _cumple_ruta_1,
    _cumple_ruta_2,
    _cumple_ruta_3,
    _cumple_ruta_4,
    _cumple_ruta_5,
    _cumple_ruta_6,
    _cumple_ruta_7,
)


# --- Trámites institucionales ---


def _cumple_ti_1(data: dict) -> bool:
    """TI-1: años rector/vicerrector >= 4."""
    return _get_float(data, "anios_rector_vicerrector") >= 4


def _cumple_ti_2(data: dict) -> bool:
    """TI-2: años dirección/planeación/calidad/financiero >= 5."""
    return _get_float(data, "anios_direccion_planeacion_calidad_financiero") >= 5


def _cumple_ti_3(data: dict) -> bool:
    """TI-3: suma TI-1 + TI-2 >= 5 (mismos campos que ti1/ti2)."""
    a = _get_float(data, "anios_rector_vicerrector")
    b = _get_float(data, "anios_direccion_planeacion_calidad_financiero")
    return (a + b) >= 5


def _usar_booleanos_generales(data: dict) -> bool:
    claves = [f"r{i}" for i in range(1, 8)]
    if not all(k in data for k in claves):
        return False
    return all(isinstance(data[k], bool) for k in claves)


def _rutas_labels_desde_booleanos_generales(data: dict) -> List[str]:
    rutas: List[str] = []
    for i in range(1, 8):
        if bool(data.get(f"r{i}")):
            rutas.append(f"Ruta {i}")
    return rutas


def _rutas_labels_desde_calculo_generales(data: dict) -> List[str]:
    rutas: List[str] = []
    for i, fn in enumerate(RUTAS_GENERALES_CALCULO, start=1):
        if fn(data):
            rutas.append(f"Ruta {i}")
    return rutas


def _usar_booleanos_ti(data: dict) -> bool:
    if not all(k in data for k in ("ti1", "ti2", "ti3")):
        return False
    return all(isinstance(data[k], bool) for k in ("ti1", "ti2", "ti3"))


def _rutas_labels_ti_desde_booleanos(data: dict) -> List[str]:
    rutas: List[str] = []
    if bool(data.get("ti1")):
        rutas.append("Ruta TI-1")
    if bool(data.get("ti2")):
        rutas.append("Ruta TI-2")
    if bool(data.get("ti3")):
        rutas.append("Ruta TI-3")
    return rutas


def _rutas_labels_ti_desde_calculo(data: dict) -> List[str]:
    rutas: List[str] = []
    if _cumple_ti_1(data):
        rutas.append("Ruta TI-1")
    if _cumple_ti_2(data):
        rutas.append("Ruta TI-2")
    if _cumple_ti_3(data):
        rutas.append("Ruta TI-3")
    return rutas


def validar_experiencia(sala: str, data: dict) -> Tuple[bool, str, List[str]]:
    """
    Valida experiencia por sala.

    Salas generales: mínimo 2 rutas entre Ruta 1..7.
    Trámites Institucionales: mínimo 1 entre TI-1..TI-3.

    Retorna: (cumple, mensaje, lista de etiquetas de rutas cumplidas)
    """
    sala_norm = (sala or "").strip().lower()
    es_ti = sala_norm in ("trámites institucionales", "tramites institucionales")

    if es_ti:
        if _usar_booleanos_ti(data):
            rutas = _rutas_labels_ti_desde_booleanos(data)
        else:
            rutas = _rutas_labels_ti_desde_calculo(data)
        cumple = len(rutas) >= 1
        msg = (
            "Cumple regla TI (al menos una condición verificada)."
            if cumple
            else "No cumple regla TI: no se verifican condiciones suficientes."
        )
        return cumple, msg, rutas

    if _usar_booleanos_generales(data):
        rutas = _rutas_labels_desde_booleanos_generales(data)
    else:
        rutas = _rutas_labels_desde_calculo_generales(data)

    cumple = len(rutas) >= 2
    msg = (
        f"Cumple: {len(rutas)} rutas verificadas (mínimo 2)."
        if cumple
        else f"No cumple: {len(rutas)} rutas verificadas (mínimo 2)."
    )
    return cumple, msg, rutas
