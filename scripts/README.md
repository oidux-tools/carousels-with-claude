# Scripts

Automações do repositório. Todas rodam a partir da raiz do repositório (a pasta que tem o `CLAUDE.md`).

## Preparar (uma vez por computador)

Precisa de Python 3.10+.

```bash
python -m pip install -r scripts/requirements.txt
```

## `indexar_midia.py` — atualiza o catálogo do banco de mídia

Percorre `midia/` e mantém `midia/catalogo.csv` em dia.

```bash
python scripts/indexar_midia.py
```

| opção       | o que faz                                                        |
|-------------|------------------------------------------------------------------|
| `--simular` | mostra o que mudaria, sem gravar nada                            |
| `--limpar`  | tira do catálogo as linhas de arquivos que não existem mais      |
| `--midia`   | aponta para outra pasta de banco (útil para testes)              |

**O que ele faz**

- Arquivo novo: cria a linha com tipo, formato, largura, altura, proporção, duração, tamanho e data de entrada.
- Arquivo que já existe: atualiza só as colunas técnicas.
- `projetos` vazio: sugere o projeto pelo início do nome do arquivo, se ele estiver em `projetos.csv`.
- Nunca mexe no que foi preenchido à mão (`projetos`, `tags`, `origem` e qualquer coluna extra que você criar).
- Arquivo apagado ou renomeado: a linha antiga **fica** no catálogo e aparece no relatório, para você levar as tags para o nome novo. Só sai com `--limpar`.
- Ignora `_entrada/`, mas avisa quantos arquivos estão esperando triagem.
- Lê o log `midia/usos.csv` e recalcula `usos` (quantas linhas do log) e `ultimo_uso` (data mais recente) de cada arquivo. Essas duas colunas nunca se digitam: um valor escrito à mão é substituído.
- Se o catálogo foi salvo pelo Excel com `;`, ele lê assim mesmo e grava de volta no padrão (`,`).

**Avisos que ele dá (não bloqueiam nada)**

- nome fora da convenção `<projeto>_<descricao>_<nn>.<ext>`;
- projeto no nome ou na coluna `projetos` que não está em `projetos.csv`;
- foto ou fundo abaixo do tamanho mínimo;
- arquivo que não conseguiu ler;
- linha do log de usos que aponta para um arquivo fora do catálogo, com data fora do formato `AAAA-MM-DD`, com projeto desconhecido ou que repete arquivo + peça + slide.

**Formatos que ele lê**

| especificação      | formatos                                          |
|--------------------|---------------------------------------------------|
| largura × altura   | jpg, png, webp, gif, bmp, tif, psd, svg, mp4, mov, m4v |
| duração            | mp4, mov, m4v, m4a, wav, mp3                       |

Outros formatos (pdf, ai, heic…) entram no catálogo só com tipo, formato e tamanho.

## `importar_decupagem.py` — traz uma decupagem para o banco

A decupagem (feita fora deste repositório) entrega uma pasta por pessoa ou assunto, arquivos `Pessoa_NNN[_destaque].jpg` e um `catalogo.csv`. O importador leva isso para `midia/`.

```bash
python scripts/importar_decupagem.py "<pasta da decupagem>" --projeto marca-exemplo --simular
python scripts/importar_decupagem.py "<pasta da decupagem>" --projeto marca-exemplo --area restrita --lote 202611_marca-exemplo_ensaio
```

| opção            | o que faz                                                                 |
|------------------|---------------------------------------------------------------------------|
| `--projeto`      | slug de `midia/projetos.csv` (obrigatório)                                |
| `--area`         | `aberta` (padrão) ou `restrita`                                           |
| `--lote`         | nome do lote, guardado na chave da área restrita                          |
| `--sem-codigo`   | na área restrita, mantém o nome da pasta (quando as pastas não são pessoas, ex.: datas de captação) |
| `--pastas`       | importa só algumas pastas (para testar)                                   |
| `--origem-midia` | preenche a coluna `origem` (ex.: `decupagem:202611_ensaio`)               |
| `--simular`      | mostra o que faria, sem copiar nem gravar                                 |

