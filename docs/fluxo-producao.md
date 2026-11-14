# Fluxo de produção

**Status:** fluxo em uso, validado em pilotos e em produção real.

Do pedido até a mesa pronta no Figma para revisão humana, e da aprovação até a entrega. A trilha de preparação (sistema, decupagem, importação, curadoria) roda em paralelo e não está aqui; veja [`how-it-works.md`](how-it-works.md).

---

## Etapas

| # | etapa | entra | sai | ferramenta | deu certo se… |
|---|---|---|---|---|---|
| B1 | **Pedido** | o pedido na fonte configurada na ficha do projeto ("Pedidos e entregas") | **pedido padrão** (ver abaixo) ou, no Notion, a tarefa salva num arquivo | a fonte do projeto (Notion, planilha, documento, outra ferramenta, texto aprovado) | o texto está separado por slide e a pasta de entrega está definida. No Notion: tarefa na base de tarefas com status de pronto para começar (no original, Ready to Start) e a tabela "Sequência / Texto da Arte" preenchida; **não filtrar por Asset Type** (carrosséis podem aparecer com outro tipo) |
| B1.1 | **Identificar o projeto** | slug do pedido padrão, ou relação `Project` da tarefa do Notion | slug do projeto | `midia/projetos.csv` (coluna `slug`; no Notion, coluna `notion_projeto`) | o projeto tem slug cadastrado; senão, para e avisa |
| B2 | **Estruturação** | tabela por slide + ficha do projeto | `projetos/<slug>/producao/<tema>.json` (capa, conteúdos, final; título, texto, lista, negrito, modelo, posição, quebras de linha) | **`scripts/estruturar_pedido.py`** (lê o pedido padrão ou a tarefa do Notion; o Notion é lido pelo Claude, pelo MCP, só leitura, e salvo num arquivo; veja `scripts/README.md`) + Claude para as exceções | todo slide tem papel e componente; viúvas resolvidas; destaque na última palavra; dúvidas marcadas como "revisar à mão" + motivo |
| B2.1 | **Distribuir em spreads** | número de slides | mapa de slides (ex.: 01 capa · 02–03 spread · 04 foto única · 05–06 spread com final) | `scripts/estruturar_pedido.py` (1 spread, diferente do último JSON do projeto) + regras de spread | pelo menos 1 spread; final no último spread; posição comparada com o carrossel anterior (ainda sem registro) |
| B3 | **Escolha das fotos** | estrutura + catálogo do projeto + aprendizados | 1 principal + 2 alternativas por slide ou spread, ordenadas, com contraste medido e motivo | ordem: **sentido** (a foto mostra a etapa do texto e o que o projeto pede em "Perfil e imagem" da ficha) → inegociáveis → coerência com a direção fotográfica (`projetos/<slug>/direcao-fotografica.md`; cor e luz medidas por `scripts/medir_coerencia.py`, que ordena e explica; cenário, pessoas e "cara de banco" seguem no olho) → contraste medido por canto (`scripts/medir_contraste.py`) → formato e usos. Consulta `midia/catalogo.csv` + `midia/usos.csv`: no desempate, prefere menos `usos` e as não usadas recentemente **no mesmo projeto**. Fontes, nesta ordem: fotos reais do cliente (`origem = decupagem:…`) → legado (`legado:figma`) → Pexels (navegador) → Freepik (conector Magnific), estes dois quando há menos de 2 opções boas no banco; externas entram como prévia e só são baixadas depois da aprovação no B6 (ver decisão "Fotos externas no B3") | nenhum slide sem opção; nada é eliminado, só ordenado; lacuna de foto vira pauta; foto escolhida de fonte externa ou do legado é baixada e entra no `midia/` com a `origem` marcada |
| B4 | **Montagem da mesa** (tarja por slide: salmão = decisão, branca = nada pendente) | estrutura + fotos | uma **seção** "<tema> · v1" na página única **"Mesa de trabalho"** do Figma do projeto, com o carrossel em componentes `Social/*` e as fotos ordenadas embaixo de cada slide | Figma: exportar a foto do arquivo de produção, enviar ao arquivo do design system (`upload_assets`), aplicar no slide (spread com recorte contínuo) | slides em instâncias do design system; fotos reais; textos do pedido |
| B5 | **Checagem** | mesa montada (screenshot) | quadro de exceções por slide, na mesa e no JSON | medição (`scripts/medir_contraste.py`) + olhar o screenshot (rosto, emenda, altura do bloco) | cada exceção com nível (inegociável / revisar à mão / recomendado), motivo e sugestão; nenhum inegociável sem ação |
| B6 | **Revisão humana** | mesa + exceções | carrossel aprovado **ou** feedback | pessoa | — (fora da automação) |
| B6.1 | **Ciclo de revisão** | feedback | aprendizados registrados + mesa v2, v3… | Claude | cada ponto do feedback vira critério escrito (da marca ou geral) **antes** de refazer; a versão anterior fica embaixo, marcada como substituída |
| B7 | **Entrega e registro** | carrossel aprovado | PNGs `01.png`…`NN.png` (**1080×1440**, formato oficial de todos os projetos) na **pasta de entrega do pedido** (padrão: `projetos/<slug>/entregas/<tema>/`; no Notion, o `Link Location` da tarefa, ex.: `AAAAMM_SM_Carrossel_<título>`, com `_editable-files/` ao lado); status de entregue na fonte do pedido, quando ela tiver status; **uma linha em `midia/usos.csv` por foto usada** | Figma (exportar cada slide), pasta de entrega, fonte do pedido, log de usos + indexador | só com confirmação humana; no log entram só as fotos da peça entregue (alternativas não), e o indexador recalcula `usos` e `ultimo_uso`; a pasta precisa estar vazia (nunca sobrescrever); status na fonte (ex.: card no Notion) só com confirmação |

