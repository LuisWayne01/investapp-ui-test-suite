import csv
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect

from pages.navbar_component import NavbarComponent
from pages.portfolio_page import PortfolioPage


def carregar_dados_investimentos_csv():
    """Lê a massa CSV com garantia de resolução de caminho dinâmico."""
    caminho = (
        Path(__file__).resolve().parent.parent
        / "data"
        / "dados_investimentos_ui.csv"
    )

    if not caminho.exists():
        raise FileNotFoundError(f"CSV não localizado em: {caminho}")

    cenarios = []
    with open(caminho, mode="r", encoding="utf-8-sig") as f:
        leitor = csv.DictReader(f)
        for linha in leitor:
            cenarios.append((
                linha["asset_name"],
                linha["amount"],
                linha["purchase_price"],
                linha["days_invested"],
                linha["planned_days"],
                linha["deve_ter_sucesso"].strip().lower() == "true",
            ))
    return cenarios


@pytest.mark.parametrize(
    "asset, amount, price, days, planned, deve_sucesso",
    carregar_dados_investimentos_csv()
)
def test_cadastro_aporte_ddt_pom(
    logged_page: Page,
    navbar: NavbarComponent,
    portfolio_page: PortfolioPage,
    asset, amount, price, days, planned, deve_sucesso
):
    """Executa múltiplos cadastros na UI delegando a interação física
    ao Page Object."""
    navbar.navegar_para_carteira()

    # Espera a carteira carregar da API antes de contar as linhas existentes.
    portfolio_page.aguardar_carregamento()
    linhas = portfolio_page.obter_linhas_por_ativo_e_prazo(asset, days, planned)
    total_antes = linhas.count()

    portfolio_page.cadastrar_aporte(
        ativo=asset,
        quantidade=amount,
        preco=price,
        dias_inv=days,
        dias_plan=planned
    )

    try:
        if deve_sucesso:
            # Exatamente uma linha nova para este ativo/prazo.
            expect(linhas).to_have_count(total_antes + 1, timeout=15000)
        else:
            expect(portfolio_page.alerta_erro).to_be_visible(timeout=10000)
    finally:
        # Remove o aporte criado (inclusive o negativo, se a aplicação o aceitou),
        # para a carteira compartilhada não acumular dados entre execuções.
        if linhas.count() > total_antes:
            portfolio_page.excluir_linha(linhas.last)