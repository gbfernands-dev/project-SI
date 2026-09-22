# Logs de IAs

Registro de interações e alterações realizadas com apoio de ferramentas de inteligência artificial neste projeto.

## Como registrar

Adicione uma entrada para cada atividade relevante, preenchendo o modelo abaixo.

---

## [AAAA-MM-DD] — Título da atividade

- **IA/ferramenta:**
- **Responsável:**
- **Objetivo:**
- **Prompt ou solicitação:**
- **Arquivos afetados:**
- **Resultado:**
- **Validação realizada:**
- **Observações:**

---

## Histórico

_Ainda não há registros._
### 2026-09-21 — Início da implementação do monólito de e-commerce

- **IA/ferramenta:** Codex.
- **Responsável:** Assistente de desenvolvimento.
- **Objetivo:** Estruturar a loja da Atlética Godzilla como monólito FastAPI, com front-end local, contratos de API, autenticação, catálogo, carrinho, pedidos e testes.
- **Solicitação:** Implementar o roadmap técnico aprovado.
- **Arquivos afetados:** Estrutura `app/`, `static/`, dependências, Docker, Render e configuração de projeto.
- **Resultado:** Implementação iniciada; backend e a primeira versão do front-end foram criados.
- **Validação realizada:** Verificação de ferramentas locais; Python 3.12 está disponível.
- **Observações:** Git, Docker e Node não estão disponíveis no PATH desta máquina. O commit desta atividade está pendente até que Git seja instalado ou disponibilizado.

### 2026-09-21 — Início do protocolo de logs e contrato visual

- **IA/ferramenta:** Codex.
- **Responsável:** Assistente de desenvolvimento.
- **Objetivo:** Tornar obrigatório o registro humano de tarefas e usar `promptcss.json` como base do design do front-end.
- **Solicitação:** Registrar tarefas, criar commits e utilizar `promptcss.json` como base de design.
- **Arquivos afetados:** `AGENTS.md`, `LOGS_IA.md`, `promptcss.json`, front-end e rotas estáticas.
- **Resultado:** Em andamento.
- **Validação realizada:** `promptcss.json` foi encontrado vazio; a configuração visual foi criada a partir da identidade da logo oficial.
- **Observações:** O commit permanece pendente pela indisponibilidade do executável Git.

### 2026-09-21 — Conclusão da implementação inicial

- **IA/ferramenta:** Codex.
- **Responsável:** Assistente de desenvolvimento.
- **Objetivo:** Concluir a primeira versão funcional da loja e validar backend, contrato e front-end.
- **Arquivos afetados:** Monólito FastAPI, front-end estático, testes, Docker, CI, documentação, migrações e configuração visual.
- **Resultado:** Loja responsiva implementada com autenticação por cookie/CSRF, catálogo filtrável, carrinho, checkout de teste, fluxo de pedido, estoque, painel administrativo, OpenAPI, Mercado Pago configurável e deploy preparado para Render.
- **Validação realizada:** Lint sem erros; 8 testes de backend aprovados com 81,72% de cobertura; 1 teste Playwright de interface aprovado.
- **Observações:** Artefatos temporários de banco e cobertura foram removidos. Git permanece indisponível neste computador, portanto o commit e a criação das branches `develop` e `main` continuam pendentes.

### 2026-09-21 — Versionamento inicial

- **IA/ferramenta:** Codex e Git for Windows.
- **Responsável:** Assistente de desenvolvimento.
- **Objetivo:** Instalar Git, criar a branch de desenvolvimento e registrar a implementação inicial em commit.
- **Arquivos afetados:** `LOGS_IA.md` e metadados Git.
- **Resultado:** Git for Windows 2.55.0.5 foi instalado, a branch `develop` foi criada a partir de `main` e a implementação inicial foi registrada no commit `0cfb714` (`feat: implementa loja da atletica godzilla`).
- **Validação realizada:** `git --version` retornou a versão instalada.
- **Observações:** O diretório não relacionado `human/` foi preservado fora do commit.

### 2026-09-21 — Publicação da branch de desenvolvimento

- **IA/ferramenta:** Codex e Git for Windows.
- **Responsável:** Assistente de desenvolvimento.
- **Objetivo:** Publicar a branch `develop` no repositório remoto configurado.
- **Arquivos afetados:** `LOGS_IA.md` e referências remotas Git.
- **Resultado:** A branch `develop` foi publicada com sucesso em `origin/develop`.
- **Validação realizada:** O remoto `https://github.com/gbfernands-dev/project-SI.git` confirmou a criação da branch e o rastreamento local foi configurado.
- **Observações:** A branch está pronta para receber pull request para `main` quando a versão for aprovada.

### 2026-09-21 — Diagnóstico da autenticação local

- **IA/ferramenta:** Codex.
- **Responsável:** Assistente de desenvolvimento.
- **Objetivo:** Identificar e corrigir a resposta HTTP 422 nas rotas de cadastro e login local.
- **Arquivos afetados:** `LOGS_IA.md`, front-end e autenticação, se necessário.
- **Resultado:** A API e o formulário foram reproduzidos com sucesso; o cadastro válido retorna HTTP 201. A interface foi ajustada para exibir o campo que falhar na validação HTTP 422.
- **Validação realizada:** Chamada direta à API local e dois testes Playwright, incluindo cadastro completo pelo navegador, foram aprovados.
- **Observações:** O HTTP 422 continuará sendo retornado quando o e-mail for inválido/ausente ou quando a senha de cadastro tiver menos de oito caracteres, mas agora a mensagem será compreensível no site.

### 2026-09-21 — Correção dos e-mails locais de exemplo

- **IA/ferramenta:** Codex.
- **Responsável:** Assistente de desenvolvimento.
- **Objetivo:** Corrigir o endereço administrativo de exemplo que usa o domínio reservado `.local`.
- **Arquivos afetados:** `LOGS_IA.md`, `.env.example` e `README.md`.
- **Resultado:** Em andamento.
- **Validação realizada:** Será incluído um teste para garantir que o exemplo de e-mail seja aceito pelo contrato de autenticação.
- **Observações:** O domínio `.local` não deve ser usado com validação de e-mail em aplicações web.
