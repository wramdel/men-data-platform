"""
Fixtures y hooks compartidos.

pythonpath en pytest.ini apunta a frontend/streamlit_app para importar services.* .
"""
from __future__ import annotations

import pandas as pd
import pytest

import services.snies_service as snies_service


@pytest.fixture
def patch_snies_programas_df(monkeypatch: pytest.MonkeyPatch):
    """
    Reemplaza load_snies_programas por un DataFrame controlado en cada prueba.
    Evita leer Excel real y deja el LRU interno fuera del camino.
    """

    def _apply(df: pd.DataFrame) -> None:
        snies_service._cached_snies_programas.cache_clear()

        def _fake_load() -> pd.DataFrame:
            return df.copy()

        monkeypatch.setattr(snies_service, "load_snies_programas", _fake_load)

    yield _apply

    snies_service._cached_snies_programas.cache_clear()
