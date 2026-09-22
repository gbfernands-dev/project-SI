const API = "/api/v1";
const content = document.querySelector("#content");
const state = { user: null, csrf: null, cart: { items: [], total_cents: 0 } };

function apiErrorMessage(detail) {
  if (Array.isArray(detail)) {
    return detail.map((issue) => `${issue.loc?.at(-1) || "campo"}: ${issue.msg}`).join(" · ");
  }
  return typeof detail === "string" ? detail : "Não foi possível concluir esta ação.";
}

async function applyDesignTokens() {
  try {
    const design = await fetch("/promptcss.json", { cache: "no-store" }).then((response) => response.json());
    const root = document.documentElement;
    const colors = design.tokens?.colors || {};
    const map = { ink: "ink", muted: "muted", background: "background", surface: "surface", surfaceAlt: "surface-2", line: "line", primary: "violet", accent: "pink", highlight: "aqua", success: "green", danger: "danger" };
    Object.entries(map).forEach(([token, property]) => { if (colors[token]) root.style.setProperty(`--${property}`, colors[token]); });
    if (design.tokens?.typography?.fontFamily) root.style.setProperty("--font-family", design.tokens.typography.fontFamily);
    if (design.tokens?.radii?.small) root.style.setProperty("--radius-small", design.tokens.radii.small);
    if (design.tokens?.radii?.medium) root.style.setProperty("--radius-medium", design.tokens.radii.medium);
    if (design.tokens?.radii?.pill) root.style.setProperty("--radius-pill", design.tokens.radii.pill);
    if (design.tokens?.shadows?.floating) root.style.setProperty("--shadow", design.tokens.shadows.floating);
  } catch (error) { console.warn("Os tokens visuais não puderam ser carregados; usando os valores de segurança.", error); }
}

