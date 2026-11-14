---
name: implementar
description: Guia a pessoa, fase por fase, a implementar o processo de carrosséis deste repositório na vida dela (pré-requisitos, primeiro projeto, material e decupagem, curadoria, design system no Figma, tom de voz e direção fotográfica, fonte dos pedidos e pasta de entrega, primeiro carrossel de teste). Use quando a pessoa disser "me ajuda a implementar", "quero implementar", "por onde eu começo?", "configura pra mim" ou pedir ajuda para colocar o processo para rodar.
---

# Implementar o processo de carrosséis

Você vai conduzir a pessoa pela implementação do processo descrito em `docs/how-it-works.md`, **uma fase por vez**. Ela pode não ser técnica: fale simples, explique o porquê em uma frase, e faça você o que for comando, arquivo ou script.

## Regras da conversa

- **Use só o que existe neste repositório.** Cada fase aponta para os arquivos que dizem como fazer. Não invente etapa, regra, campo nem ferramenta. Se a pessoa pedir algo que o processo não tem, diga que não faz parte do processo e registre a ideia no `docs/diario.md`.
- **Uma fase por vez.** No começo de cada fase, diga em 2–3 linhas o que vai acontecer e o que você vai precisar dela. No fim, mostre o que ficou pronto (arquivos) e pergunte se pode seguir.
- **Pergunte em lote, não uma coisa por mensagem.** Junte as perguntas da fase numa lista curta. O que der para descobrir sozinho (lendo arquivos, rodando um script), descubra.
- **Você preenche os arquivos.** A pessoa responde; você escreve nas fichas, nos CSVs e nos JSONs.
- **Nada sai sem confirmação:** publicar, entregar, baixar foto paga, alterar o Notion e apagar qualquer coisa de `midia/`.
- **Registre ao fechar cada fase:** uma entrada em `docs/diario.md` (pedido → feito → problemas → lição; número = último + 1). Decisão diferente do processo original vai para `docs/decisoes.md`.
- Siga também o `CLAUDE.md` da raiz.

## Primeiro: mostrar as fases e descobrir onde a pessoa está

Mostre esta lista (com ✅ no que já estiver feito) e diga qual é a próxima:

| fase | o quê | etapa do processo |
|---|---|---|
| 1 | Preparar o computador e as ferramentas | — |
| 2 | Criar o primeiro projeto (a ficha da marca) | A1 |
| 3 | Subir o material e fazer a decupagem e a importação | A2 e A3 |
| 4 | Curadoria do banco de fotos | A4 |
| 5 | Design system básico no Figma | A1 |
| 6 | Tom de voz, perfil e imagem e direção fotográfica | A1 |
| 7 | De onde vêm os pedidos e para onde vão as entregas | B1 e B7 |
| 8 | Primeiro carrossel de teste, do pedido à entrega | B1 a B7 |

**Como saber o que já está feito** (confira você, sem perguntar):

| fase | está feita quando… |
|---|---|
| 1 | `python --version` responde 3.10 ou mais, `python -c "import PIL"` funciona, e o conector do Figma aparece nas suas ferramentas (procure por "figma"); o da fonte de pedidos só importa na fase 7 |
| 2 | existe `projetos/<slug>/projeto.md` (fora do `_modelo/`) com Sobre, Público e Identidade visual preenchidos, e o slug tem linha em `midia/projetos.csv` |
| 3 | `midia/catalogo.csv` existe e tem linhas desse projeto, e `midia/_entrada/` está vazia |
| 4 | as linhas do projeto no catálogo têm `tags` e `origem`, e algumas têm `destaque = sim` |
| 5 | a ficha do projeto tem o link do arquivo de design system no Figma (pergunte se não tiver) |
| 6 | a ficha tem **Tom de voz** e **Perfil e imagem** preenchidos, e `projetos/<slug>/direcao-fotografica.md` tem a régua e de 10 a 20 fotos de referência |
| 7 | a seção **Pedidos e entregas** da ficha tem fonte, acesso, mapeamento e pasta de entrega preenchidos |
| 8 | existe `projetos/<slug>/producao/<tema>.json` e uma linha em `projetos/<slug>/producao/tempos.csv` |

