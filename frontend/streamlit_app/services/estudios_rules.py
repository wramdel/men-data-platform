"""
Reglas de validación del bloque Estudios (CONACES), sin dependencias de UI.

La UI importa estas funciones; las pruebas unitarias las ejercitan directamente.
"""
from __future__ import annotations

import unicodedata
from typing import Tuple


def _campo_amplio_clave_normalizada(s: str) -> str:
    """Normaliza texto de campo amplio para comparar sin depender de tildes ni mayúsculas."""
    t = unicodedata.normalize("NFKD", (s or "").strip())
    t = "".join(ch for ch in t if not unicodedata.combining(ch))
    return "".join(ch for ch in t.upper() if ch.isalnum())


def campo_amplio_es_educacion(s: str) -> bool:
    """
    Indica si el valor de campo amplio corresponde al campo Educación (SNIES / CINE).

    Tolera variantes como "Educación", "EDUCACION", espacios y diferencias de tildes.
    """
    return _campo_amplio_clave_normalizada(s) == "EDUCACION"


def _educacion_snies_disponible(data: dict) -> bool:
    """Hay datos SNIES de campo amplio para profesional y para el posgrado activo."""
    if not (data.get("campo_amplio_profesional") or "").strip():
        return False
    ma = bool(data.get("maestria_en_educacion"))
    doc = bool(data.get("doctorado_en_educacion"))
    if ma:
        return bool((data.get("campo_amplio_maestria") or "").strip())
    if doc:
        return bool((data.get("campo_amplio_doctorado") or "").strip())
    return False


def _campo_amplio_posgrado_activo_educacion(data: dict) -> str:
    """Posgrado activo: maestría tiene prioridad; si no, doctorado."""
    if bool(data.get("maestria_en_educacion")):
        return (data.get("campo_amplio_maestria") or "").strip()
    if bool(data.get("doctorado_en_educacion")):
        return (data.get("campo_amplio_doctorado") or "").strip()
    return ""


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
    maestria_en_educacion = bool(data.get("maestria_en_educacion"))
    doctorado_en_educacion = bool(data.get("doctorado_en_educacion"))

    has_posgrado = maestria or doctorado

    # SALA EDUCACIÓN
    if sala_norm in ("EDUCACIÓN", "EDUCACION"):
        if _educacion_snies_disponible(data):
            campo_prof = (data.get("campo_amplio_profesional") or "").strip()
            campo_pos = _campo_amplio_posgrado_activo_educacion(data)
            ok = (
                profesional_en_educacion
                and (maestria_en_educacion or doctorado_en_educacion)
                and campo_amplio_es_educacion(campo_prof)
                and campo_amplio_es_educacion(campo_pos)
            )
            return (
                ok,
                "Cumple: título profesional y posgrado en el campo de educación (validado por SNIES)."
                if ok
                else "No cumple: el título profesional y el posgrado deben pertenecer al campo amplio de educación.",
            )
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
