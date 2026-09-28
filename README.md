# Loja da Atlética Godzilla

Protótipo acadêmico de e-commerce da Atlética Godzilla UGB. O objetivo é
demonstrar a jornada completa do cliente por uma URL HTTPS gratuita, sem receber
pagamentos reais. A aplicação é um monólito FastAPI que entrega o front-end em
HTML/CSS/JavaScript e a API versionada sob `/api/v1`.

## Tecnologias

- Python 3.12, FastAPI, SQLAlchemy e Alembic.
- PostgreSQL no Supabase para homologação acadêmica e PostgreSQL Docker no desenvolvimento.
- Mercado Pago Checkout Pro exclusivamente com credenciais e usuários de teste.
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

## Homologação acadêmica

O ambiente público planejado usa Render Free, Supabase Free e Mercado Pago em
sandbox. No painel da Render, configure `APP_ENV=production`, `DATABASE_URL`,
`SECRET_KEY`, `PUBLIC_BASE_URL`, credenciais **de teste** do Mercado Pago,
`MP_WEBHOOK_SECRET`, `SUPABASE_URL` e `SUPABASE_SERVICE_KEY`. Crie o bucket
público `products` no Supabase para os uploads de imagens.

O webhook é `https://SEU-DOMINIO/api/v1/payments/webhook`. O servidor valida a
assinatura e consulta o pagamento antes de alterar o pedido. Cold start e pausa por
inatividade são limitações aceitas para a apresentação; este ambiente não deve
ser usado para uma operação comercial.

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