A pessoa pode pular para uma fase específica. Avise só o que ela vai perder (ex.: sem fotos no banco, a fase 6 fica sem fotos de referência).

---

## Fase 1 · Preparar o computador e as ferramentas

**Objetivo:** tudo instalado e conectado.

1. **Python 3.10+:** rode `python --version`. Sem Python, explique como instalar (site oficial do Python; no Windows, marcar "Add Python to PATH") e espere.
2. **Bibliotecas:** rode `python -m pip install -r scripts/requirements.txt` (só o Pillow). O numpy é opcional e deixa os scripts de foto mais rápidos.
3. **Conectores no Claude:**
   - **Figma** (obrigatório para as fases 5 e 8): design system e mesa de revisão.
   - **Fonte dos pedidos** (fase 7): se for o Notion ou outra ferramenta com conector, ligue o conector; só leitura no fluxo normal. Planilha ou documento numa pasta não precisa de conector.
   - **Pexels** não tem conector: a busca é pelo navegador do app.
   - **Freepik** (opcional): pelo conector Magnific, com o login da pessoa. O Claude nunca vê a senha.
   Se algum conector não aparecer, peça para a pessoa ligar nas configurações de conectores do Claude e abrir uma sessão nova.
4. **Onde guardar:** se a pasta estiver num drive sincronizado, tudo bem; lembre que a mídia nunca vai para o Git (`.gitignore`).

**Arquivos de apoio:** `README.md`, `scripts/README.md` (seção "Preparar").

---

## Fase 2 · Criar o primeiro projeto (A1: a ficha)

**Objetivo:** `projetos/<slug>/` criado, com a ficha da marca.

1. Pergunte o nome da marca e combine o **slug** (minúsculo, sem acento, hífen entre palavras).
2. Copie `projetos/_modelo/` para `projetos/<slug>/` e acrescente a linha em `midia/projetos.csv` (`slug,nome,notion_projeto,observacao`). O `notion_projeto` pode ficar vazio até a fase 7.
3. Peça o **material de marca** (brandguide, cores, tipografia, logos em SVG) e coloque em `projetos/<slug>/guias/`, sem mexer no original. Logos, fontes e templates de produção vão em `kit/`.
4. Siga o `docs/guia-kit-projeto.md`, passos **1 a 3**: ler as fontes (inclusive posts publicados e o arquivo de produção do Figma, se houver), extrair a identidade e preencher `projeto.md` (Sobre, Público, Temas, Identidade visual, Carrossel, Divergências, Em aberto).
5. O que for deduzido, e não escrito pela marca, leva *(deduzido; confirmar)*. Dúvida de gosto vira pergunta (passo 7 do guia).

O **Tom de voz** e o **Perfil e imagem** podem ficar para a fase 6, que é onde eles são revisados com calma.

**Arquivos de apoio:** `projetos/README.md`, `projetos/_modelo/projeto.md`, `docs/guia-kit-projeto.md`.

---

## Fase 3 · Subir o material, decupar e importar (A2 e A3)

**Objetivo:** as fotos e vídeos brutos da marca no banco, catalogados.

1. **Onde a pessoa sobe o material:** `midia/_entrada/`. É passagem, não depósito: no fim da fase ela fica vazia.
2. **Área aberta ou restrita?** Pergunte se o material tem gente que precisa de proteção (pacientes, crianças, clientes). Se sim, vai para a área **restrita** do projeto, e o nome da pessoa vira código. Explique a regra do `midia/README.md` e a decisão "Banco em duas áreas" (`docs/decisoes.md`). A restrição depende de a pasta ter acesso limitado no drive: peça para a pessoa testar antes.
3. **Decupagem (A2)** é um processo à parte. Este repositório não traz o passo a passo dela; ele só sabe o formato que o importador espera:
   - uma pasta por pessoa ou assunto: `<origem>/<Pessoa ou assunto>/<Pessoa>_<NNN>[_destaque].<ext>`;
   - um `<origem>/catalogo.csv` separado por `;`, uma linha por arquivo, com as colunas `arquivo` e `pasta` (as outras colunas são levadas para o catálogo).
   Se a pessoa não tiver uma decupagem pronta, use o **fluxo de entrada manual** do `midia/README.md` ("Fluxo de entrada"): renomear pela convenção, mover para `aberta/<tipo>/` ou `restrita/<projeto>/<tipo>/` e rodar o indexador.
