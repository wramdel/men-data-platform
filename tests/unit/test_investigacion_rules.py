"""Pruebas unitarias de services.investigacion_rules.validar_investigacion."""
from __future__ import annotations

import pytest

from services.investigacion_rules import validar_investigacion

SALA_TIC = "TIC"
SALA_TECNICOS = "Técnicos Profesionales y Tecnológicos"
SALA_TRAMITES = "Trámites Institucionales"


def _vacio() -> dict:
    return {}


@pytest.mark.unit
def test_general_sin_condiciones_no_cumple():
    estado, msg = validar_investigacion(SALA_TIC, _vacio())
    assert estado == "no_cumple"
    assert "No cumple" in msg
    assert "productos de investigación" in msg


@pytest.mark.unit
def test_general_productos_true_cumple():
    estado, msg = validar_investigacion(SALA_TIC, {"productos_investigacion": True})
    assert estado == "cumple"
    assert "al menos una condición" in msg


@pytest.mark.unit
def test_general_grupo_true_cumple():
    estado, msg = validar_investigacion("Salud y Bienestar", {"grupo_reconocido": True})
    assert estado == "cumple"


@pytest.mark.unit
def test_general_categoria_junior_cumple():
    estado, msg = validar_investigacion(SALA_TIC, {"categoria_investigador": "Junior"})
    assert estado == "cumple"


@pytest.mark.unit
def test_general_categoria_asociado_cumple():
    estado, msg = validar_investigacion("Educación", {"categoria_investigador": "Asociado"})
    assert estado == "cumple"


@pytest.mark.unit
def test_general_categoria_senior_cumple():
    estado, msg = validar_investigacion(SALA_TIC, {"categoria_investigador": "Senior"})
    assert estado == "cumple"


@pytest.mark.unit
def test_general_categoria_invalida_no_cumple():
    estado, msg = validar_investigacion(SALA_TIC, {"categoria_investigador": "Otro"})
    assert estado == "no_cumple"


@pytest.mark.unit
def test_general_multiples_condiciones_cumple():
    d = {
        "productos_investigacion": True,
        "grupo_reconocido": True,
        "categoria_investigador": "Junior",
    }
    estado, msg = validar_investigacion("Artes y Humanidades", d)
    assert estado == "cumple"


@pytest.mark.unit
def test_categoria_trim_cumple():
    estado, _ = validar_investigacion(SALA_TIC, {"categoria_investigador": "  Senior  "})
    assert estado == "cumple"


@pytest.mark.unit
def test_tecnicos_sin_general_ni_homologacion_no_cumple():
    estado, msg = validar_investigacion(SALA_TECNICOS, _vacio())
    assert estado == "no_cumple"
    assert "homologarse" in msg


@pytest.mark.unit
def test_tecnicos_homologacion_conceptos_cumple():
    d = {"anios_conceptos_tecnicos": 5.0}
    estado, msg = validar_investigacion(SALA_TECNICOS, d)
    assert estado == "cumple"
    assert "homologación" in msg.lower() or "homologación" in msg


@pytest.mark.unit
def test_tecnicos_homologacion_prototipos_cumple():
    d = {"anios_prototipos_industriales": 6.0}
    estado, _ = validar_investigacion(SALA_TECNICOS, d)
    assert estado == "cumple"


@pytest.mark.unit
def test_tecnicos_homologacion_innovacion_cumple():
    d = {"anios_innovacion_productos_servicios": 5.0}
    estado, _ = validar_investigacion(SALA_TECNICOS, d)
    assert estado == "cumple"


@pytest.mark.unit
def test_tecnicos_cumple_solo_regla_general():
    d = {"productos_investigacion": True}
    estado, msg = validar_investigacion(SALA_TECNICOS, d)
    assert estado == "cumple"
    assert "general" in msg.lower() or "homologación" in msg


@pytest.mark.unit
def test_tramites_siempre_no_aplica():
    estado, msg = validar_investigacion(SALA_TRAMITES, _vacio())
    assert estado == "no_aplica"
    assert "no aplica" in msg.lower()


@pytest.mark.unit
def test_tramites_no_aplica_aun_con_productos():
    estado, msg = validar_investigacion(
        "tramites institucionales",
        {"productos_investigacion": True, "grupo_reconocido": True},
    )
    assert estado == "no_aplica"
    assert "Trámites Institucionales" in msg
