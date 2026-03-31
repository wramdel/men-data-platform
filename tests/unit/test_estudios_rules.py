"""Reglas de estudios CONACES (módulo puro services.estudios_rules)."""
from __future__ import annotations

import pytest

from services.estudios_rules import validar_estudios


def _base_estudios(**overrides):
    """Plantilla de data alineada con el workspace (checkboxes + certificados)."""
    data = {
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
        "profesional_en_educacion": False,
        "posgrado_en_educacion": False,
    }
    data.update(overrides)
    return data


@pytest.mark.unit
def test_titulo_exterior_sin_convalidacion_falla_siempre():
    data = _base_estudios(titulo_exterior=True, convalidado=False, profesional=True, maestria=True)
    ok, msg = validar_estudios("TIC", data)
    assert ok is False
    assert "convalidación" in msg.lower()


@pytest.mark.unit
def test_sala_educacion_requiere_ambos_flags_educacion():
    data_ok = _base_estudios(profesional_en_educacion=True, posgrado_en_educacion=True)
    assert validar_estudios("Educación", data_ok)[0] is True

    data_fail = _base_estudios(profesional_en_educacion=True, posgrado_en_educacion=False)
    assert validar_estudios("Educación", data_fail)[0] is False


@pytest.mark.unit
def test_sala_salud_profesional_y_maestria():
    data = _base_estudios(profesional=True, maestria=True)
    ok, _ = validar_estudios("Salud y Bienestar", data)
    assert ok is True


@pytest.mark.unit
def test_sala_salud_especialidad_medica_sin_maestria():
    data = _base_estudios(profesional=True, especialidad_medica=True)
    ok, _ = validar_estudios("Salud y Bienestar", data)
    assert ok is True


@pytest.mark.unit
def test_sala_generica_profesional_y_doctorado():
    data = _base_estudios(profesional=True, doctorado=True)
    ok, _ = validar_estudios("TIC", data)
    assert ok is True


@pytest.mark.unit
def test_sala_tecnicos_tecnologo_y_certificados_suficientes():
    data = _base_estudios(tecnologo=True, certificados=True, duracion_certificados=5.0)
    ok, _ = validar_estudios("Técnicos Profesionales y Tecnológicos", data)
    assert ok is True


@pytest.mark.unit
def test_sala_tecnicos_insuficiente_sin_posgrado_ni_certificados_largos():
    data = _base_estudios(tecnico=True, certificados=True, duracion_certificados=4.0)
    ok, _ = validar_estudios("Técnicos Profesionales y Tecnológicos", data)
    assert ok is False


@pytest.mark.unit
def test_sala_generica_solo_maestria_sin_profesional_no_cumple():
    data = _base_estudios(maestria=True)
    ok, _ = validar_estudios("TIC", data)
    assert ok is False


@pytest.mark.unit
def test_sala_generica_solo_profesional_sin_posgrado_no_cumple():
    data = _base_estudios(profesional=True)
    ok, _ = validar_estudios("Artes y Humanidades", data)
    assert ok is False


@pytest.mark.unit
def test_sala_generica_solo_doctorado_sin_profesional_no_cumple():
    data = _base_estudios(doctorado=True)
    ok, _ = validar_estudios("Ciencias Sociales, Periodismo e Información", data)
    assert ok is False
