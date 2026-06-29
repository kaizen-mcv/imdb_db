"""Tests unitarios de los helpers y transformadores de importer."""

from imdb.importer import (
    _bool,
    _col,
    _float,
    _int,
    _limpiar_valor,
    _transformar_name_basics,
    _transformar_title_basics,
    _transformar_title_ratings,
)


class TestLimpiarValor:
    """Tests de _limpiar_valor: \\N -> None."""

    def test_null_literal_a_none(self):
        assert _limpiar_valor("\\N") is None

    def test_string_normal_sin_cambios(self):
        assert _limpiar_valor("hola") == "hola"

    def test_string_vacio_se_preserva(self):
        assert _limpiar_valor("") == ""


class TestInt:
    """Tests de _int."""

    def test_entero_valido(self):
        assert _int("42") == 42

    def test_null_a_none(self):
        assert _int("\\N") is None

    def test_valor_invalido_a_none(self):
        assert _int("abc") is None

    def test_negativo(self):
        assert _int("-5") == -5


class TestFloat:
    """Tests de _float."""

    def test_decimal_valido(self):
        assert _float("7.5") == 7.5

    def test_null_a_none(self):
        assert _float("\\N") is None

    def test_invalido_a_none(self):
        assert _float("xx") is None


class TestBool:
    """Tests de _bool."""

    def test_uno_a_true(self):
        assert _bool("1") is True

    def test_cero_a_false(self):
        assert _bool("0") is False

    def test_null_a_none(self):
        assert _bool("\\N") is None


class TestCol:
    """Tests de _col: acceso seguro a columnas."""

    def test_columna_existente(self):
        assert _col(["a", "b", "c"], 1) == "b"

    def test_columna_fuera_de_rango_devuelve_null(self):
        # IMDb a veces omite columnas finales
        assert _col(["a"], 5) == "\\N"


class TestTransformarTitleBasics:
    """Tests del transformador de title.basics."""

    def test_fila_completa(self):
        fila = [
            "tt0000001",
            "short",
            "Carmencita",
            "Carmencita",
            "0",
            "1894",
            "\\N",
            "1",
            "Documentary,Short",
        ]
        resultado = _transformar_title_basics(fila)
        assert resultado == (
            "tt0000001",
            "short",
            "Carmencita",
            "Carmencita",
            False,
            1894,
            None,
            1,
            "Documentary,Short",
        )

    def test_con_valores_null(self):
        fila = [
            "tt0000002",
            "\\N",
            "Titulo",
            "\\N",
            "\\N",
            "\\N",
            "\\N",
            "\\N",
            "\\N",
        ]
        resultado = _transformar_title_basics(fila)
        assert resultado[0] == "tt0000002"
        assert resultado[1] is None
        assert resultado[4] is None
        assert resultado[8] is None


class TestTransformarTitleRatings:
    """Tests del transformador de title.ratings."""

    def test_rating_valido(self):
        fila = ["tt0000001", "5.7", "2084"]
        resultado = _transformar_title_ratings(fila)
        assert resultado == ("tt0000001", 5.7, 2084)


class TestTransformarNameBasics:
    """Tests del transformador de name.basics."""

    def test_persona_viva(self):
        fila = [
            "nm0000001",
            "Fred Astaire",
            "1899",
            "1987",
            "soundtrack,actor",
            "tt0043044,tt0053137",
        ]
        resultado = _transformar_name_basics(fila)
        assert resultado[0] == "nm0000001"
        assert resultado[1] == "Fred Astaire"
        assert resultado[2] == 1899
        assert resultado[3] == 1987