4. **Importação (A3):** rode primeiro com `--simular` e mostre o resultado; depois rode de verdade.
   ```
   python scripts/importar_decupagem.py "<pasta da decupagem>" --projeto <slug> --simular
   python scripts/importar_decupagem.py "<pasta da decupagem>" --projeto <slug> --lote AAAAMM_<slug>_<assunto>
   ```
   Área restrita: `--area restrita` (código por pessoa) ou `--area restrita --sem-codigo` (quando as pastas são datas ou eventos, não pessoas).
5. Confira o relatório do indexador e corrija os avisos.

**Arquivos de apoio:** `midia/README.md`, `scripts/README.md` (importar_decupagem, indexar_midia), `docs/decisoes.md` ("Decupagem fora, importação dentro", "Banco em duas áreas", "Área restrita: código só quando a pasta é uma pessoa").

---

## Fase 4 · Curadoria do banco (A4)

**Objetivo:** o banco pronto para a escolha de fotos.

1. Rode `python scripts/indexar_midia.py` e mostre um resumo (quantos arquivos, avisos).
2. Com a pessoa, complete no `midia/catalogo.csv` as colunas manuais: `tags`, `origem` (`decupagem:<lote>`, `legado:figma`, `banco:pexels`, `propria`…), `projetos` quando servir a mais de um, e `destaque = sim` nas melhores. O indexador nunca sobrescreve essas colunas.
3. Para olhar as fotos, monte folhas de contato numa pasta temporária (nunca dentro do repositório).
4. Se a marca já tem fotos usadas antes (legado), siga a decisão "Legado" do `docs/decisoes.md`.
5. Explique o log `midia/usos.csv`: ele só cresce, e quem escreve é o B7, na entrega.

**Arquivos de apoio:** `midia/README.md` (Catálogo, Origem, Log de uso, Como achar as coisas), `scripts/README.md`.

---

## Fase 5 · Design system básico no Figma (A1)

**Objetivo:** o arquivo de design system da marca com os componentes que a montagem usa.

1. Siga o `docs/guia-kit-projeto.md`, passos **4 a 6**:
   - **Fundamentos:** variáveis (Primitivas, Marca, Espaçamento) → estilos de cor e de texto → logos;
   - **Social Media:** `Social/Capa`, `Social/Conteúdo` + `Social/Item de lista`, `Social/Final` e a seção de contraste;
   - tudo em **1080 × 1440** (spread de 2160 × 1440), que é o formato oficial;
   - conferência com screenshot e instância nova.
2. Antes de mexer no Figma: carregue as skills do Figma indicadas no guia, abra o arquivo e **inspecione** o que já existe.
3. Prioridade quando há prazo: Fundamentos → capa → conteúdo. Final, collab e documentação depois.
4. No Figma do projeto, crie as duas páginas de produção: **"Mesa de trabalho"** e **"Entregues"** (decisão "Mesa de trabalho numa página só").
5. Anote os links do Figma (design system e produção) no cabeçalho da ficha.
6. Leve as dúvidas de gosto à pessoa numa lista só (passo 7 do guia) e marque como provisório o que ficar em aberto.

**Arquivos de apoio:** `docs/guia-kit-projeto.md` (passos 4 a 8 e as tabelas de armadilhas), `docs/decisoes.md` ("Componentes de slide no Figma", "Viúvas", "Contraste antes de sombra", "Spreads", "Collab", "Formato oficial").

