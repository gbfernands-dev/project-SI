from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, File, HTTPException, Request, Response, UploadFile, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.config import get_settings
from app.database import Base, engine, get_db
from app.models import (
    CartItem,
    Category,
    Order,
    OrderItem,
    OrderStatus,
    PaymentEvent,
    PaymentStatus,
    Product,
    ProductVariant,
    Role,
    Session as UserSession,
    User,
)
from app.schemas import (
    CartItemCreate,
    CartOut,
    CategoryCreate,
    CategoryOut,
    CheckoutOut,
    Message,
    OrderOut,
    OrderStatusUpdate,
    ProductCreate,
    ProductOut,
    ProductUpdate,
    SessionOut,
    UserLogin,
    UserOut,
    UserRegister,
    VariantCreate,
    VariantOut,
)
from app.security import (
    SESSION_COOKIE,
    create_session,
    get_current_session,
    get_current_user,
    hash_password,
    require_admin,
    require_user,
    verify_csrf,
    verify_password,
)
from app.services import (
    compact_json,
    create_payment_preference,
    get_mercado_pago_payment,
    save_product_image,
    verify_mercado_pago_signature,
)


settings = get_settings()


def seed_demo_catalog(db: Session) -> None:
    if db.query(Category).count():
        return
    vestuario = Category(name="Vestuário", slug="vestuario")
    acessorios = Category(name="Acessórios", slug="acessorios")
    db.add_all([vestuario, acessorios])
    db.flush()
    products = [
        Product(
            category=vestuario,
            name="Camiseta Godzilla",
            slug="camiseta-godzilla",
            description="Camiseta oficial demonstrativa da Atlética Godzilla.",
            price_cents=6500,
            variants=[ProductVariant(size=size, stock=10) for size in ("P", "M", "G", "GG")],
        ),
        Product(
            category=vestuario,
            name="Moletom Godzilla",
            slug="moletom-godzilla",
            description="Moletom demonstrativo para os dias de jogo.",
            price_cents=12900,
            variants=[ProductVariant(size=size, stock=6) for size in ("M", "G", "GG")],
        ),
        Product(
            category=acessorios,
            name="Caneca Godzilla",
            slug="caneca-godzilla",
            description="Caneca demonstrativa com a energia da Atlética Godzilla.",
            price_cents=3500,
            variants=[ProductVariant(size="Único", stock=20)],
        ),
    ]
    db.add_all(products)
    db.commit()


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = next(get_db())
    try:
        seed_demo_catalog(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="Loja Atlética Godzilla API",
    version="1.0.0",
    description="Contrato da API do monólito de e-commerce da Atlética Godzilla.",
    lifespan=lifespan,
)
app.mount("/static", StaticFiles(directory=settings.static_dir), name="static")


def product_query(db: Session):
    return db.query(Product).options(joinedload(Product.category), joinedload(Product.variants))


def get_product_or_404(db: Session, product_id: int) -> Product:
    product = product_query(db).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado.")
    return product


def cart_response(db: Session, user_id: int) -> CartOut:
    records = (
        db.query(CartItem)
        .options(joinedload(CartItem.variant).joinedload(ProductVariant.product).joinedload(Product.category), joinedload(CartItem.variant).joinedload(ProductVariant.product).joinedload(Product.variants))
        .filter(CartItem.user_id == user_id)
        .all()
    )
    items = []
    total = 0
    for record in records:
        product = record.variant.product
        item = {"id": record.id, "quantity": record.quantity, "variant": record.variant, "product": product}
        items.append(item)
        total += product.price_cents * record.quantity
    return CartOut(items=items, total_cents=total)


def order_out(order: Order) -> OrderOut:
    return OrderOut.model_validate(order)


@app.get("/api/v1/health", response_model=Message, tags=["system"])
def health() -> Message:
    return Message(message="ok")


@app.get("/assets/logo", include_in_schema=False)
def logo() -> FileResponse:
    return FileResponse(settings.logo_path, media_type="image/png")


@app.get("/promptcss.json", include_in_schema=False)
def design_tokens() -> FileResponse:
    return FileResponse(Path(settings.static_dir.parent / "promptcss.json"), media_type="application/json")


@app.post("/api/v1/auth/register", response_model=SessionOut, status_code=status.HTTP_201_CREATED, tags=["auth"])
def register(payload: UserRegister, response: Response, db: Session = Depends(get_db)) -> SessionOut:
    user = User(name=payload.name.strip(), email=str(payload.email).lower(), password_hash=hash_password(payload.password))
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Este e-mail já está cadastrado.")
    token, session = create_session(db, user)
    response.set_cookie(SESSION_COOKIE, token, httponly=True, samesite="lax", secure=settings.is_production, max_age=7 * 86400)
    return SessionOut(user=UserOut.model_validate(user), csrf_token=session.csrf_token)


