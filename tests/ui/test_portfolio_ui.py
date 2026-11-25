
from playwright.sync_api import Page, expect

import random

from playwright.sync_api import Page, expect

from pages.navbar_component import NavbarComponent
from pages.portfolio_page import PortfolioPage


<<<<<<< HEAD
def test_cadastrar_novo_aporte_carteira(
    logged_page: Page,
    navbar: NavbarComponent,
    portfolio_page: PortfolioPage
):
    navbar.navegar_para_carteira()

    dias_inv = "0"
    dias_plan = "365"

    portfolio_page.cadastrar_aporte(
        ativo="Poupança",
        quantidade="2500.00",
        preco="1.00",
        dias_inv=dias_inv,
        dias_plan=dias_plan
    )

    linha_aporte = (
        portfolio_page.obter_linha_por_ativo_e_prazo(
            "Poupança",
            dias_inv,
            dias_plan
        )
    )

    expect(linha_aporte).to_be_visible(timeout=5000)

    expect(linha_aporte).to_contain_text(
        "Poupança"
=======
def _prazo_unico() -> tuple[str, str]:
    """Gera dias decorridos/planejados únicos para achar a linha certa na tabela."""
    dias_inv = str(random.randint(100, 999))
    dias_plan = str(int(dias_inv) + 365)
    return dias_inv, dias_plan


# ===================== Integrante 3 — Cadastro de aportes (US02) =====================
def test_formulario_de_aporte_exibe_todos_os_campos(
    logged_page: Page, navbar: NavbarComponent, portfolio_page: PortfolioPage
):
    """Valida que a aba Carteira mostra todos os campos do formulário."""
    navbar.navegar_para_carteira()

    expect(portfolio_page.secao_carteira).to_be_visible()
    expect(portfolio_page.select_ativo).to_be_visible()
    expect(portfolio_page.input_quantidade).to_be_visible()
    expect(portfolio_page.input_preco_compra).to_be_visible()
    expect(portfolio_page.input_dias_investidos).to_be_visible()
    expect(portfolio_page.input_dias_planejados).to_be_visible()
    expect(portfolio_page.botao_adicionar).to_be_enabled()


def test_cadastrar_novo_aporte_carteira(
    logged_page: Page, navbar: NavbarComponent, portfolio_page: PortfolioPage
):
    """Cadastra um aporte e valida a inserção exata da linha na tabela."""
    navbar.navegar_para_carteira()
    dias_inv, dias_plan = _prazo_unico()

    portfolio_page.aguardar_carregamento()
    portfolio_page.cadastrar_aporte("CDB", "10", "100.00", dias_inv, dias_plan)

    linha = portfolio_page.obter_linha_por_ativo_e_prazo("CDB", dias_inv, dias_plan)
    try:
        expect(linha).to_be_visible(timeout=10000)
        expect(linha).to_contain_text("CDB")
        expect(linha).to_contain_text(f"{dias_inv} / {dias_plan} dias")
        expect(linha).to_contain_text("R$")
    finally:
        if linha.count() > 0:
            portfolio_page.excluir_linha(linha)


def test_formulario_limpa_campos_apos_cadastro(
    logged_page: Page, navbar: NavbarComponent, portfolio_page: PortfolioPage
):
    """Depois de salvar, quantidade e preço voltam vazios."""
    navbar.navegar_para_carteira()
    dias_inv, dias_plan = _prazo_unico()

    portfolio_page.cadastrar_aporte("Poupança", "5", "1.00", dias_inv, dias_plan)

    linha = portfolio_page.obter_linha_por_ativo_e_prazo("Poupança", dias_inv, dias_plan)
    try:
        expect(linha).to_be_visible(timeout=10000)
        expect(portfolio_page.input_quantidade).to_have_value("")
        expect(portfolio_page.input_preco_compra).to_have_value("")
    finally:
        if linha.count() > 0:
            portfolio_page.excluir_linha(linha)


# ============ Integrante 4 — Exclusão e métricas consolidadas (US02) ============
def test_excluir_ativo_remove_linha_da_tabela(
    logged_page: Page, navbar: NavbarComponent, portfolio_page: PortfolioPage
):
    """Cadastra um ativo, exclui e confere que a linha sumiu."""
    navbar.navegar_para_carteira()
    dias_inv, dias_plan = _prazo_unico()

    portfolio_page.cadastrar_aporte("LCI", "3", "50.00", dias_inv, dias_plan)
    linha = portfolio_page.obter_linha_por_ativo_e_prazo("LCI", dias_inv, dias_plan)
    expect(linha).to_have_count(1, timeout=10000)

    portfolio_page.excluir_linha(linha)

    expect(linha).to_have_count(0, timeout=10000)


def test_exclusao_trata_alerta_de_confirmacao(
    logged_page: Page, navbar: NavbarComponent, portfolio_page: PortfolioPage
):
    """Se a tela abrir alert/confirm, o Page Object aceita e a exclusão é concluída."""
    navbar.navegar_para_carteira()
    dias_inv, dias_plan = _prazo_unico()

    portfolio_page.cadastrar_aporte("LCA", "2", "20.00", dias_inv, dias_plan)
    linha = portfolio_page.obter_linha_por_ativo_e_prazo("LCA", dias_inv, dias_plan)
    expect(linha).to_be_visible(timeout=10000)

    portfolio_page.excluir_linha(linha)

    # A exclusão não fica travada esperando o diálogo: a linha some.
    expect(linha).to_have_count(0, timeout=10000)
    print(f"Diálogos exibidos na exclusão: {portfolio_page.mensagens_dialogo or 'nenhum'}")


def test_patrimonio_total_recalcula_apos_exclusao(
    logged_page: Page, navbar: NavbarComponent, portfolio_page: PortfolioPage
):
    """Após excluir um item, o card PATRIMÔNIO ATUAL deve ser igual à soma da coluna Valor Atual."""
    navbar.navegar_para_carteira()
    dias_inv, dias_plan = _prazo_unico()

    portfolio_page.cadastrar_aporte("Fundo DI", "10", "100.00", dias_inv, dias_plan)
    linha = portfolio_page.obter_linha_por_ativo_e_prazo("Fundo DI", dias_inv, dias_plan)
    expect(linha).to_be_visible(timeout=10000)
    assert portfolio_page.obter_valor_atual_da_linha(linha) > 0

    portfolio_page.excluir_linha(linha)
    expect(linha).to_have_count(0, timeout=10000)

    patrimonio_no_card, soma_da_tabela = portfolio_page.aguardar_patrimonio_igual_a_soma()
    print(f"Card: R$ {patrimonio_no_card:.2f} | Soma da tabela: R$ {soma_da_tabela:.2f}")

    assert abs(patrimonio_no_card - soma_da_tabela) < 0.02, (
        f"Card PATRIMÔNIO ATUAL mostra R$ {patrimonio_no_card:.2f}, "
        f"mas a soma da coluna Valor Atual é R$ {soma_da_tabela:.2f}"
>>>>>>> origin/main
    )