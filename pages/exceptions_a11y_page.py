from playwright.sync_api import Page, Locator

from pages.base_page import BasePage


# Script JS que calcula a razão de contraste (WCAG 2.x) entre a cor do texto
# e a primeira cor de fundo não transparente do elemento ou de seus ancestrais.
_JS_CONTRASTE = """
(el) => {
    const rgb = (s) => (s.match(/[\\d.]+/g) || []).map(Number);
    const lum = ([r, g, b]) => {
        const c = [r, g, b].map(v => {
            v = v / 255;
            return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
        });
        return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2];
    };
    const fundo = (node) => {
        while (node) {
            const st = getComputedStyle(node);
            const cor = rgb(st.backgroundColor);
            if (cor.length >= 3 && (cor.length === 3 || cor[3] > 0)) return cor;
            if (st.backgroundImage && st.backgroundImage.includes('gradient')) {
                const m = st.backgroundImage.match(/rgba?\\([^)]*\\)/);
                if (m) return rgb(m[0]);
            }
            node = node.parentElement;
        }
        return [255, 255, 255];
    };
    const l1 = lum(rgb(getComputedStyle(el).color));
    const l2 = lum(fundo(el));
    return (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
}
"""


class ExceptionsA11yPage(BasePage):
    """Integrante 8 — caminhos negativos e acessibilidade básica.

    Concentra os seletores e as verificações via JavaScript para que o arquivo
    de teste não precise usar page.locator(...).
    """

    def __init__(self, page: Page):
        super().__init__(page)
        self.tela_boas_vindas = page.locator("[data-testid='welcome-hero']")
        self.botao_login_boas_vindas = page.locator(
            "[data-testid='hero-login-btn']"
        )
        self.titulo_app = page.locator("[data-testid='app-title']")
        self.formulario_carteira = page.locator(
            "[data-testid='section-portfolio'] form"
        )
        self.imagens = page.locator("img")
        self.botoes = page.locator("button")

    # ---------- Validação nativa de formulário (HTML5) ----------

    def campo_e_valido(self, campo: Locator) -> bool:
        """True se o campo passa na validação do navegador."""
        return campo.evaluate("el => el.checkValidity()")

    def mensagem_de_validacao(self, campo: Locator) -> str:
        """Mensagem que o navegador mostra no balão de erro do campo."""
        return campo.evaluate("el => el.validationMessage")

    def limpar_campo(self, campo: Locator):
        campo.fill("")

    def digitar_tecla_a_tecla(self, campo: Locator, texto: str):
        """Digita como um usuário (o input type=number descarta letras)."""
        campo.click()
        campo.press_sequentially(texto)

    # ---------- Acessibilidade ----------

    def total_imagens_sem_alt(self) -> int:
        return self.page.locator("img:not([alt]), img[alt='']").count()

    def botoes_sem_nome_acessivel(self) -> list:
        """Lista os botões visíveis sem texto, aria-label ou title."""
        return self.botoes.evaluate_all(
            """bs => bs
                .filter(b => b.offsetParent !== null)
                .filter(b => !(b.innerText.trim() || b.getAttribute('aria-label') || b.title))
                .map(b => b.outerHTML)"""
        )

    def razao_de_contraste(self, elemento: Locator) -> float:
        elemento.wait_for(state="visible")
        return round(elemento.evaluate(_JS_CONTRASTE), 2)

    def idioma_da_pagina(self) -> str:
        return self.page.locator("html").get_attribute("lang") or ""
