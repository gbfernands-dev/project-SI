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
### 2026-09-28 — Início da revisão técnica do repositório

- **IA/ferramenta:** Codex.
- **Responsável:** Assistente de desenvolvimento.
- **Objetivo:** Examinar o repositório em busca de falhas e oportunidades de melhoria, sem alterar o comportamento da aplicação.
- **Solicitação:** Analisar o repositório e reportar falhas ou pontos de melhoria.
- **Arquivos afetados:** `LOGS_IA.md` (registro da atividade); código, configuração e testes serão apenas inspecionados.
- **Resultado:** Revisão iniciada.
- **Validação realizada:** Estrutura do projeto e estado inicial do Git verificados.
- **Observações:** Não há alterações de produto planejadas nesta etapa.

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
- **Resultado:** Os exemplos passaram a usar `admin@godzilla-ugb.com`, aceito pelo validador da API.
- **Validação realizada:** Lint aprovado e 9 testes de backend aprovados com 81,72% de cobertura, incluindo cadastro do e-mail administrativo de exemplo.
- **Observações:** O domínio `.local` não deve ser usado com validação de e-mail em aplicações web.

### 2026-09-28 — Conclusão da revisão técnica do repositório

- **IA/ferramenta:** Codex.
- **Responsável:** Assistente de desenvolvimento.
- **Objetivo:** Identificar falhas funcionais, riscos de segurança, problemas de implantação e oportunidades de melhoria.
- **Solicitação:** Analisar o repositório e reportar falhas ou pontos de melhoria.
- **Arquivos afetados:** `LOGS_IA.md`; os demais arquivos foram somente inspecionados.
- **Resultado:** Revisão concluída. Foram priorizados problemas no ciclo de webhooks e pagamentos, concorrência de estoque, redirecionamento do Checkout Pro, sessões inválidas, migrações, contrato visual, uploads, CI e dependências.
- **Validação realizada:** Leitura estática do backend, front-end, migrações, testes e arquivos de implantação; compilação sintática de `app/` e `tests/`; validação JSON de `promptcss.json`; consulta à documentação oficial do Mercado Pago; Ruff 0.15.12 executado, com três alertas `UP042`.
- **Observações:** A suíte Pytest não iniciou porque o Python local 3.11.9 não possui SQLAlchemy. A criação de um ambiente temporário para instalar as dependências foi bloqueada pela política de execução antes de criar arquivos. O projeto declara Python 3.12 e Ruff 0.8.4, portanto os alertas do Ruff local devem ser reconfirmados no ambiente oficial. Nenhuma correção de produto foi aplicada.

### 2026-09-28 — Início do registro das pendências técnicas

- **IA/ferramenta:** Codex.
- **Responsável:** Assistente de desenvolvimento.
- **Objetivo:** Transformar os achados da revisão técnica em um documento Markdown editável e acompanhável.
- **Solicitação:** Salvar as questões encontradas em um arquivo Markdown que será atualizado conforme as pendências forem resolvidas.
- **Arquivos afetados:** `LOGS_IA.md` e novo arquivo `PENDENCIAS_TECNICAS.md`.
- **Resultado:** Organização do backlog técnico iniciada.
- **Validação realizada:** Achados da revisão anterior consolidados e priorizados.
- **Observações:** O documento terá estados, critérios de aceite e campos para registrar resolução e validação.

### 2026-09-28 — Conclusão do registro das pendências técnicas

- **IA/ferramenta:** Codex.
- **Responsável:** Assistente de desenvolvimento.
- **Objetivo:** Disponibilizar um backlog editável para acompanhar a resolução dos achados da revisão técnica.
- **Arquivos afetados:** `PENDENCIAS_TECNICAS.md` e `LOGS_IA.md`.
- **Resultado:** Documento criado com 18 pendências priorizadas, resumo de estados, evidências, critérios de aceite, campos de resolução/validação e histórico de atualizações.
- **Validação realizada:** `git diff --check` aprovado; foram contados 18 itens no resumo e 18 seções detalhadas; criação registrada no commit `d89bb5b`.
- **Observações:** Nenhum arquivo funcional da aplicação foi alterado. O backlog deve ser atualizado no mesmo commit de cada correção relacionada.

### 2026-09-28 — Início do fluxograma da jornada do usuário

- **IA/ferramenta:** Codex.
- **Responsável:** Assistente de desenvolvimento.
- **Objetivo:** Representar visualmente a trajetória correta do cliente na loja, incluindo decisões, exceções e integrações.
- **Solicitação:** Criar um fluxograma SVG com a trajetória do usuário e os casos corretos identificados na análise do código.
- **Arquivos afetados:** `LOGS_IA.md` e novo SVG em `docs/`.
- **Resultado:** Modelagem do fluxo iniciada.
- **Validação realizada:** Escopo definido com quatro raias: cliente, aplicação, Mercado Pago e administração.
- **Observações:** O diagrama representará o comportamento recomendado após a resolução das pendências, não apenas o comportamento atual.
