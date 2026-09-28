# Pendências técnicas

Backlog vivo dos riscos e melhorias identificados na revisão técnica de 2026-09-28.

## Como atualizar

1. Ao iniciar um item, altere seu estado para `Em andamento` e informe responsável e data.
2. Registre decisões e mudanças no campo **Resolução**.
3. Marque cada critério de aceite concluído com `[x]`.
4. Só altere o estado para `Resolvido` depois de preencher **Validação** e **Commit/PR**.
5. Atualize o resumo e o histórico no final deste arquivo.

Estados permitidos: `Pendente`, `Em andamento`, `Bloqueado`, `Resolvido` e `Risco aceito`.

## Resumo

| ID | Prioridade | Estado | Assunto |
|---|---|---|---|
| PAY-001 | Crítica | Pendente | Webhooks posteriores do mesmo pagamento são ignorados |
| EST-001 | Crítica | Pendente | Pagamento pode ser aprovado sem estoque disponível |
| PAY-002 | Alta | Pendente | Checkout prioriza URL de sandbox |
| AUTH-001 | Alta | Pendente | Cookie de sessão inválido pode causar HTTP 500 |
| DB-001 | Alta | Pendente | Migrações não são aplicadas de forma determinística |
| CFG-001 | Alta | Pendente | Produção pode iniciar com configuração de desenvolvimento |
| UI-001 | Alta | Pendente | Contrato de tokens visuais está divergente |
| PAY-003 | Alta | Pendente | Pagamento não é conciliado por valor e moeda |
| CI-001 | Média | Pendente | CI não exercita PostgreSQL nem toda a suíte de backend |
| SEC-001 | Média | Pendente | Upload confia no MIME informado pelo cliente |
| SEC-002 | Média | Pendente | Há conteúdo persistido inserido no DOM sem escape |
| DEP-001 | Média | Pendente | Dependência vulnerável e dependências de teste em produção |
| CART-001 | Média | Pendente | Aprovação limpa itens não relacionados do carrinho |
| AUTH-002 | Média | Pendente | Faltam limitação de login e limpeza de sessões expiradas |
| DB-002 | Média | Pendente | Integridade numérica depende somente da API |
| ADM-001 | Média | Pendente | Painel não identifica o cliente do pedido |
| OPS-001 | Média | Pendente | Contexto e imagem Docker incluem arquivos desnecessários |
| OPS-002 | Média | Pendente | Health check, observabilidade e respostas HTTP são limitados |

## Pendências detalhadas

### PAY-001 — Processar o ciclo completo de notificações de pagamento

