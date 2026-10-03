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
