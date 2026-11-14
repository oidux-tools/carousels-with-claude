# Banco de mídia

Lugar único para todo o material bruto usado nos conteúdos: fotos, vídeos, ícones, logos, trilhas…

## Princípio

- **O primeiro nível de pasta é a fronteira de acesso:** `aberta/` (equipe toda) ou `restrita/<projeto>/` (só quem cuida daquele projeto).
- **Na área aberta, cada arquivo mora na pasta do seu tipo** e a ligação com projetos é metadado (nome do arquivo + catálogo): uma foto que serve a três projetos continua sendo um arquivo só.
- **Na área restrita, o projeto é pasta**, porque o conteúdo pertence a um único cliente.
- **Catálogo, log de usos e projetos são únicos** para as duas áreas, na raiz de `midia/`.

## Estrutura

```
midia/
├── _entrada/              caixa de entrada: o que chegou e ainda não foi tratado
├── aberta/                equipe toda
│   ├── foto/ ilustracao/ icone/ logo/ fundo/ video/ audio/
├── restrita/              acesso limitado, uma pasta por projeto
│   └── <projeto>/
│       ├── _chave.json    código → nome (só quem tem acesso à área vê)
│       └── foto/ video/ …
├── catalogo.csv    o que cada arquivo é: uma linha por arquivo, das duas áreas
├── usos.csv        o que aconteceu com ele: uma linha por uso em peça entregue
└── projetos.csv    lista dos projetos válidos (slugs)
```

Três peças, cada uma com um papel:

| peça | responde | muda quando |
|---|---|---|
| pastas (área e tipo) | onde está o arquivo e quem pode abrir | entra mídia nova |
| `catalogo.csv` | o que a imagem é (dimensões, descrição, origem, licença) | entra mídia nova ou alguém completa a descrição |
| `usos.csv` | onde, quando e em que tema ela foi usada | uma peça é entregue |

## Tipos

| tipo         | o que entra                                    | formatos comuns  | mínimo recomendado                  |
|--------------|------------------------------------------------|------------------|-------------------------------------|
| `foto`       | fotografias: banco, ensaios, produto, pessoas  | jpg, png, webp   | lado menor ≥ 1080 px                |
| `ilustracao` | ilustrações, grafismos, elementos decorativos  | svg, png         | vetor (svg) sempre que possível     |
| `icone`      | ícones isolados                                | svg, png         | vetor (svg)                         |
| `logo`       | logos de clientes, parceiros e marcas citadas  | svg, png, pdf    | vetor; png com fundo transparente   |
| `fundo`      | fundos, texturas, padrões                      | jpg, png         | ≥ 1080 × 1350 px                    |
| `video`      | clipes, b-roll, gravações                      | mp4, mov         | 1080p, mp4 (H.264)                  |
| `audio`      | trilhas, efeitos, locuções                     | mp3, wav         | wav ou mp3 ≥ 192 kbps               |

Precisa de um tipo novo? Cria a pasta, adiciona aqui na tabela e registra em `docs/decisoes.md`.

## Nome do arquivo

```
<projeto>_<descricao>_<nn>.<ext>
```

- **projeto**: um slug de `projetos.csv`. Use `geral` quando servir a qualquer projeto.
- **descricao**: 2 a 5 palavras que descrevem o conteúdo, separadas por hífen.
- **nn**: sequência de 2 dígitos, só quando houver variações do mesmo assunto.
- Tudo minúsculo, sem acento, sem espaço. `_` separa campos, `-` separa palavras.

Exemplos:

```
aberta/foto/marca-exemplo_equipe-reuniao-escritorio_01.jpg
aberta/foto/marca-exemplo_equipe-reuniao-escritorio_02.jpg
aberta/logo/outra-marca_horizontal-branco.svg
aberta/video/geral_cidade-timelapse-noite.mp4
restrita/marca-exemplo/foto/marca-exemplo_rk7m2qx-014.jpg
```

**Na área restrita**, a descrição dá lugar a um **código neutro**: `r` + 6 caracteres aleatórios (minúsculas e números, sem 0/o, 1/l/i), estável por pessoa ou grupo. O código não diz nada do setor nem de quem é; a tradução fica em `restrita/<projeto>/_chave.json`, que só quem tem acesso à área consegue abrir e que nunca vai para o Git. O importador gera o código e a chave (`--area restrita`).

## Catálogo (`catalogo.csv`)

Uma linha por arquivo. CSV em UTF-8, separado por vírgula. Campos com vários valores usam `|` (ex.: `marca-exemplo|outra-marca`).

