"""Pruebas del servicio SNIES sin leer archivos (DataFrame inyectado)."""
from __future__ import annotations

import pytest

from services.snies_service import (
    get_programa_detalle,
    get_snies_instituciones,
    get_titulos_por_institucion_y_nivel,
    map_nivel_ui_to_snies,
)

from tests.fixtures.snies_sample_data import dataframe_programas_snies_minimo, dataframe_programas_snies_vacio


@pytest.mark.unit
def test_map_nivel_ui_profesional_incluye_universitario():
    valores = map_nivel_ui_to_snies("Profesional")
    assert "UNIVERSITARIO" in valores
    assert "PROFESIONAL" in valores


@pytest.mark.unit
def test_map_nivel_ui_desconocido_devuelve_lista_vacia():
    assert map_nivel_ui_to_snies("Nivel inventado") == []


@pytest.mark.unit
def test_get_snies_instituciones_vacio_si_dataframe_sin_filas(patch_snies_programas_df):
    patch_snies_programas_df(dataframe_programas_snies_vacio())
    assert get_snies_instituciones() == []


@pytest.mark.unit
def test_get_snies_instituciones_ordenadas_y_unicas(patch_snies_programas_df):
    patch_snies_programas_df(dataframe_programas_snies_minimo())
    inst = get_snies_instituciones()
    assert inst == sorted(inst)
    assert inst == ["INSTITUCIÓN BETA", "UNIVERSIDAD EJEMPLO ALPHA"]


@pytest.mark.unit
def test_get_titulos_filtra_institucion_y_nivel(patch_snies_programas_df):
    patch_snies_programas_df(dataframe_programas_snies_minimo())
    titulos = get_titulos_por_institucion_y_nivel("UNIVERSIDAD EJEMPLO ALPHA", "Profesional")
    assert titulos == ["LICENCIADO EN MATEMÁTICAS"]


@pytest.mark.unit
def test_get_programa_detalle_campos_esperados(patch_snies_programas_df):
    patch_snies_programas_df(dataframe_programas_snies_minimo())
    det = get_programa_detalle(
        "UNIVERSIDAD EJEMPLO ALPHA",
        "Profesional",
        "LICENCIADO EN MATEMÁTICAS",
    )
    assert det is not None
    assert det["nombre_institucion"] == "UNIVERSIDAD EJEMPLO ALPHA"
    assert det["titulo_otorgado"] == "LICENCIADO EN MATEMÁTICAS"
    assert "Matemáticas" in det["campo_amplio"]
    assert det["nivel_formacion"] == "UNIVERSITARIO"


@pytest.mark.unit
def test_get_programa_detalle_sin_coincidencia(patch_snies_programas_df):
    patch_snies_programas_df(dataframe_programas_snies_minimo())
    assert get_programa_detalle("NO EXISTE", "Profesional", "X") is None


@pytest.mark.unit
def test_get_titulos_institucion_valida_nivel_sin_filas_en_data(patch_snies_programas_df):
    """Institución existe pero ningún programa coincide con el nivel mapeado (p. ej. Doctorado)."""
    patch_snies_programas_df(dataframe_programas_snies_minimo())
    assert (
        get_titulos_por_institucion_y_nivel("UNIVERSIDAD EJEMPLO ALPHA", "Doctorado") == []
    )


@pytest.mark.unit
def test_get_titulos_institucion_inexistente_lista_vacia(patch_snies_programas_df):
    patch_snies_programas_df(dataframe_programas_snies_minimo())
    assert get_titulos_por_institucion_y_nivel("UNIVERSIDAD FANTASMA", "Profesional") == []


@pytest.mark.unit
def test_get_titulos_y_detalle_robustos_espacios_en_institucion(patch_snies_programas_df):
    patch_snies_programas_df(dataframe_programas_snies_minimo())
    inst = "  UNIVERSIDAD EJEMPLO ALPHA  "
    assert get_titulos_por_institucion_y_nivel(inst, "Profesional") == ["LICENCIADO EN MATEMÁTICAS"]
    det = get_programa_detalle(inst, "  Profesional ", "LICENCIADO EN MATEMÁTICAS")
    assert det is not None
    assert det["titulo_otorgado"] == "LICENCIADO EN MATEMÁTICAS"


@pytest.mark.unit
def test_map_nivel_ui_robusto_mayusculas_y_espacios():
    assert map_nivel_ui_to_snies("  PROFESIONAL ") == map_nivel_ui_to_snies("Profesional")
