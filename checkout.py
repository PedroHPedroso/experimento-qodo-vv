import sqlite3


def buscar_cupom(codigo_cupom):
    with sqlite3.connect("loja.db") as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS cupons ("
            "codigo TEXT PRIMARY KEY, percentual REAL NOT NULL, ativo INTEGER NOT NULL)"
        )
        cursor = conn.execute(
            "SELECT percentual, ativo FROM cupons WHERE codigo = ?",
            (codigo_cupom,),
        )
        resultado = cursor.fetchone()

    if resultado is None or not resultado[1]:
        return None
    return resultado


def calcular_total_pedido(itens, codigo_cupom=None, cliente_vip=False):
    """
    Calcula o valor final do pedido com descontos e frete.

    Descontos VIP e de cupom não são cumulativos: aplica-se apenas o maior.
    O total após descontos não pode ser negativo. Frete grátis exige total
    estritamente maior que R$ 200,00.
    """
    subtotal = 0.0
    for item in itens:
        preco = item["preco"]
        quantidade = item["quantidade"]
        if preco < 0 or quantidade < 0:
            raise ValueError("preço e quantidade não podem ser negativos")
        subtotal += preco * quantidade

    descontos = [subtotal * 0.10 if cliente_vip else 0.0]
    if codigo_cupom:
        cupom = buscar_cupom(codigo_cupom)
        if cupom:
            descontos.append(subtotal * (cupom[0] / 100))

    desconto = max(descontos)
    total = max(subtotal - desconto, 0.0)
    frete = 0.0 if total > 200 else 20.0
    return total + frete
