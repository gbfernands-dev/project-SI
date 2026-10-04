AGENTS.md
Protocolo de Trabalho para Agentes de IA

Este documento define as regras obrigatórias para qualquer agente de IA que trabalhe neste repositório.

O objetivo é manter o projeto:

Limpo.

Organizado.

Fácil de navegar.

Fácil de entender por humanos e agentes.

Testável.

Versionável.

Com histórico de alterações rastreável.

Livre de arquivos temporários e artefatos desnecessários.

Consistente com os padrões arquiteturais existentes.

Estas regras devem ser seguidas em todas as tarefas, sem exceção.

1. Regra de ouro: entender antes de alterar

Antes de modificar qualquer arquivo:

Entenda a estrutura atual do projeto.

Identifique a arquitetura utilizada.

Localize os arquivos relacionados à tarefa.

Leia os testes existentes relacionados ao código.

Procure por documentação e configurações relevantes.

Verifique se já existe uma implementação semelhante.

Evite criar novos arquivos ou diretórios sem necessidade.

Nunca faça:

Criar arquivos "só para testar".

Duplicar funcionalidades existentes.

Criar uma segunda implementação quando já existe uma solução.

Mover arquivos sem entender suas dependências.

Alterar arquitetura sem necessidade.

Espalhar arquivos pela raiz do projeto.

Princípio

Antes de criar algo, procure se aquilo já existe.

2. Diretório limpo e organizado

A estrutura do projeto deve ser previsível.

Cada arquivo deve possuir uma responsabilidade clara e estar no diretório apropriado.

Evite:

/
├── teste.js
├── teste-final.js
├── teste-final-2.js
├── novo.js
├── novo2.js
├── temp.js
├── debug.js
├── backup.js
└── coisa-importante.js


Prefira uma estrutura coerente com a arquitetura do projeto:

/
├── src/
├── tests/
├── docs/
├── scripts/
├── config/
├── public/
├── LOGS_IA.md
├── AGENTS.md
├── promptcss.json
├── package.json
└── README.md


A estrutura real deve respeitar a tecnologia e arquitetura existentes.

Regra

Não criar um diretório apenas porque ele parece organizado.

O diretório deve representar uma responsabilidade real.

3. Dez boas práticas obrigatórias para programação com agentes de IA
3.1 Explorar antes de modificar

O agente deve investigar o código existente antes de escrever código.

Deve procurar:

Implementações existentes.

Funções relacionadas.

Componentes semelhantes.

Testes existentes.

Configurações.

Dependências.

Convenções do projeto.

Evite assumir que algo não existe sem procurar.

3.2 Fazer a menor alteração possível

Prefira alterações pequenas, localizadas e fáceis de revisar.

Não refatore partes não relacionadas à tarefa apenas porque encontrou código que poderia ser melhorado.

Regra

Uma tarefa deve produzir somente as mudanças necessárias para atingir seu objetivo.

Refatorações independentes devem ser tratadas como tarefas separadas.

3.3 TDD obrigatório

Todas as alterações de código devem seguir TDD.

Não existe exceção.

O ciclo obrigatório é:

RED
 ↓
Escrever um teste que falha
 ↓
GREEN
 ↓
Implementar o mínimo necessário
 ↓
REFACTOR
 ↓
Melhorar o código sem quebrar os testes

Ordem obrigatória

Criar ou alterar o teste.

Executar o teste e confirmar que ele falha pelo motivo esperado.

Implementar a funcionalidade.

Executar novamente os testes.

Confirmar que passaram.

Refatorar quando necessário.

Executar novamente a suíte relevante.

Executar validações adicionais quando apropriado.

Proibido

Implementar primeiro e criar o teste depois apenas para validar a implementação.

4. Usar subagents quando houver vantagem real

O agente principal pode utilizar subagents quando isso aumentar a qualidade, velocidade ou segurança da execução.

Não utilizar subagents apenas para dividir uma tarefa simples artificialmente.

Bons casos para subagents

Utilize subagents quando houver tarefas que possam ser executadas de maneira independente, por exemplo:

Investigação

Um subagent pode analisar:

Estrutura do projeto.

Arquitetura.

Dependências.

Implementações existentes.

Possíveis pontos de impacto.

Testes

Um subagent pode analisar:

Testes existentes.

Casos extremos.

