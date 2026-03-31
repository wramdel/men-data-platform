"""
Integración ligera: flujo SNIES (lista → título → detalle) sobre fixture común.

Las reglas de estudios siguen en test_estudios_rules; aquí solo se cruza el “contrato”
de datos (mismo tipo dict que consume validar_estudios más adelante si se conecta a SNIES).
"""
from __future__ import annotations

import pytest

from services.snies_service import get_programa_detalle, get_snies_instituciones, get_titulos_por_institucion_y_nivel
from services.estudios_rules import validar_estudios

from tests.fixtures.snies_sample_data import dataframe_programas_snies_minimo


def _campo_amplio_indica_educacion(campo_amplio: str) -> bool:
    """Criterio de texto para alinear SNIES (campo amplio) con la Sala Educación en integración."""
    c = (campo_amplio or "").lower()
    return "educación" in c or "educacion" in c


def _cumple_sala_educacion_con_detalle_snies(detalle: dict | None, data: dict) -> bool:
    """
    Ensamble de reglas de sala + evidencia SNIES: exige flags de educación y campo amplio coherente.
    (Contrato probado aquí hasta que se consolide en validar_estudios si aplica.)
    """
    ok_base, _ = validar_estudios("Educación", data)
    if not ok_base:
        return False
    if not detalle:
        return ok_base
    return _campo_amplio_indica_educacion(detalle.get("campo_amplio", ""))


@pytest.mark.integration
def test_flujo_snies_maestria_luego_validar_datos_paralelos(patch_snies_programas_df):
    """Selección SNIES coherente con flags académicos usados en reglas (demo de ensamble)."""
    patch_snies_programas_df(dataframe_programas_snies_minimo())
    inst = get_snies_instituciones()
    assert "UNIVERSIDAD EJEMPLO ALPHA" in inst

    titulos = get_titulos_por_institucion_y_nivel("UNIVERSIDAD EJEMPLO ALPHA", "Maestría")
    assert titulos == ["MAESTRO EN EDUCACIÓN"]

    det = get_programa_detalle("UNIVERSIDAD EJEMPLO ALPHA", "Maestría", "MAESTRO EN EDUCACIÓN")
    assert det is not None
    assert "Educación" in det["campo_amplio"]

    # Bloque estudios genérico (no sala Educación): profesional + maestría cumple
    data = {
        "titulo_exterior": False,
        "convalidado": False,
        "profesional": True,
        "maestria": True,
        "doctorado": False,
        "especialidad_medica": False,
        "tecnico": False,
        "tecnologo": False,
        "certificados": False,
        "duracion_certificados": 0.0,
        "profesional_en_educacion": False,
        "posgrado_en_educacion": False,
    }
    ok, _ = validar_estudios("Ingeniería, Industria y Construcción", data)
    assert ok is True


@pytest.mark.integration
def test_sala_educacion_falla_si_campo_amplio_snies_no_es_educacion(patch_snies_programas_df):
    patch_snies_programas_df(dataframe_programas_snies_minimo())
    det = get_programa_detalle(
        "UNIVERSIDAD EJEMPLO ALPHA",
        "Profesional",
        "LICENCIADO EN MATEMÁTICAS",
    )
    assert det is not None
    assert not _campo_amplio_indica_educacion(det["campo_amplio"])

    data_edu = {
        "titulo_exterior": False,
        "convalidado": False,
        "profesional": False,
        "maestria": False,
        "doctorado": False,
        "especialidad_medica": False,
        "tecnico": False,
        "tecnologo": False,
        "certificados": False,
        "duracion_certificados": 0.0,
        "profesional_en_educacion": True,
        "posgrado_en_educacion": True,
    }
    assert _cumple_sala_educacion_con_detalle_snies(det, data_edu) is False


@pytest.mark.integration
def test_sala_educacion_puede_cumplir_con_campo_amplio_educacion_snies(patch_snies_programas_df):
    patch_snies_programas_df(dataframe_programas_snies_minimo())
    det = get_programa_detalle(
        "UNIVERSIDAD EJEMPLO ALPHA",
        "Maestría",
        "MAESTRO EN EDUCACIÓN",
    )
    assert det is not None
    assert _campo_amplio_indica_educacion(det["campo_amplio"])

    data_edu = {
        "titulo_exterior": False,
        "convalidado": False,
        "profesional": False,
        "maestria": False,
        "doctorado": False,
        "especialidad_medica": False,
        "tecnico": False,
        "tecnologo": False,
        "certificados": False,
        "duracion_certificados": 0.0,
        "profesional_en_educacion": True,
        "posgrado_en_educacion": True,
    }
    assert _cumple_sala_educacion_con_detalle_snies(det, data_edu) is True
