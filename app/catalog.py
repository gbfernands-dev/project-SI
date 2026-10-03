"""Catálogo inicial aprovado, sincronizado de forma idempotente com o banco."""

from dataclasses import dataclass
from pathlib import Path

from sqlalchemy.orm import Session

from app.models import Category, Product, ProductImage, ProductVariant


CATALOG_ROOT = Path(__file__).resolve().parents[1] / "catalogo-godzilla-ugb"
LEGACY_DEMO_SLUGS = {"camiseta-godzilla", "moletom-godzilla", "caneca-godzilla"}


@dataclass(frozen=True)
class CatalogProduct:
    directory: str | None
    category_name: str
    category_slug: str
    name: str
    slug: str
    description: str
    price_cents: int
    sizes: tuple[str, ...]


CATALOG = (
    CatalogProduct("01-camisa-oficial", "Esportivo", "esportivo", "Camisa Oficial Godzilla UGB", "camisa-oficial-godzilla-ugb", "Camisa esportiva unissex da Godzilla UGB em roxo profundo e preto, com grafismo tonal inspirado em escamas, escudo no peito e acabamento leve. Criada para jogos, torcida e eventos universitários.", 8990, ("P", "M", "G", "GG")),
    CatalogProduct("02-camiseta-oversized", "Camisetas", "camisetas", "Camiseta Oversized Godzilla Core", "camiseta-oversized-godzilla-core", "Camiseta unissex preta de modelagem oversized, com assinatura minimalista na frente e arte ampla do mascote nas costas. Uma peça streetwear para usar dentro e fora da faculdade.", 7990, ("P", "M", "G", "GG")),
    CatalogProduct("03-camiseta-essential", "Camisetas", "camisetas", "Camiseta Essential Godzilla", "camiseta-essential-godzilla", "Camiseta unissex de modelagem regular, base escura, logo discreta no peito e assinatura Godzilla UGB nas costas. Uma opção versátil para o dia a dia.", 5990, ("P", "M", "G", "GG")),
    CatalogProduct("04-moletom-heavy", "Moletons e casacos", "moletons-e-casacos", "Moletom Oversized Godzilla Heavy", "moletom-oversized-godzilla-heavy", "Moletom unissex preto de estrutura encorpada, modelagem oversized, capuz amplo, bolso canguru e arte Godzilla em roxo e cinza. Desenvolvido para unir conforto, presença e estilo urbano.", 14990, ("P", "M", "G", "GG")),
    CatalogProduct("05-corta-vento-night", "Moletons e casacos", "moletons-e-casacos", "Corta-vento Godzilla Night", "corta-vento-godzilla-night", "Jaqueta corta-vento unissex preta com recortes em roxo escuro, fechamento por zíper e identidade visual discreta. Leve e funcional para dias frios, treinos e eventos.", 13990, ("P", "M", "G", "GG")),
    CatalogProduct("06-short-esportivo", "Esportivo", "esportivo", "Short Esportivo Godzilla", "short-esportivo-godzilla", "Short esportivo unissex preto com detalhes laterais roxos, tecido leve e cintura ajustável. Indicado para treinos, jogos e uso casual.", 6990, ("P", "M", "G", "GG")),
    CatalogProduct("07-caneca-com-tirante", "Acessórios", "acessorios", "Caneca com Tirante Godzilla", "caneca-com-tirante-godzilla", "Caneca personalizada da Godzilla UGB com acabamento resistente e tirante exclusivo incluso. Ideal para festas, jogos e eventos da atlética. Capacidade de 500 ml.", 3500, ("Único",)),
    CatalogProduct("08-bone-minimal", "Acessórios", "acessorios", "Boné Godzilla Minimal", "bone-godzilla-minimal", "Boné preto ajustável com símbolo Godzilla bordado em roxo na frente e detalhe UGB. Design discreto para combinar com as peças esportivas e streetwear da coleção.", 5490, ("Único",)),
    CatalogProduct("09-pochete-utility", "Acessórios", "acessorios", "Pochete Godzilla Utility", "pochete-godzilla-utility", "Pochete preta de nylon com detalhes roxos, compartimentos com zíper e alça regulável. Prática para festas, jogos e rotina universitária.", 6490, ("Único",)),
    CatalogProduct("10-copo-termico", "Acessórios", "acessorios", "Copo Térmico Godzilla", "copo-termico-godzilla", "Copo térmico preto fosco com aplicação roxa da marca Godzilla UGB e tampa reutilizável. Capacidade de 473 ml.", 4990, ("Único",)),
    CatalogProduct("11-tirante-monster", "Acessórios", "acessorios", "Tirante Dupla Face Godzilla Monster", "tirante-dupla-face-godzilla-monster", "Tirante dupla face vendido separadamente. Uma face roxa destaca a força do mascote; a outra usa base preta e repetição da assinatura Godzilla UGB.", 1990, ("Único",)),
    CatalogProduct("12-tirante-scale", "Acessórios", "acessorios", "Tirante Dupla Face Godzilla Scale", "tirante-dupla-face-godzilla-scale", "Tirante dupla face vendido separadamente. A face externa combina preto e padrão tonal de escamas; a face interna apresenta roxo escuro e assinatura minimalista Godzilla.", 1990, ("Único",)),
    CatalogProduct(None, "Testes", "testes", "Testar pagamento real", "testar-pagamento-real", "Produto de R$ 0,50 para validar o Checkout Pro no ambiente de teste do Mercado Pago. Nenhuma cobrança real é feita enquanto o checkout estiver configurado como teste.", 50, ("Único",)),
)


def image_files(directory: str) -> list[Path]:
    product_directory = CATALOG_ROOT / directory
    return sorted(path for path in product_directory.iterdir() if path.suffix.lower() in {".png", ".webp"})


def image_url(path: Path) -> str:
    return f"/catalog-assets/{path.relative_to(CATALOG_ROOT).as_posix()}"


def synchronize_catalog(db: Session) -> None:
    for legacy in db.query(Product).filter(Product.slug.in_(LEGACY_DEMO_SLUGS)).all():
        legacy.is_active = False

    categories: dict[str, Category] = {}
    for item in CATALOG:
        category = categories.get(item.category_slug) or db.query(Category).filter_by(slug=item.category_slug).first()
        if category is None:
            category = Category(name=item.category_name, slug=item.category_slug)
            db.add(category)
            db.flush()
        else:
            category.name = item.category_name
        categories[item.category_slug] = category

        product = db.query(Product).filter_by(slug=item.slug).first()
        if product is None:
            product = Product(slug=item.slug, variants=[])
            db.add(product)
        product.category = category
        product.name = item.name
        product.description = item.description
        product.price_cents = item.price_cents
        product.is_active = True

        existing_sizes = {variant.size for variant in product.variants}
        initial_stock = 10 if len(item.sizes) > 1 else 20
        for size in item.sizes:
            if size not in existing_sizes:
                product.variants.append(ProductVariant(size=size, stock=initial_stock))

        files = image_files(item.directory) if item.directory else []
        desired_images = (
            [
                ProductImage(
                    url=image_url(path),
                    alt_text=f"{item.name} — {path.stem.replace('-', ' ')}",
                    position=position,
                )
                for position, path in enumerate(files, start=1)
            ]
            if files
            else [ProductImage(url="/assets/logo", alt_text=item.name, position=1)]
        )
        product.image_url = desired_images[0].url
        current = [(image.url, image.alt_text, image.position) for image in product.images]
        desired = [(image.url, image.alt_text, image.position) for image in desired_images]
        if current != desired:
            product.images.clear()
            db.flush()
            product.images.extend(desired_images)

    db.commit()
