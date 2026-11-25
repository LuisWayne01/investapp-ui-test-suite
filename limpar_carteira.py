"""Apaga TODOS os aportes da carteira do usuário de teste (TEST_USER do .env).

Use antes da execução final da suíte: a carteira é compartilhada entre os
integrantes e acumula aportes de execuções anteriores, o que deixa a API lenta
e faz testes falharem por tempo.

Uso (na pasta do projeto):
    .venv\\Scripts\\python.exe limpar_carteira.py
"""
import os
import sys

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

from pages.login_modal_page import LoginModalPage
from pages.navbar_component import NavbarComponent
from pages.portfolio_page import PortfolioPage

load_dotenv()
UI_BASE_URL = os.getenv("UI_BASE_URL", "http://investapp-frontend.s3-website-us-east-1.amazonaws.com")
TEST_USER = os.getenv("TEST_USER", "")
TEST_PASSWORD = os.getenv("TEST_PASSWORD", "")


def main() -> int:
    if not TEST_USER or not TEST_PASSWORD:
        print("Preencha TEST_USER e TEST_PASSWORD no arquivo .env.")
        return 1

    with sync_playwright() as p:
        navegador = p.chromium.launch(headless=True)
        page = navegador.new_page()
        navbar = NavbarComponent(page)
        login = LoginModalPage(page)
        carteira = PortfolioPage(page)

        page.goto(UI_BASE_URL)
        navbar.clicar_entrar()
        login.realizar_login(TEST_USER, TEST_PASSWORD)
        if not navbar.aguardar_sessao_ativa():
            print("Login não concluído em 30 s. Tente de novo em instantes.")
            navegador.close()
            return 1

        navbar.navegar_para_carteira()
        carteira.aguardar_carregamento()
        total = carteira.linhas_de_ativos.count()
        print(f"Aportes encontrados na carteira de {TEST_USER}: {total}")

        if total:
            carteira.excluir_todas_as_linhas(carteira.linhas_de_ativos)

        print(f"Aportes restantes: {carteira.linhas_de_ativos.count()}")
        print(f"Patrimônio atual: {carteira.obter_texto_patrimonio_total()}")
        navegador.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