## Pedido padrão (o que o B2 lê)

Cada pessoa recebe pedidos de um jeito. Para o B2 não depender da ferramenta, todo pedido é convertido, antes do B2, num **pedido padrão**: um arquivo `.md` com quatro informações. Exemplo completo: `scripts/exemplos/pedido-padrao-exemplo.md`.

```
# Pedido de carrossel

- projeto: marca-exemplo
- tema: rotina-de-cuidados
- titulo: Rotina de cuidados no verão
- pasta_entrega: projetos/marca-exemplo/entregas/rotina-de-cuidados/
- fonte: planilha de pauta
- id:

| Sequência | Texto da Arte |
|---|---|
| Slide 1 | Título da capa |
| Slide 2 | Título<br><br>Parágrafo. |
| Slide 3 | Título<br>• item<br>• item<br>• item |
| Slide 4 | Título<br><br>Parágrafo.<br><br>**Frase em negrito.** |
| Slide 5 | Fechamento. |
```

| campo | o que é |
|---|---|
| `projeto` | slug de `midia/projetos.csv` (obrigatório) |
| `tema` | vira o nome do JSON (`producao/<tema>.json`) e da pasta de entrega |
| `titulo` | nome do conteúdo (opcional) |
| `pasta_entrega` | onde os PNGs vão no B7. Padrão, se a pessoa não tiver outro lugar: `projetos/<slug>/entregas/<tema>/` |
| `fonte` | de onde o pedido veio (opcional) |
| `id` | ID do pedido na fonte, se houver (opcional) |

- **Uma linha por slide**, na ordem. `<br>` quebra linha e `<br><br>` separa parágrafos. `**negrito**` (ou `<b>negrito</b>`) marca a frase em negrito. Linhas com `•`, `-` ou `1.` viram lista.
- A linha `+++` e as linhas vazias são ignoradas.
- O texto vai **como o cliente mandou** (ou como você aprovou): a conversão para o pedido padrão só muda o formato, nunca as palavras.

## De onde vêm os pedidos

A fonte é configurada uma vez por projeto, na ficha (`projetos/<slug>/projeto.md`, seção "Pedidos e entregas"): qual é a fonte, como o Claude acessa (conector, pasta, arquivo) e qual campo dela vira cada campo do pedido padrão. Na produção, o Claude lê a fonte e converte para o pedido padrão antes do B2.

**Exemplo: Notion, como no processo original.** O script também lê a tarefa direto (sem converter):

