# InvestApp — Suíte de Testes de UI (Pytest + Playwright + POM)

Laboratório 4 — Testes Automatizados de Interface Web.

- **Aplicação:** http://investapp-frontend.s3-website-us-east-1.amazonaws.com/
- **Swagger da API:** https://5bm1nctd1f.execute-api.us-east-1.amazonaws.com/docs

## Estrutura

```
pages/                      -> Page Objects (seletores + ações)
  base_page.py              -> [Líder] classe base
  navbar_component.py       -> [Líder] barra de navegação
  login_modal_page.py       -> [Líder] modal de login (US01)
  portfolio_page.py         -> [Integrantes 3/4] carteira (US02) — versão inicial do roteiro
  yield_simulator_page.py   -> [Integrante 5] (a criar)
  tax_optimizer_page.py     -> [Integrante 6] (a criar)
  asset_manager_page.py     -> [Integrante 2] (a criar)
tests/ui/
  conftest.py               -> [Líder] fixtures globais (logged_page, navbar, login_modal...)
  test_auth_ui.py           -> [Líder] testes do LoginModal (US01)
  test_asset_manager_ui.py  -> [Integrante 2]
  test_portfolio_ui.py      -> [Integrantes 3 e 4]
  test_yield_simulation_ui.py -> [Integrante 5]
  test_tax_optimizer_ui.py  -> [Integrante 6]
  test_portfolio_ddt_ui.py  -> [Integrante 7]
  test_exceptions_and_a11y_ui.py -> [Integrante 8]
tests/data/dados_investimentos_ui.csv -> [Integrante 7]
```

## Regra de ouro (critério de avaliação 10.2)

Os arquivos `test_*.py` **não podem** ter `page.locator(...)`. Todo seletor fica dentro
de uma classe em `pages/`; o teste só chama métodos dos Page Objects e faz `expect(...)`.

## Setup (cada integrante)

### Windows (PowerShell)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
playwright install chromium
copy .env.example .env   # depois edite TEST_USER e TEST_PASSWORD
```

### Codespaces / Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
playwright install chromium
playwright install-deps
cp .env.example .env     # depois edite TEST_USER e TEST_PASSWORD
```

O `.env` **não vai para o GitHub** (está no `.gitignore`). Cada um cria o seu a partir do `.env.example`.

## Executar

```bash
python -m pytest tests/ui -v -s                      # headless
python -m pytest tests/ui --headed --slowmo 300      # navegador visível
python -m pytest tests/ui/test_auth_ui.py --headed   # só um arquivo
python -m pytest tests/ui -v -s --video=on --screenshot=on
python -m pytest tests/ui --tracing=on --html=playwright-report.html --self-contained-html
```

No VS Code: aba **Testing** (tubo de ensaio) ou **F5** com a configuração
"Debug: Playwright UI Tests (Visual Headed)".

## Fixtures disponíveis (conftest.py)

| Fixture | O que entrega |
|---|---|
| `base_url` | URL da aplicação (do `.env`) |
| `navbar` | `NavbarComponent` |
| `login_modal` | `LoginModalPage` |
| `portfolio_page` | `PortfolioPage` |
| `logged_page` | `Page` já autenticada com `TEST_USER`/`TEST_PASSWORD` |

Quem criar um Page Object novo (ex.: `YieldSimulatorPage`) adiciona a fixture
correspondente no `conftest.py` seguindo o mesmo padrão.

Ao final de cada teste é salvo um print em `reports/screenshots/` e anexado ao relatório HTML.

## Fluxo de Git do grupo

1. `git pull` antes de começar.
2. Cada integrante trabalha nos **seus** arquivos e faz commits com o próprio usuário do GitHub
   (o professor avalia o histórico de commits distribuído entre os 8).
3. `git pull --rebase` e depois `git push`.
