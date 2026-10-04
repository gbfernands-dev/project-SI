# Plano de implementação funcional

## Objetivo

Entregar um protótipo acadêmico demonstrável por uma URL HTTPS gratuita, com
cadastro, catálogo, carrinho, checkout e confirmação de pagamento integralmente
no sandbox do Mercado Pago. O projeto não receberá dinheiro real.

## Responsabilidades

- **Código e automação:** implementação, testes, migrações, configuração do
  Render/Supabase, webhook sandbox e documentação.
- **Responsável pelo projeto:** contas externas, autorização do GitHub, inserção
  de segredos nos painéis e teste final com usuários de teste.
- **Fora do escopo:** pagamento ou estorno real, operação comercial, domínio
  próprio, alta disponibilidade e políticas jurídicas definitivas.

As ações externas estão resumidas em [`Gb_tasks.txt`](Gb_tasks.txt). O estado de
cada achado técnico é acompanhado em
[`PENDENCIAS_TECNICAS.md`](PENDENCIAS_TECNICAS.md).

## Pipeline de execução

### Fase 1 — Base funcional

- Corrigir sessão inexistente para responder HTTP 401 (`AUTH-001`).
- Limpar somente os itens do carrinho vinculados ao pedido (`CART-001`).
- Alinhar `promptcss.json`, CSS, JavaScript e teste de contrato (`UI-001`).
- Exibir a identificação necessária do cliente no painel (`ADM-001`).

**Saída:** jornada local previsível e testes de regressão aprovados.

### Fase 2 — Banco e configuração

- Tornar a migração inicial explícita e determinística (`DB-001`).
- Validar configuração de homologação ao iniciar (`CFG-001`).
- Testar SQLAlchemy/Alembic com PostgreSQL e Supabase (`DB-003`).
- Usar Storage para imagens persistentes (`STO-001`).

**Saída:** banco vazio sobe por migração e a aplicação não depende do
filesystem efêmero do Render.

### Fase 3 — Mercado Pago sandbox

- Manter Checkout Pro pela Preferences API; `PAY-005` fica encerrado por decisão.
- Selecionar `sandbox_init_point` no ambiente acadêmico (`PAY-002`).
- Processar atualizações repetidas de maneira idempotente (`PAY-001`).
- Validar assinatura e contrato do webhook (`PAY-004`).
- Cobrir aprovação, rejeição, cancelamento e repetição com respostas
  simuladas do provedor.

**Saída:** checkout sandbox completo, sem habilitação de dinheiro real.

### Fase 4 — CI/CD e publicação

- Executar lint, Alembic, todos os testes de backend, Playwright e build Docker.
- Publicar apenas a branch `main` depois da CI aprovada.
- Usar Render Free, PostgreSQL/Storage do Supabase Free e HTTPS `onrender.com`.
- Validar `/api/v1/health` e a jornada completa pela URL pública.

**Saída:** URL válida para apresentação e limitações gratuitas documentadas.

## Fluxo obrigatório por item

1. Registrar o início em `LOGS_IA.md`.
2. Localizar implementação, testes e dependências afetadas.
3. Escrever ou alterar o teste e confirmar RED.
4. Implementar o mínimo e confirmar GREEN.
5. Refatorar sem alterar o comportamento e repetir os testes.
6. Executar lint, suíte relacionada e validações adicionais.
7. Atualizar a pendência e o registro final.
8. Criar um commit pequeno contendo alteração, testes e log.

## Critério de conclusão acadêmica

- [ ] Cadastro, login, catálogo e carrinho funcionam pela URL pública.
- [ ] Checkout abre o sandbox do Mercado Pago.
- [ ] Webhook repetido não duplica pedido nem baixa de estoque.
- [ ] Pedido aprovado aparece para cliente e administrador.
- [ ] Migrações funcionam em um banco vazio.
- [ ] CI está verde e o endpoint de saúde responde.
- [ ] Nenhum segredo está versionado.
- [ ] Limitações de cold start e pausa gratuita estão registradas.

