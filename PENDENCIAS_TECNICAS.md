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
| PAY-004 | Alta | Pendente | Contrato e tempo de resposta do webhook precisam seguir a documentação oficial |
| PAY-005 | Média | Pendente | É necessário decidir entre manter Preferences API ou migrar para Orders API |
| ADM-002 | Média | Pendente | Preparação e entrega não possuem trilha de auditoria |
| COM-001 | Média | Pendente | Cliente não é notificado quando o pedido fica disponível |
| DEPLOY-001 | Alta | Pendente | Publicação gratuita precisa ser preparada como homologação pública |
| DB-003 | Alta | Pendente | Conexão PostgreSQL do Supabase precisa ser validada para produção |
| STO-001 | Média | Pendente | Bucket e políticas do Supabase Storage precisam ser configurados |
| BIZ-001 | Alta | Pendente | Conteúdo jurídico e informações comerciais ainda são provisórios |
| EXT-001 | Alta | Pendente | Aplicação e credenciais do Mercado Pago dependem do responsável |
| EXT-002 | Alta | Pendente | Contas e autorizações de Render/Supabase dependem do responsável |
| OPS-003 | Alta | Pendente | Administrador inicial e segredos de produção precisam ser provisionados |

## Confronto com o fluxograma recomendado

Já estavam documentados: ciclo de estados do pagamento (`PAY-001`), reserva e concorrência de estoque (`EST-001`), sandbox/produção (`PAY-002`), sessão inválida (`AUTH-001`), migrações/configuração (`DB-001` e `CFG-001`), conciliação financeira (`PAY-003`), carrinho (`CART-001`) e escape no DOM (`SEC-002`).

Ainda não estavam documentados e foram incluídos nesta revisão:

- Contrato, prazo de confirmação e processamento não bloqueante do webhook (`PAY-004`).
- Decisão entre Preferences API e Orders API (`PAY-005`).
- Auditoria de preparação/retirada (`ADM-002`) e notificação do cliente (`COM-001`).
- Publicação gratuita e limitações operacionais (`DEPLOY-001`).
- Compatibilidade do Supabase com SQLAlchemy/Alembic (`DB-003`) e configuração do Storage (`STO-001`).
- Políticas e dados comerciais definitivos (`BIZ-001`).
- Ações externas exclusivas para Mercado Pago, Render e Supabase (`EXT-001` e `EXT-002`).
- Provisionamento e operação segura da conta administrativa (`OPS-003`).

## Separação por responsabilidade

### Executável por código, terminal e recursos da IDE

O assistente consegue implementar, testar e documentar estes itens sem acessar contas pessoais:

- `PAY-001` a `PAY-005`, exceto a escolha comercial final e o fornecimento de credenciais.
- `EST-001`, `AUTH-001`, `AUTH-002`, `CART-001` e `DB-001` a `DB-003` na parte de código/configuração.
- `UI-001`, `CI-001`, `SEC-001`, `SEC-002`, `DEP-001`, `ADM-001`, `ADM-002`, `OPS-001` e `OPS-002`.
- Preparar `render.yaml`, migrações, validação de ambiente, testes automatizados, integração com Supabase e documentação do deploy.
- Implementar notificações (`COM-001`) depois que o canal for escolhido e suas credenciais forem disponibilizadas.

### Execução compartilhada

Estes itens possuem uma parte técnica automatizável e uma etapa externa que exige participação do responsável:

| Item | O assistente pode fazer | O responsável precisa fazer |
|---|---|---|
| `DEPLOY-001` | Preparar configuração, comandos, health check e corrigir falhas de build. | Criar/autorizar a conta Render, conectar o GitHub e confirmar o primeiro deploy. |
| `DB-003` | Adaptar SQLAlchemy, SSL, pool e migrações para o Supabase. | Criar o projeto e inserir a URL secreta no painel da hospedagem. |
| `STO-001` | Implementar upload seguro e validar URLs públicas. | Criar/autorizar o projeto, bucket e credenciais; aprovar se as imagens serão públicas. |
| `COM-001` | Implementar evento, fila/repetição e integração escolhida. | Escolher canal, remetente e provedor; verificar conta/domínio quando exigido. |
| `OPS-003` | Tornar o bootstrap seguro e documentar rotação/revogação. | Escolher a conta administrativa e cadastrar os segredos no painel. |
| Mercado Pago ponta a ponta | Corrigir código, criar testes e validar sandbox tecnicamente. | Fornecer credenciais de teste pelo painel e realizar o teste como vendedor/comprador. |

