import random

from playwright.sync_api import Page, expect

from pages.navbar_component import NavbarComponent
from pages.portfolio_page import PortfolioPage


def _prazo_unico():
    """Prazo aleatório para identificar só o aporte deste teste."""
    return str(random.randint(100, 499)), str(random.randint(500, 999))


# --- Integrante 4: exclusão de ativos e métricas consolidadas ---
def test_excluir_ativo_remove_da_tabela(
    logged_page: Page, navbar: NavbarComponent, portfolio_page: PortfolioPage
):
    """Cadastra um aporte, exclui e confere que ele sumiu da tabela."""
    dias_inv, dias_plan = _prazo_unico()
    navbar.navegar_para_carteira()
    portfolio_page.cadastrar_aporte("Poupança", "100.00", "1.00", dias_inv, dias_plan)

    linhas = portfolio_page.obter_linhas_por_ativo_e_prazo("Poupança", dias_inv, dias_plan)
    expect(linhas).to_have_count(1, timeout=15000)

    portfolio_page.excluir_ativo_por_prazo("Poupança", dias_inv, dias_plan, confirmar=True)

    expect(linhas).to_have_count(0, timeout=15000)


def test_cancelar_exclusao_mantem_ativo(
    logged_page: Page, navbar: NavbarComponent, portfolio_page: PortfolioPage
):
    """Cancela o alerta de confirmação e confere que o ativo continua na tabela."""
    dias_inv, dias_plan = _prazo_unico()
    navbar.navegar_para_carteira()
    portfolio_page.cadastrar_aporte("Poupança", "100.00", "1.00", dias_inv, dias_plan)

    linhas = portfolio_page.obter_linhas_por_ativo_e_prazo("Poupança", dias_inv, dias_plan)
    expect(linhas).to_have_count(1, timeout=15000)

    portfolio_page.excluir_ativo_por_prazo("Poupança", dias_inv, dias_plan, confirmar=False)

    expect(linhas).to_have_count(1)

    # Limpeza: remove o aporte de teste
    portfolio_page.excluir_ativo_por_prazo("Poupança", dias_inv, dias_plan, confirmar=True)
    expect(linhas).to_have_count(0, timeout=15000)


def test_exclusao_recalcula_patrimonio_total(
    logged_page: Page, navbar: NavbarComponent, portfolio_page: PortfolioPage
):
    """Exclui um aporte e confere que o card de Patrimônio Total diminui."""
    dias_inv, dias_plan = _prazo_unico()
    navbar.navegar_para_carteira()
    portfolio_page.cadastrar_aporte("Poupança", "5000.00", "1.00", dias_inv, dias_plan)

    linhas = portfolio_page.obter_linhas_por_ativo_e_prazo("Poupança", dias_inv, dias_plan)
    expect(linhas).to_have_count(1, timeout=15000)

    texto_antes = portfolio_page.card_patrimonio_total.inner_text()
    patrimonio_antes = portfolio_page.obter_patrimonio_total()

    portfolio_page.excluir_ativo_por_prazo("Poupança", dias_inv, dias_plan)

    expect(portfolio_page.card_patrimonio_total).not_to_have_text(texto_antes, timeout=5000)
    assert portfolio_page.obter_patrimonio_total() < patrimonio_antes