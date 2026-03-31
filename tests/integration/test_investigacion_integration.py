"""Flujos realistas de validación de investigación (estado + mensaje)."""
from __future__ import annotations

import pytest

from services.investigacion_rules import validar_investigacion


@pytest.mark.integration
def test_flujo_sala_general_cumple_y_mensaje_corto():
    data = {
        "productos_investigacion": True,
        "grupo_reconocido": False,
        "categoria_investigador": "",
    }
    estado, msg = validar_investigacion("Ingeniería, Industria y Construcción", data)
    assert estado == "cumple"
    assert "Cumple investigación" in msg


@pytest.mark.integration
def test_flujo_sala_general_no_cumple_mensaje_completo():
    data = {
        "productos_investigacion": False,
        "grupo_reconocido": False,
        "categoria_investigador": "Inválida",
    }
    estado, msg = validar_investigacion("Ciencias Naturales, Matemáticas y Estadística", data)
    assert estado == "no_cumple"
    assert "Junior" in msg and "Asociado" in msg


@pytest.mark.integration
def test_flujo_tecnicos_homologacion_mensaje_unificado():
    data = {
        "productos_investigacion": False,
        "anios_conceptos_tecnicos": 0,
        "anios_prototipos_industriales": 5.0,
        "anios_innovacion_productos_servicios": 0,
    }
    estado, msg = validar_investigacion("Técnicos Profesionales y Tecnológicos", data)
    assert estado == "cumple"
    assert "satisface regla general y/o homologación" in msg


@pytest.mark.integration
def test_flujo_tecnicos_falla_mensaje_compuesto():
    data = {
        "anios_conceptos_tecnicos": 2.0,
        "anios_prototipos_industriales": 1.0,
        "anios_innovacion_productos_servicios": 0.0,
    }
    estado, msg = validar_investigacion("Técnicos Profesionales y Tecnológicos", data)
    assert estado == "no_cumple"
    assert "No cumple:" in msg
    assert "homologarse" in msg


@pytest.mark.integration
def test_flujo_tramites_no_aplica_mensaje_fijo():
    estado, msg = validar_investigacion(
        "Trámites Institucionales",
        {"productos_investigacion": True, "categoria_investigador": "Senior"},
    )
    assert estado == "no_aplica"
    assert "requisito de investigación no aplica" in msg