---

## Fase 6 · Tom de voz, perfil e imagem e direção fotográfica (A1)

**Objetivo:** escrever como a marca fala e o que (e como) a foto deve mostrar. É isso que dá sentido à escolha das fotos no B3.

1. **Tom de voz** (seção da `projeto.md`): como fala, como não fala, palavras da marca, com **3 frases reais** dos posts (guia, passo 2).
2. **Perfil e imagem** (seção da `projeto.md`): tipo de projeto, o que o feed precisa provar, o que a imagem mostra e nunca mostra, cuidados com pessoas, fonte de foto preferida. Fonte: o que a equipe já registrou sobre o cliente. Se ela usa o Notion, peça para rodar no Notion AI o prompt do guia (passo 1, item 7) e salve a resposta em `projetos/<slug>/guias/perfil-notion.md`.
3. **Direção fotográfica** (`projetos/<slug>/direcao-fotografica.md`, a partir do modelo): a régua por aspecto (luz, cor, textura, profundidade, cenário, pessoas, pose, enquadramento), o que denuncia "cara de banco", "aceita com ajuste leve × não salva" e **10 a 20 fotos de referência** do banco (caminhos de `midia/…`, de preferência destaques reais). Marque a fonte de cada linha ([brandguide], [Notion], [ficha], [observado]). Não invente estilo: o que for gosto vira pergunta.
4. Teste a régua: rode `python scripts/medir_coerencia.py "<uma pasta com 3 ou 4 fotos>" --projeto <slug>` e mostre se as palavras batem com o que a pessoa vê.

**Arquivos de apoio:** `projetos/_modelo/projeto.md`, `projetos/_modelo/direcao-fotografica.md`, `docs/guia-kit-projeto.md` (passos 1, 2 e 3), `docs/decisoes.md` ("Perfil e imagem", "Fotos externas no B3", item 12), `scripts/README.md` (medir_coerencia).

---

## Fase 7 · De onde vêm os pedidos e para onde vão as entregas (B1 e B7)

**Objetivo:** combinar uma vez como o pedido chega e onde o carrossel pronto é entregue, e escrever isso na seção **"Pedidos e entregas"** da ficha (`projetos/<slug>/projeto.md`).

1. **Explique o pedido padrão** em 2 linhas: tudo o que chega vira um arquivo com projeto, tema, pasta de entrega e o texto por slide (tabela "Sequência / Texto da Arte"). Mostre `scripts/exemplos/pedido-padrao-exemplo.md`.
2. **Pergunte de onde vêm os pedidos.** Exemplos: Notion, outra ferramenta de tarefas, planilha, documentos numa pasta, ou "eu peço à IA para escrever a partir de um tema".
3. **Descubra como acessar** e teste com um pedido real, só lendo:
   - ferramenta com conector (Notion e outras): ligue o conector e leia um pedido;
   - planilha ou documentos: combine a pasta ou o arquivo e leia um;
   - texto escrito pela IA: combine onde a pessoa dá o tema. Deixe claro que o texto **só vira pedido depois que ela aprovar**, e que daí em diante ninguém reescreve (o B2 só organiza).
4. **Monte o mapeamento** de cada campo da fonte para o pedido padrão (`projeto`, `tema`, `titulo`, `pasta_entrega`, tabela, `id`) e diga quando um pedido está pronto para começar (ex.: um status). Escreva tudo na seção "Pedidos e entregas" da ficha.
5. **Se a fonte for o Notion** (como no processo original), os campos de hoje estão em `docs/fluxo-producao.md`, "De onde vêm os pedidos": base de tarefas com status de pronto para começar, relação `Project`, tabela "Sequência / Texto da Arte" no corpo da página (uma linha por slide; `+++` é ignorada), `Link Location` (pasta de entrega), `Name`, ID único e `Asset Type`. Cadastre o ID da página do projeto na coluna `notion_projeto` de `midia/projetos.csv` e troque `PREFIXO_ID` em `scripts/estruturar_pedido.py` pelo prefixo da base. Use nomes da própria pessoa, nunca os do exemplo.
6. **Entrega:** pergunte onde os PNGs devem ficar. Se a fonte não disser e a pessoa não tiver outro lugar, o padrão é `projetos/<slug>/entregas/<tema>/` (fora do Git). Os PNGs são sempre 1080 × 1440, `01.png`, `02.png`…, e só são gravados com confirmação. Se a fonte tiver status (ex.: "entregue"), anote qual, para mudar só com confirmação.
7. **Teste a conversão:** gere o pedido padrão de um pedido real e rode `python scripts/estruturar_pedido.py "<pedido>.md" --simular`. Mostre a estrutura e as exceções.