| campo do Notion | vira | observação |
|---|---|---|
| base de tarefas, status de pronto para começar (no original, "Ready to Start") | quando pegar o pedido | o Claude lê pelo conector, só leitura, e salva a resposta do `notion-fetch` num arquivo |
| relação `Project` | `projeto` | o ID da página do projeto vai na coluna `notion_projeto` de `midia/projetos.csv` |
| tabela "Sequência / Texto da Arte" no corpo da página | a tabela | uma linha por slide; `+++` é ignorada |
| `Link Location` | `pasta_entrega` | a pasta onde os PNGs são gravados |
| `Name` | `titulo` | |
| ID único (propriedade "ID") | `id` | com o prefixo da base (`PREFIXO_ID` em `scripts/estruturar_pedido.py`) |
| `Asset Type` | — | só gera aviso "recomendado" se não for "Social Media Carousel" |
| `Final Due Date`, `Client Delivery Date` | — | vão para `origem` no JSON |

Exemplo de tarefa salva: `scripts/exemplos/tarefa-notion-exemplo.md`.

**Outras fontes** (planilha, documento, outra ferramenta): o mapeamento fica escrito na ficha, e o Claude gera o pedido padrão a partir dela.

**Texto gerado pela IA** é uma fonte como as outras, e acontece **antes** do B1: a partir de um tema, o Claude escreve o texto por slide, **você aprova** (ou ajusta) e só então ele vira pedido padrão. Daí em diante vale a mesma regra de sempre: o B2 organiza e não reescreve.

## Tempo de cada mesa

Toda mesa tem uma linha em `projetos/<slug>/producao/tempos.csv` (horário local, `AAAA-MM-DD HH:MM`). Cabeçalho:

```
mesa,tarefa_notion,demanda_criada,preparo_inicio,mesa_pronta,revisao_inicio,revisao_fim,entregue,observacao
```

| marco | quando | quem registra |
|---|---|---|
| `demanda_criada` | a tarefa foi criada no Notion | Claude (lê do Notion) |
| `preparo_inicio` | começou a ler a tarefa (B1) | Claude |
| `mesa_pronta` | a mesa ficou pronta para revisão (fim do B5) | Claude |
| `revisao_inicio` | você começou a revisar | Claude, quando você avisar ("comecei a revisar") ou pela primeira mensagem de revisão |
| `revisao_fim` | você aprovou | Claude, quando você aprovar |
| `entregue` | a peça foi entregue (B7) | Claude, junto com a entrega |

Os tempos que importam saem daí:
- **espera:** demanda criada → início do preparo;
- **preparo:** início → mesa pronta (a parte automática);
- **fila de revisão:** mesa pronta → início da revisão;
- **revisão:** início → fim da revisão (a parte humana);
- **ciclo total:** demanda criada → entregue.

A mesa no Figma mostra um cartão com esses marcos, atualizado a cada etapa. Marco que não foi registrado fica em branco, sem estimativa.

## Regras que valem em todas as etapas

- **Regra não é filtro:** inegociável bloqueia; recomendado pode ceder com motivo; o resto vira exceção registrada.
- **Nada é publicado nem alterado no Notion** sem confirmação humana.
- **O texto do pedido é do cliente:** a estruturação organiza e ajusta tipografia (viúvas, quebras de linha nos títulos), mas não reescreve o conteúdo. Mudança de sentido vira "revisar à mão".

## Como o pedido vira estrutura

