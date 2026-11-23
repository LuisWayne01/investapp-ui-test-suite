from playwright.sync_api import Page, Locator

from pages.base_page import BasePage


def converter_moeda_para_float(texto: str) -> float:
    """Converte um texto como 'R$ 1.234,56' para 1234.56."""
    limpo = (
        texto.replace("R$", "")
        .replace("\xa0", "")
        .replace(" ", "")
        .replace(".", "")
        .replace(",", ".")
    )
    return float(limpo) if limpo else 0.0


class PortfolioPage(BasePage):
    """Representa a aba da Carteira de Investimentos (Portfolio.jsx) — US02.

    Integrante 3: cadastro de aportes e validação da inserção na tabela.
    Integrante 4: exclusão de ativos, alertas de confirmação e Patrimônio Total.
    """

    def __init__(self, page: Page):
        super().__init__(page)
        self.secao_carteira = page.locator("[data-testid='section-portfolio']")

        # Formulário de Cadastro
        self.select_ativo = page.locator("[data-testid='select-asset-name']")
        self.input_quantidade = page.locator("[data-testid='input-asset-amount']")
        self.input_preco_compra = page.locator("[data-testid='input-asset-price']")
        self.input_dias_investidos = page.locator("[data-testid='input-asset-days-invested']")
        self.input_dias_planejados = page.locator("[data-testid='input-asset-planned-days']")
        self.botao_adicionar = page.locator("[data-testid='btn-add-asset']")

        # Indicadores e Tabela
        self.card_patrimonio_total = page.locator("[data-testid='summary-current-val']")
        self.card_projecao_futura = page.locator("[data-testid='summary-future-val']")
        self.linhas_tabela_carteira = page.locator("[data-testid='table-portfolio'] tbody tr")
        self.linhas_de_ativos = page.locator("[data-testid^='portfolio-row-']")
        self.alerta_erro = page.locator("[data-testid='portfolio-error']")

        # [Integrante 4] Alertas nativos (alert/confirm) são aceitos e registrados.
        self.mensagens_dialogo = []
        page.on("dialog", self._aceitar_dialogo)

    # ================= Integrante 3 — Cadastro de aportes =================
    def aguardar_carregamento(self):
        """Espera a aba Carteira aparecer e a lista de investimentos chegar da API."""
        self.secao_carteira.wait_for(state="visible")
        self.linhas_tabela_carteira.first.wait_for(state="visible")
        self.page.wait_for_load_state("networkidle")

    def selecionar_ativo(self, ativo: str):
        self.select_ativo.wait_for(state="visible")
        try:
            self.select_ativo.select_option(value=ativo, timeout=5000)
        except Exception:
            self.select_ativo.select_option(label=ativo)

    def preencher_formulario(self, ativo: str, quantidade: str, preco: str, dias_inv: str, dias_plan: str):
        """Preenche os cinco campos do formulário sem submeter."""
        self.selecionar_ativo(ativo)
        self.input_quantidade.fill(quantidade)
        self.input_preco_compra.fill(preco)
        self.input_dias_investidos.fill(dias_inv)
        self.input_dias_planejados.fill(dias_plan)

    def submeter_formulario(self):
        self.botao_adicionar.click()

    def cadastrar_aporte(self, ativo: str, quantidade: str, preco: str, dias_inv: str, dias_plan: str):
        """Preenche todos os campos do formulário e submete o novo aporte."""
        self.preencher_formulario(ativo, quantidade, preco, dias_inv, dias_plan)
        self.submeter_formulario()

    def obter_linha_por_ativo(self, nome_ativo: str) -> Locator:
        """Retorna a última linha da tabela que contém o ativo informado."""
        return self.linhas_de_ativos.filter(has_text=nome_ativo).last

    def obter_linha_por_ativo_e_prazo(self, nome_ativo: str, dias_inv: str, dias_plan: str) -> Locator:
        """Localiza a linha do ativo que corresponde aos dias cadastrados."""
        texto_prazo = f"{dias_inv} / {dias_plan} dias"
        return self.linhas_de_ativos.filter(has_text=nome_ativo).filter(has_text=texto_prazo).last

    def obter_ultimo_ativo_cadastrado(self, nome_ativo: str) -> Locator:
        """Retorna a última linha inserida na tabela para o ativo informado."""
        return self.obter_linha_por_ativo(nome_ativo)

    def total_de_ativos_listados(self) -> int:
        """Retorna o número atual de registros na tabela, ignorando a mensagem de vazio."""
        self.aguardar_carregamento()
        return self.linhas_de_ativos.count()

    def obter_botao_excluir(self, linha: Locator) -> Locator:
        return linha.locator("[data-testid^='btn-delete-asset-']")

    def excluir_linha(self, linha: Locator):
        """Clica em Excluir na linha informada (usado também na limpeza dos testes)."""
        self.obter_botao_excluir(linha).click()

    # ================= Integrante 4 — Exclusão e métricas =================
    def _aceitar_dialogo(self, dialog):
        """Aceita alert/confirm da tela e guarda a mensagem exibida."""
        self.mensagens_dialogo.append(dialog.message)
        try:
            dialog.accept()
        except Exception:
            pass  # outro handler já tratou o diálogo

    def excluir_todas_as_linhas(self, linhas: Locator):
        """Exclui uma a uma as linhas encontradas (limpeza de dados de teste)."""
        self.page.wait_for_load_state("networkidle")
        while linhas.count() > 0:
            total_antes = self.linhas_de_ativos.count()
            self.excluir_linha(linhas.last)
            self.page.wait_for_function(
                "([sel, n]) => document.querySelectorAll(sel).length < n",
                arg=["[data-testid^='portfolio-row-']", total_antes],
            )

    def obter_linhas_negativas(self, nome_ativo: str, dias_inv: str, dias_plan: str) -> Locator:
        """Linhas do ativo/prazo com Valor Atual negativo (aporte que deveria ter sido barrado)."""
        texto_prazo = f"{dias_inv} / {dias_plan} dias"
        return (self.linhas_de_ativos.filter(has_text=nome_ativo)
                .filter(has_text=texto_prazo).filter(has_text="-R$"))

    def excluir_primeiro_ativo(self):
        """Clica no botão de exclusão da primeira linha da tabela."""
        self.excluir_linha(self.linhas_de_ativos.first)

    def obter_valor_atual_da_linha(self, linha: Locator) -> float:
        """Lê a coluna 'Valor Atual' (4ª coluna) da linha."""
        return converter_moeda_para_float(linha.locator("td").nth(3).inner_text())

    def somar_coluna_valor_atual(self) -> float:
        """Soma a coluna 'Valor Atual' de todas as linhas da tabela."""
        self.page.wait_for_load_state("networkidle")
        textos = self.linhas_de_ativos.locator("td:nth-child(4)").all_inner_texts()
        return round(sum(converter_moeda_para_float(t) for t in textos), 2)

    def obter_patrimonio_total(self) -> float:
        """Lê o card PATRIMÔNIO ATUAL e devolve o valor numérico."""
        return converter_moeda_para_float(self.card_patrimonio_total.inner_text())

    def obter_texto_patrimonio_total(self) -> str:
        return self.card_patrimonio_total.inner_text()
