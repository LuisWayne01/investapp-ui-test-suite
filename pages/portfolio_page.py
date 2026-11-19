import re
from playwright.sync_api import Page, Locator

from pages.base_page import BasePage


class PortfolioPage(BasePage):
    """Representa a aba da Carteira de Investimentos (Portfolio.jsx) — US02.

    Versão inicial copiada do roteiro, criada pelo líder porque o conftest.py a importa.
    Os Integrantes 3 e 4 evoluem esta classe.
    """

    def __init__(self, page: Page):
        super().__init__(page)
        # Formulário de Cadastro
        self.select_ativo = page.locator("[data-testid='select-asset-name']")
        self.input_quantidade = page.locator("[data-testid='input-asset-amount']")
        self.input_preco_compra = page.locator("[data-testid='input-asset-price']")
        self.input_dias_investidos = page.locator("[data-testid='input-asset-days-invested']")
        self.input_dias_planejados = page.locator("[data-testid='input-asset-planned-days']")
        self.botao_adicionar = page.locator("[data-testid='btn-add-asset']")

        # Indicadores e Tabela
        self.card_patrimonio_total = page.locator("[data-testid='summary-current-val']")
        self.linhas_tabela_carteira = page.locator("[data-testid='table-portfolio'] tbody tr")
        self.alerta_erro = page.locator("[data-testid='portfolio-error']")

    def cadastrar_aporte(self, ativo: str, quantidade: str, preco: str, dias_inv: str, dias_plan: str):
        """Preenche todos os campos do formulário e submete o novo aporte."""
        self.select_ativo.wait_for(state="visible")
        try:
            self.select_ativo.select_option(value=ativo)
        except Exception:
            self.select_ativo.select_option(label=f"{ativo}")
        self.input_quantidade.fill(quantidade)
        self.input_preco_compra.fill(preco)
        self.input_dias_investidos.fill(dias_inv)
        self.input_dias_planejados.fill(dias_plan)
        with self.page.expect_response(lambda r: r.request.method == "POST", timeout=15000):
            self.botao_adicionar.click()

    def obter_linha_por_ativo_e_prazo(self, nome_ativo: str, dias_inv: str, dias_plan: str) -> Locator:
        """Localiza a linha do ativo que corresponde aos dias cadastrados."""
        texto_prazo = f"{dias_inv} / {dias_plan} dias"
        return self.linhas_tabela_carteira.filter(has_text=nome_ativo).filter(has_text=texto_prazo).first

    def obter_ultimo_ativo_cadastrado(self, nome_ativo: str) -> Locator:
        """Retorna a última linha inserida na tabela para o ativo informado."""
        return self.linhas_tabela_carteira.filter(has_text=nome_ativo).last

    def excluir_primeiro_ativo(self, confirmar: bool = True):
        """Exclui a primeira linha, tratando o alerta de confirmação."""
        botao_excluir = self.linhas_tabela_carteira.first.locator("[data-testid^='btn-delete-asset-']")
        # O handler precisa ser registrado ANTES do clique
        self.page.once("dialog", lambda d: d.accept() if confirmar else d.dismiss())
        botao_excluir.click()

    def total_de_ativos_listados(self) -> int:
        """Retorna o número atual de registros na tabela, ignorando a mensagem de vazio."""
        self.page.wait_for_selector("[data-testid='table-portfolio'] tbody", timeout=5000)
        if self.linhas_tabela_carteira.filter(has_text="Nenhum ativo cadastrado").count() > 0:
            return 0
        return self.linhas_tabela_carteira.count()

        # --- Integrante 4: exclusão e métricas consolidadas ---
    def excluir_ativo_por_prazo(self, nome_ativo: str, dias_inv: str, dias_plan: str, confirmar: bool = True):
        """Exclui especificamente o aporte do ativo com aquele prazo."""
        linha = self.obter_linha_por_ativo_e_prazo(nome_ativo, dias_inv, dias_plan)
        botao_excluir = linha.locator("[data-testid^='btn-delete-asset-']")
        self.page.once("dialog", lambda d: d.accept() if confirmar else d.dismiss())
        botao_excluir.click()

    @staticmethod
    def _moeda_para_float(texto: str) -> float:
        """Converte 'R$ 1.234,56' em 1234.56."""
        limpo = re.sub(r"[^\d,.-]", "", texto)
        return float(limpo.replace(".", "").replace(",", "."))

    def obter_patrimonio_total(self) -> float:
        """Lê o card de Patrimônio Total como número."""
        return self._moeda_para_float(self.card_patrimonio_total.inner_text())

    def obter_linhas_por_ativo_e_prazo(self, nome_ativo: str, dias_inv: str, dias_plan: str) -> Locator:
        """Todas as linhas do ativo com aquele prazo (sem o .first), útil para contar."""
        texto_prazo = f"{dias_inv} / {dias_plan} dias"
        return self.linhas_tabela_carteira.filter(has_text=nome_ativo).filter(has_text=texto_prazo)