- **1ª linha de cada slide** → título; o resto → parágrafos. Linhas com `•` → lista.
- **Lista de 1 item** não cabe no componente (3 a 5): vira parágrafo e entra como "revisar à mão".
- **Mais de 2 parágrafos** num slide: o componente só tem 2 + frase em negrito. O 3º vai para o negrito e entra como "revisar à mão" (muda a ênfase).
- **Frase que parece incompleta** ("Uma das importantes"): mantém e marca.
- **Último slide** do pedido → final. Linha "+++" e slides vazios são ignorados. O "+++" é do modelo de tabela do pedido e não entra nem quando traz texto; nenhum slide é acrescentado ao que o cliente mandou (ex.: assinatura).
- **Quebra simples** (`<br />`) junta as linhas no mesmo parágrafo; **linha em branco** separa parágrafos.
- **Lista depois de uma frase** ("…, como:") fica parágrafo + lista, na ordem do pedido (campo `ordem`).
- **Texto colorido** (amarelo, itálico) é anotação para o designer: sai da arte, vai para `notas_producao` e vira "revisar à mão".
- **Bloco com link** (produto, imagem de referência) também sai da arte: vai para `referencias` e vira "revisar à mão".
- **Linha em negrito** no meio do slide vira a frase em negrito. Se ela vem antes de outro texto, o slide sai como "revisar à mão" ("vem antes de outro texto; conferir a ordem"), porque o componente mostra o negrito no fim.
- **Negrito que atravessa linhas** (`<b>Título<br><br>Frase.<br></b>Texto`) vale de onde abre até onde fecha. **Negrito no final** também vira `negrito`.
- **1ª linha longa** (mais de 80 caracteres) não é título: o slide fica sem título e vira "revisar à mão". O script nunca inventa título.
- **Final sem título** (só parágrafos longos): modelo A, último parágrafo como frase de fechamento. **Final com uma frase só**: vira título e, se for longa, "revisar à mão".
- **Título com dois-pontos no fim** parece introdução de lista: "revisar à mão". Título com ponto final, destaque em palavra fraca ("são") ou destaque repetido de outro slide: "recomendado".
- **Itens separados por linha em branco** (`• a<br><br>• b`) são **uma lista só**.
- **Slide que começa direto na lista** continua a lista do slide anterior. O script coloca os dois num spread e a exceção diz isso ("decidir se repete o título").
- **Erros de digitação do cliente** (".Isso" no começo do parágrafo, falta de espaço depois de ":") passam pelo script. Só "frase sem ponto final" é marcada.
- **A posição do texto do B2 é provisória:** quem decide é o B3, pela medição de contraste e pelos rostos.

## Fotos

- **Medir sempre.** O "tom" e o "espaço livre" escritos no catálogo erraram em 3 de 4 escolhas num piloto.
- **A medição não vê rostos.** Conferir no screenshot da mesa; texto sobre rosto é inegociável.
- **Texto longe da emenda.** Dentro de instância não dá para desenhar a continuação da sombra no slide vizinho; um bloco com Escurecer junto da emenda corta seco.
- **Toda foto usada mora no `midia/`.** Se veio do legado do Figma ou de um banco externo, é baixada no momento da escolha e entra com `origem` (`legado:figma`, `banco:freepik`…). O uso fica no log `midia/usos.csv`, e não no catálogo: o catálogo diz o que a imagem é, e o log diz onde ela foi usada.
- **Fotos claras dominam** bancos em alguns temas (ex.: consultório). Quando nada passa de 3:1, a mesa sai com a melhor opção, o Escurecer ligado e a exceção para decisão humana.
- **O banco cobre bem alguns temas e mal outros.** Quando um tema precisa de foto externa em vários slides, isso é um achado: vira lacuna para pauta.
- **As externas também tendem a ser claras.** Pexels e Freepik devolvem muita luz de estúdio; meça antes de aceitar.
- **Dá para medir a prévia.** A miniatura pública (Pexels 1600 px, Freepik ~600 px) basta para medir o contraste e montar a mesa; nada é baixado nem entra no `midia/` antes da aprovação.
- **Rosto é o que mais escapa.** O screenshot a 30% mostra texto encostado em rosto; a 15% não. Reenquadrar (deslocar o recorte) costuma resolver.
- **Área restrita** entra como alternativa com a marca "RESTRITA · cuidado" na legenda.

## O que vale virar script (prioridade)

Já virou script (veja `scripts/README.md`):
- a medição de contraste por canto (`scripts/medir_contraste.py`);
- a medição de coerência de cor (`scripts/medir_coerencia.py`);
- a leitura da tabela do Notion → JSON da estrutura (`scripts/estruturar_pedido.py`, B2 e B2.1).

Falta:

1. **Montar a mesa a partir do JSON** (instâncias, propriedades, textos com destaque, recorte do spread, cartões de fotos, tarjas). Hoje o Claude faz isso no Figma pelo conector, uma chamada por mesa a partir de uma "spec" tirada do JSON, mais o envio das fotos (`upload_assets` nos cartões de sugestão) e uma chamada que copia a foto principal para o slide, com o recorte do spread calculado.
2. **Lista de candidatas do B3** (busca no catálogo por palavras do slide, sem as `restrita` de sensibilidade, com usos e destaque no peso).
3. **Exportar e enviar as fotos** do arquivo de produção para o arquivo da mesa (só para o legado do Figma; o banco local já sobe direto).

A escolha de tema da foto, a checagem de rosto e a decisão sobre exceções continuam com o Claude e com a pessoa.