**O que acontece**

- Foto: cópia otimizada (lado maior 2400 px, JPEG 85), só com autor e copyright nos metadados. Vídeo: cópia direta.
- **Área aberta:** `midia/aberta/<tipo>/<projeto>_<pasta>-<NNN>.jpg` (ex.: `marca-exemplo_ensaio-003.jpg`).
- **Área restrita:** `midia/restrita/<projeto>/<tipo>/<projeto>_<codigo>-<NNN>.jpg` (ex.: `marca-exemplo_rk7m2qx-003.jpg`). Cada pasta ganha um código aleatório e estável; a tradução vai para `midia/restrita/<projeto>/_chave.json` (fora do Git). O nome da pasta também é trocado pelo código nos textos que vão para o catálogo.
- O número da foto é o mesmo da decupagem; o destaque vai para a coluna `destaque`, não no nome.
- As colunas da decupagem entram no catálogo, menos `arquivo`, `pasta`, `projeto`, `numero`, `tipo` e `orientacao`. A coluna `grupo` guarda a pasta (aberta) ou o código (restrita).
- Reimportar é seguro: o que já foi copiado fica, os códigos não mudam e as colunas da decupagem são atualizadas.
- No fim, roda o indexador.

**Achar o original em alta:** na aberta, o grupo é a pasta; na restrita, a `_chave.json` traduz o código. O número da foto é o mesmo da decupagem.

## `medir_contraste.py` — mede o contraste do texto em cada foto (B3)

Para cada foto e cada posição do bloco de texto, calcula a razão de contraste do creme do texto (`#F0EBDC`) contra a parte mais clara do fundo atrás do bloco. Serve para **ordenar** fotos e posições na escolha das fotos (B3) e na checagem (B5). Não elimina nada.

```bash
python scripts/medir_contraste.py midia/aberta/foto/marca-exemplo_ensaio-003.jpg
python scripts/medir_contraste.py "<pasta>" --formato spread
python scripts/medir_contraste.py "<pasta>" --bloco 700x400 --json
```

| opção                | o que faz                                                                    |
|----------------------|------------------------------------------------------------------------------|
| entradas             | uma ou mais imagens, ou pastas (lê jpg, png, webp, tif, bmp)                 |
| `--formato`          | `slide` (1080×1350, padrão) ou `spread` (2160×1350, medido em duas metades)  |
| `--bloco LxA`        | tamanho aproximado do bloco de texto (padrão `570x480`)                      |
| `--json`             | saída em JSON, para outras etapas usarem                                     |
| `--limite-movimento` | a partir de que variação o fundo conta como movimentado (padrão 40)          |

**Cor do texto:** o padrão é o creme `#F0EBDC` (constante `CREME` no início do script), a cor de texto sobre foto da primeira marca em que o processo rodou. Troque pela cor de texto sobre foto da sua marca antes de medir.

**Como mede**

- Recorta a foto como o slide recorta (preencher, centralizado). No spread, recorta 2160×1350 e mede cada metade.
- Aplica a camada Contraste (`#141414` a 10% em Linear Burn), que fica ligada nos slides.
- Em cada posição (sup-esq, sup-dir, inf-esq, inf-dir, centro), o bloco encosta na margem de 90 px. A área medida é o bloco + 40 px (20 de cada lado).
- Compara o creme com o **95º percentil** da luminância dessa área, pela fórmula de contraste do WCAG.
- "Variação" é o desvio-padrão do cinza na área (0–255). Acima do limite, o fundo conta como movimentado.

**Níveis** (decisões "Contraste antes de sombra" e "Regra não é filtro")

| nível     | quando                                          |
|-----------|-------------------------------------------------|
| `ok`      | ≥ 4,5:1 e fundo calmo                           |
| `revisar` | entre 3:1 e 4,5:1, ou fundo movimentado         |
| `abaixo`  | < 3:1 (inegociável: trocar canto, reenquadrar ou trocar a foto; Escurecer é o último recurso) |

