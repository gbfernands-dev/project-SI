# Loja da Atlética Godzilla

Protótipo acadêmico de e-commerce da Atlética Godzilla UGB. O objetivo é
oferecer a jornada completa do cliente por uma URL HTTPS. A aplicação é um
monólito FastAPI que entrega o front-end em
HTML/CSS/JavaScript e a API versionada sob `/api/v1`.

## Tecnologias

- Python 3.12, FastAPI, SQLAlchemy e Alembic.
- PostgreSQL no Supabase para homologação acadêmica e PostgreSQL Docker no desenvolvimento.
- Mercado Pago Checkout Pro, com ambiente definido exclusivamente por configuração privada do servidor.
- Tokens visuais em `promptcss.json`, carregados pelo navegador.
- TDD com Pytest/Playwright, contratos OpenAPI e CI no GitHub Actions.

## Rodar e testar localmente

1. Instale Docker Desktop e execute `docker compose up --build` na raiz.
2. Abra [http://localhost:8000](http://localhost:8000). O `index.html` é servido pelo FastAPI, por isso a interface, cookies, API, banco e fluxo de teste funcionam juntos.
3. Para criar o administrador, execute:

   ```powershell
docker compose exec -e ADMIN_EMAIL=admin@godzilla-ugb.com -e ADMIN_PASSWORD=uma-senha-segura web python -m app.bootstrap
   ```

4. Entre com essa conta em `/conta` e abra o painel administrativo.
5. Sem `MP_ACCESS_TOKEN`, o checkout usa o modo de teste local. O botão **Aprovar pagamento de teste** confirma o pedido e reduz o estoque uma única vez.

Para rodar testes dentro do container:

```powershell
docker compose exec web pytest tests/test_auth_and_cart.py tests/test_contract.py
docker compose exec web pytest tests/test_admin_and_payments.py
docker compose exec web playwright install --with-deps chromium
docker compose exec web pytest --no-cov tests/e2e
```

## Ambiente público

O ambiente público usa Render Free, PostgreSQL/Storage do Supabase Free e
Mercado Pago em produção. O Blueprint versionado em `render.yaml` fixa Python
3.12, executa as migrações e o bootstrap administrativo antes de iniciar o
FastAPI, publica somente a branch `main` e aguarda os checks da CI.

Para criar o serviço:

1. Integre esta versão em `main` e confirme que `render.yaml` está publicado no GitHub.
2. Crie o bucket público `products` no Supabase.
3. Abra o [Blueprint no Render](https://dashboard.render.com/blueprint/new?repo=https://github.com/gbfernands-dev/project-SI) e autorize somente este repositório.
4. Preencha no Dashboard os valores marcados como `sync: false`: `DATABASE_URL`,
   `MP_PUBLIC_KEY`, `MP_ACCESS_TOKEN`, `MP_CLIENT_ID`, `MP_CLIENT_SECRET`, `MP_WEBHOOK_SECRET`, `SUPABASE_URL`,
   `SUPABASE_SERVICE_KEY`, `ADMIN_EMAIL` e `ADMIN_PASSWORD`.
5. Aplique o Blueprint e valide `https://SEU-DOMINIO/api/v1/health`.

Use a URL PostgreSQL do pooler do Supabase em `DATABASE_URL` e mantenha Access
Token, Client Secret e a chave `service_role` do Supabase somente no backend.
O Checkout Pro envia o Access Token no cabeçalho `Authorization`; Client ID e
Client Secret ficam reservados para fluxos OAuth e nunca são enviados ao navegador.
O Render fornece `RENDER_EXTERNAL_URL`, usado automaticamente como URL pública;
defina `PUBLIC_BASE_URL` manualmente apenas se adotar um domínio próprio.

O webhook é `https://SEU-DOMINIO/api/v1/payments/webhook`. O servidor valida a
assinatura, consulta o pagamento e confere valor, moeda e ambiente antes de alterar
o pedido. Em produção, o produto interno de validação de R$ 0,50 é ocultado
automaticamente. Cold start e pausa por inatividade continuam sendo limitações
operacionais do plano gratuito.

## Branches e qualidade

- `develop`: integração da versão em desenvolvimento.
- `main`: versão de homologação; a Render publica somente essa branch.
- Crie branches de funcionalidade a partir de `develop` e use pull request para integrar.
- Pull requests de `develop` para `main` só devem ser aceitos depois do CI verde. Ative a proteção da branch `main` nas configurações do GitHub para tornar isso obrigatório.

## Documentação

- [Tarefas do responsável](docs/Gb_tasks.txt)
- [Plano de implementação funcional](docs/PLANO_IMPLEMENTACAO.md)
- [Pendências técnicas](docs/PENDENCIAS_TECNICAS.md)
- [Relatório para revisão](docs/RELATORIO_PARA_REVISAO_AGENTE.md)
- [Fluxograma da jornada](docs/fluxograma-jornada-usuario.svg)

## Registro de atividades

Siga `AGENTS.md`: antes de iniciar e ao terminar uma tarefa, registre uma entrada humana em `LOGS_IA.md` e crie um commit descritivo. Caso o Git não esteja disponível, registre a pendência sem manipular `.git` manualmente.
