# Experimento A — Módulo de Cálculo de Pedidos

Este repositório foi criado para uma investigação prática da disciplina de
Engenharia de Software III sobre o tema **Inspeção em Software: Verificação e
Validação de Software**. O objetivo é observar como uma ferramenta de IA pode
ajudar a identificar defeitos no código e quais cuidados ainda exigem análise
humana.

O exemplo é um módulo pequeno de checkout em [`checkout.py`](checkout.py). Ele
calcula o total de um pedido com desconto VIP, cupons armazenados em SQLite e
frete. As regras descritas no código servem como referência para comparar o
comportamento esperado com o comportamento implementado.

## Como o Qodo é usado

O Qodo analisa o Pull Request e aponta possíveis problemas de segurança,
correção e confiabilidade. Na revisão deste experimento, ele apontou, entre
outros casos, uma consulta vulnerável a SQL Injection, aplicação de cupons
inativos, total negativo e falta de preparação do banco de dados. Os achados
foram examinados antes de aplicar correções: uma sugestão da IA não substitui
uma verificação humana.

Os testes automatizados em [`tests/test_checkout.py`](tests/test_checkout.py)
foram adicionados para verificar as regras e reproduzir os cenários da revisão.
Eles cobrem cupons ativos e inativos, tentativa de SQL Injection, cupom de
100%, desconto VIP, entradas negativas, banco inexistente e o limite de
R$ 200,00 para o frete. O Qodo foi usado na **revisão**; os testes foram
escritos separadamente com `pytest`.

## Executar os testes

Com Python instalado, execute na raiz do projeto:

```powershell
py -m pip install pytest
py -m pytest -q
```

Cada teste utiliza um diretório temporário, de modo que a execução não depende
de um arquivo `loja.db` preexistente. A configuração de revisão do Qodo está
em [`.pr_agent.toml`](.pr_agent.toml).