| coluna          | preenchimento | exemplo                            |
|-----------------|---------------|------------------------------------|
| `arquivo`       | auto          | `aberta/foto/marca-exemplo_equipe-reuniao_01.jpg` (caminho dentro de `midia/`; é a chave) |
| `area`          | auto (pasta)  | `aberta` ou `restrita:marca-exemplo` |
| `tipo`          | auto (pasta)  | `foto`                             |
| `formato`       | auto (extensão) | `jpg`                            |
| `largura`       | auto          | `1080` (px)                        |
| `altura`        | auto          | `1350` (px)                        |
| `proporcao`     | auto          | `4:5`                              |
| `duracao_s`     | auto          | `12.5` (só vídeo e áudio)          |
| `tamanho_mb`    | auto          | `2.4`                              |
| `projetos`      | auto pelo nome + manual | `marca-exemplo\|outra-marca`      |
| `tags`          | manual        | `pessoas\|escritorio\|azul`        |
| `origem`        | manual (ou pelo importador) | `decupagem:202611_ensaio`, `banco:freepik`, `legado:figma` (ver abaixo) |
| `adicionado_em` | auto          | `2026-11-14`                       |
| `usos`          | auto (do log) | `3`: linhas em `usos.csv` para este arquivo |
| `ultimo_uso`    | auto (do log) | `2026-11-16`: a data mais recente no log |

"auto" = o indexador preenche lendo o próprio arquivo ou o log (`python scripts/indexar_midia.py`, detalhes em [`scripts/README.md`](../scripts/README.md)). "manual" = só uma pessoa sabe; o indexador nunca sobrescreve o que foi preenchido à mão. **`usos` e `ultimo_uso` nunca se digitam:** são recalculados a cada rodada a partir de `usos.csv`, e qualquer valor escrito à mão é substituído.

## Origem

De onde a imagem veio. Um valor por arquivo, no formato `tipo:detalhe`:

| origem | quando usar |
|---|---|
| `decupagem:<lote>` | material real do cliente, vindo de uma decupagem (ex.: `decupagem:202611_ensaio`) |
| `banco:freepik`, `banco:pexels`, `banco:adobe-stock`… | banco de imagens externo; a foto só é baixada quando é escolhida para uma peça |
| `legado:figma` | imagens que um projeto já usava antes do banco (ex.: as fotos de uma página de fotos no Figma de produção e os originais no Drive), já importadas para `aberta/foto/` |
| `propria` | produzida pela sua equipe |
| `ia` | gerada por IA |

Para imagens de banco externo, vale preencher também as colunas `licenca`, `autor` e `link_original` (colunas extras são preservadas pelo indexador).

## Log de uso (`usos.csv`)

Uma linha **por imagem, por peça entregue**. Uma alternativa sugerida e não usada não entra; uma peça recusada também não. Quem registra é a etapa B7 (entrega), junto com a confirmação humana.

| coluna | exemplo | observação |
|---|---|---|
| `data` | `2026-11-16` | dia da entrega (`AAAA-MM-DD`) |
| `arquivo` | `aberta/foto/marca-exemplo_consulta-01.jpg` | caminho dentro de `midia/`, igual ao catálogo |
| `projeto` | `marca-exemplo` | slug de `projetos.csv` |
| `peca` | `rotina-de-cuidados` | nome da mesa ou peça |
| `tarefa_notion` | `TAREFA-101` | ID da tarefa no Notion, se houver |
| `slide` | `04` ou `02-03` | slide ou spread onde a imagem entrou |
| `tema` | `rotina de cuidados` | assunto da peça, em texto livre |

O log só cresce: uma linha registrada não é apagada nem editada. Se algo foi registrado errado, corrige-se na hora e explica-se no diário. O indexador lê o log, conta os usos e avisa quando uma linha aponta para um arquivo que não está no catálogo.

## Fluxo de entrada

1. Joga o material novo em `_entrada/`.
2. Renomeia seguindo a convenção acima.
3. Move para `aberta/<tipo>/` (ou `restrita/<projeto>/<tipo>/`, se for sensível).
4. Roda o indexador (`python scripts/indexar_midia.py`) e corrige os avisos que ele mostrar.
5. No catálogo, completa `tags` e `origem`, e `projetos` se o arquivo servir a mais de um projeto.

`_entrada/` é passagem, não depósito: o ideal é ela ficar vazia ao fim de cada sessão de triagem.

## Como achar as coisas

- **Por projeto**: filtre `projetos` contendo o slug, ou procure arquivos que começam com `<projeto>_`.
- **Por área**: filtre `area` (`aberta` ou `restrita:<projeto>`).
- **Por formato de post**: filtre `proporcao` (`4:5` carrossel/feed, `9:16` stories/reels, `1:1` quadrado).
- **Por assunto**: filtre `tags` ou busque pela descrição no nome.
- **Pouco usadas**: ordene por `usos` (menor primeiro) e `ultimo_uso` (mais antigo primeiro). Para ver onde uma imagem já apareceu, filtre `usos.csv` pelo `arquivo`.
- Para filtrar com conforto, abra `catalogo.csv` no Google Sheets ou no Excel (Dados → De Texto/CSV).
