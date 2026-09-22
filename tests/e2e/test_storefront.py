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
