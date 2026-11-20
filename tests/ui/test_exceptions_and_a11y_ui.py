import random

import pytest
from playwright.sync_api import Page, expect, TimeoutError as PlaywrightTimeoutError

from pages.exceptions_a11y_page import ExceptionsA11yPage
from pages.login_modal_page import LoginModalPage
from pages.navbar_component import NavbarComponent
from pages.portfolio_page import PortfolioPage

CONTRASTE_MINIMO_WCAG_AA = 4.5


@pytest.fixture
def a11y_page(page: Page) -> ExceptionsA11yPage:
    return ExceptionsA11yPage(page)


# ======================= Caminhos negativos =======================

def test_login_com_campos_vazios_nao_submete(
    page: Page,
    base_url: str,
    navbar: NavbarComponent,
    login_modal: LoginModalPage,
    a11y_page: ExceptionsA11yPage
):
    """Formulário de login vazio não deve ser submetido."""
    page.goto(base_url)
    navbar.clicar_entrar()
    expect(login_modal.container_modal).to_be_visible()

    a11y_page.limpar_campo(login_modal.campo_usuario)
    a11y_page.limpar_campo(login_modal.campo_senha)
    login_modal.submeter()

    assert not a11y_page.campo_e_valido(login_modal.campo_usuario)
    assert a11y_page.mensagem_de_validacao(login_modal.campo_usuario) != ""
    expect(login_modal.container_modal).to_be_visible()
    expect(navbar.botao_sair).not_to_be_visible()


def test_aporte_com_formulario_vazio_nao_insere(
    logged_page: Page,
    navbar: NavbarComponent,
    portfolio_page: PortfolioPage,
    a11y_page: ExceptionsA11yPage
):
    """Submeter o aporte vazio não deve criar uma linha."""
    navbar.navegar_para_carteira()
    total_antes = portfolio_page.total_de_ativos_listados()

    a11y_page.limpar_campo(portfolio_page.input_quantidade)
    a11y_page.limpar_campo(portfolio_page.input_preco_compra)
    portfolio_page.botao_adicionar.click()

    assert not a11y_page.campo_e_valido(portfolio_page.input_quantidade)
    assert not a11y_page.campo_e_valido(portfolio_page.input_preco_compra)
    assert portfolio_page.total_de_ativos_listados() == total_antes


def test_aporte_negativo_exibe_erro(
    logged_page: Page,
    navbar: NavbarComponent,
    portfolio_page: PortfolioPage
):
    """Quantidade negativa deve ser rejeitada pela aplicação."""
    navbar.navegar_para_carteira()

    dias_inv = str(random.randint(100, 8000))
    dias_plan = str(int(dias_inv) + 10000)

    try:
        portfolio_page.cadastrar_aporte(
            "Poupança", "-200", "1.00", dias_inv, dias_plan
        )

        expect(portfolio_page.alerta_erro).to_be_visible(timeout=10000)

    finally:
        # Remove somente a linha criada por este teste, caso tenha sido aceita.
        linha = portfolio_page.obter_linha_por_ativo_e_prazo(
            "Poupança", dias_inv, dias_plan
        )

        try:
            linha.wait_for(state="visible", timeout=3000)
            botao_excluir = linha.locator(
                "[data-testid^='btn-delete-asset-']"
            )

            def aceitar_confirmacao(dialog):
                dialog.accept()

            portfolio_page.page.on("dialog", aceitar_confirmacao)
            try:
                botao_excluir.click()
            finally:
                portfolio_page.page.remove_listener(
                    "dialog", aceitar_confirmacao
                )

        except PlaywrightTimeoutError:
            pass


def test_campo_numerico_bloqueia_letras(
    logged_page: Page,
    navbar: NavbarComponent,
    portfolio_page: PortfolioPage,
    a11y_page: ExceptionsA11yPage
):
    """O campo numérico não deve aceitar letras."""
    navbar.navegar_para_carteira()

    a11y_page.limpar_campo(portfolio_page.input_quantidade)
    a11y_page.digitar_tecla_a_tecla(
        portfolio_page.input_quantidade, "abc"
    )

    expect(portfolio_page.input_quantidade).to_have_value("")


def test_funcionalidades_bloqueadas_sem_login(
    page: Page,
    base_url: str,
    navbar: NavbarComponent,
    portfolio_page: PortfolioPage,
    a11y_page: ExceptionsA11yPage
):
    """As funcionalidades da carteira ficam indisponíveis sem login."""
    page.goto(base_url)

    expect(a11y_page.tela_boas_vindas).to_be_visible()
    expect(navbar.link_carteira).to_have_count(0)
    expect(navbar.link_gerenciar_taxas).to_have_count(0)
    expect(portfolio_page.botao_adicionar).to_have_count(0)


# ========================= Acessibilidade =========================

def test_pagina_declara_idioma(
    page: Page,
    base_url: str,
    a11y_page: ExceptionsA11yPage
):
    """A página deve declarar o idioma para leitores de tela."""
    page.goto(base_url)

    assert a11y_page.idioma_da_pagina().lower().startswith("pt")


def test_imagens_possuem_texto_alternativo(
    logged_page: Page,
    navbar: NavbarComponent,
    a11y_page: ExceptionsA11yPage
):
    """As imagens das abas devem possuir texto alternativo."""
    abas = (
        navbar.navegar_para_carteira,
        navbar.navegar_para_simulador,
        navbar.navegar_para_otimizador_fiscal,
        navbar.navegar_para_gerenciar_taxas,
    )

    for abrir_aba in abas:
        abrir_aba()
        assert a11y_page.total_imagens_sem_alt() == 0


def test_botoes_possuem_nome_acessivel(
    logged_page: Page,
    navbar: NavbarComponent,
    a11y_page: ExceptionsA11yPage
):
    """Os botões visíveis devem possuir nome acessível."""
    navbar.navegar_para_carteira()

    assert a11y_page.botoes_sem_nome_acessivel() == []


def test_contraste_minimo_da_tela_inicial(
    page: Page,
    base_url: str,
    navbar: NavbarComponent,
    a11y_page: ExceptionsA11yPage
):
    """Os elementos da tela inicial devem atender ao contraste WCAG AA."""
    page.goto(base_url)

    elementos = {
        "Título do app": a11y_page.titulo_app,
        "Botão Entrar no Sistema": navbar.botao_entrar,
        "Botão Fazer Login para Começar": a11y_page.botao_login_boas_vindas,
    }

    for nome, elemento in elementos.items():
        razao = a11y_page.razao_de_contraste(elemento)
        print(f"Contraste {nome}: {razao}:1")
        assert razao >= CONTRASTE_MINIMO_WCAG_AA, (
            f"{nome} com contraste {razao}:1"
        )
