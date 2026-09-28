# Relatório para revisão independente por agente

## Objetivo desta leitura

Este documento transforma uma varredura estática do repositório em uma pauta de
revisão. O agente revisor deve **verificar cada afirmação diretamente no código**,
ponderar o impacto no uso pretendido e propor uma prioridade. Não aplique alterações
somente porque um item aparece aqui.

Contexto conhecido: trata-se de uma loja FastAPI, com pagamentos Mercado Pago,
PostgreSQL/Supabase em produção e uma interface HTML/CSS/JS entregue pela própria
aplicação. Há fluxo local de demonstração sem credencial Mercado Pago.

## Decisão de produto necessária antes de propor correções

Confirme com o responsável uma das alternativas abaixo:

1. **Demonstração acadêmica:** não receberá pagamentos reais nem terá operação de
   estoque real.
2. **Venda real:** aceitará dinheiro de clientes e precisa de consistência de
   estoque, segurança de upload, recuperação de erros e operação de produção.

Essa decisão muda a prioridade dos itens de pagamento, catálogo demonstrativo e
mock. Caso a resposta não exista, trate o projeto como potencialmente produtivo por
prudência, mas marque a suposição na recomendação.

## Achados a verificar

### R1 — Estoque não é reservado no checkout

- **Evidência:** `app/main.py`, funções `checkout` e `approve_order_payment`.
  O checkout apenas compara `cart_item.quantity` com `variant.stock`; a redução de
  estoque ocorre mais tarde, quando o pagamento é aprovado.
- **Cenário a reproduzir mentalmente ou por teste:** duas contas compram a última
  unidade; ambas iniciam checkout e pagam antes do primeiro webhook ser processado.
- **Risco:** o segundo pagamento pode ser aceito pelo provedor e o webhook retornar
  conflito por falta de estoque, deixando um pagamento sem pedido atendível.
- **O que conferir:** transações, lock de linha/atualização condicional, reserva com
  expiração, cancelamento/reembolso e idempotência sob concorrência.
- **Prioridade sugerida:** crítica para venda real; baixa para demonstração isolada.

### R2 — Aprovar um pedido limpa itens novos do carrinho

- **Evidência:** `app/main.py`, `approve_order_payment`, usa um `delete` por
  `user_id` depois de aprovar a ordem.
- **Cenário:** cliente inicia checkout com A, volta e adiciona B; a aprovação de A
  apaga A e B.
- **Risco:** perda silenciosa de intenção de compra e comportamento inesperado.
- **O que conferir:** remover exclusivamente os itens/quantidades do pedido, ou
  limpar o carrinho no momento de criar a ordem com uma estratégia explícita.
- **Prioridade sugerida:** alta.

### R3 — Upload confia em nome e tipo declarados pelo cliente

- **Evidência:** `app/services.py`, `save_product_image`. O código valida
  `file.content_type`, mas monta o nome final a partir da extensão de
  `file.filename`; não faz decodificação/validação real da imagem.
- **Cenário:** upload administrativo de conteúdo HTML/JS com extensão `.html`,
  declarando `image/jpeg`.
- **Risco:** arquivo pode ser servido pelo `StaticFiles` com tipo baseado na extensão
  e executar no mesmo domínio; também há arquivos corrompidos ou com tipo divergente.
- **O que conferir:** validar magic bytes e decodificar com biblioteca de imagem,
  reencodar, fixar extensão por formato, bloquear SVG/HTML e adicionar cabeçalhos de
  proteção no conteúdo estático.
- **Prioridade sugerida:** crítica se administradores puderem fazer upload real.

### R4 — Dados de demonstração entram em produção

- **Evidência:** `app/main.py`, `lifespan` chama `seed_demo_catalog` sem condicionar
  ao ambiente.
- **Risco:** banco de produção novo recebe produtos fictícios automaticamente.
- **O que conferir:** se os produtos iniciais são realmente desejados em produção;
  separar seed explícito de bootstrap e proteger por ambiente/comando administrativo.
- **Prioridade sugerida:** alta para venda real.

### R5 — Alembic é contornado na inicialização e no deploy

- **Evidência:** `app/main.py` chama `Base.metadata.create_all`; a migration inicial
  também usa `create_all`; `render.yaml` inicia apenas o Uvicorn e não executa
  `alembic upgrade head`.
- **Risco:** o banco funciona por criação implícita, mas o histórico de schema não
  representa alterações de forma confiável e futuras migrações podem divergir.
- **O que conferir:** estratégia de bootstrap para banco vazio, comando de migração
  no deploy, migration explícita por tabela/coluna e ausência de `drop_all` fora de
  testes.
- **Prioridade sugerida:** alta.

### R6 — Confirmação de webhook tem validação de negócio incompleta

- **Evidência:** `app/main.py`, rota `/api/v1/payments/webhook`. Após consultar o
  pagamento, o código usa `external_reference` e `status == "approved"`, mas não
  compara valor, moeda e demais dados do pedido.
