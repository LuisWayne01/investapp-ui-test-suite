
from playwright.sync_api import Page, expect

from pages.navbar_component import NavbarComponent
from pages.tax_optimizer_page import TaxOptimizerPage


def test_simulacao_resgate_melhor_opcao(
    logged_page: Page,
    navbar: NavbarComponent
):
    """Valida a recomendação de menor imposto no resgate."""

    otimizador = TaxOptimizerPage(logged_page)

    navbar.navegar_para_otimizador_fiscal()
    expect(otimizador.secao_otimizador).to_be_visible()

    otimizador.simular_resgate("1000")

    expect(otimizador.tabela_resultados).to_be_visible()

    melhor_opcao = otimizador.obter_melhor_opcao()
    expect(melhor_opcao).to_be_visible()
    expect(melhor_opcao).to_contain_text("MELHOR OPÇÃO")
