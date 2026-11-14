# Guia · como a IA cria o kit de um projeto novo (A1)

Passo a passo para o Claude montar o **kit de produção** de uma marca nova: a ficha (`projeto.md`), o design system no Figma e as regras de carrossel. Vale para qualquer marca e setor.

- **De onde vem:** este guia foi escrito depois de montar o kit de duas marcas reais. Os nomes, arquivos e estilos delas não estão aqui; ficou só a **estrutura** e os erros que a prática mostrou. Copie a estrutura, nunca o estilo de outra marca.
- **Onde fica no processo:** trilha A, etapa **A1 · Sistema e estilo** (`docs/how-it-works.md`). O kit é o que o B4 (montagem) consome depois.
- **Regras gerais** que valem aqui: `docs/decisoes.md` e `docs/aprendizados-carrossel.md`.

> ⚠️ **Gosto da marca não se supõe.** O que não estiver claro nas referências vira pergunta para você (passo 7). Monte com a melhor leitura, deixe marcado como provisório e pergunte.

---

## Ordem de trabalho

| passo | o quê | sai o quê |
|---|---|---|
| 1 | Ler e localizar as fontes | lista de referências e onde estão |
| 2 | Extrair a identidade | notas de cor, fonte, logo, tom, carrossel |
| 3 | Preencher a ficha | `projetos/<slug>/projeto.md` e `guias/` |
| 4 | Figma · Fundamentos | variáveis → estilos → logos |
| 5 | Figma · Social Media | capa → conteúdo (+ item de lista) → final → contraste |
| 6 | Conferir | checklist com screenshot e instância nova |
| 7 | Perguntar | lista de dúvidas de gosto para você |
| 8 | Registrar | decisões, diário, aprendizados |

**Prioridade quando há prazo:** Fundamentos → capa → conteúdo destravam a produção. Final, collab e documentação vêm depois.

---

## 1. O que ler primeiro e onde procurar

Leia nesta ordem, **só lendo**, sem alterar nada nas fontes:

1. **Repositório:** `CLAUDE.md`, `README.md`, `projetos/README.md`, `projetos/_modelo/`, a ficha e os aprendizados do projeto (mesmo vazios), `docs/aprendizados-carrossel.md`.
2. **Brandguide / manual de marca** (PDF, site, Figma do branding). Normalmente: guia, cores, tipografia, logos em SVG/PNG/PDF. Ler o texto e **renderizar as páginas** (PyMuPDF: `pymupdf.open(pdf)[i].get_pixmap(dpi=55)`); muitos guias têm regra só na imagem.
3. **Posts publicados:** a pasta onde ficam as entregas da marca (ex.: pastas `AAAAMM_Carousel_<tema>` com `01.png`…) ou o próprio Instagram. Monte uma **folha de contato** por carrossel (todos os slides lado a lado, numa imagem só) e olhe os mais recentes primeiro.
4. **Arquivo de produção no Figma** (onde os posts foram feitos), se houver. É a fonte mais precisa: fontes reais, tamanhos, degradês, efeitos, margens. Ler por script (`use_figma` só leitura) a árvore de camadas de 2 ou 3 carrosséis recentes: tipo, posição, tamanho, preenchimento, fonte de cada trecho de texto.
5. **Kit pronto**, se a marca já tiver (por exemplo, um plugin do Figma feito para ela): ler **também o código do plugin**, que guarda medidas que os documentos não dizem.
6. **Fotos:** `midia/catalogo.csv` filtrado pelo slug, e as fotos reais do banco. Monte **folhas de contato** (no scratchpad, nunca no repositório) com uma amostra dos destaques (`destaque = sim`) e com os posts publicados, e descreva o que vê: luz, cor, textura, profundidade, cenário, pessoas, pose, enquadramento. É a base da `direcao-fotografica.md` (passo 2).
7. **O que a equipe já registrou no Notion** sobre o cliente (briefings, reuniões, orientações de foto, feedbacks). Rode no **Notion AI** (ou na ferramenta onde a equipe guarda isso) o prompt abaixo e guarde a resposta em `projetos/<slug>/guias/perfil-notion.md`. Ele é a fonte do bloco "Perfil e imagem" da ficha.

   ```
   Procure em todo o workspace tudo o que existe sobre o cliente "<Nome>": páginas de cliente, projetos, briefings, reuniões, propostas, levantamentos de conteúdo, feedbacks e tarefas de Social Media. Monte um resumo usando só o que estiver escrito; onde não houver informação, escreva "não encontrado".
   Perfil: tipo; serviços; público; o que o Instagram precisa provar; tom de voz.
   Imagem: o que as fotos devem mostrar; o que nunca mostrar; cuidados com pessoas (pacientes, crianças, equipe, dados); fontes de foto citadas; feedbacks sobre fotos ou artes aprovadas ou recusadas.
   Fontes: o link de cada informação.
   ```

