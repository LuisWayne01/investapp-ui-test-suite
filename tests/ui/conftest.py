import os

import pytest
from playwright.sync_api import Page, expect
from pages.asset_manager_page import AssetManagerPage
from pages.navbar_component import NavbarComponent
from pages.login_modal_page import LoginModalPage
from pages.portfolio_page import PortfolioPage
from pages.yield_simulator_page import YieldSimulatorPage

UI_BASE_URL = os.getenv("UI_BASE_URL", "http://investapp-frontend.s3-website-us-east-1.amazonaws.com")
TEST_USER = os.getenv("TEST_USER", "userXX")
TEST_PASSWORD = os.getenv("TEST_PASSWORD", "password")


@pytest.fixture
def asset_manager_page(page: Page) -> AssetManagerPage:
    return AssetManagerPage(page)


@pytest.fixture(scope="session")
def base_url():
    return UI_BASE_URL


@pytest.fixture
def navbar(page: Page) -> NavbarComponent:
    return NavbarComponent(page)


@pytest.fixture
def login_modal(page: Page) -> LoginModalPage:
    return LoginModalPage(page)


@pytest.fixture
def portfolio_page(page: Page) -> PortfolioPage:
    return PortfolioPage(page)


@pytest.fixture
def logged_page(page: Page, base_url: str, navbar: NavbarComponent, login_modal: LoginModalPage) -> Page:
    """
    Fixture que entrega o navegador logado via POM.
    Abre o sistema, clica em Entrar na Navbar, executa o login e aguarda a sessão ativa.
    """
    page.goto(base_url)
    navbar.clicar_entrar()
    expect(login_modal.container_modal).to_be_visible()

    login_modal.realizar_login(TEST_USER, TEST_PASSWORD)
    expect(navbar.botao_sair).to_be_visible(timeout=10000)

    return page


@pytest.fixture
def yield_page(page: Page) -> YieldSimulatorPage:
    return YieldSimulatorPage(page)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Captura a tela ao final de cada teste e anexa ao relatório HTML (pytest-html)."""
    outcome = yield
    report = outcome.get_result()
    extras = getattr(report, "extras", [])

    if report.when == "call":
        page = item.funcargs.get("page")
        if page:
            screenshot_dir = os.path.join("reports", "screenshots")
            os.makedirs(screenshot_dir, exist_ok=True)
            screenshot_path = os.path.join(screenshot_dir, f"{item.name}.png")
            page.screenshot(path=screenshot_path, full_page=True)

            pytest_html_plugin = item.config.pluginmanager.getplugin("html")
            if pytest_html_plugin:
                extras.append(pytest_html_plugin.extras.image(os.path.abspath(screenshot_path)))
        report.extras = extras
