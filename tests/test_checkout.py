import sqlite3

import pytest

from checkout import buscar_cupom, calcular_total_pedido


@pytest.fixture(autouse=True)
def banco_isolado(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)


def cadastrar_cupom(codigo, percentual, ativo):
    # A primeira consulta cria a tabela no banco ainda vazio.
    buscar_cupom("inexistente")
    with sqlite3.connect("loja.db") as conn:
        conn.execute(
            "INSERT INTO cupons (codigo, percentual, ativo) VALUES (?, ?, ?)",
            (codigo, percentual, ativo),
        )


def test_banco_inexistente_e_cupom_desconhecido(tmp_path):
    assert not (tmp_path / "loja.db").exists()
    assert calcular_total_pedido([{"preco": 100, "quantidade": 1}], "NOVO") == 120
    assert (tmp_path / "loja.db").exists()
    with sqlite3.connect("loja.db") as conn:
        assert conn.execute("SELECT name FROM sqlite_master WHERE name = 'cupons'").fetchone()


@pytest.mark.parametrize("ativo, esperado", [(1, 170), (0, 220)])
def test_cupom_ativo_ou_inativo(ativo, esperado):
    cadastrar_cupom("OFF25", 25, ativo)
    assert calcular_total_pedido([{"preco": 200, "quantidade": 1}], "OFF25") == esperado


def test_sql_injection_nao_fabrica_cupom():
    cadastrar_cupom("REAL", 10, 1)
    codigo_malicioso = "' UNION ALL SELECT 100,1 --"
    assert buscar_cupom(codigo_malicioso) is None
    assert calcular_total_pedido([{"preco": 300, "quantidade": 1}], codigo_malicioso) == 300


def test_cupom_de_100_por_cento_com_vip_nao_gera_total_negativo():
    cadastrar_cupom("GRATIS", 100, 1)
    assert calcular_total_pedido([{"preco": 300, "quantidade": 1}], "GRATIS", True) == 20


def test_vip_recebe_10_por_cento():
    assert calcular_total_pedido([{"preco": 300, "quantidade": 1}], cliente_vip=True) == 270


def test_vip_e_cupom_aplicam_apenas_o_maior_desconto():
    cadastrar_cupom("OFF20", 20, 1)
    assert calcular_total_pedido([{"preco": 300, "quantidade": 1}], "OFF20", True) == 240


@pytest.mark.parametrize("item", [
    {"preco": -1, "quantidade": 1},
    {"preco": 100, "quantidade": -1},
])
def test_valores_negativos_sao_rejeitados(item):
    with pytest.raises(ValueError):
        calcular_total_pedido([item])


@pytest.mark.parametrize("subtotal, esperado", [(200, 220), (201, 201)])
def test_frete_no_limite_de_200(subtotal, esperado):
    assert calcular_total_pedido([{"preco": subtotal, "quantidade": 1}]) == esperado