Cobertura.

Cenários que deveriam ser testados.

Revisão

Um subagent pode revisar:

Código.

Segurança.

Performance.

Arquitetura.

Possíveis regressões.

Documentação

Um subagent pode verificar:

Documentação desatualizada.

Inconsistências.

Necessidade de atualização de README ou docs.

Regra para uso de subagents

Antes de utilizar um subagent, o agente principal deve conseguir responder:

"O que este subagent fará que será mais eficiente ou confiável do que eu fazer sozinho?"

Se não houver uma resposta clara, não utilizar.

Subagents não substituem validação

O agente principal continua responsável pelo resultado final.

Nunca assumir que:

"O subagent disse que está correto."

significa que a tarefa está validada.

O agente principal deve revisar o resultado e executar os testes necessários.

5. Registro obrigatório em LOGS_IA.md

Toda tarefa deve ser registrada em:

LOGS_IA.md


O registro deve acontecer:

Antes de iniciar a tarefa.

Imediatamente após concluir a tarefa.

Registro inicial

Antes de modificar o código, registrar:

Data.

Objetivo.

Arquivos potencialmente envolvidos.

Abordagem planejada.

Limitações ou riscos conhecidos.

Exemplo:

## 2026-09-28 — Início

### Objetivo
Adicionar validação de e-mail no formulário de cadastro.

### Arquivos envolvidos
- src/components/RegisterForm.tsx
- tests/RegisterForm.test.tsx

### Abordagem
Implementar seguindo TDD.

### Riscos
Verificar compatibilidade com validações existentes.

Registro final

Após concluir:

Resultado.

Arquivos alterados.

Testes executados.

Resultado dos testes.

Validações realizadas.

Limitações conhecidas.

Subagents utilizados, quando houver.

Exemplo:

## 2026-09-28 — Conclusão

### Resultado
Validação de e-mail adicionada.

### Arquivos alterados
- src/components/RegisterForm.tsx
- tests/RegisterForm.test.tsx

### Testes
- RegisterForm.test.tsx — PASS
- Suíte completa — PASS

### Validação
Lint executado com sucesso.

### Limitações
Nenhuma conhecida.

### Subagents
- Code Review Agent — revisão de implementação.

6. Git e commits obrigatórios

Cada tarefa deve possuir um commit pequeno e descritivo.

O commit deve conter:

A alteração relacionada à tarefa.

O registro correspondente em LOGS_IA.md.

Exemplo
git add src/components/RegisterForm.tsx tests/RegisterForm.test.tsx LOGS_IA.md
git commit -m "feat: adiciona validação de email no cadastro"

Princípios de commits

Prefira:

feat: adiciona validação de email
test: adiciona testes para autenticação
fix: corrige cálculo do carrinho
refactor: simplifica serviço de pagamentos
docs: atualiza documentação da API


Evite:

mudanças
update
fix
coisas
alterações
teste

Falha no Git

Se:

Git não estiver instalado;

Git não estiver disponível no PATH;

O commit falhar;

O repositório estiver indisponível;

o agente deve:

Registrar a falha em LOGS_IA.md.

Explicar a causa.

Deixar claro que o commit está pendente.

Nunca

Modificar .git manualmente para simular um commit.

7. Terminal sempre em segundo plano

Comandos de terminal devem ser executados em segundo plano.

O objetivo é evitar que processos ou janelas de terminal apareçam aleatoriamente durante a execução.

Isso se aplica principalmente a:

Testes.

Build.

Lint.

Servidores locais.

Scripts.

Ferramentas de desenvolvimento.

Processos persistentes devem ser tratados de maneira controlada e encerrados quando não forem mais necessários.

8. Design e tokens visuais

O arquivo:

promptcss.json


é a fonte de verdade dos tokens visuais do front-end.

Alterações relacionadas a:

Cores.

Paleta.

Tipografia.

Espaçamento.

Bordas.

Sombras.

Tokens.

Componentes visuais.

devem respeitar essa fonte de verdade.

Quando necessário, atualizar:

promptcss.json


e garantir que o carregamento dos tokens no navegador continue funcionando.

Proibido

Criar valores visuais duplicados espalhados pelo código quando eles deveriam ser controlados pelos tokens.

Evite:

color: #123456;


quando esse valor deveria vir de um token.