@app.post("/api/v1/auth/login", response_model=SessionOut, tags=["auth"])
def login(payload: UserLogin, response: Response, db: Session = Depends(get_db)) -> SessionOut:
    user = db.query(User).filter(User.email == str(payload.email).lower()).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="E-mail ou senha inválidos.")
    token, session = create_session(db, user)
    response.set_cookie(SESSION_COOKIE, token, httponly=True, samesite="lax", secure=settings.is_production, max_age=7 * 86400)
    return SessionOut(user=UserOut.model_validate(user), csrf_token=session.csrf_token)


@app.get("/api/v1/auth/me", response_model=SessionOut, tags=["auth"])
def me(session: UserSession = Depends(get_current_session), db: Session = Depends(get_db)) -> SessionOut:
    user = db.get(User, session.user_id)
    return SessionOut(user=UserOut.model_validate(user), csrf_token=session.csrf_token)


@app.post("/api/v1/auth/logout", response_model=Message, tags=["auth"])
def logout(response: Response, session: UserSession = Depends(verify_csrf), db: Session = Depends(get_db)) -> Message:
    db.delete(session)
    db.commit()
    response.delete_cookie(SESSION_COOKIE)
    return Message(message="Sessão encerrada.")


@app.get("/api/v1/categories", response_model=list[CategoryOut], tags=["catalog"])
def list_categories(db: Session = Depends(get_db)) -> list[Category]:
    return db.query(Category).order_by(Category.name).all()


@app.get("/api/v1/products", response_model=list[ProductOut], tags=["catalog"])
def list_products(
    q: str | None = None,
    category: str | None = None,
    size: str | None = None,
    min_price: int | None = None,
    max_price: int | None = None,
    db: Session = Depends(get_db),
) -> list[Product]:
    query = product_query(db).filter(Product.is_active.is_(True))
    if q:
        pattern = f"%{q.strip()}%"
        query = query.filter(or_(Product.name.ilike(pattern), Product.description.ilike(pattern)))
    if category:
        query = query.join(Product.category).filter(Category.slug == category)
    if size:
        query = query.join(Product.variants).filter(ProductVariant.size == size, ProductVariant.stock > 0)
    if min_price is not None:
        query = query.filter(Product.price_cents >= min_price)
    if max_price is not None:
        query = query.filter(Product.price_cents <= max_price)
    return query.order_by(Product.name).distinct().all()


@app.get("/api/v1/products/{slug}", response_model=ProductOut, tags=["catalog"])
def product_detail(slug: str, db: Session = Depends(get_db)) -> Product:
    product = product_query(db).filter(Product.slug == slug, Product.is_active.is_(True)).first()
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado.")
    return product


