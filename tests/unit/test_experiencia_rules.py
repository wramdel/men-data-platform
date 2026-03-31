"""Pruebas unitarias de reglas de experiencia (cálculo por ruta y agregación)."""
from __future__ import annotations

import pytest

from services.experiencia_rules import (
    _cumple_ruta_1,
    _cumple_ruta_2,
    _cumple_ruta_3,
    _cumple_ruta_4,
    _cumple_ruta_5,
    _cumple_ruta_6,
    _cumple_ruta_7,
    validar_experiencia,
)


def _bool_rutas(**activas: bool) -> dict:
    """Siete booleanos r1..r7 (modo compatible con Streamlit)."""
    data = {f"r{i}": False for i in range(1, 8)}
    for k, v in activas.items():
        data[k] = v
    return data


def _bool_ti(ti1: bool = False, ti2: bool = False, ti3: bool = False) -> dict:
    return {"ti1": ti1, "ti2": ti2, "ti3": ti3}


# --- Rutas individuales (helpers) ---


@pytest.mark.unit
def test_ruta_1_cumple():
    assert _cumple_ruta_1({"r1_anios_docencia_total": 5, "r1_anios_docencia_posgrado": 2}) is True


@pytest.mark.unit
def test_ruta_1_falla_por_docencia_insuficiente():
    assert _cumple_ruta_1({"r1_anios_docencia_total": 4, "r1_anios_docencia_posgrado": 2}) is False
    assert _cumple_ruta_1({"r1_anios_docencia_total": 5, "r1_anios_docencia_posgrado": 1}) is False


@pytest.mark.unit
def test_ruta_2_cumple():
    d = {"r2_anios_docencia_total": 5, "experiencia_investigacion": True}
    assert _cumple_ruta_2(d) is True


@pytest.mark.unit
def test_ruta_3_cumple_por_rc():
    assert _cumple_ruta_3({"tramites_rc_o_institucionales": 4, "tramites_acreditacion": 0}) is True


@pytest.mark.unit
def test_ruta_3_cumple_por_acreditacion():
    assert _cumple_ruta_3({"tramites_rc_o_institucionales": 0, "tramites_acreditacion": 2}) is True


@pytest.mark.unit
def test_ruta_4_cumple_por_sala():
    assert _cumple_ruta_4({"anios_integrante_sala_conaces": 1, "sesiones_banco_elegibles": 0}) is True


@pytest.mark.unit
def test_ruta_4_cumple_por_sesiones():
    assert _cumple_ruta_4({"anios_integrante_sala_conaces": 0, "sesiones_banco_elegibles": 4}) is True


@pytest.mark.unit
def test_ruta_5_cumple():
    assert _cumple_ruta_5({"r5_anios_docencia_total": 3, "anios_ejercicio_profesional": 5}) is True


@pytest.mark.unit
def test_ruta_6_cumple():
    assert _cumple_ruta_6({"r6_anios_docencia_total": 3, "anios_direccion_academica": 5}) is True


@pytest.mark.unit
def test_ruta_7_cumple():
    assert _cumple_ruta_7({"anios_diseno_o_gestion_curricular": 5}) is True


# --- Regla agregada salas generales (booleanos) ---


@pytest.mark.unit
def test_regla_general_cumple_con_dos_rutas():
    ok, msg, rutas = validar_experiencia("TIC", _bool_rutas(r1=True, r3=True))
    assert ok is True
    assert len(rutas) == 2
    assert "mínimo 2" in msg or "2 rutas" in msg


@pytest.mark.unit
def test_regla_general_falla_con_una_sola_ruta():
    ok, _, rutas = validar_experiencia("Educación", _bool_rutas(r7=True))
    assert ok is False
    assert len(rutas) == 1


@pytest.mark.unit
def test_regla_general_falla_con_cero_rutas():
    ok, _, rutas = validar_experiencia("Artes y Humanidades", _bool_rutas())
    assert ok is False
    assert rutas == []


# --- Trámites institucionales ---


@pytest.mark.unit
def test_tramites_cumple_con_ti_1():
    ok, msg, rutas = validar_experiencia("Trámites Institucionales", _bool_ti(ti1=True))
    assert ok is True
    assert rutas == ["Ruta TI-1"]
    assert "Cumple regla TI" in msg


@pytest.mark.unit
def test_tramites_cumple_con_ti_2():
    ok, _, rutas = validar_experiencia("tramites institucionales", _bool_ti(ti2=True))
    assert ok is True
    assert "Ruta TI-2" in rutas


@pytest.mark.unit
def test_tramites_cumple_con_ti_3():
    ok, _, rutas = validar_experiencia("Trámites Institucionales", _bool_ti(ti3=True))
    assert ok is True
    assert "Ruta TI-3" in rutas


@pytest.mark.unit
def test_tramites_falla_con_cero_rutas():
    ok, msg, rutas = validar_experiencia("Trámites Institucionales", _bool_ti())
    assert ok is False
    assert rutas == []
    assert "No cumple regla TI" in msg