**Ordem**

- Posições de cada foto: melhor nível primeiro, depois longe da emenda, depois maior razão. No spread, as posições do lado de dentro de cada metade levam a nota "junto da emenda".
- Fotos: pela melhor posição. No spread, vale a pior das duas metades, porque as duas costumam ter texto.

**O que ele não faz**

- **Não vê rostos nem a emenda.** Texto sobre rosto e corte seco na emenda continuam sendo checagem visual, no screenshot da mesa.
- Não sabe o sentido da foto: o sentido vem antes do contraste no B3.
- Não lê o enquadramento real do Figma: supõe recorte centralizado. Se a foto for reenquadrada, meça de novo o recorte.
- O limite de "movimentado" (40) ainda não foi calibrado com fotos reais.

Usa numpy se estiver instalado (resolução cheia); sem numpy, mede 1 a cada 2 pixels, com o mesmo resultado nos testes.

## `medir_coerencia.py` — mede a coerência de cor da foto com o projeto (B3)

Compara a cor e a luz de cada candidata com a **régua** do projeto (a assinatura de cor das fotos de referência) e diz, em palavras, onde ela se afasta. Serve para **ordenar** candidatas no critério "coerência com a direção fotográfica" do B3, principalmente as externas (Pexels, Freepik). Não elimina nada.

```bash
python scripts/medir_coerencia.py "<pasta de prévias>" --projeto marca-exemplo
python scripts/medir_coerencia.py foto1.jpg foto2.jpg --projeto outra-marca --json
python scripts/medir_coerencia.py "<pasta>" --projeto marca-exemplo --referencias "<outra pasta>"
```

| opção           | o que faz                                                                     |
|-----------------|-------------------------------------------------------------------------------|
| entradas        | uma ou mais imagens, ou pastas (lê jpg, png, webp, tif, bmp); podem ser prévias no scratchpad |
| `--projeto`     | slug do projeto (obrigatório)                                                 |
| `--referencias` | usa estas fotos ou pastas como régua, no lugar da direção e do catálogo (testes) |
| `--json`        | saída em JSON, para outras etapas                                             |
| `--cache`       | pasta do cache da régua (padrão: pasta temporária do sistema, `coerencia-carrosseis`) |
| `--sem-cache`   | recalcula a régua sem ler nem gravar cache                                    |

**De onde vem a régua**

1. A lista de fotos em `projetos/<slug>/direcao-fotografica.md`, se o arquivo existir. O script pega os caminhos de `midia/…` (ex.: `midia/restrita/marca-exemplo/foto/marca-exemplo_captacao-15-10-1555.jpg`) que estão numa seção cujo título tem "referência"; sem essa seção, pega todos os caminhos do arquivo. Caminho que não existe vira aviso.
2. Senão, as fotos do projeto no catálogo com `destaque = sim` e origem real (`decupagem:…` ou `legado:…`).

A régua fica em cache (leva alguns segundos para ~200 fotos num drive de rede) e é refeita sozinha se a lista ou os arquivos mudarem. Nada é gravado em `midia/`.

**O que mede** (em miniatura de 256 px, no espaço Lab)

| medida      | como                                   | palavras                                   |
|-------------|----------------------------------------|--------------------------------------------|
| temperatura | média de b* (+ amarelo, − azul)        | mais quente / mais fria que o projeto      |
| saturação   | croma médio                            | saturação acima / abaixo (mais lavada)     |
| brilho      | média de L*                            | mais clara / mais escura que o projeto     |
| contraste   | desvio-padrão de L*                    | contraste acima / abaixo (mais chapada)    |
| tom         | média de a* (+ rosado, − verde)        | tom puxado para o rosado / para o verde    |
| paleta      | distribuição de matiz das áreas com cor (8 faixas: vermelho/rosa, laranja/pele, amarelo, verde, ciano, azul, roxo, magenta) | paleta diferente (com as faixas que predominam) |

**Como compara**