**Ordem de autoridade quando as fontes divergem**
- Para **estilo de post** (layout, tamanhos, cores aplicadas): **posts publicados e arquivo de produção** vencem o brandguide. Anote a diferença na ficha (seção "Divergências").
- Para **regras de marca** (logo, área de respiro, cores proibidas, tom): o brandguide vence.
- Se o brandguide pedir uma fonte que **não está disponível no Figma**, use a de rascunho que o próprio arquivo de produção usa, e anote. *(Num dos casos, as duas fontes do brandguide não existiam no Figma, e os posts usavam outras duas do Google Fonts.)*

> ⚠️ O formato oficial de todos os projetos é **1080 × 1440 (3:4)**. Monte os componentes nesse tamanho, mesmo que posts antigos da marca usem outro.

## 2. O que extrair

Monte uma nota (pode ser no próprio `projeto.md`) com:

- **Cores:** hex de cada cor, **onde** ela aparece nos posts (fundo, texto sobre foto, texto sobre claro, degradê, detalhe) e o que é proibido. Separe *primitivas* (a paleta) de *papéis* (texto sobre foto, fundo do painel…).
- **Fontes:** família e peso de cada papel (título da capa, título de conteúdo, palavra em destaque, texto, lista, assinatura), tamanho, entrelinha, espaçamento entre letras, caixa (alta ou normal). Ver se o título mistura duas fontes numa linha (destaque): se sim, a entrelinha tem que ser em **pixels** (passo 4).
- **Logos:** versões (completa, símbolo, logotipo, assinatura com frase), cores permitidas, tamanho mínimo, área de respiro, onde cada versão aparece no carrossel.
- **Elementos gráficos:** grafismos, marca d'água, halos, marcadores de lista, ruído/granulação, filtro de foto.
- **Tom de voz:** como fala e como não fala, com 3 frases reais dos posts.
- **Estrutura de carrossel:** número típico de slides, o que é capa, miolo e fechamento, se há slide só de assinatura, se há spreads, onde ficam os títulos, como o texto ganha contraste sobre a foto (sombra, degradê, véu, painel).
- **Medidas:** margens reais (posição x/y do texto nos posts), largura das caixas de texto, distância título → texto, entre parágrafos, entre itens de lista.
- **Fotografia:** luz, cor, tratamento (filtro), o que evitar. Vira a ficha `projetos/<slug>/direcao-fotografica.md` (modelo em `_modelo/`): a régua por aspecto, o que denuncia "cara de banco" neste projeto, "aceita com ajuste leve × não salva" e **10 a 20 fotos de referência** do banco (caminhos de `midia/…`, de preferência destaques reais), que o `scripts/medir_coerencia.py` usa como régua. Marque cada linha com a fonte ([brandguide], [Notion], [observado]); o que for só gosto vira pergunta (passo 7).

## 3. Como preencher a ficha

1. Copie o material de marca para `projetos/<slug>/guias/` **sem mexer no original** (o Git ignora essa pasta). Copie o brandguide, cores, tipografia e logos em SVG; não copie projetos de vídeo nem arquivos de conceito.
2. Preencha `projetos/<slug>/projeto.md` seguindo o `_modelo/`, na mesma ordem do modelo:
   - cabeçalho (slug, status, área, links, **Figma de design system e de produção**, fonte do resumo);
   - Sobre · Público · Temas · Tom de voz (com exemplos reais);
   - **Perfil e imagem:** tipo de projeto, o que o feed prova, o que a imagem mostra e nunca mostra, cuidados com pessoas e fonte de foto preferida, a partir do `guias/perfil-notion.md`. É a base do critério de sentido do B3;
   - Identidade visual: tabela de cores (nome, hex, uso), fontes (oficial × usada no Figma), logos, elementos, fotos;
   - Carrossel: formato, estrutura, modelos de capa e de conteúdo, tipografia (tabela de estilos), espaçamentos, viúvas, contraste, checklist;
   - **Divergências** entre brandguide e posts;
   - **Em aberto**: as perguntas do passo 7.
3. Público e tom deduzidos (e não escritos na marca) levam *(deduzido; confirmar)*.

## 4. Figma · Fundamentos

