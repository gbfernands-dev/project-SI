# Protocolo de trabalho assistido por IA

## Registro e versionamento obrigatório

Antes de iniciar uma nova tarefa e imediatamente após concluir uma tarefa, a pessoa ou agente responsável deve:

1. Registrar a atividade em `LOGS_IA.md`, usando linguagem clara para pessoas.
2. Informar objetivo, arquivos afetados, resultado, validação e limitações conhecidas.
3. Criar um commit Git pequeno e descritivo que contenha o registro e a alteração relacionada.

Se o Git não estiver instalado, não estiver disponível no PATH ou o commit falhar, registrar a causa em `LOGS_IA.md` e deixar o commit pendente. Nunca editar a pasta `.git` manualmente para simular um commit.

## Design

`promptcss.json` é a fonte de verdade dos tokens visuais do front-end. Mudanças em paleta, tipografia, espaçamento ou componentes devem atualizar esse arquivo e manter o carregamento de tokens no navegador funcionando.