- Para cada medida, a régua é a **mediana** das referências e a **variação normal** do projeto (desvio absoluto mediano × 1,4826, com um piso para um projeto muito homogêneo não exagerar diferenças pequenas).
- O desvio da candidata é medido nessa unidade: até 1 = **dentro**, de 1 a 2 = **um pouco** fora, acima de 2 = fora. Na paleta, só conta ser mais diferente do que as próprias referências costumam ser.
- **Distância** = média quadrática dos seis desvios (cada um limitado a 4). Até 1 = `coerente`, de 1 a 2 = `perto`, acima de 2 = `destoa`.
- Também diz de quantas fotos do próprio projeto a candidata está mais longe ("mais longe que 41% das fotos do projeto"), para calibrar.
- Ordem: menor distância primeiro.

**Testes (no processo original)**

- Variações de uma foto real contra a régua do próprio projeto: original 0,77 · mais saturada 0,83 · pouco mais fria 1,32 · mais escura 1,63 · preto e branco 1,63 · mais fria 2,09. As palavras batem com a alteração feita.
- Dois projetos, destaques divididos ao meio (metade vira régua, a outra metade é candidata): régua do projeto 1, mesmo projeto 0,94 × outro 1,71; régua do projeto 2, 1,00 × 1,21. Separa na média, mas há sobreposição quando os dois projetos têm luz quente e pele.
- Sem numpy, o resultado é o mesmo.

**O que ele não faz**

- **Não vê cenário, pessoas nem "cara de banco".** Pessoa brasileira e real, naturalidade, retoque, filtro e cena de banco continuam sendo checagem visual, contra a direção fotográfica.
- Não sabe o sentido da foto: o sentido vem antes da coerência no B3.
- Mede a foto inteira, não o recorte do slide. Marca-d'água da prévia (Freepik) entra na conta.
- A régua é tão boa quanto as referências. Quando as referências misturam luzes diferentes (ex.: quarto e sala), a variação de brilho fica larga, e "mais escura" só aparece em diferenças grandes. A lista curada em `direcao-fotografica.md` deve deixar a régua mais justa.
- As faixas (1 e 2) e os pisos ainda não foram calibrados com escolhas reais de quem revisa.

Usa numpy se estiver instalado; sem numpy, faz a mesma conta em Python puro (mais lento).

## `estruturar_pedido.py` — transforma o pedido na estrutura do carrossel (B2)

Lê o **pedido padrão** (`.md`, formato em `docs/fluxo-producao.md`) ou a **tarefa do Notion** (a tabela "Sequência / Texto da Arte" e as propriedades) e grava `projetos/<slug>/producao/<tema>.json`, no formato descrito abaixo (exemplo de entrada em `scripts/exemplos/`). O texto do cliente **não é reescrito**: o script só organiza, marca o destaque e resolve viúvas. O que pede decisão vira exceção com motivo.

**Pedido padrão:** é só passar o arquivo. O projeto sai do campo `projeto` (slug de `midia/projetos.csv`), e o tema, do campo `tema`.

```bash
python scripts/estruturar_pedido.py scripts/exemplos/pedido-padrao-exemplo.md --simular
```

**Tarefa do Notion · passo 1 — o Claude busca a tarefa (o script não fala com o Notion)**

1. Pelo MCP do Notion, **só leitura**: `notion-fetch` com a URL ou o ID da página da tarefa (base Tasks).
2. Salva a resposta num arquivo no scratchpad da sessão (ex.: `<scratchpad>/notion/TAREFA-101.md`). Serve qualquer um dos dois:
   - o JSON inteiro que o `notion-fetch` devolve (com o campo `text`);
   - só o texto da página, com os blocos `<properties>{…}</properties>` e `<content>…</content>`.
   O arquivo é temporário: o que importa dele (URL, ID, prazos, pasta) fica em `origem` no JSON gerado.

**Tarefa do Notion · passo 2 — roda o script**

```bash
python scripts/estruturar_pedido.py "<scratchpad>/notion/TAREFA-101.md" --simular
python scripts/estruturar_pedido.py "<scratchpad>/notion/TAREFA-101.md"
```