**Arquivos de apoio:** `docs/fluxo-producao.md` ("Pedido padrão", "De onde vêm os pedidos", B1 e B7), `projetos/_modelo/projeto.md` ("Pedidos e entregas"), `scripts/exemplos/pedido-padrao-exemplo.md`, `scripts/exemplos/tarefa-notion-exemplo.md`, `scripts/README.md` (estruturar_pedido), `docs/decisoes.md` ("Entrada e saída flexíveis").

---

## Fase 8 · Primeiro carrossel de teste (B1 a B7)

**Objetivo:** rodar a trilha B inteira uma vez, parando na revisão humana.

1. **B1 · Pedido:** leia um pedido da fonte configurada na fase 7 e converta para o pedido padrão (ou, no Notion, salve a tarefa num arquivo temporário, só leitura). Texto escrito pela IA só entra depois de aprovado.
2. **B2 · Estruturação:** `python scripts/estruturar_pedido.py "<pedido>" --simular`, depois sem `--simular`. Mostre as exceções ("revisar à mão", "recomendado").
3. **B3 · Fotos:** 1 principal + 2 alternativas por slide, na ordem de critérios e de fontes do `docs/how-it-works.md`; `medir_coerencia.py` e `medir_contraste.py` para ordenar. Externas só como prévia.
4. **B4 · Mesa:** uma seção "<tema> · v1" na página "Mesa de trabalho", com os componentes `Social/*`, em três faixas (carrossel, tarja de decisão, sugestões de foto). Veja `docs/fluxo-producao.md` (B4 e "O que vale virar script").
5. **B5 · Checagem:** contraste medido + screenshot (rosto, emenda, texto cortado), exceções com nível, motivo e sugestão.
6. **B6 e B6.1 · Revisão:** a pessoa olha a mesa. Cada ponto do feedback vira critério escrito **antes** de refazer (`projetos/<slug>/aprendizados.md` ou `docs/aprendizados-carrossel.md`); a mesa ganha v2 e a v1 fica embaixo, marcada.
7. **B7 · Entrega (só com confirmação):** PNGs 1080 × 1440 `01.png`…`NN.png` na pasta de entrega do pedido (vazia: nunca sobrescrever), uma linha por foto usada em `midia/usos.csv`, indexador, seção movida para "Entregues", status na fonte se houver.
8. **Tempo:** registre os marcos em `projetos/<slug>/producao/tempos.csv` desde o B1 (cabeçalho em `docs/fluxo-producao.md`, "Tempo de cada mesa"). Só horário real.

**Arquivos de apoio:** `docs/how-it-works.md`, `docs/fluxo-producao.md`, `scripts/README.md` (estruturar_pedido, medir_contraste, medir_coerencia), `docs/aprendizados-carrossel.md`, `midia/README.md` (Log de uso).

---

## Ao terminar as 8 fases

Diga à pessoa que, daqui para a frente, cada pedido segue a trilha B (fase 8; resumo em "Como pedir um carrossel" e "Como você recebe", no `README.md`) e que cada revisão deixa a próxima mesa melhor. Lembre o que ainda é feito à mão pelo Claude (montagem da mesa no B4 e registro do B7) e onde ver o processo: `docs/fluxo.html`.
