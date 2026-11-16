
import re

from playwright.sync_api import Page, Locator

from pages.base_page import BasePage


class AssetManagerPage(BasePage):
    """Representa a aba Gerenciar Taxas (AssetManager.jsx — US05).

    A tela tem uma tabela com uma linha por ativo. Colunas:
    Ativo | Categoria | Taxa anual salva | Nova taxa (input) | Ação (botão).
    """

    def __init__(self, page: Page):
        super().__init__(page)

        self.titulo = page.get_by_role(
            "heading", name=re.compile("Configuração das Taxas")
        )

        self.linhas_tabela = page.locator("table tbody tr")

        self.mensagens_dialogo = []
        page.on("dialog", self._aceitar_dialogo)

    # ---------- Localizadores relativos à linha do ativo ----------

    def _aceitar_dialogo(self, dialog):
        """Aceita alert/confirm da tela e guarda a mensagem exibida."""
        self.mensagens_dialogo.append(dialog.message)
        dialog.accept()

    def obter_linha(self, nome_ativo: str) -> Locator:
        """Encontra a linha correspondente ao ativo informado."""

        celula_nome = self.page.get_by_role(
            "cell", name=nome_ativo, exact=True
        )

        linhas = self.linhas_tabela.filter(has=celula_nome)

        return linhas

    def obter_celula_taxa_salva(self, nome_ativo: str) -> Locator:
        """Retorna a célula da taxa anual salva."""
        return self.obter_linha(nome_ativo).locator("td").nth(2)

    def obter_campo_nova_taxa(self, nome_ativo: str) -> Locator:
        """Retorna o campo para digitar a nova taxa."""
        return self.obter_linha(nome_ativo).locator("input")

    def obter_botao_salvar(self, nome_ativo: str) -> Locator:
        """Retorna o botão Salvar Alteração."""
        return self.obter_linha(nome_ativo).get_by_role(
            "button", name="Salvar Alteração"
        )

    # ---------- Ações ----------

    def total_de_ativos_listados(self) -> int:
        self.linhas_tabela.first.wait_for(state="visible")
        return self.linhas_tabela.count()

    def obter_valor_campo(self, nome_ativo: str) -> str:
        """Obtém o valor atual do campo Nova taxa."""
        return self.obter_campo_nova_taxa(nome_ativo).input_value()

    def alterar_taxa(self, nome_ativo: str, nova_taxa: str):
        """Preenche o campo com a nova taxa."""
        self.obter_campo_nova_taxa(nome_ativo).fill(nova_taxa)

    def salvar_taxa(self, nome_ativo: str):
        """Clica no botão para salvar a nova taxa."""
        self.obter_botao_salvar(nome_ativo).click()

    def alterar_e_salvar_taxa(
        self, nome_ativo: str, nova_taxa: str
    ):
        """Preenche a nova taxa e clica em Salvar."""
        self.alterar_taxa(nome_ativo, nova_taxa)
        self.salvar_taxa(nome_ativo)
