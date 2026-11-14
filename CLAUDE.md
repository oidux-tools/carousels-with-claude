# Instruções para o Claude

- Responder em português (BR), em linguagem simples: quem usa este repositório pode não ser técnico.
- **Implementação guiada:** quando a pessoa disser "me ajuda a implementar", "quero implementar", "por onde eu começo?", "configura pra mim" ou algo parecido, use a skill `implementar` (`.claude/skills/implementar/SKILL.md`) e siga as fases dela, uma por vez.
- Este projeto é construído aos poucos, em conversa: processo primeiro, ferramenta depois. Não criar pastas ou áreas "para o futuro" sem o processo estar definido.
- O mapa do processo é `docs/how-it-works.md` (trilhas A e B, etapas A1–A4 e B1–B7). Ao falar de um processo ou etapa, usar esses nomes e códigos.
- Versão visual do processo: `docs/fluxo.html`. Ao mudar `docs/how-it-works.md` ou `docs/fluxo-producao.md`, **não** atualizar o visual na hora: anotar a mudança em "Pendente no visual", no fim do `how-it-works.md`. Ao fechar uma etapa ou antes de um commit, se houver pendências, perguntar à pessoa se já atualiza o visual ou se espera acumular mais. Ao atualizar, esvaziar a lista e trocar a data (no `how-it-works.md` e no topo do `fluxo.html`).
- Antes de criar ou mover algo, ler o `README.md` da raiz e o da pasta envolvida, e seguir as convenções de nome de lá.
- Toda decisão de estrutura ou processo vai para `docs/decisoes.md`.
- Ao fim de cada etapa, acrescentar uma entrada em `docs/diario.md` (pedido → feito → problemas → lição), incluindo o que deu errado. O número é sempre o **último do arquivo + 1**, lido na hora de escrever (várias sessões podem escrever nele). Antes de cada commit, conferir se o diário está em dia.
- Ao trabalhar em um projeto, ler primeiro `projetos/<slug>/projeto.md` (com o bloco Perfil e imagem), `projetos/<slug>/aprendizados.md` e `projetos/<slug>/direcao-fotografica.md`, e também `docs/aprendizados-carrossel.md`; na dúvida, o guia original em `guias/` vence.
- Feedback de revisão vira aprendizado: o que é da marca vai para `projetos/<slug>/aprendizados.md`; o que vale para qualquer projeto vai para `docs/aprendizados-carrossel.md`.
- Banco de mídia: regras em `midia/README.md`. Nunca versionar arquivos de mídia; nunca apagar nada de `midia/` sem confirmação.
- Nada sai sem uma pessoa: publicar, entregar, baixar foto paga e alterar o Notion (ou outra fonte de pedidos) só com confirmação.

## Como pedir um carrossel

- A pessoa indica o pedido do jeito dela: um link de tarefa, "o próximo pedido pronto", um arquivo, ou um tema para a IA escrever.
- A fonte, o acesso e o mapeamento de campos estão na ficha do projeto, seção "Pedidos e entregas". Leia a fonte (só leitura) e converta para o **pedido padrão** (`docs/fluxo-producao.md`): projeto, tema, pasta de entrega e a tabela "Sequência / Texto da Arte". Na tarefa do Notion, o script também lê o arquivo salvo direto.
- Texto escrito pela IA a partir de um tema só vira pedido depois que a pessoa aprova. Depois disso, ninguém reescreve: o B2 só organiza.
- Siga B1 a B5 (`docs/how-it-works.md`, `docs/fluxo-producao.md`) até a mesa pronta e pare na revisão humana (B6).

## Como a pessoa recebe

- **Revisão:** uma seção "<tema> · v1" na página "Mesa de trabalho" do Figma do projeto (carrossel, tarja de decisão, sugestões de foto). Feedback vira critério escrito antes da v2.
- **Entrega (B7), só com confirmação:** PNGs 1080 × 1440 `01.png`…`NN.png` na `pasta_entrega` do pedido; sem outra, `projetos/<slug>/entregas/<tema>/`. Pasta precisa estar vazia (nunca sobrescrever). Registro em `midia/usos.csv` e `tempos.csv`; status na fonte só com confirmação.