- **Risco:** associação indevida de um pagamento a pedido, principalmente diante de
  erro de integração ou referência reutilizada.
- **O que conferir:** assinatura segundo a documentação vigente do Mercado Pago,
  idempotência atômica, valor em centavos, moeda BRL, identificador de preferência e
  tratamento de referência inválida sem resposta 500.
- **Prioridade sugerida:** crítica para venda real.

### R7 — Contrato administrativo e interface divergem

- **Evidência:** `static/js/app.js` tenta ler `order.user?.name` no painel; o modelo
  `OrderOut` em `app/schemas.py` não declara `user` e a rota administrativa devolve
  esse modelo.
- **Efeito atual esperado:** a tela exibe sempre o fallback `Cliente`.
- **O que conferir:** se a interface deve exibir nome do comprador; se sim, criar um
  DTO administrativo mínimo e evitar expor dados desnecessários na API comum.
- **Prioridade sugerida:** média.

### R8 — Configuração `SECRET_KEY` não produz efeito

- **Evidência:** `app/config.py` a lê; não há uso posterior em `app/` para assinar,
  cifrar ou derivar dados. As sessões usam token aleatório armazenado no banco.
- **Risco:** documentação e variáveis de deploy induzem uma proteção inexistente.
- **O que conferir:** remover a variável/documentação ou usá-la para uma finalidade
  legítima e documentada. Não introduzir JWT apenas para justificar a variável.
- **Prioridade sugerida:** média.

### R9 — Dependências de desenvolvimento na imagem de produção

- **Evidência:** `requirements.txt` reúne FastAPI, Pytest, Pytest-Cov, Playwright e
  Ruff; `Dockerfile` instala o arquivo inteiro.
- **Risco:** imagem maior, superfície de dependências maior e build mais lento.
- **O que conferir:** separar requisitos de execução e desenvolvimento, mantendo o
  CI com as ferramentas de teste/lint necessárias.
- **Prioridade sugerida:** baixa a média.

### R10 — Compatibilidade/lint

- **Evidência:** `python -m ruff check .` reportou três `UP042` em
  `app/models.py`: enums `str, Enum` podem migrar para `StrEnum` no Python 3.12.
- **Ponderação:** é modernização, não falha de produto. Só faça se não houver
  incompatibilidade com SQLAlchemy, serialização ou a versão Python suportada.
- **Prioridade sugerida:** baixa.

## Outros pontos para revisão, sem classificação definitiva

- Sessões expiradas retornam 401, mas não são removidas do banco. Avaliar limpeza
  periódica e remoção da cookie no cliente.
- `ProductUpdate.category_id` aceita `null` no esquema, embora a coluna seja
  obrigatória; confirmar se isso gera erro 500 em vez de erro de validação.
- O fluxo do Mercado Pago escolhe `sandbox_init_point` antes de `init_point` sempre.
  Confirmar se o ambiente e as credenciais devem determinar essa escolha.
- O front-end administrativo permite criar variações, mas não expõe upload de imagem
  nem edição de produto/variação, apesar de a API oferecer essas rotas. Confirmar se
  são funções intencionalmente somente de API.
- O fluxograma em `docs/` descreve o fluxo recomendado, incluindo reserva atômica;
  não deve ser interpretado como descrição fiel da implementação atual.

## Arquivos e informações que não parecem fazer parte do produto versionado

- `app/__pycache__/`, `tests/**/__pycache__/` e `.ruff_cache/` são artefatos locais
  ignorados pelo Git. Não estão rastreados e podem ser removidos localmente quando
  necessário; não são achado de produto.
- Não foi encontrado `.env` rastreado nem credencial real no histórico de arquivos
  inspecionado. As senhas em `.env.example`, Docker Compose e CI são exemplos locais.
- `PENDENCIAS_TECNICAS.md` contém backlog de outra atividade e não foi alterado por
  esta análise; use-o como contexto, mas não o sobrescreva sem conciliar alterações.

## Validações realizadas e limites

- Inspeção estática dos arquivos rastreados do backend, front-end, testes,
  migrações, deploy e documentação.
- `python -m compileall -q app tests`: aprovado.
- `promptcss.json`: JSON válido.
- `git diff --check`: aprovado durante a auditoria.
- Pytest não iniciou porque o Python local não tinha o pacote `sqlalchemy`.
- `python -m ruff check .`: três avisos `UP042`; o binário `ruff` não está no PATH.

## Entrega esperada do agente revisor

Para cada R1–R10, responda em uma tabela ou lista com: confirmação/refutação,
evidência atualizada, impacto para o modo de produto decidido, prioridade, correção
mínima segura, testes necessários e eventuais efeitos colaterais. Não remova mocks,
seeds ou variáveis de configuração sem registrar a decisão de produto correspondente.
