# InvestApp — Suíte de Testes de UI (Pytest + Playwright + POM)

Laboratório 4 — Testes Automatizados de Interface Web.

- **Aplicação:** http://investapp-frontend.s3-website-us-east-1.amazonaws.com/
- **Swagger da API:** https://5bm1nctd1f.execute-api.us-east-1.amazonaws.com/docs

## Divisão de tarefas

| Integrante | Page Object (`pages/`) | Testes (`tests/ui/`) | Cobertura |
|---|---|---|---|
| 1 — Luis Felipe (líder) | `base_page.py`, `navbar_component.py`, `login_modal_page.py` | `conftest.py`, `test_auth_ui.py` | Infraestrutura, fixtures, LoginModal (US01) |
| 2 — Julio Henrique | `asset_manager_page.py` | `test_asset_manager_ui.py` | Gerenciar Taxas (US05) |
| 3 — Raphael Vinícius | `portfolio_page.py` (cadastro) | `test_portfolio_ui.py` (cadastro) | Cadastro de aportes (US02) |
| 4 — Emanuelly Simoura | `portfolio_page.py` (exclusão e métricas) | `test_portfolio_ui.py` (exclusão) | Exclusão e Patrimônio Total (US02) |
| 5 — Nayara Monteiro | `yield_simulator_page.py` | `test_yield_simulation_ui.py` | Simulador de Rentabilidade (US03) |
| 6 — Bernardo Clinton | `tax_optimizer_page.py` | `test_tax_optimizer_ui.py` | Otimizador Fiscal (US04) |
| 7 — Caique Augusto | — (usa `portfolio_page.py`) | `test_portfolio_ddt_ui.py` + `tests/data/dados_investimentos_ui.csv` | Data-Driven Testing via CSV |
| 8 — João Eduardo | `exceptions_a11y_page.py` | `test_exceptions_and_a11y_ui.py` | Caminhos negativos e acessibilidade |
| 9 — Ana Júlia | — (usa os Page Objects existentes) | `test_navegacao_ui.py` *(em andamento)* | Navegação entre abas, logout e `DEFEITOS_ENCONTRADOS.md` |

## Regra de ouro (critério de avaliação 10.2)

Os arquivos `test_*.py` **não podem** ter `page.locator(...)`, seletores nem cliques diretos.
Todo seletor fica dentro de uma classe em `pages/`; o teste só chama métodos dos
Page Objects e faz `expect(...)`/`assert`.

## Setup (cada integrante)

### Windows (PowerShell)
```powershell
python -m venv .venv
.venv\Scripts\pip install --upgrade pip
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python -m playwright install chromium
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

O `.env` **não vai para o GitHub** (está no `.gitignore`). As credenciais do grupo são
passadas em mensagem privada — nunca em commits, prints ou no relatório.

## Executar

Antes da execução final, limpe a carteira do usuário de teste (ela é compartilhada e
acumula aportes, o que deixa a API lenta):

```bash
python limpar_carteira.py
```

```bash
python -m pytest tests/ui -v -s                      # execução completa (log do relatório)
python -m pytest tests/ui -v --tb=line               # resumo curto das falhas
python -m pytest tests/ui --headed --slowmo 300      # navegador visível
python -m pytest tests/ui/test_auth_ui.py --headed   # só um arquivo
python -m pytest tests/ui -v -s --video=on --screenshot=on
python -m pytest tests/ui --html=relatorio.html --self-contained-html
```

No VS Code: aba **Testing** (tubo de ensaio) → Refresh → ▶ Run All.

## Fixtures disponíveis (conftest.py)

| Fixture | O que entrega |
|---|---|
| `base_url` | URL da aplicação (do `.env`) |
| `logged_page` | `Page` já autenticada com `TEST_USER`/`TEST_PASSWORD` (espera até 30 s pela API) |
| `navbar` | `NavbarComponent` |
| `login_modal` | `LoginModalPage` |
| `portfolio_page` | `PortfolioPage` |
| `yield_page` | `YieldSimulatorPage` |
| `asset_manager_page` | `AssetManagerPage` |

Ao final de cada teste é salvo um print em `reports/screenshots/` e anexado ao relatório HTML.

## Defeitos encontrados na aplicação

Os testes abaixo **falham de propósito**: eles detectam erros reais do InvestApp
(roteiro, item 10.3). Detalhes em `DEFEITOS_ENCONTRADOS.md`.

| # | Defeito (confirmado manualmente no site) | Testes que detectam |
|---|---|---|
| 1 | **Taxa salva não aparece.** Em Gerenciar Taxas, salvar 7.25 na Poupança exibe "Sua taxa personalizada para Poupança foi salva com sucesso!", mas a coluna continua em 6.17% a.a. A API mantém 10 registros "Poupança" com taxas diferentes; o salvamento atualiza um deles e a tela sempre exibe o primeiro. | `test_alterar_taxa_atualiza_coluna_salva`, `test_taxa_alterada_persiste_apos_navegar` |
| 2 | **Aporte negativo aceito.** Na Carteira, quantidade -200 é enviada sem mensagem de erro (o campo não tem valor mínimo) e o aporte é gravado com valores negativos (ex.: `Poupança 77 / 365 dias -R$ 202,54`). | `test_cadastro_aporte_ddt_pom[...-200.00...False]`, `test_aporte_negativo_exibe_erro` |
| 3 | **API sem autenticação e dados compartilhados.** `GET /api/assets` responde sem token (a documentação exige login) e lista ativos de teste de outras turmas (`ATIVO_TESTE_UPSERT_QA`, `string`, ...). | Verificação manual |
| 4 | **Simulador com CDB errado.** Em Simulador Rentabilidade, todas as colunas "CDB" mostram o mesmo valor (-R$ 105,93) e +0,00%/mês, apesar de a taxa ser 10,50% a.a. (~0,83%/mês). O simulador identifica os aportes pelo nome e repete os dados do primeiro CDB, que é um aporte negativo. Também cria uma coluna por aporte (190 colunas) em vez de uma por ativo. | Verificação manual |
| 5 | **Card de patrimônio zerado.** Com a carteira cheia, "PATRIMÔNIO ATUAL" e "PROJEÇÃO FUTURA TOTAL" mostram R$ 0,00; o console registra erro HTTP 400 em uma chamada da API. | `test_patrimonio_total_recalcula_apos_exclusao` |

## Fluxo de Git do grupo

1. `git pull origin main` antes de começar.
2. Crie uma branch: `git checkout -b feature/integrante-X`.
3. Trabalhe nos **seus** arquivos e faça commits com o seu próprio usuário do GitHub
   (o professor avalia o histórico de commits de cada integrante).
4. `git pull origin main`, depois `git push -u origin feature/integrante-X`.
5. Abra um Pull Request para o `main`; o líder revisa e faz o merge.
