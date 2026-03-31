"""Ensamble validar_experiencia con datos crudos (sin booleanos precalculados)."""
from __future__ import annotations

import pytest

from services.experiencia_rules import validar_experiencia


@pytest.mark.integration
def test_sala_general_dos_rutas_distintas_por_calculo_cumple():
    """Dos rutas satisfechas vía campos numéricos (sin claves r1..r7 bool)."""
    data = {
        "r1_anios_docencia_total": 5,
        "r1_anios_docencia_posgrado": 2,
        "tramites_acreditacion": 2,
    }
    ok, msg, rutas = validar_experiencia("Ingeniería, Industria y Construcción", data)
    assert ok is True
    assert set(rutas) == {"Ruta 1", "Ruta 3"}
    assert "2 rutas" in msg


@pytest.mark.integration
def test_sala_general_una_sola_ruta_por_calculo_falla():
    data = {
        "r1_anios_docencia_total": 5,
        "r1_anios_docencia_posgrado": 2,
    }
    ok, _, rutas = validar_experiencia("Ciencias Naturales, Matemáticas y Estadística", data)
    assert ok is False
    assert rutas == ["Ruta 1"]


@pytest.mark.integration
def test_tramites_institucionales_una_ruta_especial_por_calculo_cumple():
    """TI-1 desde años (misma lógica que la UI) sin pasar ti1/ti2/ti3 booleanos."""
    data = {"anios_rector_vicerrector": 4.0, "anios_direccion_planeacion_calidad_financiero": 0.0}
    ok, _, rutas = validar_experiencia("Trámites Institucionales", data)
    assert ok is True
    assert rutas == ["Ruta TI-1"]
