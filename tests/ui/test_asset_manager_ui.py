
from playwright.sync_api import Page, expect

from pages.navbar_component import NavbarComponent
from pages.asset_manager_page import AssetManagerPage

ATIVOS_ESPERADOS = [
    "Poupança", "Fundo DI", "CDB", "LCI", "LCA",
    "Ações Vale", "Ações Petrobrás",
]
ATIVO_TESTE = "Poupança"


def _escolher_taxa_nova(taxa_original: str) -> str:
    """Escolhe um valor diferente do atual."""
    return "7.35" if taxa_original == "7.25" else "7.25"


def test_tabela_de_taxas_exibida(
    logged_page: Page,
    navbar: NavbarComponent,
    asset_manager_page: AssetManagerPage,
):
    """Valida que a aba Gerenciar Taxas lista os ativos com suas taxas."""
    navbar.navegar_para_gerenciar_taxas()

    expect(asset_manager_page.titulo).to_be_visible()
    expect(asset_manager_page.linhas_tabela.first).to_be_visible()

    assert asset_manager_page.total_de_ativos_listados() >= len(
        ATIVOS_ESPERADOS
    )

    for ativo in ATIVOS_ESPERADOS:
        expect(asset_manager_page.obter_linha(ativo)).to_be_visible()
        expect(
            asset_manager_page.obter_celula_taxa_salva(ativo)
        ).to_contain_text("a.a.")


def test_alterar_taxa_atualiza_coluna_salva(
    logged_page: Page,
    navbar: NavbarComponent,
    asset_manager_page: AssetManagerPage,
):
    """Altera a taxa de um ativo e confere a coluna 'Taxa anual salva'."""
    navbar.navegar_para_gerenciar_taxas()

    taxa_original = asset_manager_page.obter_valor_campo(ATIVO_TESTE)
    nova_taxa = _escolher_taxa_nova(taxa_original)

    try:
        asset_manager_page.alterar_e_salvar_taxa(ATIVO_TESTE, nova_taxa)

        expect(
            asset_manager_page.obter_celula_taxa_salva(ATIVO_TESTE)
        ).to_contain_text(f"{nova_taxa}% a.a.", timeout=8000)

    finally:
        # A tabela de taxas é compartilhada: restaura o valor original.
        asset_manager_page.alterar_e_salvar_taxa(
            ATIVO_TESTE, taxa_original
        )


def test_taxa_alterada_persiste_apos_navegar(
    logged_page: Page,
    navbar: NavbarComponent,
    asset_manager_page: AssetManagerPage,
):
    """Salva uma taxa, sai da aba, volta e confere que o valor persistiu."""
    navbar.navegar_para_gerenciar_taxas()

    taxa_original = asset_manager_page.obter_valor_campo(ATIVO_TESTE)
    nova_taxa = _escolher_taxa_nova(taxa_original)

    try:
        asset_manager_page.alterar_e_salvar_taxa(ATIVO_TESTE, nova_taxa)

        expect(
            asset_manager_page.obter_celula_taxa_salva(ATIVO_TESTE)
        ).to_contain_text(f"{nova_taxa}% a.a.", timeout=8000)

        # Remonta a tela: vai para a Carteira e volta para Gerenciar Taxas.
        navbar.navegar_para_carteira()
        navbar.navegar_para_gerenciar_taxas()

        expect(
            asset_manager_page.obter_celula_taxa_salva(ATIVO_TESTE)
        ).to_contain_text(f"{nova_taxa}% a.a.", timeout=8000)

    finally:
        asset_manager_page.alterar_e_salvar_taxa(
            ATIVO_TESTE, taxa_original
        )
