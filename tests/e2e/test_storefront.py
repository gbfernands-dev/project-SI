from playwright.sync_api import Page


def test_storefront_renders_design_and_catalog(page: Page, live_server):
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.goto(live_server)
    assert page.title() == "Atlética Godzilla | UGB"
    assert page.get_by_role("heading", name="Vista a força do Godzilla.").is_visible()
    page.wait_for_timeout(500)
    products = page.locator("#products")
    assert page.locator(".product-card").count() >= 1, {"errors": errors, "html": products.inner_html()}
    card_with_gallery = page.locator(".product-card:has(.card-gallery-thumbnail)").first
    assert card_with_gallery.locator(".card-gallery-thumbnail").count() >= 2
    card_main_image = card_with_gallery.locator(".product-image img")
    first_source = card_main_image.get_attribute("src")
    card_with_gallery.locator(".card-gallery-thumbnail").nth(1).click()
    assert card_main_image.get_attribute("src") != first_source
    assert card_with_gallery.locator(".product-image").evaluate(
        "element => getComputedStyle(element).backgroundColor"
    ) == "rgb(255, 255, 255)"
    assert not errors


def test_customer_can_register_from_the_browser(page: Page, live_server):
    page.goto(f"{live_server}/conta")
    page.get_by_role("button", name="Criar conta").click()
    page.get_by_label("Nome").fill("Cliente Godzilla")
    page.get_by_label("E-mail").fill("cliente@ugb.edu.br")
    page.get_by_label("Senha").fill("segredo123")
    page.get_by_role("button", name="Criar conta", exact=True).last.click()
    page.get_by_role("heading", name="Olá, Cliente").wait_for()


def test_product_gallery_uses_the_approved_white_background(page: Page, live_server):
    page.goto(live_server)
    page.locator(".product-card a").first.click()
    page.wait_for_url("**/produto/**")

    thumbnails = page.locator(".gallery-thumbnail")
    assert thumbnails.count() >= 2
    main_image = page.locator("#gallery-main")
    first_source = main_image.get_attribute("src")
    thumbnails.nth(1).click()
    assert main_image.get_attribute("src") != first_source
    assert page.locator(".product-detail-image").evaluate("element => getComputedStyle(element).backgroundColor") == "rgb(255, 255, 255)"


def test_home_is_mobile_friendly_and_hero_logo_has_no_square_border(page: Page, live_server):
    page.set_viewport_size({"width": 390, "height": 844})
    page.goto(live_server)
    page.locator("#products .product-card").first.wait_for()

    assert page.locator(".hero-art img").evaluate("element => getComputedStyle(element).borderRadius") == "50%"
    assert page.locator("body").evaluate("element => element.scrollWidth <= window.innerWidth")
    assert page.get_by_role("button", name="Abrir menu").is_visible()
    page.get_by_role("button", name="Abrir menu").click()
    assert page.get_by_role("navigation").is_visible()


def test_admin_panels_match_each_account_scope(page: Page, live_server):
    page.goto(f"{live_server}/conta")
    page.get_by_label("E-mail").fill("admin@admin.com")
    page.get_by_label("Senha").fill("site-password-123")
    page.get_by_role("button", name="Entrar", exact=True).last.click()
    page.get_by_role("link", name="Abrir painel").click()
    page.get_by_role("heading", name="Saúde e configurações").wait_for()
    assert page.get_by_role("heading", name="Contas criadas").is_visible()

    page.goto(f"{live_server}/conta")
    page.get_by_role("button", name="Sair").click()
    page.get_by_role("heading", name="Vista a força do Godzilla.").wait_for()
    page.goto(f"{live_server}/conta")
    page.get_by_label("E-mail").fill("atletica@atletica.com")
    page.get_by_label("Senha").fill("athletics-password-123")
    page.get_by_role("button", name="Entrar", exact=True).last.click()
    page.get_by_role("link", name="Abrir painel").click()
    page.get_by_role("heading", name="Produtos").wait_for()
    assert page.get_by_role("heading", name="Saúde e configurações").count() == 0
    assert page.get_by_role("heading", name="Contas criadas").count() == 0
    assert page.get_by_role("button", name="Editar").first.is_visible()
    assert page.get_by_role("button", name="Excluir").first.is_visible()