| opção            | o que faz                                                                    |
|------------------|------------------------------------------------------------------------------|
| `--tema`         | nome do arquivo sem `.json` (padrão: o campo `tema` do pedido padrão; senão, até 4 palavras fortes do título da capa) |
| `--saida`        | grava em outro caminho (útil para testes)                                    |
| `--sobrescrever` | permite substituir um JSON que já existe (sem ela, o script para)            |
| `--simular`      | mostra o JSON e o relatório, sem gravar                                      |

**Projeto:** no pedido padrão, o slug vem do campo `projeto`. Na tarefa do Notion, sai da relação `Project`, comparada com a coluna `notion_projeto` de `midia/projetos.csv`. Sem correspondência, o script **para** e avisa.

**ID do Notion:** o número da propriedade "ID" ganha o prefixo de `PREFIXO_ID` (no início do script; padrão `TAREFA`). Troque pelo prefixo da sua base.

**O que ele monta**

- **Papel:** 1º slide com texto = capa (`Social/Capa`, modelo A; B se tiver mais de uma linha), último = final (`Social/Final`), o resto = conteúdo (`Social/Conteúdo`). Linha `+++` e slides vazios são ignorados e anotados.
- **Título:** 1ª linha do slide. Destaque na última palavra, com `*asteriscos*` e a pontuação fora; a palavra vai também em `destaque`. Títulos não recebem U+00A0.
- **Corpo:** linha em branco separa parágrafos; quebra simples junta as linhas. Linhas com `•`, `-`, `*` ou `1.` viram lista (`marcador` Ponto ou Número). Linha em negrito vira `negrito`, no conteúdo e no final, mesmo quando o `<b>` do Notion abre numa linha e fecha em outra; ela sai do parágrafo.
- **Viúvas:** cada parágrafo, item, negrito e texto do final sai com as 3 últimas palavras unidas por U+00A0 (2 em textos de 4 palavras).
- **Spread:** um, no primeiro par de slides de conteúdo cujo spread seja **diferente** do último JSON do mesmo projeto em `producao/`. A posição do texto alterna (sup-esq, inf-dir, sup-dir, inf-esq) e é **provisória**: quem decide é a foto, no B3/B5.
- **Fotos:** `spreads[].fotos` sai vazio; o B3 preenche.

**Exceções que ele marca**

| nível         | quando                                                                        |
|---------------|-------------------------------------------------------------------------------|
| revisar à mão | lista de 1 item (vira parágrafo); lista fora de 3 a 5 itens; mais de uma lista |
| revisar à mão | 3 blocos de texto (o 3º vai para o negrito); mais que isso (nada é cortado)    |
| revisar à mão | frase em negrito do cliente antes de outro texto (o componente mostra o negrito no fim) |
| revisar à mão | slide sem título (1ª linha com mais de 80 caracteres); título com `:` no fim   |
| revisar à mão | frase que parece incompleta ("Uma das importantes"), palavra repetida, texto com `:` no fim sem nada depois |
| revisar à mão | texto colorido no Notion (anotação para o designer) e blocos com link: saem da arte e vão para `notas_producao` / `referencias` |
| revisar à mão | final só com uma frase longa; final sem título (vira modelo A)                 |
| recomendado   | título longo (capa > 54, conteúdo > 60, final > 35 caracteres); título com ponto final; destaque em palavra fraca; destaque repetido |
| recomendado   | mais de ~45 palavras no corpo; parágrafo sem pontuação final; Asset Type diferente de "Social Media Carousel" |

**O que ele não faz**

- Não escolhe fotos, não mede contraste, não sabe se o tema é médico (a revisão técnica do conteúdo e as exceções de foto entram no B3–B5).
- Não sabe que o título "cabe": as contagens de caracteres são aproximadas, sem medir a fonte.
- A detecção de frase incompleta é uma heurística estreita (padrão "Um/Uma dos/das" sem "mais", palavra repetida). Erros de digitação passam.
- Não altera nada no Notion.
