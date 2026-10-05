from pathlib import Path
from types import SimpleNamespace

from app.catalog import synchronize_catalog
from app.database import SessionLocal


DIVERGENT_MODEL_PHOTOS = (
    "01-camisa-oficial/04-modelos-frente.png",
    "01-camisa-oficial/05-modelos-costas.png",
    "02-camiseta-oversized/05-modelos-costas.png",
    "04-moletom-heavy/04-modelos-frente.png",
    "04-moletom-heavy/05-modelos-costas.png",
    "05-corta-vento-night/04-modelos-frente.png",
    "05-corta-vento-night/05-modelos-costas.png",
    "06-short-esportivo/05-modelos-costas.png",
    "09-pochete-utility/04-em-uso.png",
)


def test_catalog_uses_mockups_as_source_of_truth():
    catalog_root = Path("catalogo-godzilla-ugb")

    assert all(not (catalog_root / relative_path).exists() for relative_path in DIVERGENT_MODEL_PHOTOS)
    assert "AAA Godzilla" not in (catalog_root / "README-imagens.md").read_text(encoding="utf-8")
    assert "AAU Godzilla UGB" in (catalog_root / "README-imagens.md").read_text(encoding="utf-8")


def test_storefront_exposes_complete_catalog_with_ordered_gallery(client):
    products = client.get("/api/v1/products").json()

    assert len(products) == 13
    assert {product["category"]["name"] for product in products} == {
        "Acessórios",
        "Camisetas",
        "Esportivo",
        "Moletons e casacos",
        "Testes",
    }
    official_shirt = next(product for product in products if product["slug"] == "camisa-oficial-godzilla-ugb")
    assert official_shirt["price_cents"] == 8990
    assert [variant["size"] for variant in official_shirt["variants"]] == ["P", "M", "G", "GG"]
    assert official_shirt["image_url"] == official_shirt["images"][0]["url"]
    assert [image["position"] for image in official_shirt["images"]] == [1, 2]
    assert all("guia-de-" not in image["url"] for image in official_shirt["images"])

    payment_test = next(product for product in products if product["slug"] == "testar-pagamento-real")
    assert payment_test["name"] == "Testar pagamento real"
    assert payment_test["price_cents"] == 50
    assert payment_test["image_url"] == "/assets/logo"
    assert [variant["size"] for variant in payment_test["variants"]] == ["Único"]


def test_catalog_assets_are_served_without_size_guides(client):
    products = client.get("/api/v1/products").json()
    images = [image for product in products for image in product["images"]]
    guide_images = [image for image in images if "guia-de-" in image["url"]]

    assert guide_images == []
    for image in images:
        response = client.get(image["url"])
        assert response.status_code == 200, image["url"]
        assert response.headers["content-type"] in {"image/png", "image/webp"}


def test_production_catalog_hides_the_payment_validation_product(client, monkeypatch):
    monkeypatch.setattr("app.catalog.get_settings", lambda: SimpleNamespace(mp_environment="production"))
    db = SessionLocal()
    try:
        synchronize_catalog(db)
    finally:
        db.close()

    slugs = {product["slug"] for product in client.get("/api/v1/products").json()}
    assert "testar-pagamento-real" not in slugs