Prefira o mecanismo de tokens já utilizado pelo projeto.

9. Qualidade de código

Todo código novo ou alterado deve seguir princípios de Clean Code.

Priorizar:

Nomes claros.

Funções pequenas.

Responsabilidades bem definidas.

Baixo acoplamento.

Alta coesão.

Código simples.

Tratamento explícito de erros.

Interfaces claras.

Evitar duplicação.

Evitar abstrações prematuras.

Evitar
function x(a, b, c) {
  // lógica difícil de entender
}


Preferir:

function calculateOrderTotal(items, discount, shipping) {
  // ...
}


O código deve ser compreensível sem depender de comentários para explicar lógica confusa.

10. Validar antes de considerar a tarefa concluída

Uma tarefa não está concluída apenas porque o código foi escrito.

Antes de finalizar:

Executar os testes criados ou alterados.

Executar os testes relacionados.

Executar a suíte completa quando for viável.

Executar lint quando disponível.

Executar type-check quando disponível.

Executar build quando relevante.

Verificar alterações no Git.

Revisar arquivos criados.

Verificar se arquivos temporários foram deixados para trás.

Atualizar LOGS_IA.md.

Criar o commit.

Fluxo obrigatório de trabalho

Toda tarefa deve seguir este fluxo:

┌──────────────────────┐
│ 1. Receber a tarefa  │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│ 2. Registrar no LOG  │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│ 3. Explorar projeto  │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│ 4. Avaliar subagents │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│ 5. Escrever testes   │
│       (RED)          │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│ 6. Implementar       │
│       (GREEN)        │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│ 7. Refatorar         │
│      (REFACTOR)      │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│ 8. Validar tudo      │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│ 9. Limpar projeto    │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│ 10. Atualizar LOG    │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│ 11. Criar commit     │
└──────────────────────┘

Checklist obrigatório

Antes de finalizar qualquer tarefa, verificar:

Investigação

 Entendi a estrutura do projeto.

 Procurei implementações existentes.

 Procurei testes existentes.

 Identifiquei os arquivos afetados.

 Evitei criar arquivos desnecessários.

Subagents

 Avaliei se subagents seriam vantajosos.

 Usei subagents quando realmente agregaram valor.

 Revisei pessoalmente os resultados dos subagents.

TDD

 Criei/alterei o teste antes da implementação.

 Confirmei o estado RED.

 Implementei o mínimo necessário.

 Confirmei o estado GREEN.

 Refatorei quando necessário.

 Executei os testes novamente.

Código

 O código segue Clean Code.

 Não introduzi duplicação desnecessária.

 Não criei abstrações prematuras.

 Mantive a arquitetura existente.

 promptcss.json foi respeitado quando aplicável.

Organização

 Não deixei arquivos temporários.

 Não deixei arquivos de debug.

 Não deixei backups desnecessários.

 Arquivos estão nos diretórios corretos.

 A raiz do projeto continua limpa.

Validação

 Testes executados.

 Lint executado quando disponível.

 Type-check executado quando disponível.

 Build executado quando relevante.

 Git diff revisado.

 Git status revisado.

Registro

 Registrei o início da tarefa em LOGS_IA.md.

 Registrei a conclusão da tarefa.

 Registrei arquivos alterados.

 Registrei testes e validações.

 Registrei limitações conhecidas.

 Registrei subagents utilizados, se houver.

Git

 Commit pequeno e focado.

 Commit possui mensagem descritiva.

 LOGS_IA.md está incluído no commit.

 Se o commit falhou, a causa está registrada.

 .git nunca foi manipulado manualmente.

Princípios fundamentais

O agente deve sempre priorizar:

Entender antes de alterar.

Testar antes de implementar.

Alterar o mínimo necessário.

Reutilizar antes de criar.

Manter a estrutura limpa.

Usar subagents quando houver vantagem real.

Validar antes de declarar concluído.

Registrar todas as tarefas.

Manter commits pequenos e rastreáveis.

Deixar o projeto mais organizado do que estava.

Regra final

Ao terminar uma tarefa, o próximo agente ou desenvolvedor deve conseguir entender facilmente o que foi feito, por que foi feito, onde foi feito e como verificar o resultado.

O agente não deve apenas fazer o código funcionar.

Ele deve preservar a organização, testabilidade, rastreabilidade e manutenibilidade do projeto.