const currency = (cents) => new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(cents / 100);
const escapeHtml = (value = "") => String(value).replace(/[&<>'"]/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" })[char]);

async function api(path, options = {}) {
  const headers = { ...(options.body instanceof FormData ? {} : { "Content-Type": "application/json" }), ...(options.headers || {}) };
  if (state.csrf && !["GET", "HEAD"].includes(options.method || "GET")) headers["X-CSRF-Token"] = state.csrf;
  const response = await fetch(`${API}${path}`, { credentials: "same-origin", ...options, headers });
  if (response.status === 204) return null;
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(apiErrorMessage(data.detail));
  return data;
}

function notify(message) {
  const toast = document.querySelector("#toast");
  toast.textContent = message; toast.classList.add("show");
  clearTimeout(notify.timer); notify.timer = setTimeout(() => toast.classList.remove("show"), 3500);
}

function navigate(path) { history.pushState({}, "", path); render(); window.scrollTo(0, 0); }

function image(product, className = "") {
  return `<img class="${className}" src="${escapeHtml(product.image_url || "/assets/logo")}" alt="${escapeHtml(product.name)}" />`;
}

function productCard(product) {
  return `<article class="product-card"><a href="/produto/${encodeURIComponent(product.slug)}" data-link><div class="product-image">${image(product, product.image_url ? "" : "fallback-logo")}</div></a><div class="product-info"><span class="category-label">${escapeHtml(product.category.name)}</span><h3>${escapeHtml(product.name)}</h3><div class="card-footer"><span class="price">${currency(product.price_cents)}</span><a class="text-link" href="/produto/${encodeURIComponent(product.slug)}" data-link>Ver produto →</a></div></div></article>`;
}

async function loadSession() {
  try { const session = await api("/auth/me"); state.user = session.user; state.csrf = session.csrf_token; }
  catch { state.user = null; state.csrf = null; }
  if (state.user) { try { state.cart = await api("/cart"); } catch { /* session can have no cart */ } }
  else state.cart = { items: [], total_cents: 0 };
  updateHeader();
}

function updateHeader() {
  document.querySelector("#cart-count").textContent = state.cart.items.reduce((count, item) => count + item.quantity, 0);
  document.querySelector("#account-link").innerHTML = state.user ? `◉ <span>${escapeHtml(state.user.name.split(" ")[0])}</span>` : "◉ <span>Conta</span>";
}

async function home() {
  const categories = await api("/categories");
  content.innerHTML = `<section class="hero"><div><span class="eyebrow">Loja oficial · UGB</span><h1>Vista a <span class="highlight">força</span> do Godzilla.</h1><p>Produtos da Atlética Godzilla para levar a energia da torcida, dentro e fora da faculdade.</p><a class="button" href="#catalogo">Ver coleção</a></div><div class="hero-art"><img src="/assets/logo" alt="Mascote Godzilla da atlética" /></div></section><section id="catalogo" class="section"><div class="section-heading"><div><span class="eyebrow">Coleção</span><h2>Encontre o seu item</h2></div><span class="muted">Retirada na faculdade</span></div><form id="filters" class="filter-bar"><input name="q" type="search" placeholder="Buscar produtos" aria-label="Buscar produtos" /><select name="category" aria-label="Categoria"><option value="">Todas as categorias</option>${categories.map(c => `<option value="${c.slug}">${escapeHtml(c.name)}</option>`).join("")}</select><select name="size" aria-label="Tamanho"><option value="">Todos os tamanhos</option><option>P</option><option>M</option><option>G</option><option>GG</option><option>Único</option></select><input name="min_price" type="number" min="0" placeholder="Preço mín." aria-label="Preço mínimo em centavos" /><input name="max_price" type="number" min="0" placeholder="Preço máx." aria-label="Preço máximo em centavos" /><button class="button" type="submit">Filtrar</button></form><div id="products" class="product-grid" aria-live="polite"></div></section>`;
  const products = content.querySelector("#products");
  async function showProducts(params = new URLSearchParams()) {
    products.innerHTML = "<p class='muted'>Carregando produtos...</p>";
    const data = await api(`/products${params.toString() ? `?${params}` : ""}`);
    products.innerHTML = data.length ? data.map(productCard).join("") : "<div class='empty'>Nenhum produto encontrado com esses filtros.</div>";
  }
  await showProducts();
  content.querySelector("#filters").addEventListener("submit", async (event) => { event.preventDefault(); const values = new FormData(event.currentTarget); const params = new URLSearchParams(); for (const [key, value] of values) if (value) params.set(key, value); try { await showProducts(params); } catch (error) { notify(error.message); } });
}

async function productPage(slug) {
  const product = await api(`/products/${encodeURIComponent(slug)}`);
  content.innerHTML = `<section class="section"><a class="text-link" href="/" data-link>← Voltar à loja</a><div class="layout-two" style="margin-top:1rem"><div class="product-detail-image">${image(product)}</div><div class="panel"><span class="category-label">${escapeHtml(product.category.name)}</span><h1 class="detail-title">${escapeHtml(product.name)}</h1><p class="price">${currency(product.price_cents)}</p><p class="detail-description">${escapeHtml(product.description)}</p><form id="add-to-cart" class="stack"><label>Tamanho<select name="variant_id">${product.variants.map(v => `<option value="${v.id}" ${v.stock ? "" : "disabled"}>${escapeHtml(v.size)} — ${v.stock ? `${v.stock} em estoque` : "esgotado"}</option>`).join("")}</select></label><label>Quantidade<input name="quantity" type="number" min="1" max="10" value="1" /></label><button class="button" type="submit">Adicionar ao carrinho</button></form></div></div></section>`;
  content.querySelector("#add-to-cart").addEventListener("submit", async (event) => { event.preventDefault(); if (!state.user) return navigate("/conta"); const form = new FormData(event.currentTarget); try { state.cart = await api("/cart/items", { method: "POST", body: JSON.stringify({ variant_id: Number(form.get("variant_id")), quantity: Number(form.get("quantity")) }) }); updateHeader(); notify("Produto adicionado ao carrinho."); } catch (error) { notify(error.message); } });
}

async function cartPage() {
  if (!state.user) { content.innerHTML = `<section class="section"><div class="empty">Entre na sua conta para usar o carrinho.<br /><br /><a class="button" href="/conta" data-link>Entrar</a></div></section>`; return; }
  state.cart = await api("/cart"); updateHeader();
  const items = state.cart.items;
  content.innerHTML = `<section class="section"><div class="section-heading"><div><span class="eyebrow">Seu pedido</span><h1 style="font-size:clamp(2.3rem,5vw,4rem);max-width:none">Carrinho</h1></div></div><div class="layout-two"><div class="panel">${items.length ? items.map(item => `<div class="cart-row"><img src="${escapeHtml(item.product.image_url || "/assets/logo")}" alt="" /><div><strong>${escapeHtml(item.product.name)}</strong><br /><small class="muted">${escapeHtml(item.variant.size)} · ${item.quantity} unidade(s)</small><br /><span class="price">${currency(item.product.price_cents * item.quantity)}</span></div><button class="button secondary" data-remove="${item.id}">Remover</button></div>`).join("") : "<div class='empty'>Seu carrinho está vazio.</div>"}</div><aside class="panel"><h2>Resumo</h2><div class="summary-row"><span>Total</span><strong class="total">${currency(state.cart.total_cents)}</strong></div><p class="notice">Após o pagamento aprovado, a Atlética preparará o pedido para retirada na faculdade.</p>${items.length ? "<button id='checkout' class='button'>Ir para pagamento</button>" : ""}</aside></div></section>`;
  content.querySelectorAll("[data-remove]").forEach(button => button.addEventListener("click", async () => { try { state.cart = await api(`/cart/items/${button.dataset.remove}`, { method: "DELETE" }); updateHeader(); await cartPage(); } catch (error) { notify(error.message); } }));
  content.querySelector("#checkout")?.addEventListener("click", async () => { try { const checkout = await api("/orders/checkout", { method: "POST" }); if (checkout.checkout_url.startsWith("/")) navigate(checkout.checkout_url); else window.location.assign(checkout.checkout_url); } catch (error) { notify(error.message); } });
}

function loginForm() {
  return `<div class="panel"><div class="tabs"><button class="active" data-auth-tab="login">Entrar</button><button data-auth-tab="register">Criar conta</button></div><form id="auth-form" class="stack"><div id="name-field" class="hidden"><label>Nome<input name="name" autocomplete="name" minlength="2" /></label></div><label>E-mail<input name="email" type="email" autocomplete="email" required /></label><label>Senha<input name="password" type="password" autocomplete="current-password" minlength="8" required /></label><button class="button" type="submit">Entrar</button><p class="muted">A conta permite acompanhar seu pedido e a retirada. Não coletamos endereço nesta versão.</p></form></div>`;
}

function renderOrders(orders) {
  return orders.length ? orders.map(order => `<article class="order-card"><div><strong>Pedido #${order.id}</strong><br /><small class="muted">${new Date(order.created_at).toLocaleDateString("pt-BR")} · ${order.items.map(i => `${i.product_name} (${i.size})`).join(", ")}</small></div><div style="text-align:right"><span class="status ${order.status}">${order.status === "awaiting_payment" ? "aguardando pagamento" : order.status === "paid" ? "pago" : order.status === "available" ? "disponível" : "retirado"}</span><br /><strong>${currency(order.total_cents)}</strong></div></article>`).join("") : "<div class='empty'>Você ainda não possui pedidos.</div>";
}

async function accountPage() {
  if (!state.user) {
    content.innerHTML = `<section class="section account-shell"><span class="eyebrow">Área do cliente</span><h1 style="font-size:3rem">Sua conta</h1>${loginForm()}</section>`;
    let register = false;
    const form = content.querySelector("#auth-form");
    content.querySelectorAll("[data-auth-tab]").forEach(tab => tab.addEventListener("click", () => { register = tab.dataset.authTab === "register"; content.querySelectorAll("[data-auth-tab]").forEach(t => t.classList.toggle("active", t === tab)); content.querySelector("#name-field").classList.toggle("hidden", !register); content.querySelector("#name-field input").required = register; form.querySelector("button").textContent = register ? "Criar conta" : "Entrar"; }));
    form.addEventListener("submit", async (event) => { event.preventDefault(); const data = Object.fromEntries(new FormData(form)); try { const session = await api(register ? "/auth/register" : "/auth/login", { method: "POST", body: JSON.stringify(data) }); state.user = session.user; state.csrf = session.csrf_token; state.cart = await api("/cart"); updateHeader(); notify(register ? "Conta criada. Bem-vindo à Atlética!" : "Login realizado."); navigate("/conta"); } catch (error) { notify(error.message); } });
    return;
  }
  const orders = await api("/orders");
  content.innerHTML = `<section class="section"><div class="section-heading"><div><span class="eyebrow">Área do cliente</span><h1 style="font-size:clamp(2.3rem,5vw,4rem);max-width:none">Olá, ${escapeHtml(state.user.name.split(" ")[0])}</h1></div><button id="logout" class="button secondary">Sair</button></div><div class="layout-two"><div class="panel"><h2>Meus pedidos</h2>${renderOrders(orders)}</div><aside class="panel"><h2>Informações</h2><p><strong>${escapeHtml(state.user.name)}</strong><br /><span class="muted">${escapeHtml(state.user.email)}</span></p>${state.user.role === "admin" ? "<a href='/admin' data-link class='button'>Abrir painel</a>" : ""}</aside></div></section>`;
  content.querySelector("#logout").addEventListener("click", async () => { try { await api("/auth/logout", { method: "POST" }); state.user = null; state.csrf = null; state.cart = { items: [], total_cents: 0 }; updateHeader(); navigate("/"); } catch (error) { notify(error.message); } });
}

async function orderPage(orderId) {
  if (!state.user) return navigate("/conta");
  const order = await api(`/orders/${orderId}`);
  const testMode = new URLSearchParams(location.search).get("modo") === "teste" && order.payment_status === "pending";
  content.innerHTML = `<section class="section account-shell"><div class="panel"><span class="eyebrow">Pedido #${order.id}</span><h1 style="font-size:3rem">${testMode ? "Pagamento de teste" : "Acompanhe seu pedido"}</h1><p class="notice">${testMode ? "Você está no modo de demonstração local. Nenhum valor será cobrado." : "O status será atualizado quando o pagamento for confirmado."}</p><div class="summary-row"><span>Total</span><strong class="total">${currency(order.total_cents)}</strong></div><div>${renderOrders([order])}</div>${testMode ? "<button id='approve-test' class='button'>Aprovar pagamento de teste</button>" : ""}<p><a href="/conta" data-link class="text-link">Ir para meus pedidos →</a></p></div></section>`;
  content.querySelector("#approve-test")?.addEventListener("click", async () => { try { const approved = await api(`/payments/mock/orders/${order.id}/approve`, { method: "POST" }); notify("Pagamento de teste aprovado!"); navigate(`/pedido/${approved.id}`); } catch (error) { notify(error.message); } });
}

async function adminPage() {
  if (!state.user || state.user.role !== "admin") { content.innerHTML = `<section class="section"><div class="empty">Acesso administrativo necessário.</div></section>`; return; }
  const [products, categories, orders] = await Promise.all([api("/admin/products"), api("/categories"), api("/admin/orders")]);
  content.innerHTML = `<section class="section"><div class="section-heading"><div><span class="eyebrow">Gestão</span><h1 style="font-size:clamp(2.3rem,5vw,4rem);max-width:none">Painel admin</h1></div></div><div class="admin-layout"><form id="product-form" class="panel stack"><h2>Novo produto</h2><label>Nome<input name="name" required minlength="2" /></label><label>Slug<input name="slug" required pattern="[a-z0-9-]+" placeholder="camiseta-godzilla" /></label><label>Categoria<select name="category_id">${categories.map(c => `<option value="${c.id}">${escapeHtml(c.name)}</option>`).join("")}</select></label><label>Preço (centavos)<input name="price_cents" type="number" min="1" required /></label><label>Descrição<textarea name="description" required minlength="5"></textarea></label><button class="button">Cadastrar produto</button></form><div class="panel admin-list"><h2>Produtos e estoque</h2>${products.map(product => `<div class="admin-row"><div><strong>${escapeHtml(product.name)}</strong><br /><small>${product.variants.map(v => `${v.size}: ${v.stock}`).join(" · ") || "Sem variações"}</small></div><button class="button secondary" data-product="${product.id}">Adicionar tamanho</button></div>`).join("")}</div><div class="panel admin-list"><h2>Pedidos</h2>${orders.length ? orders.map(order => `<div class="admin-row"><div><strong>#${order.id} — ${currency(order.total_cents)}</strong><br /><small>${escapeHtml(order.user?.name || "Cliente")} · ${order.status}</small></div>${order.status === "paid" ? `<button class="button secondary" data-order="${order.id}" data-status="available">Disponível</button>` : order.status === "available" ? `<button class="button secondary" data-order="${order.id}" data-status="picked_up">Retirado</button>` : `<span class="status ${order.status}">${order.status}</span>`}</div>`).join("") : "<p class='muted'>Nenhum pedido ainda.</p>"}</div></div></section>`;
  content.querySelector("#product-form").addEventListener("submit", async (event) => { event.preventDefault(); const raw = Object.fromEntries(new FormData(event.currentTarget)); raw.category_id = Number(raw.category_id); raw.price_cents = Number(raw.price_cents); try { const created = await api("/admin/products", { method: "POST", body: JSON.stringify(raw) }); await api(`/admin/products/${created.id}/variants`, { method: "POST", body: JSON.stringify({ size: "Único", stock: 0 }) }); notify("Produto cadastrado."); render(); } catch (error) { notify(error.message); } });
  content.querySelectorAll("[data-product]").forEach(button => button.addEventListener("click", async () => { const size = prompt("Tamanho (ex.: P, M, G, GG):"); const stock = Number(prompt("Estoque inicial:", "0")); if (!size || Number.isNaN(stock) || stock < 0) return; try { await api(`/admin/products/${button.dataset.product}/variants`, { method: "POST", body: JSON.stringify({ size, stock }) }); notify("Variação criada."); render(); } catch (error) { notify(error.message); } }));
  content.querySelectorAll("[data-order]").forEach(button => button.addEventListener("click", async () => { try { await api(`/admin/orders/${button.dataset.order}/status`, { method: "PATCH", body: JSON.stringify({ status: button.dataset.status }) }); notify("Status atualizado."); render(); } catch (error) { notify(error.message); } }));
}

function contentPage(title, body) { content.innerHTML = `<section class="section account-shell"><span class="eyebrow">Atlética Godzilla</span><div class="panel"><h1 style="font-size:clamp(2.4rem,5vw,4rem);max-width:none">${title}</h1>${body}</div></section>`; }

function staticPage(route) {
  const pages = {
    "/sobre": ["Sobre nós", "<p class='detail-description'>A Atlética Godzilla UGB reúne estudantes, torcida e esporte. Esta loja apoia a identidade da nossa comunidade com produtos para os eventos e para o dia a dia.</p>"],
    "/contato": ["Contato", "<p class='detail-description'>Para dúvidas sobre pedidos e retirada, procure os canais oficiais da Atlética Godzilla ou a equipe responsável na faculdade.</p>"],
    "/privacidade": ["Privacidade", "<p class='detail-description'>Coletamos somente nome, e-mail e senha para permitir acesso à conta e acompanhamento dos pedidos. Os dados não são vendidos nem usados para fins diferentes da operação da loja acadêmica.</p>"],
    "/trocas": ["Trocas e devoluções", "<p class='detail-description'>Antes de retirar, confira tamanho e disponibilidade. Para solicitar troca, entre em contato com a Atlética informando o número do pedido. Este texto é uma política acadêmica editável.</p>"],
  };
  const page = pages[route]; if (page) contentPage(...page); else contentPage("Página não encontrada", "<p class='detail-description'>O caminho informado não existe.</p><a class='button' href='/' data-link>Voltar para a loja</a>");
}

async function render() {
  const route = location.pathname.replace(/\/$/, "") || "/";
  document.querySelectorAll("nav a").forEach(a => a.classList.toggle("active", a.getAttribute("href") === route));
  try {
    if (route === "/") await home();
    else if (route.startsWith("/produto/")) await productPage(decodeURIComponent(route.split("/").pop()));
    else if (route === "/carrinho") await cartPage();
    else if (route === "/conta") await accountPage();
    else if (route.startsWith("/pedido/")) await orderPage(route.split("/").pop());
    else if (route === "/admin") await adminPage();
    else staticPage(route);
  } catch (error) { content.innerHTML = `<section class="section"><div class="empty">${escapeHtml(error.message)}<br /><br /><a class="button" href="/" data-link>Voltar para a loja</a></div></section>`; }
}

document.addEventListener("click", (event) => { const link = event.target.closest("a[data-link]"); if (link && link.origin === location.origin) { event.preventDefault(); navigate(link.pathname); } });
window.addEventListener("popstate", render);
document.querySelector("#nav-toggle").addEventListener("click", (event) => { const nav = document.querySelector("#main-nav"); nav.classList.toggle("open"); event.currentTarget.setAttribute("aria-expanded", nav.classList.contains("open")); });

await applyDesignTokens();
await loadSession();
render();
