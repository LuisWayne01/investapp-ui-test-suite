from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from pages.base_page import BasePage

# A API roda em AWS Lambda e pode demorar para "acordar" (cold start).
TEMPO_LOGIN_MS = 30000


class NavbarComponent(BasePage):
    """Encapsula as ações e seletores da barra de navegação global (Navbar.jsx)."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.botao_entrar = page.locator("[data-testid='btn-open-login']")
        self.botao_sair = page.locator("[data-testid='btn-logout']")
        self.link_carteira = page.locator("[data-testid='nav-portfolio']")
        self.link_simulador_rendimento = page.locator("[data-testid='nav-yield-sim']")
        self.link_otimizador_fiscal = page.locator("[data-testid='nav-tax-sim']")
        self.link_gerenciar_taxas = page.locator("[data-testid='nav-asset-rates']")

    def clicar_entrar(self):
        self.botao_entrar.click()

    def clicar_sair(self):
        self.botao_sair.click()

    def aguardar_sessao_ativa(self, timeout: int = TEMPO_LOGIN_MS) -> bool:
        """Espera o botão Sair aparecer depois do login.

        Devolve True/False em vez de falhar com expect(): assim, se o login
        não responder, o log do pytest não imprime a tela com a senha digitada.
        """
        try:
            self.botao_sair.wait_for(state="visible", timeout=timeout)
            return True
        except PlaywrightTimeoutError:
            return False

    def navegar_para_carteira(self):
        self.link_carteira.click()

    def navegar_para_simulador(self):
        self.link_simulador_rendimento.click()

    def navegar_para_otimizador_fiscal(self):
        self.link_otimizador_fiscal.click()

    def navegar_para_gerenciar_taxas(self):
        self.link_gerenciar_taxas.click()