- **Prioridade:** Crítica
- **Estado:** Pendente
- **Responsável:** Não atribuído
- **Problema:** `PaymentEvent.payment_id` é único e o webhook retorna imediatamente quando esse pagamento já foi registrado. Se o primeiro evento estiver `pending`, uma atualização posterior para `approved` será ignorada.
- **Impacto:** Pedidos pagos podem permanecer como aguardando pagamento.
- **Evidências:** [`app/main.py`](app/main.py#L352), [`app/models.py`](app/models.py#L112)
- **Critérios de aceite:**
  - [ ] Registrar notificações por identificador de evento ou manter histórico de estados por pagamento.
  - [ ] Permitir a transição idempotente de `pending` para `approved`.
  - [ ] Tratar atualizações rejeitadas, canceladas, estornadas ou reembolsadas conforme a regra de negócio.
  - [ ] Testar duas notificações sequenciais com o mesmo `payment_id` e estados diferentes.
- **Resolução:** _A preencher._
- **Validação:** _A preencher._
- **Commit/PR:** _A preencher._

### EST-001 — Reservar e atualizar estoque de forma atômica

- **Prioridade:** Crítica
- **Estado:** Pendente
- **Responsável:** Não atribuído
- **Problema:** O checkout apenas consulta o estoque. A redução ocorre depois da aprovação, sem reserva, bloqueio de linha ou atualização condicional atômica.
- **Impacto:** Dois pagamentos concorrentes podem vender mais unidades do que existem; um cliente também pode pagar e receber erro de estoque durante o webhook.
- **Evidências:** [`app/main.py`](app/main.py#L281), [`app/main.py`](app/main.py#L322)
- **Critérios de aceite:**
  - [ ] Definir a estratégia de reserva, expiração e liberação de estoque.
  - [ ] Usar bloqueio transacional ou atualização condicional no PostgreSQL.
  - [ ] Definir reconciliação ou estorno quando um pagamento aprovado não puder ser atendido.
  - [ ] Criar teste de concorrência com pedidos disputando a última unidade.
- **Resolução:** _A preencher._
- **Validação:** _A preencher._
- **Commit/PR:** _A preencher._

### PAY-002 — Selecionar a URL correta do Checkout Pro

- **Prioridade:** Alta
- **Estado:** Pendente
- **Responsável:** Não atribuído
- **Problema:** `sandbox_init_point` é escolhido antes de `init_point`, mesmo quando a aplicação está em produção.
- **Impacto:** Clientes reais podem ser enviados ao ambiente de testes do Mercado Pago.
- **Evidência:** [`app/services.py`](app/services.py#L13)
- **Critérios de aceite:**
  - [ ] Usar `sandbox_init_point` somente com credenciais ou ambiente de teste.
  - [ ] Usar `init_point` em produção.
  - [ ] Testar respostas contendo simultaneamente os dois campos.
- **Resolução:** _A preencher._
- **Validação:** _A preencher._
- **Commit/PR:** _A preencher._

### AUTH-001 — Retornar 401 para sessões inexistentes

- **Prioridade:** Alta
- **Estado:** Pendente
- **Responsável:** Não atribuído
- **Problema:** O código acessa `session.expires_at` quando a consulta não encontra uma sessão.
- **Impacto:** Cookie forjado, removido ou antigo pode causar HTTP 500.
- **Evidência:** [`app/security.py`](app/security.py#L44)
- **Critérios de aceite:**
  - [ ] Verificar `session is None` antes de acessar seus atributos.
  - [ ] Retornar HTTP 401 de maneira uniforme para sessão inexistente ou expirada.
  - [ ] Adicionar testes para cookie aleatório, sessão removida e sessão expirada.
- **Resolução:** _A preencher._
- **Validação:** _A preencher._
- **Commit/PR:** _A preencher._

### DB-001 — Tornar migrações determinísticas e obrigatórias no deploy

- **Prioridade:** Alta
- **Estado:** Pendente
- **Responsável:** Não atribuído
- **Problema:** A migração inicial chama o metadata atual, a aplicação usa `create_all()` na inicialização e o deploy não executa `alembic upgrade head`.
- **Impacto:** Bancos existentes podem não receber alterações; bancos novos podem executar uma versão histórica diferente conforme os modelos evoluírem.
- **Evidências:** [`migrations/versions/20260921_0001_initial_schema.py`](migrations/versions/20260921_0001_initial_schema.py#L17), [`app/main.py`](app/main.py#L106), [`render.yaml`](render.yaml#L7)
- **Critérios de aceite:**
  - [ ] Substituir `Base.metadata.create_all/drop_all` da revisão por operações Alembic explícitas.
  - [ ] Executar `alembic upgrade head` no processo de deploy.
  - [ ] Remover a criação automática de schema da inicialização normal.
  - [ ] Testar migração de banco vazio e atualização a partir da revisão anterior.
- **Resolução:** _A preencher._
- **Validação:** _A preencher._
- **Commit/PR:** _A preencher._

### CFG-001 — Validar configuração de produção ao iniciar

- **Prioridade:** Alta
- **Estado:** Pendente
- **Responsável:** Não atribuído
- **Problema:** `APP_ENV` usa `development` por padrão e o blueprint da Render não declara as variáveis essenciais. Uma configuração incompleta pode habilitar cookie sem `Secure`, pagamento de teste, webhook sem assinatura ou URLs apontando para localhost. Upload local também é efêmero na Render.
- **Evidências:** [`app/config.py`](app/config.py#L9), [`render.yaml`](render.yaml#L1)
- **Critérios de aceite:**
  - [ ] Falhar rapidamente em produção sem banco, URL pública, credenciais e segredo do webhook válidos.
  - [ ] Rejeitar valores desconhecidos de `APP_ENV`.
  - [ ] Garantir armazenamento persistente de imagens em produção.
  - [ ] Documentar e testar a configuração mínima de deploy.
- **Resolução:** _A preencher._
- **Validação:** _A preencher._
- **Commit/PR:** _A preencher._

### UI-001 — Unificar a fonte de verdade dos tokens visuais

- **Prioridade:** Alta
- **Estado:** Pendente
- **Responsável:** Não atribuído
- **Problema:** `promptcss.json` oferece `color_system` e `css_system`, o navegador procura `tokens.colors` e o teste exige outra estrutura e outra cor. O CSS mantém ainda uma terceira configuração fixa.
- **Impacto:** Os tokens não são aplicados pelo navegador e o contrato automatizado fica inconsistente.
- **Evidências:** [`promptcss.json`](promptcss.json#L64), [`static/js/app.js`](static/js/app.js#L12), [`static/css/main.css`](static/css/main.css#L1), [`tests/test_contract.py`](tests/test_contract.py#L9)
- **Critérios de aceite:**
  - [ ] Definir um único schema versionado para `promptcss.json`.
  - [ ] Fazer JavaScript, CSS e teste consumirem os mesmos nomes e valores.
  - [ ] Manter fallback explícito apenas para falha de carregamento.
  - [ ] Validar o schema e a aplicação dos tokens em teste automatizado.
- **Resolução:** _A preencher._
- **Validação:** _A preencher._
- **Commit/PR:** _A preencher._

### PAY-003 — Conciliar valor, moeda e pedido no webhook

- **Prioridade:** Alta
- **Estado:** Pendente
- **Responsável:** Não atribuído
- **Problema:** Depois de consultar o pagamento, o webhook verifica apenas `status` e `external_reference`.
- **Impacto:** Um pagamento incompatível pode ser associado a um pedido se os dados externos estiverem incorretos ou forem manipulados em outro fluxo.
- **Evidência:** [`app/main.py`](app/main.py#L352)
- **Critérios de aceite:**
  - [ ] Conferir valor total, moeda, recebedor e referência externa.
  - [ ] Validar que o pagamento pertence à preferência criada para aquele pedido.
  - [ ] Registrar divergências sem aprovar o pedido.
  - [ ] Cobrir divergência de valor e moeda com testes.
- **Resolução:** _A preencher._
- **Validação:** _A preencher._
- **Commit/PR:** _A preencher._

### CI-001 — Executar a suíte real contra PostgreSQL

- **Prioridade:** Média
- **Estado:** Pendente
- **Responsável:** Não atribuído
- **Problema:** A fixture substitui a conexão do workflow por SQLite. A etapa principal também não executa `test_admin_and_payments.py`.
- **Impacto:** Diferenças de PostgreSQL e regressões administrativas/financeiras podem chegar ao merge.
- **Evidências:** [`tests/conftest.py`](tests/conftest.py#L1), [`.github/workflows/ci.yml`](.github/workflows/ci.yml#L25)
- **Critérios de aceite:**
  - [ ] Preservar `DATABASE_URL` do CI ou criar uma suíte específica de integração PostgreSQL.
  - [ ] Executar todos os testes de backend no workflow.
  - [ ] Testar migrações no CI.
  - [ ] Manter cobertura mínima sem ocultar arquivos críticos.
- **Resolução:** _A preencher._
- **Validação:** _A preencher._
- **Commit/PR:** _A preencher._

### SEC-001 — Validar e normalizar imagens enviadas

- **Prioridade:** Média
- **Estado:** Pendente
- **Responsável:** Não atribuído
- **Problema:** O servidor confia no `Content-Type` e na extensão fornecidos pelo cliente e lê o arquivo inteiro antes de confirmar o limite.
- **Impacto:** Conteúdo inválido ou ativo pode ser hospedado no domínio; arquivos grandes podem consumir memória desnecessariamente.
- **Evidência:** [`app/services.py`](app/services.py#L66)
- **Critérios de aceite:**
  - [ ] Validar assinatura e decodificação real da imagem.
  - [ ] Regravar a imagem em formato permitido e gerar a extensão internamente.
  - [ ] Limitar bytes e dimensões durante o processamento.
  - [ ] Testar MIME falso, extensão falsa, imagem corrompida e arquivo excedente.
- **Resolução:** _A preencher._
- **Validação:** _A preencher._
- **Commit/PR:** _A preencher._

### SEC-002 — Escapar todos os dados persistidos renderizados no DOM

- **Prioridade:** Média
- **Estado:** Pendente
- **Responsável:** Não atribuído
- **Problema:** Nomes e tamanhos presentes em pedidos e na lista administrativa são interpolados em `innerHTML` sem `escapeHtml`.
- **Impacto:** Dados maliciosos persistidos podem executar JavaScript no navegador de clientes ou administradores.
- **Evidência:** [`static/js/app.js`](static/js/app.js#L101)
- **Critérios de aceite:**
  - [ ] Escapar toda string dinâmica usada em templates HTML.
  - [ ] Preferir criação de nós e `textContent` para conteúdo de usuário.
  - [ ] Adicionar uma Content Security Policy compatível com a aplicação.
  - [ ] Criar teste com nome e tamanho contendo HTML malicioso.
- **Resolução:** _A preencher._
- **Validação:** _A preencher._
- **Commit/PR:** _A preencher._

### DEP-001 — Atualizar e separar dependências

- **Prioridade:** Média
- **Estado:** Pendente
- **Responsável:** Não atribuído
- **Problema:** `requests==2.32.3` é afetado pela CVE-2024-47081. Pytest, Ruff e Playwright também são instalados na imagem de produção.
- **Evidências:** [`requirements.txt`](requirements.txt#L1), [`Dockerfile`](Dockerfile#L4), [GHSA-9hjg-9r4m-mvj7](https://github.com/advisories/GHSA-9hjg-9r4m-mvj7)
- **Critérios de aceite:**
  - [ ] Atualizar Requests para uma versão corrigida e compatível.
  - [ ] Separar dependências de execução e desenvolvimento/teste.
  - [ ] Adicionar auditoria automatizada de dependências.
  - [ ] Executar testes e revisar mudanças incompatíveis após as atualizações.
- **Resolução:** _A preencher._
- **Validação:** _A preencher._
- **Commit/PR:** _A preencher._

### CART-001 — Vincular a limpeza do carrinho ao pedido aprovado

- **Prioridade:** Média
- **Estado:** Pendente
- **Responsável:** Não atribuído
- **Problema:** A aprovação remove todos os itens atuais do usuário, inclusive itens adicionados depois da criação do pedido. O mesmo carrinho também pode gerar pedidos pendentes repetidos.
- **Evidência:** [`app/main.py`](app/main.py#L322)
- **Critérios de aceite:**
  - [ ] Remover ou marcar somente os itens que originaram o pedido.
  - [ ] Definir comportamento do carrinho logo após o checkout.
  - [ ] Impedir checkout duplicado causado por repetição da mesma solicitação.
  - [ ] Testar item adicionado entre checkout e aprovação.
- **Resolução:** _A preencher._
- **Validação:** _A preencher._
- **Commit/PR:** _A preencher._

### AUTH-002 — Fortalecer o ciclo de autenticação

- **Prioridade:** Média
- **Estado:** Pendente
- **Responsável:** Não atribuído
- **Problema:** Não há limitação de tentativas de login, política de revogação global nem limpeza de sessões expiradas.
- **Impacto:** Maior exposição a força bruta e crescimento indefinido da tabela de sessões.
- **Evidências:** [`app/main.py`](app/main.py#L188), [`app/security.py`](app/security.py#L30)
- **Critérios de aceite:**
  - [ ] Limitar tentativas por conta e origem, com estratégia documentada.
  - [ ] Remover sessões expiradas periodicamente.
  - [ ] Definir revogação após troca de senha ou ação administrativa.
  - [ ] Adicionar testes de expiração e revogação.
- **Resolução:** _A preencher._
- **Validação:** _A preencher._
- **Commit/PR:** _A preencher._

### DB-002 — Aplicar restrições de integridade no banco

- **Prioridade:** Média
- **Estado:** Pendente
- **Responsável:** Não atribuído
- **Problema:** Preço, estoque, quantidade e total não possuem `CHECK CONSTRAINTS`; a integridade depende apenas dos schemas HTTP.
- **Evidência:** [`app/models.py`](app/models.py#L53)
- **Critérios de aceite:**
  - [ ] Impedir preço, estoque, quantidade e total negativos no PostgreSQL.
  - [ ] Definir limites coerentes com a regra de negócio.
  - [ ] Criar migração explícita para as restrições.
  - [ ] Testar violações pela camada de persistência.
- **Resolução:** _A preencher._
- **Validação:** _A preencher._
- **Commit/PR:** _A preencher._

### ADM-001 — Exibir a identificação do cliente no painel

- **Prioridade:** Média
- **Estado:** Pendente
- **Responsável:** Não atribuído
- **Problema:** O frontend tenta usar `order.user`, mas `OrderOut` não inclui o usuário; todos os pedidos aparecem como “Cliente”.
- **Evidências:** [`app/schemas.py`](app/schemas.py#L116), [`static/js/app.js`](static/js/app.js#L127)
- **Critérios de aceite:**
  - [ ] Criar uma resposta administrativa com os dados mínimos necessários do cliente.
  - [ ] Não ampliar a resposta usada pelo próprio cliente com dados desnecessários.
  - [ ] Testar identificação de pedidos de usuários diferentes.
- **Resolução:** _A preencher._
- **Validação:** _A preencher._
- **Commit/PR:** _A preencher._

### OPS-001 — Reduzir e proteger a imagem Docker

- **Prioridade:** Média
- **Estado:** Pendente
- **Responsável:** Não atribuído
- **Problema:** Não existe `.dockerignore`, e o Dockerfile copia o repositório inteiro e instala ferramentas de desenvolvimento em produção.
- **Impacto:** Imagem maior, builds mais lentos e risco de incluir `.git`, arquivos locais ou segredos ignorados apenas pelo Git.
- **Evidência:** [`Dockerfile`](Dockerfile#L1)
- **Critérios de aceite:**
  - [ ] Criar `.dockerignore` incluindo `.git`, `.env`, bancos, caches, testes e artefatos locais.
  - [ ] Instalar apenas dependências de execução na imagem final.
  - [ ] Considerar build em múltiplos estágios e imagem base fixada de forma reproduzível.
  - [ ] Inspecionar o conteúdo final da imagem.
- **Resolução:** _A preencher._
- **Validação:** _A preencher._
- **Commit/PR:** _A preencher._

### OPS-002 — Melhorar operação, diagnóstico e limites da API

- **Prioridade:** Média
- **Estado:** Pendente
- **Responsável:** Não atribuído
- **Problema:** O health check responde `ok` sem verificar banco; não há paginação, logging estruturado, métricas ou política explícita de cabeçalhos de segurança.
- **Evidências:** [`app/main.py`](app/main.py#L158), [`render.yaml`](render.yaml#L9)
- **Critérios de aceite:**
  - [ ] Separar liveness e readiness, verificando dependências na readiness.
  - [ ] Adicionar logging com identificador de requisição e eventos de pagamento.
  - [ ] Paginar listagens de produtos e pedidos.
  - [ ] Definir CSP, HSTS, `X-Content-Type-Options` e demais cabeçalhos aplicáveis.
- **Resolução:** _A preencher._
- **Validação:** _A preencher._
- **Commit/PR:** _A preencher._

## Ordem recomendada

1. PAY-001 e EST-001.
2. PAY-002, PAY-003 e AUTH-001.
3. DB-001 e CFG-001.
4. UI-001 e CI-001.
5. SEC-001, SEC-002 e DEP-001.
6. Demais itens operacionais e de manutenção.

## Histórico

| Data | Alteração | Responsável | Referência |
|---|---|---|---|
| 2026-09-28 | Documento criado a partir da revisão técnica inicial. | Codex | Criação do backlog técnico |