**Arquivo:** um arquivo `-<slug>` só de design system, com a página **Design System**. Dentro dela, dois quadros lado a lado:

```
Design System
├── Fundamentos — <Marca>        (x 0)
│   ├── Título
│   ├── Cores          (amostras + tabela de tokens de uso)
│   ├── Tipografia     (famílias, estilos, regra do destaque, regra das viúvas)
│   ├── Espaçamentos   (barras com valor, variável e uso)
│   └── Logos          (componentes com variantes de cor)
└── Social Media — <Marca>       (x 2400)
    ├── Título
    ├── 01 · Capas
    ├── 02 · Conteúdo
    ├── 03 · Final
    └── 04 · Contraste e legibilidade
```

Antes de criar: carregue as skills `figma-use` (e `figma-generate-library` para componentes), abra uma sessão (`create_session`) e **inspecione o arquivo** (páginas, variáveis, estilos existentes).

### 4.1 Variáveis (primeiro)

Três coleções, um modo cada:
- **Primitivas:** a paleta crua (`cor/…`; se a marca já tem nomes, use os da marca, ex. `neutral/paper`, `accent/bordo`). Sem escopo (não aparecem nos seletores).
- **Marca:** papéis, como **apelido** (alias) das primitivas: `texto/sobre-foto`, `texto/sobre-claro`, `fundo/…`, `logo/…`, `destaque/…`. Escopo explícito: `TEXT_FILL` para texto, `FRAME_FILL`/`SHAPE_FILL` para fundo.
- **Espaçamento:** margem e todo espaço que se repete (título → texto, entre parágrafos, entre itens, marcador → texto, padding de painel). Escopo `GAP` + `WIDTH_HEIGHT`. Descrição em cada uma.

> ⚠️ O Figma não tem "estilo de espaçamento": espaçamento é **variável**.
> ⚠️ Toda medida nova num componente nasce como variável. Larguras de caixa e medidas da documentação não precisam.

### 4.2 Estilos

- **Cor:** um estilo `Cor/<Nome>` por primitiva, **ligado à variável** (`setBoundVariableForPaint`, que devolve uma tinta nova: reatribuir).
- **Texto:** um estilo por papel, nomeado por slide (`Capa/Título`, `Capa/Destaque`, `Conteúdo/Título`, `Conteúdo/Destaque`, `Conteúdo/Texto`, `Final/…`). Descrição em todos.

> ⚠️ **Entrelinha em pixels** quando dois estilos dividem a linha (título + destaque): a mesma entrelinha fixa nos dois. Em porcentagem, a linha com o destaque fica mais aberta.
> ⚠️ Ajuste sempre o **estilo**, nunca o texto solto, e anote onde o design system se afasta do kit.
> ⚠️ Nomes de peso variam por família (`SemiBold` × `Semi Bold`): liste com `listAvailableFontsAsync()` antes de usar.

### 4.3 Logos

- Um **conjunto de componentes por versão** (`Logo/Símbolo`, `Logo/Logotipo`, `Logo/Assinatura`…), com a propriedade **Cor** como variante (as cores permitidas pela marca).
- Fonte: os **SVG oficiais** (`createNodeFromSvg`). Se a versão usada nos posts só existir no Figma de produção, exporte-a de lá em SVG (leitura) e recrie.
- Corte o quadro ao desenho (os SVGs costumam vir com prancheta enorme) e ligue a cor à variável `logo/…`.
- Cada logo aparece **uma vez** nos Fundamentos, dentro do quadro; nada solto na página.

Ao terminar os Fundamentos: **screenshot do quadro inteiro** e conferência (passo 6) antes de seguir.

## 5. Figma · Social Media

### 5.1 Regras de construção (valem para todo componente `Social/*`)

