
from playwright.sync_api import Page
from pages.base_page import BasePage


class TaxOptimizerPage(BasePage):
    """Tela do Otimizador Fiscal de Resgate (US04)."""

    def __init__(self, page: Page):
        super().__init__(page)

        self.secao_otimizador = page.locator(
            "[data-testid='section-tax-simulator']"
        )
        self.input_valor_resgate = page.locator(
            "[data-testid='input-withdraw-amount']"
        )
        self.botao_simular = page.locator(
            "[data-testid='btn-calc-withdrawal']"
        )
        self.tabela_resultados = page.locator(
            "[data-testid='table-tax-optimization']"
        )
        self.linhas_resultados = self.tabela_resultados.locator(
            "tbody tr"
        )

    def definir_valor_resgate(self, valor: str):
        self.input_valor_resgate.wait_for(state="visible")
        self.input_valor_resgate.fill(valor)

    def simular(self):
        self.botao_simular.click()

    def simular_resgate(self, valor: str):
        self.definir_valor_resgate(valor)
        self.simular()

    def obter_melhor_opcao(self):
        return self.linhas_resultados.first
