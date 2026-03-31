"""
Reglas del bloque Investigación (CONACES), sin dependencias de UI.
"""
from __future__ import annotations

from typing import Tuple


def validar_investigacion(sala: str, data: dict) -> Tuple[str, str]:
    """
    Valida el bloque de Investigación según reglas claras por sala.

    Retorna:
      - estado: uno de ["cumple", "no_cumple", "no_aplica"]
      - mensaje explicativo
    """
    sala_norm = (sala or "").strip().lower()

    # Regla especial: Trámites Institucionales => no aplica
    if sala_norm in ("trámites institucionales", "tramites institucionales"):
        return (
            "no_aplica",
            "Para la Sala de Trámites Institucionales el requisito de investigación no aplica.",
        )

    productos_investigacion = bool(data.get("productos_investigacion"))
    grupo_reconocido = bool(data.get("grupo_reconocido"))
    categoria_investigador = (data.get("categoria_investigador") or "").strip()

    categoria_ok = categoria_investigador in {"Junior", "Asociado", "Senior"}

    # Regla general para salas distintas a Trámites
    cumple_general = productos_investigacion or grupo_reconocido or categoria_ok
    if not cumple_general:
        msg_general = (
            "No cumple: se requiere al menos una de las siguientes condiciones: "
            "productos de investigación verificables, grupo reconocido o categoría de investigador "
            "(Junior, Asociado o Senior)."
        )
    else:
        msg_general = "Cumple investigación con al menos una condición verificada."

    # Regla especial: Técnicos Profesionales y Tecnológicos => homologación adicional
    sala_norm_tecnicos = "técnicos profesionales y tecnológicos"
    if sala_norm == sala_norm_tecnicos:
        anios_conceptos_tecnicos = float(data.get("anios_conceptos_tecnicos") or 0.0)
        anios_prototipos_industriales = float(data.get("anios_prototipos_industriales") or 0.0)
        anios_innovacion_productos_servicios = float(data.get("anios_innovacion_productos_servicios") or 0.0)

        cumple_homologacion = (
            anios_conceptos_tecnicos >= 5
            or anios_prototipos_industriales >= 5
            or anios_innovacion_productos_servicios >= 5
        )

        if cumple_general or cumple_homologacion:
            return (
                "cumple",
                "Cumple investigación: satisface regla general y/o homologación (≥ 5 años en conceptos, prototipos o innovación).",
            )

        return (
            "no_cumple",
            msg_general
            + " Además, para esta sala puede homologarse con 5 años o más en conceptos técnicos, prototipos industriales o innovación.",
        )

    # Salas generales
    if cumple_general:
        return "cumple", msg_general
    return "no_cumple", msg_general