- **Um componente por tipo de slide.** O que muda o layout (posição, estilo) é **variante**; o que só aparece ou some (subtítulo, lista, halo, escurecer) é **liga/desliga** (decisão "Componentes de slide").
- Slide em **auto layout**, padding ligado à variável de margem; **fundo em posição absoluta** (foto, véus, degradês, contraste, marca d'água).
- Textos de **estilo único** (subtítulo, parágrafo, frase) ganham campo de texto no painel. O **título não**: ele mistura fontes (destaque) e o campo de texto apagaria a mistura.
- Camada de foto: retângulo chamado **"Foto (trocar imagem)"** com preenchimento provisório (degradê no tom da marca) ou uma foto real da marca.
- Nomes de variante iguais aos do JSON/automação, quando houver (`sup-esq`, `inf-dir`…).
- Quadro de documentação ao lado de cada seção: **propriedades**, **especificações por variante** e **regras**.

> ⚠️ **Opacidade de camada ligada a variável vai na camada, não na tinta**: a opacidade da tinta não passa para as instâncias.
> ⚠️ **Nada de vírgula dentro do valor de uma variante** ("F · Inferior direita, alinhada" quebra). A vírgula só separa propriedades.
> ⚠️ Depois de **clonar uma variante**, confira se as propriedades continuam ligadas.
> ⚠️ Em auto layout, defina o modo de altura **depois** de qualquer `resize()`.
> ⚠️ **Quadros com texto não recortam conteúdo** (`clipsContent = false`): o descendente do itálico (g, j, p, ç) passa da caixa. Só o slide recorta.
> ⚠️ O efeito de sombra/escurecer **pode atravessar** para o slide vizinho num spread; o que não pode é corte seco na emenda.

### 5.2 Capa · `Social/Capa`

1. Descubra a **lógica** das capas publicadas antes de criar variações: por exemplo, oposição de cantos (texto num canto, marca no oposto) ou estilos de fundo com texto centralizado.
2. Variante principal = essa lógica (ex.: Posição A–F, ou Estilo A–C).
3. Liga/desliga para os opcionais (subtítulo, marca d'água, halo, "arraste", escurecer).
4. Teste com **título de 4 linhas** numa instância nova: a margem não pode ser invadida.

### 5.3 Conteúdo · `Social/Conteúdo` e `Social/Item de lista`

1. Levante os **layouts reais** do miolo (onde fica o título, onde fica o texto, como ganham contraste) e transforme cada um numa variante.
2. Liga/desliga: Título, Parágrafo 1, Lista, Item 4, Item 5, Parágrafo 2, Frase de destaque, Escurecer, conforme a marca.
3. Lista com componente próprio (`Social/Item de lista`): marcador da marca + texto, gap por variável, marcador numérico com **largura fixa**. A lista nativa do Figma não deixa colorir o marcador nem usar as variáveis.
4. Textos padrão já com as **3 últimas palavras unidas por espaço não separável** (U+00A0), regra das viúvas.
5. Se a marca usa spread: exemplo de spread com foto contínua e o quadro "foto fixa, texto livre" (decisão "Spreads").

> ⚠️ **Exemplo vira molde.** Todo exemplo que mostra uma só possibilidade precisa de uma linha dizendo o que é fixo e o que é livre.

### 5.4 Final · `Social/Final`

- Variantes pelos modelos de fechamento publicados (painel, frase grande, slide só de assinatura…).
- **Collab:** só se fizer sentido para a marca. Padrão: a marca vira a versão reduzida e cede espaço a até 2 parceiras, por **troca de instância** com um componente `Social/Logo parceira (espaço)`.
- Elemento que aparece numa referência mas não no guia entra **opcional e desligado**, com pergunta registrada.

### 5.5 Contraste e legibilidade

Seção curta com a escada da decisão "Contraste antes de sombra" adaptada à marca: qual cor de texto sobre foto, qual recurso de contraste a marca usa (sombra, degradê, véu, painel) e a medida de referência (até que cinza o texto claro dá 4,5:1). E o quadro "Regra não é filtro".

## 6. O que conferir no fim

- [ ] **Screenshot** de cada quadro (Fundamentos, Capas, Conteúdo, Final) depois de criar. Defeitos de opacidade e corte só aparecem na imagem, não nos dados.
- [ ] **Instância nova** de cada componente, fora do componente principal, em cada variante. Trocar texto, ligar e desligar cada propriedade.
- [ ] Título de **4 linhas** e lista com item de **duas linhas** em instância nova: margem intacta, nada sobreposto.
- [ ] Descendentes do destaque (g, j, p, ç) inteiros no screenshot.
- [ ] **Auditoria por script:** todo padding e gap dos componentes ligado a variável; todo texto com estilo; toda cor ligada a variável ou estilo.
- [ ] Contraste do texto sobre o fundo provisório e sobre uma foto real medido (meta 4,5:1; mínimo 3:1).
- [ ] Logos: uma vez cada nos Fundamentos, cores certas, nada solto na página.
- [ ] Ficha (`projeto.md`) com o link do Figma, os estilos e as divergências.

## 7. O que perguntar a você (em vez de supor)

Pergunte, em uma lista só, o que for gosto e não estiver claro:

- divergências entre brandguide e posts (qual vale daqui para a frente);
- fonte oficial × fonte disponível no Figma;
- formato do post (4:5 × 3:4) quando os posts variam;
- elementos que aparecem em alguns posts e não em outros (halo, "arraste", selo, slide só de assinatura);
- se há spread, collab, CTA padrão;
- público e tom, quando deduzidos;
- cores que aparecem nos posts mas não no guia (ex.: um bordô mais escuro só nos degradês).

Monte com a melhor leitura e deixe a dúvida escrita na ficha ("Em aberto") e na documentação do Figma ("provisório").

## 8. Registrar

- Decisões de estrutura → `docs/decisoes.md` (entrada nova no fim).
- A etapa → `docs/diario.md` (número = último + 1, lido na hora).
- O que é da marca → `projetos/<slug>/aprendizados.md`; o que vale para qualquer projeto → `docs/aprendizados-carrossel.md`.
- Mudou o mapa do processo? Anote em "Pendente no visual" (`docs/how-it-works.md`).
- Problemas novos que a prática mostrar → corrigir **este guia**.

---

## Armadilhas já vistas, em uma linha cada

| armadilha | o que fazer |
|---|---|
| medida que só existe no código do plugin | ler o código também |
| logos soltos e repetidos | um de cada, dentro dos Fundamentos |
| cor ligada a variável perde a opacidade | reaplicar a opacidade; conferir por screenshot |
| ajuste no texto solto | ajustar o estilo e anotar a diferença do kit |
| variante clonada perde propriedade | religar e conferir |
| variação feita pela posição, sem a lógica | entender a lógica antes |
| vírgula em nome de variante; opacidade na tinta | parênteses; opacidade na camada; testar com instância nova |
| entrelinha desigual com destaque | entrelinha fixa em px nos dois estilos |
| item de lista sobreposto; números desalinhados | altura "abraçar" depois do resize; largura fixa no número |
| viúvas | espaço não separável nas 3 últimas palavras, na geração |
| sombra cortada na emenda | pode atravessar; não pode cortar |
| exemplo vira molde | escrever o que é fixo e o que é livre |
| "tem X em tudo" | levantar onde X aparece antes de mudar |
| espaço digitado à mão | auditar por script; criar variável |
| regra que trava | inegociável × recomendado × exceção registrada |
| elemento só da referência | opcional e desligado, com pergunta |
| logo de parceira colada | troca de instância |
| `imageHash` de outro arquivo fica vazio | exportar a imagem e enviar com `upload_assets` |
| descendente cortado por máscara | quadro de texto sem recorte |

### Armadilhas vistas no kit da segunda marca

| armadilha | o que fazer |
|---|---|
| **degradê ligado a variável perde a transparência**: o Figma aceita a variável no ponto do degradê, mas força o alfa para 100% | degradês com hex fixo; anotar na documentação qual variável cada um representa |
| efeito **Ruído** (`NOISE`) recusa a chave `blendMode` | criar o efeito sem `blendMode` |
| ruído no **quadro inteiro** gera moiré nas miniaturas | pôr o ruído numa camada de fundo (retângulo) e conferir o screenshot em tamanho real |
| efeito **Vidro** (`GLASS`) "some" sobre fundo liso | é normal: ele refrata o que está atrás; conferir sobre foto ou degradê |
| elemento que só existe no Figma de produção (assinatura vetorizada, halo, marcador) | ler e exportar de lá (`exportAsync({format:'SVG_STRING'})`, só leitura) e recriar com `createNodeFromSvg`; camada sem preenchimento (vidro) exporta vazia: copiar os `vectorPaths` |
| SVG oficial com prancheta enorme | recortar o componente aos limites dos vetores e só então reescalar |
| mudar `visible` de uma camada ligada a propriedade muda o **padrão da propriedade** para todas as variantes | ajustar o padrão com `editComponentProperty` e não esconder camada ligada |
| componente de 3 variantes (3 × 1080) mais largo que o quadro de 2240 px | variantes em grade de 2 colunas; exemplos em instância reduzida (66%) |
| trocar o texto de um título com duas fontes deixa tudo num estilo só | documentar na regra da capa: reaplicar os estilos depois de trocar o texto |
| foto real nos exemplos: `upload_assets` só aceita id de nó simples (não camada de instância) | subir em retângulos temporários, copiar o `imageHash` para a camada "Foto" da instância e apagar os temporários |
| três palavras unidas não cabem em coluna estreita | na coluna estreita, unir 2 palavras (ver `docs/aprendizados-carrossel.md`) |
| a auditoria achou espaços digitados à mão (rodapé da capa, collab) | criar a variável e ligar; rodar a auditoria de novo |