@app.get("/api/v1/cart", response_model=CartOut, tags=["cart"])
def get_cart(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> CartOut:
    return cart_response(db, user.id)


@app.post("/api/v1/cart/items", response_model=CartOut, status_code=status.HTTP_201_CREATED, tags=["cart"])
def add_cart_item(payload: CartItemCreate, user: User = Depends(require_user), db: Session = Depends(get_db)) -> CartOut:
    variant = db.get(ProductVariant, payload.variant_id)
    if not variant or not variant.product.is_active:
        raise HTTPException(status_code=404, detail="Variação não encontrada.")
    existing = db.query(CartItem).filter(CartItem.user_id == user.id, CartItem.variant_id == variant.id).first()
    requested = payload.quantity + (existing.quantity if existing else 0)
    if requested > variant.stock:
        raise HTTPException(status_code=409, detail="Quantidade indisponível em estoque.")
    if existing:
        existing.quantity = requested
    else:
        db.add(CartItem(user_id=user.id, variant_id=variant.id, quantity=payload.quantity))
    db.commit()
    return cart_response(db, user.id)


@app.delete("/api/v1/cart/items/{item_id}", response_model=CartOut, tags=["cart"])
def remove_cart_item(item_id: int, user: User = Depends(require_user), db: Session = Depends(get_db)) -> CartOut:
    item = db.query(CartItem).filter(CartItem.id == item_id, CartItem.user_id == user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado no carrinho.")
    db.delete(item)
    db.commit()
    return cart_response(db, user.id)


@app.post("/api/v1/orders/checkout", response_model=CheckoutOut, tags=["orders"])
def checkout(user: User = Depends(require_user), db: Session = Depends(get_db)) -> CheckoutOut:
    cart = (
        db.query(CartItem)
        .options(joinedload(CartItem.variant).joinedload(ProductVariant.product))
        .filter(CartItem.user_id == user.id)
        .all()
    )
    if not cart:
        raise HTTPException(status_code=400, detail="Seu carrinho está vazio.")
    order = Order(user_id=user.id, total_cents=0)
    payment_items = []
    for cart_item in cart:
        variant, product = cart_item.variant, cart_item.variant.product
        if cart_item.quantity > variant.stock or not product.is_active:
            raise HTTPException(status_code=409, detail=f"Estoque insuficiente para {product.name}.")
        order.total_cents += product.price_cents * cart_item.quantity
        order.items.append(OrderItem(variant_id=variant.id, product_name=product.name, size=variant.size, unit_price_cents=product.price_cents, quantity=cart_item.quantity))
        payment_items.append({"title": f"{product.name} ({variant.size})", "quantity": cart_item.quantity, "unit_price": product.price_cents / 100, "currency_id": "BRL"})
    db.add(order)
    db.flush()
    checkout_url = create_payment_preference(order.id, payment_items)
    db.commit()
    db.refresh(order)
    return CheckoutOut(order=order_out(order), checkout_url=checkout_url)


@app.get("/api/v1/orders", response_model=list[OrderOut], tags=["orders"])
def my_orders(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[OrderOut]:
    orders = db.query(Order).options(joinedload(Order.items)).filter(Order.user_id == user.id).order_by(Order.created_at.desc()).all()
    return [order_out(order) for order in orders]


@app.get("/api/v1/orders/{order_id}", response_model=OrderOut, tags=["orders"])
def get_order(order_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> OrderOut:
    order = db.query(Order).options(joinedload(Order.items)).filter(Order.id == order_id).first()
    if not order or (order.user_id != user.id and user.role != Role.ADMIN):
        raise HTTPException(status_code=404, detail="Pedido não encontrado.")
    return order_out(order)


def approve_order_payment(db: Session, order: Order, payment_id: str) -> None:
    if order.payment_status == PaymentStatus.APPROVED:
        return
    cart_items = []
    for item in order.items:
        variant = db.get(ProductVariant, item.variant_id)
        if not variant or variant.stock < item.quantity:
            raise HTTPException(status_code=409, detail="Estoque indisponível ao aprovar pagamento.")
        cart_items.append((variant, item.quantity))
    for variant, quantity in cart_items:
        variant.stock -= quantity
    order.payment_status = PaymentStatus.APPROVED
    order.status = OrderStatus.PAID
    order.payment_id = payment_id
    db.query(CartItem).filter(CartItem.user_id == order.user_id).delete()


@app.post("/api/v1/payments/mock/orders/{order_id}/approve", response_model=OrderOut, tags=["payments"])
def mock_approve_payment(order_id: int, user: User = Depends(require_user), db: Session = Depends(get_db)) -> OrderOut:
    if settings.is_production or settings.mp_access_token:
        raise HTTPException(status_code=404, detail="Pagamento de teste indisponível.")
    order = db.query(Order).options(joinedload(Order.items)).filter(Order.id == order_id, Order.user_id == user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado.")
    approve_order_payment(db, order, f"mock-{order.id}")
    db.commit()
    db.refresh(order)
    return order_out(order)


@app.post("/api/v1/payments/webhook", status_code=status.HTTP_204_NO_CONTENT, tags=["payments"])
async def mercado_pago_webhook(request: Request, db: Session = Depends(get_db)) -> Response:
    payload = await request.json()
    signature = request.headers.get("x-signature")
    request_id = request.headers.get("x-request-id")
    if not verify_mercado_pago_signature(payload, signature, request_id):
        raise HTTPException(status_code=401, detail="Assinatura de webhook inválida.")
    payment_id = str(payload.get("data", {}).get("id", ""))
    if not payment_id or db.query(PaymentEvent).filter(PaymentEvent.payment_id == payment_id).first():
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    payment = get_mercado_pago_payment(payment_id)
    db.add(PaymentEvent(payment_id=payment_id, payload=compact_json(payment)))
    order_id = payment.get("external_reference")
    if payment.get("status") == "approved" and order_id:
        order = db.query(Order).options(joinedload(Order.items)).filter(Order.id == int(order_id)).first()
        if order:
            approve_order_payment(db, order, payment_id)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/api/v1/admin/products", response_model=list[ProductOut], tags=["admin"])
def admin_products(_: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[Product]:
    # Authorization is checked explicitly to keep GET requests CSRF-free.
    if _.role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="Acesso administrativo necessário.")
    return product_query(db).order_by(Product.name).all()


@app.post("/api/v1/admin/categories", response_model=CategoryOut, status_code=201, tags=["admin"])
def create_category(payload: CategoryCreate, _: User = Depends(require_admin), db: Session = Depends(get_db)) -> Category:
    category = Category(name=payload.name.strip(), slug=payload.slug)
    db.add(category)
    try:
        db.commit()
        db.refresh(category)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Categoria já existe.")
    return category


@app.post("/api/v1/admin/products", response_model=ProductOut, status_code=201, tags=["admin"])
def create_product(payload: ProductCreate, _: User = Depends(require_admin), db: Session = Depends(get_db)) -> Product:
    if not db.get(Category, payload.category_id):
        raise HTTPException(status_code=404, detail="Categoria não encontrada.")
    product = Product(**payload.model_dump())
    db.add(product)
    try:
        db.commit()
        return get_product_or_404(db, product.id)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Slug já utilizado.")


@app.patch("/api/v1/admin/products/{product_id}", response_model=ProductOut, tags=["admin"])
def update_product(product_id: int, payload: ProductUpdate, _: User = Depends(require_admin), db: Session = Depends(get_db)) -> Product:
    product = get_product_or_404(db, product_id)
    values = payload.model_dump(exclude_unset=True)
    if "category_id" in values and not db.get(Category, values["category_id"]):
        raise HTTPException(status_code=404, detail="Categoria não encontrada.")
    for field, value in values.items():
        setattr(product, field, value)
    try:
        db.commit()
        return get_product_or_404(db, product.id)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Slug já utilizado.")


@app.post("/api/v1/admin/products/{product_id}/variants", response_model=VariantOut, status_code=201, tags=["admin"])
def create_variant(product_id: int, payload: VariantCreate, _: User = Depends(require_admin), db: Session = Depends(get_db)) -> ProductVariant:
    get_product_or_404(db, product_id)
    variant = ProductVariant(product_id=product_id, **payload.model_dump())
    db.add(variant)
    try:
        db.commit()
        db.refresh(variant)
        return variant
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Este tamanho já existe no produto.")


@app.patch("/api/v1/admin/variants/{variant_id}", response_model=VariantOut, tags=["admin"])
def update_variant(variant_id: int, payload: VariantCreate, _: User = Depends(require_admin), db: Session = Depends(get_db)) -> ProductVariant:
    variant = db.get(ProductVariant, variant_id)
    if not variant:
        raise HTTPException(status_code=404, detail="Variação não encontrada.")
    variant.size, variant.stock = payload.size, payload.stock
    try:
        db.commit()
        db.refresh(variant)
        return variant
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Este tamanho já existe no produto.")


@app.post("/api/v1/admin/products/{product_id}/image", response_model=ProductOut, tags=["admin"])
async def upload_image(product_id: int, file: UploadFile = File(...), _: User = Depends(require_admin), db: Session = Depends(get_db)) -> Product:
    product = get_product_or_404(db, product_id)
    product.image_url = await save_product_image(file)
    db.commit()
    return get_product_or_404(db, product.id)


@app.get("/api/v1/admin/orders", response_model=list[OrderOut], tags=["admin"])
def admin_orders(_: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[OrderOut]:
    if _.role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="Acesso administrativo necessário.")
    orders = db.query(Order).options(joinedload(Order.items)).order_by(Order.created_at.desc()).all()
    return [order_out(order) for order in orders]


@app.patch("/api/v1/admin/orders/{order_id}/status", response_model=OrderOut, tags=["admin"])
def update_order_status(order_id: int, payload: OrderStatusUpdate, _: User = Depends(require_admin), db: Session = Depends(get_db)) -> OrderOut:
    order = db.query(Order).options(joinedload(Order.items)).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado.")
    expected = OrderStatus.PAID if payload.status == "available" else OrderStatus.AVAILABLE
    if order.status != expected:
        raise HTTPException(status_code=409, detail="Transição de status inválida.")
    order.status = OrderStatus(payload.status)
    db.commit()
    db.refresh(order)
    return order_out(order)


@app.get("/", include_in_schema=False)
@app.get("/{full_path:path}", include_in_schema=False)
def frontend(full_path: str = "") -> FileResponse:
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404)
    return FileResponse(settings.static_dir / "index.html")