### Exclusivo do responsável pelo projeto

O assistente não pode substituir estas ações pessoais, contratuais ou financeiras:

- `EXT-001`: criar/verificar a conta vendedora e a aplicação do Mercado Pago; aceitar termos; ativar credenciais; acessar o segredo do webhook; concluir verificações de identidade e dados financeiros.
- `EXT-002`: criar as contas Render e Supabase, aceitar termos, autorizar acesso ao GitHub e controlar eventual forma de pagamento/limite de gastos.
- `BIZ-001`: fornecer razão/nome do responsável, contato oficial, regras reais de retirada, troca, cancelamento, privacidade e tratamento de dados.
- Aprovar a entrada em produção, inserir segredos diretamente nos painéis e decidir quem terá acesso a eles. Segredos não devem ser enviados por chat nem versionados.
- Executar e conferir uma compra e um eventual estorno reais com valor mínimo, após a homologação completa.
- Configurar DNS de domínio próprio, caso seja desejado. Um domínio próprio é opcional para a primeira URL `onrender.com`.

## Viabilidade de ambiente gratuito

### Decisão

**Viável para homologação pública com URL HTTPS válida. Não recomendado como produção comercial permanente com pagamentos reais.**

Arquitetura gratuita mais compatível com o repositório atual:

1. **Render Free Web Service:** executa o monólito FastAPI e fornece uma URL HTTPS `onrender.com` com TLS gerenciado.
2. **Supabase Free:** PostgreSQL persistente e bucket `products` para imagens.
3. **Mercado Pago com credenciais de teste:** usa a URL pública para `PUBLIC_BASE_URL`, retornos e webhook.

A URL esperada pelo nome atual do serviço é `https://loja-atletica-godzilla.onrender.com`, mas o endereço final só é confirmado pelo Render no primeiro deploy e depende da disponibilidade do nome.

### Limitações verificadas

- O Render gratuito adormece depois de 15 minutos sem tráfego e pode levar cerca de um minuto para responder novamente. A própria Render declara que instâncias gratuitas não devem ser usadas para aplicações de produção.
- O filesystem do Render é efêmero; SQLite e uploads locais são perdidos em reinícios, deploys ou suspensão.
- O PostgreSQL gratuito da Render expira após 30 dias, portanto não é adequado para esta loja. O Supabase é a alternativa gratuita persistente mais coerente com o código atual.
- O Supabase Free pode pausar projetos com pouca atividade em sete dias; o banco entra em somente leitura acima de 500 MB e o Storage inclui 1 GB.
- O Mercado Pago espera confirmação do webhook em aproximadamente 22 segundos e realiza novas tentativas quando ela não chega. Um cold start de cerca de um minuto pode fazer a primeira entrega falhar, atrasando a confirmação.
- Migrações pré-deploy são um recurso pago da Render. No plano gratuito, será necessário executar uma migração idempotente no comando de inicialização ou em um processo controlado alternativo.
- A branch configurada para deploy é `main`, enquanto o trabalho atual está em `develop`; será necessário integrar e publicar a versão aprovada antes do deploy.

Fontes oficiais consultadas:

- [Render — Deploy for Free](https://render.com/docs/free)
- [Render — primeira implantação e URL onrender.com](https://render.com/docs/your-first-deploy)
- [Render — comandos de deploy](https://render.com/docs/deploys)
- [Supabase — pausa de projetos gratuitos](https://supabase.com/docs/guides/platform/free-project-pausing)
- [Supabase — limites de banco](https://supabase.com/docs/guides/platform/database-size)
- [Supabase — limites e cobrança](https://supabase.com/docs/guides/platform/billing-on-supabase)

## Viabilidade do Mercado Pago

### Decisão

**A integração é tecnicamente viável, mas o código atual ainda não deve processar dinheiro real.** O Checkout Pro via Preferences API continua disponível; para integrações novas, a documentação também oferece o fluxo mais recente via Orders API. A decisão arquitetural está registrada em `PAY-005`.

Antes de pagamentos reais, precisam estar resolvidos pelo menos `PAY-001`, `EST-001`, `PAY-002`, `PAY-003`, `PAY-004`, `DB-001`, `CFG-001` e `DEPLOY-001`.

É possível testar primeiro com a URL gratuita e credenciais de teste. Para produção, o Mercado Pago exige conta vendedora, aplicação, URL do site, ativação de credenciais produtivas e HTTPS. O Render fornece HTTPS, mas suas limitações gratuitas tornam recomendável usar uma instância sempre ativa antes de aceitar pagamentos reais.

Fontes oficiais consultadas:

- [Mercado Pago — requisitos do Checkout Pro](https://www.mercadopago.com.br/developers/en/docs/checkout-pro/requirements)
- [Mercado Pago — contas de teste](https://www.mercadopago.com.br/developers/pt/docs/checkout-pro-preferences/test-accounts)
- [Mercado Pago — subir Preferences API em produção](https://www.mercadopago.com.br/developers/pt/docs/checkout-pro-preferences/go-to-production)
- [Mercado Pago — webhooks e assinatura](https://www.mercadopago.com.br/developers/pt/docs/links-and-debts/additional-content/your-integrations/notifications/webhooks?scope=prod)
- [Mercado Pago — prazo e repetição das notificações Checkout Pro](https://www.mercadopago.com.br/developers/pt/docs/checkout-pro-orders/notifications?scope=prod)

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

### PAY-004 — Adequar o webhook ao contrato e ao prazo do Mercado Pago

- **Prioridade:** Alta
- **Estado:** Pendente
- **Responsável:** Código/IDE, com validação compartilhada em sandbox
- **Problema:** O endpoint consulta a API do Mercado Pago e atualiza o banco antes de responder. A chamada HTTP síncrona possui timeout de 15 segundos e ocorre dentro de uma rota `async`. A validação de assinatura também precisa ser confrontada com a origem oficial de `data.id` e com o SDK/documento vigente.
- **Impacto:** Cold start, lentidão externa ou divergência de assinatura podem provocar timeout, repetição de notificações e atraso na confirmação do pedido.
- **Evidências:** [`app/main.py`](app/main.py#L352), [`app/services.py`](app/services.py#L38), [documentação oficial de webhooks](https://www.mercadopago.com.br/developers/pt/docs/links-and-debts/additional-content/your-integrations/notifications/webhooks?scope=prod)
- **Critérios de aceite:**
  - [ ] Validar assinatura com o contrato oficial vigente e casos reais de sandbox.
  - [ ] Definir resposta rápida e persistência idempotente antes do processamento demorado, ou comprovar processamento dentro do prazo.
  - [ ] Não bloquear o event loop com `requests` dentro da rota assíncrona.
  - [ ] Tratar repetição, ordem invertida e indisponibilidade temporária da API externa.
  - [ ] Testar assinatura válida, assinatura inválida, duplicata, timeout e reprocessamento.
- **Resolução:** _A preencher._
- **Validação:** _A preencher._
- **Commit/PR:** _A preencher._

### PAY-005 — Decidir entre Preferences API e Orders API

- **Prioridade:** Média
- **Estado:** Pendente
- **Responsável:** Compartilhado
- **Problema:** O código usa Checkout Pro via Preferences API. O fluxo permanece disponível, mas a documentação atual também apresenta Orders API como caminho recomendado para novas integrações.
- **Impacto:** Corrigir o fluxo atual sem uma decisão pode gerar retrabalho posterior ou ampliar desnecessariamente o escopo antes da primeira homologação.
- **Evidências:** [`app/services.py`](app/services.py#L13), [referência de Preferences API](https://www.mercadopago.com.br/developers/pt/reference/online-payments/checkout-pro-preferences/overview), [checklist de Orders API](https://www.mercadopago.com.br/developers/en/docs/checkout-pro-orders/go-to-production?scope=prod)
- **Critérios de aceite:**
  - [ ] Comparar prazo, recursos, idempotência e esforço de migração.
  - [ ] Registrar a decisão e o motivo no repositório.
  - [ ] Se Preferences for mantida, implementar corretamente `init_point`, preferência, consulta de pagamento e webhooks.
  - [ ] Se Orders for escolhida, planejar migração de endpoints, estados, notificações e testes.
- **Resolução:** _A preencher._
- **Validação:** _A preencher._
- **Commit/PR:** _A preencher._

### ADM-002 — Registrar auditoria da preparação e retirada

- **Prioridade:** Média
- **Estado:** Pendente
- **Responsável:** Código/IDE
- **Problema:** O pedido guarda apenas o estado atual. Não há histórico, data nem administrador responsável por marcar o pedido como disponível ou retirado.
- **Impacto:** Não é possível explicar alterações, corrigir enganos ou comprovar quem entregou um pedido.
- **Evidências:** [`app/models.py`](app/models.py#L76), [`app/main.py`](app/main.py#L469)
- **Critérios de aceite:**
  - [ ] Registrar estado anterior, novo estado, data, administrador e observação opcional.
  - [ ] Impedir transições inválidas no banco/serviço.
  - [ ] Exibir o histórico necessário no painel administrativo.
  - [ ] Testar autoria e sequência das transições.
- **Resolução:** _A preencher._
- **Validação:** _A preencher._
- **Commit/PR:** _A preencher._

### COM-001 — Notificar o cliente sobre disponibilidade

- **Prioridade:** Média
- **Estado:** Pendente
- **Responsável:** Compartilhado
- **Problema:** O cliente só descobre o estado consultando a conta. Não existe notificação quando o pedido passa para `available`.
- **Impacto:** Retiradas podem atrasar e gerar atendimento manual.
- **Evidências:** [`app/main.py`](app/main.py#L469), [`static/js/app.js`](static/js/app.js#L105)
- **Critérios de aceite:**
  - [ ] Escolher canal inicial: e-mail, WhatsApp autorizado ou somente aviso dentro da conta.
  - [ ] Definir remetente, consentimento e conteúdo aprovado pelo responsável.
  - [ ] Enviar de forma idempotente e registrar sucesso/falha.
  - [ ] Repetir falhas temporárias sem duplicar mensagens.
- **Resolução:** _A preencher._
- **Validação:** _A preencher._
- **Commit/PR:** _A preencher._

### DEPLOY-001 — Publicar uma homologação gratuita no Render

- **Prioridade:** Alta
- **Estado:** Pendente
- **Responsável:** Compartilhado
- **Problema:** O repositório possui `render.yaml`, mas faltam variáveis declaradas, migração compatível com plano gratuito, banco persistente externo e validação real do build. A branch configurada é `main`, enquanto as mudanças atuais estão em `develop`.
- **Impacto:** O deploy pode iniciar com SQLite/configuração insegura ou falhar sem criar uma URL utilizável.
- **Evidências:** [`render.yaml`](render.yaml#L1), [`app/config.py`](app/config.py#L9), [Render Free](https://render.com/docs/free)
- **Critérios de aceite:**
  - [ ] Corrigir os bloqueadores técnicos críticos antes de expor a aplicação.
  - [ ] Declarar variáveis não secretas e placeholders `sync: false` para segredos.
  - [ ] Executar migrações idempotentes sem depender de `preDeployCommand` pago.
  - [ ] Integrar a versão aprovada em `main` e publicar no remoto.
  - [ ] Confirmar URL HTTPS, health/readiness, logs e persistência após reinício.
  - [ ] Rotular o ambiente gratuito como homologação, não produção comercial.
- **Resolução:** _A preencher._
- **Validação:** _A preencher._
- **Commit/PR:** _A preencher._

### DB-003 — Validar a conexão SQLAlchemy com Supabase

- **Prioridade:** Alta
- **Estado:** Pendente
- **Responsável:** Compartilhado
- **Problema:** A URL padrão local não representa o pooler do Supabase. É necessário confirmar driver `psycopg`, formato da URL, SSL, limites de conexão e compatibilidade com Alembic.
- **Impacto:** O serviço pode falhar no boot, esgotar conexões ou executar migrações no endereço errado.
- **Evidências:** [`app/database.py`](app/database.py#L7), [`migrations/env.py`](migrations/env.py#L11), [Supabase com SQLAlchemy](https://supabase.com/docs/guides/troubleshooting/using-sqlalchemy-with-supabase-FUqebT)
- **Critérios de aceite:**
  - [ ] Usar URL `postgresql+psycopg` compatível com o pooler e senha corretamente codificada.
  - [ ] Configurar SSL e pool apropriado para a instância gratuita.
  - [ ] Executar Alembic e suíte de integração em um projeto de homologação.
  - [ ] Validar reconexão após pausa/reinício do Supabase.
- **Resolução:** _A preencher._
- **Validação:** _A preencher._
- **Commit/PR:** _A preencher._

### STO-001 — Configurar o bucket de imagens no Supabase

- **Prioridade:** Média
- **Estado:** Pendente
- **Responsável:** Compartilhado
- **Problema:** O código espera um bucket público chamado `products`, mas o repositório não o cria nem documenta políticas, tipos aceitos e limite de tamanho no serviço externo.
- **Impacto:** Uploads podem falhar ou arquivos podem ficar expostos com políticas inadequadas.
- **Evidências:** [`app/services.py`](app/services.py#L66), [arquivos públicos no Supabase Storage](https://supabase.com/docs/guides/storage/serving/downloads), [limites de upload](https://supabase.com/docs/guides/storage/uploads/file-limits)
- **Critérios de aceite:**
  - [ ] Criar o bucket `products` com decisão explícita sobre acesso público.
  - [ ] Restringir MIME e tamanho no bucket e também na aplicação.
  - [ ] Manter `SUPABASE_SERVICE_KEY` somente no backend.
  - [ ] Testar upload, leitura pública, substituição e remoção segura.
- **Resolução:** _A preencher._
- **Validação:** _A preencher._
- **Commit/PR:** _A preencher._

### BIZ-001 — Substituir textos acadêmicos por políticas reais

- **Prioridade:** Alta
- **Estado:** Pendente
- **Responsável:** Exclusivo do responsável para o conteúdo; código/IDE para publicação
- **Problema:** Privacidade, contato e trocas usam textos genéricos ou declaradamente editáveis. Não há identificação completa do responsável pela loja nem regras aprovadas para retirada, cancelamento, troca e tratamento de dados.
- **Impacto:** Usuários podem receber informação incompleta e o projeto pode não refletir suas obrigações comerciais e de proteção de dados.
- **Evidência:** [`static/js/app.js`](static/js/app.js#L138)
- **Critérios de aceite:**
  - [ ] Responsável fornecer e aprovar os textos e contatos oficiais.
  - [ ] Revisar requisitos legais aplicáveis com pessoa qualificada quando necessário.
  - [ ] Publicar versões datadas das políticas.
  - [ ] Informar claramente retirada, cancelamento, troca e canal de suporte.
- **Resolução:** _A preencher._
- **Validação:** _A preencher._
- **Commit/PR:** _A preencher._

### EXT-001 — Criar e ativar a integração do Mercado Pago

- **Prioridade:** Alta
- **Estado:** Pendente
- **Responsável:** Exclusivo do responsável pelo projeto
- **Problema:** Credenciais e aplicação reais dependem de uma conta vendedora, aceitação de termos, URL pública e eventuais verificações de identidade/financeiras.
- **Impacto:** Sem essas ações, o assistente consegue preparar o código, mas não validar sandbox completo nem receber pagamentos reais.
- **Fonte:** [Mercado Pago — subir em produção](https://www.mercadopago.com.br/developers/pt/docs/checkout-pro-preferences/go-to-production)
- **Critérios de aceite:**
  - [ ] Criar/verificar a conta vendedora e a aplicação.
  - [ ] Ativar credenciais de teste e criar/identificar vendedor e comprador de teste.
  - [ ] Configurar a URL HTTPS do webhook e obter seu segredo.
  - [ ] Inserir segredos diretamente no painel da hospedagem, sem versioná-los.
  - [ ] Somente depois da homologação, ativar credenciais produtivas e realizar teste real controlado.
- **Resolução:** _A preencher pelo responsável._
- **Validação:** _A preencher pelo responsável._
- **Referência externa:** _A preencher sem incluir segredos._

### EXT-002 — Criar e autorizar os recursos de hospedagem

- **Prioridade:** Alta
- **Estado:** Pendente
- **Responsável:** Exclusivo do responsável pelo projeto
- **Problema:** Render e Supabase exigem contas, aceitação de termos, autorização do repositório e controle de cobrança/limites.
- **Impacto:** A configuração pode ser preparada em código, mas nenhum serviço ou URL real existe até essas autorizações serem concluídas.
- **Critérios de aceite:**
  - [ ] Criar organização/projeto no Supabase e guardar os dados de recuperação.
  - [ ] Criar workspace no Render e autorizar somente o repositório necessário.
  - [ ] Revisar limites gratuitos, alertas e eventual limite de gastos antes de informar forma de pagamento.
  - [ ] Confirmar quem será administrador e quem poderá visualizar segredos/logs.
- **Resolução:** _A preencher pelo responsável._
- **Validação:** _A preencher pelo responsável._
- **Referência externa:** _A preencher sem incluir segredos._

### OPS-003 — Provisionar administrador e segredos de produção

- **Prioridade:** Alta
- **Estado:** Pendente
- **Responsável:** Compartilhado
- **Problema:** O bootstrap promove ou redefine a senha do e-mail informado. Ainda não existe procedimento operacional aprovado para criação, rotação, revogação e recuperação da conta administrativa.
- **Impacto:** Credenciais fracas, compartilhadas ou expostas podem comprometer catálogo, estoque, pedidos e uploads.
- **Evidências:** [`app/bootstrap.py`](app/bootstrap.py#L9), [`.env.example`](.env.example#L1)
- **Critérios de aceite:**
  - [ ] Responsável escolher um e-mail administrativo controlado e senha exclusiva forte.
  - [ ] Executar o bootstrap sem expor senha em log, histórico de shell ou repositório.
  - [ ] Revogar sessões anteriores quando senha ou papel forem alterados.
  - [ ] Documentar rotação, recuperação e remoção de acesso.
- **Resolução:** _A preencher._
- **Validação:** _A preencher._
- **Commit/PR:** _A preencher._

## Ordem recomendada

1. `AUTH-001`, `PAY-001`, `EST-001`, `PAY-002`, `PAY-003` e `PAY-004`.
2. Decidir `PAY-005`; em seguida concluir o fluxo de sandbox.
3. `DB-001`, `DB-003`, `CFG-001`, `STO-001` e `DEPLOY-001`.
4. Responsável concluir `EXT-001`, `EXT-002`, `OPS-003` e fornecer conteúdo de `BIZ-001`.
5. Publicar a homologação gratuita e validar URL, banco, storage e webhook com credenciais de teste.
6. `UI-001`, `CI-001`, `SEC-001`, `SEC-002`, `DEP-001`, `ADM-001`, `ADM-002` e `COM-001`.
7. Somente após todos os bloqueadores e testes: avaliar instância sempre ativa e aprovar pagamentos reais.

## Histórico

| Data | Alteração | Responsável | Referência |
|---|---|---|---|
| 2026-09-28 | Documento criado a partir da revisão técnica inicial. | Codex | Criação do backlog técnico |
| 2026-09-28 | Confronto com o fluxograma, inclusão de lacunas, matriz de responsabilidades e viabilidade de Render/Supabase/Mercado Pago. | Codex | Análise de produção gratuita |
