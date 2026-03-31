"""
DataFrames mínimos que imitan columnas usadas en services/snies_service.py.

Los nombres deben alinearse con Programas.xlsx (incl. tildes) para que _pick_col los resuelva.
"""
from __future__ import annotations

import pandas as pd


def dataframe_programas_snies_minimo() -> pd.DataFrame:
    """
    Tres filas, dos instituciones, para probar filtro por institución y nivel.
    """
    return pd.DataFrame(
        {
            "NOMBRE_INSTITUCIÓN": [
                "UNIVERSIDAD EJEMPLO ALPHA",
                "UNIVERSIDAD EJEMPLO ALPHA",
                "INSTITUCIÓN BETA",
            ],
            "TITULO_OTORGADO": [
                "LICENCIADO EN MATEMÁTICAS",
                "MAESTRO EN EDUCACIÓN",
                "TÉCNICO LABORAL EN SISTEMAS",
            ],
            "NIVEL_DE_FORMACIÓN": [
                "UNIVERSITARIO",
                "MAESTRÍA",
                "TÉCNICO PROFESIONAL",
            ],
            "CINE_F_2013_AC_CAMPO_AMPLIO": [
                "Ciencias Naturales, Matemáticas y Estadística",
                "Educación",
                "TIC",
            ],
            "NIVEL_ACADÉMICO": [
                "Universitario",
                "Posgrado",
                "Técnico profesional",
            ],
        }
    )


def dataframe_programas_snies_vacio() -> pd.DataFrame:
    """Mismo esquema que el mínimo pero sin filas (casos vacíos)."""
    return pd.DataFrame(
        columns=[
            "NOMBRE_INSTITUCIÓN",
            "TITULO_OTORGADO",
            "NIVEL_DE_FORMACIÓN",
            "CINE_F_2013_AC_CAMPO_AMPLIO",
            "NIVEL_ACADÉMICO",
        ]
    )
