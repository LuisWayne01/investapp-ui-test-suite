import pytest
from playwright.sync_api import Page, expect
from pages.navbar_component import NavbarComponent
from pages.yield_simulator_page import YieldSimulatorPage


def test_simulador_exibe_campos_iniciais(
    logged_page: Page, navbar: NavbarComponent,
    yield_page: YieldSimulatorPage
):
    navbar.navegar_para_simulador()
    expect(yield_page.secao_simulador).to_be_visible()
    expect(yield_page.input_meses).to_be_visible()
    expect(yield_page.botao_calcular).to_be_enabled()


@pytest.mark.parametrize("meses", ["1", "12", "60"])
def test_calculo_renderiza_tabela_mensal(
    logged_page: Page, navbar: NavbarComponent,
    yield_page: YieldSimulatorPage, meses: str
):
    navbar.navegar_para_simulador()
    yield_page.simular_para_meses(meses)
    expect(yield_page.tabela_mensal).to_be_visible(timeout=10000)
    expect(yield_page.linhas_mensal.first).to_be_visible()


def test_tabela_consolidada_por_tipo_de_ativo(
    logged_page: Page, navbar: NavbarComponent,
    yield_page: YieldSimulatorPage
):
    navbar.navegar_para_simulador()
    yield_page.simular_para_meses("12")
    expect(yield_page.tabela_consolidado).to_be_visible(timeout=10000)
    expect(yield_page.linhas_consolidado.first).to_be_visible()
    expect(yield_page.linhas_consolidado).not_to_have_count(0)