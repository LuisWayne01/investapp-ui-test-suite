from playwright.sync_api import Page, Locator
from pages.base_page import BasePage


class YieldSimulatorPage(BasePage):
    """Aba Simulador de Rentabilidade (YieldSimulator.jsx)."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.secao_simulador = page.locator("[data-testid='section-yield-simulator']")
        self.input_meses = page.locator("[data-testid='input-sim-months']")
        self.botao_calcular = page.locator("[data-testid='btn-calc-monthly']")

        self.tabela_mensal = page.locator("[data-testid='table-monthly-projection']")
        self.linhas_mensal = self.tabela_mensal.locator("tbody tr")
        self.cabecalho_mensal = self.tabela_mensal.locator("thead th")

        self.tabela_consolidado = page.locator("[data-testid='table-type-summary']")
        self.linhas_consolidado = self.tabela_consolidado.locator("tbody tr")

    def definir_meses(self, meses: str):
        self.input_meses.wait_for(state="visible")
        self.input_meses.fill(meses)

    def calcular(self):
        self.botao_calcular.click()

    def simular_para_meses(self, meses: str):
        self.definir_meses(meses)
        self.calcular()

    def linha_consolidado_por_tipo(self, tipo: str) -> Locator:
        return self.linhas_consolidado.filter(has_text=tipo).first