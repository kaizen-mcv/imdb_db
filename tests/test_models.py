"""Tests de coherencia de la metadata de modelos."""

from imdb.models import DATASETS, LOAD_ORDER


def test_load_order_cubre_todos_los_datasets():
    """Todos los datasets deben estar en LOAD_ORDER."""
    assert set(LOAD_ORDER) == set(DATASETS.keys())


def test_cada_dataset_tiene_campos_requeridos():
    campos = {"url", "table", "model", "columns"}
    for nombre, info in DATASETS.items():
        assert campos.issubset(info.keys()), (
            f"{nombre} no tiene todos los campos"
        )


def test_cada_dataset_apunta_a_un_tsv_gz():
    for nombre, info in DATASETS.items():
        assert info["url"].endswith(".tsv.gz"), nombre


def test_tablas_unicas():
    """Ninguna tabla aparece en dos datasets."""
    tablas = [info["table"] for info in DATASETS.values()]
    assert len(tablas) == len(set(tablas))
