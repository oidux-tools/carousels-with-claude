# Registro de decisões

Uma entrada por decisão de estrutura ou processo: o que foi decidido e por quê. Entradas novas vão no fim.

As decisões abaixo vêm do processo original e explicam o porquê de cada regra. Quando você decidir algo diferente no seu projeto, acrescente uma entrada nova no fim dizendo o que mudou.

---

## Banco de mídia organizado por tipo; projeto é metadado

- **Decisão:** na área aberta de `midia/`, cada arquivo mora na pasta do seu tipo (foto, video, logo…). O projeto vai no nome do arquivo e na coluna `projetos` do catálogo.
- **Por quê:** a mesma mídia pode servir a vários projetos. Pastas por projeto obrigariam a duplicar arquivos e perder o controle de qual é a versão certa.

## Catálogo de mídia em CSV

- **Decisão:** `midia/catalogo.csv`, uma linha por arquivo, com colunas técnicas (preenchidas automaticamente) e colunas de contexto (projetos, tags, origem).
- **Por quê:** abre em qualquer lugar (Sheets, Excel, script), versiona bem no Git e não prende a nenhuma ferramenta.

## Mídia fora do Git

- **Decisão:** o Git versiona estrutura, documentação, catálogos e scripts. Arquivos de mídia são ignorados.
- **Por quê:** arquivos pesados incham o repositório; o Drive (ou outro armazenamento) faz backup e sincronização deles.

## Indexador do catálogo em Python, só com Pillow

- **Decisão:** `scripts/indexar_midia.py` preenche as colunas técnicas do catálogo. Depende só do Pillow; vídeo (mp4/mov), wav e mp3 são lidos direto pelo script, sem instalar ffmpeg.
- **Por quê:** é a menor instalação que cobre todos os formatos comuns do banco.
- **Regras:** o script nunca sobrescreve colunas manuais e nunca apaga linhas sozinho (só com `--limpar`), para não perder tags quando um arquivo é renomeado.

## Projetos em três camadas: guias, ficha e kit

- **Decisão:** cada projeto tem `projetos/<slug>/` com `guias/` (material original), `projeto.md` (resumo prático em texto) e `kit/` (arquivos de produção). O slug é o mesmo de `midia/projetos.csv`.
- **Por quê:** os guias costumam ser PDFs longos. Um resumo em texto deixa as regras (cores, fontes, tom) à mão para pessoas e automações, sem perder o original como referência.
- **Guias e kits ficam fora do Git**, como a mídia; só os `.md` são versionados.

## Componentes de slide no Figma: variante para posição, liga/desliga para elementos opcionais, auto layout

- **Decisão:** cada tipo de slide é **um componente só**. O que muda o layout (a posição) vira **variante**; o que só aparece ou some (subtítulo, marca d'água) vira **propriedade liga/desliga**. O slide usa auto layout com padding ligado à variável de margem, e o fundo (foto, contraste, marca d'água) fica em posição absoluta.
- **Por quê:** evita multiplicar variantes (6 posições × 2 tipos de título seriam 12) e garante a margem quando o texto cresce.
- **Regras:**
  - O título **não** ganha campo de texto no painel, porque perderia a palavra em destaque (que usa outra fonte). Elementos de estilo único (subtítulo) ganham.
  - Opacidade de camada ligada a variável vai na **camada**, não na tinta: a opacidade da tinta não passa para as instâncias.

## Viúvas: proibidas em textos e listas, resolvidas com espaço não separável

- **Decisão:**
  - Em textos corridos e itens de lista, a última linha precisa ter pelo menos 3 palavras. Em títulos, viúva é tolerada, mas evitada.
  - Toda automação que gerar texto (scripts, Claude) une as 3 últimas palavras de cada parágrafo e item com espaço não separável (U+00A0). Em parágrafos de 4 palavras, une só as 2 últimas.
- **Por quê:** o Figma não tem controle nativo de viúvas nem "balancear texto". Unir as últimas palavras é a solução que funciona em qualquer ferramenta e não depende de quem diagrama.

## Collab: versão reduzida da marca + até 2 parceiras no rodapé do final

- **Decisão:** em collab com outras marcas, o slide final troca a assinatura completa pela **versão reduzida** da marca (monograma ou símbolo) e abre espaço para até **2 logos parceiras** (3 marcas no total), na mesma linha. No Figma, isso é uma variante de assinatura do `Social/Final`, com troca de instância para as logos.
- **Por quê:** a assinatura completa ocupa a largura do painel. Com a versão reduzida, a marca continua presente e as parceiras ganham espaço igual.
- **Selo do final:** opcional, desligado por padrão.

## Regra não é filtro: três níveis e exceção registrada

- **Decisão:** toda regra de produção se encaixa num destes níveis:
  - **Inegociável:** nunca quebra. Texto sobre rosto, contraste abaixo de 3:1, corte seco na emenda do spread, viúva em texto ou lista.
  - **Recomendado:** busca-se sempre, mas pode ceder com motivo. 4,5:1 sem sombra, canto com espaço livre, fundo calmo, foto pouco usada.
  - **Exceção registrada:** quando nada atende ao recomendado, usa-se a melhor opção disponível, o slide é marcado como "revisar à mão" e o motivo é escrito. Uma pessoa decide se aceita, ajusta ou troca.
- **Por quê:** regras duras demais deixam poucas fotos "permitidas", e o feed fica repetitivo. Uma exceção bem feita e visível é melhor do que travar ou repetir.
- **Na automação:**
  - Os scripts **ordenam** as opções, não eliminam.
  - A automação devolve o resultado com a marcação de revisão e o motivo, em vez de falhar.
  - Só o nível inegociável bloqueia.

## Contraste antes de sombra

- **Decisão:** a legibilidade vem da escolha da foto e da posição do texto. A sombra (Escurecer) é o último recurso, desligada por padrão em capas e conteúdo.
- **Ordem:**
  1. Canto livre e escuro.
  2. Medir: a cor do texto × a parte mais clara atrás do texto (bloco + 40 px), meta de 4,5:1.
  3. Entre 3:1 e 4,5:1, ou com fundo movimentado: trocar o canto ou reenquadrar.
  4. Escurecer. Abaixo de 3:1, trocar a foto.
- **Por quê:** a sombra deixa o post mais pesado e repetitivo. Uma foto bem escolhida dispensa a sombra.
- **Medida:** o critério é objetivo (razão de contraste WCAG), então pode ser automatizado lendo a foto. A meta de 4,5:1 fica acima do mínimo para texto grande (3:1) porque o post é lido no celular.

## Spreads: pelo menos um por carrossel, em posição variável

- **Decisão:**
  - Todo carrossel tem pelo menos um spread (foto horizontal em dois slides seguidos). A posição varia de um carrossel para o outro.
  - Ao montar um carrossel, consultar o anterior do mesmo projeto e escolher outra posição de spread e de texto.
  - Os slides fora de spread usam a própria foto.
- **Por quê:** dá ritmo ao carrossel e variedade ao feed.
- **Consequência:** para variar em relação ao anterior, a automação precisa saber como foi o último carrossel. O script do B2 compara com o último JSON do projeto.
- **O que o spread fixa e o que deixa livre:**
  - **Fixo:** a foto é uma só e corre contínua pelos dois slides, sem corte na emenda, inclusive a sombra.
  - **Livre:** o texto de cada metade. O formato (parágrafos, lista com pontos ou números, só título, só frase em negrito) sai do conteúdo, e a posição sai do espaço livre da foto.
- **Para a automação:**
  - A instrução do gerador deve dizer explicitamente que cada metade escolhe seu formato.
  - Dar a ela vários exemplos diferentes, porque um exemplo só vira molde.

## Decupagem fora, importação dentro

- **Decisão:** a decupagem (organizar, renomear e catalogar material bruto) é um processo à parte, usado em qualquer projeto. Este repositório só **importa** o resultado dela, com `scripts/importar_decupagem.py`.
- **Na importação:**
  - Os originais ficam intocados na decupagem; o banco recebe cópias otimizadas (lado maior 2400 px, JPEG 85, só autor e copyright nos metadados).
  - O nome segue `<projeto>_<grupo>-<NNN>`: o grupo é o nome da pasta, e o número é o mesmo da decupagem, então o original é fácil de achar.
  - As colunas da decupagem vêm para o catálogo, menos as que só descrevem a pasta de origem. Elas são atualizadas a cada reimportação; as colunas manuais do banco nunca.
  - **Sem camada obrigatória de autorização:** a autorização de uso é pedida antes da decupagem, então o que chega já está liberado.
- **Por quê:** a decupagem é genérica e serve a qualquer projeto; o banco só precisa receber o material no formato dele. Uma checagem repetida aqui só atrasaria o fluxo.

## Catálogo separado de onde o arquivo mora

- **Decisão:** os arquivos ficam em `midia/`. A coluna `arquivo` do catálogo é um caminho **relativo** ao banco (`aberta/foto/marca-exemplo_ensaio-003.jpg`), nunca um caminho do computador.
- **Por quê:** o volume de mídia tende a crescer muito; separar "o que existe" (catálogo) de "onde está" (armazenamento) permite trocar o armazenamento sem refazer nada. Muda só o endereço-base de onde a automação puxa e para onde devolve o arquivo.

## Demanda do Notion → projeto daqui pelo projeto do Notion

- **Decisão:** cada projeto daqui guarda o ID do seu projeto no Notion (coluna `notion_projeto` em `midia/projetos.csv`). Ao ler uma tarefa da base **Tasks**, a automação segue a relação `Project` e acha o slug por esse ID.
- **Por quê:**
  - O **cliente** do Notion não serve: um mesmo cliente pode ter mais de uma marca.
  - O **Asset Type** não é confiável: carrosséis podem estar marcados com outro tipo.
  - Só o projeto identifica a marca com segurança.
- **Regra:** tarefa de projeto sem slug cadastrado não entra na automação; ela é avisada ("projeto do Notion sem correspondência").

## Toda mesa registra o próprio tempo

- **Decisão:** cada mesa tem uma linha em `projetos/<slug>/producao/tempos.csv`, com seis marcos: demanda criada, início do preparo, mesa pronta, início da revisão, fim da revisão e entrega. O mesmo vale como um cartão na própria mesa do Figma.
- **Por quê:** separar o tempo da máquina (preparo) do tempo humano (revisão) e do tempo parado (espera, fila). Só assim dá para saber onde a automação realmente ganha tempo.
- **Regra:** só se registra horário real. Marco não registrado fica em branco; nada de estimativa. Num piloto, uma divisão estimada somou 50 min, quando o real foi 13.

## Mesa de revisão: versões, tarja de decisão e feedback que vira critério

- **Decisão:**
  - A mesa no Figma é versionada (v1, v2…). A versão atual fica no topo; as anteriores ficam embaixo, marcadas como substituídas.
  - Cada slide tem uma **tarja**: salmão quando pede decisão humana, branca quando não há nada pendente. Fotos alternativas e motivos ficam como apoio, em uma linha.
  - **Layout em três faixas alinhadas:** em cima o carrossel inteiro, em ordem e lado a lado (pronto para ajustar as fotos direto nos slides); embaixo de cada slide, os comentários; por último, as fotos sugeridas.
  - Todo feedback de revisão é registrado como critério antes de refazer: o que é da marca vai para `projetos/<slug>/aprendizados.md`; o que é geral vai para `docs/aprendizados-carrossel.md`.
  - Na escolha da foto, o **sentido** vem antes do contraste.
- **Por quê:** quem revisa olha, não lê. E o mesmo erro não pode voltar no próximo carrossel.

## Imagens: repositório, catálogo e log de uso separados

- **Decisão:** três peças, cada uma com um papel.
  - **pastas de `midia/`:** onde o arquivo mora. Toda imagem usada numa peça fica aqui, venha de onde vier.
  - **`midia/catalogo.csv`:** o que a imagem é (dimensões, descrição, origem, licença). Uma linha por arquivo.
  - **`midia/usos.csv`:** o que aconteceu com ela. Uma linha por imagem, por peça **entregue** (data, arquivo, projeto, peça, tarefa do Notion, slide, tema). Alternativa sugerida e não usada não entra.
- **Origem padronizada:** `decupagem:<lote>`, `banco:freepik` / `banco:pexels` / `banco:adobe-stock`…, `legado:figma`, `propria`, `ia`.
- **`usos` e `ultimo_uso`** no catálogo são calculados pelo indexador a partir do log, nunca digitados.
- **Fonte externa ou legado:** a foto é baixada quando escolhida e entra no `midia/` com a origem marcada.
- **Por quê:** um contador digitado no catálogo fica desatualizado e não diz onde a imagem foi usada. O log registra o fato uma vez, e a contagem sai dele. O B3 passa a preferir fotos pouco usadas e não usadas recentemente no mesmo projeto.

## Banco em duas áreas: aberta e restrita, com chave de códigos

- **Decisão:** `midia/` tem duas áreas:
  - `midia/aberta/<tipo>/`: equipe toda, organizada por tipo;
  - `midia/restrita/<projeto>/<tipo>/`: acesso limitado por projeto.

  `catalogo.csv`, `usos.csv` e `projetos.csv` são **únicos**, na raiz de `midia/`, com uma coluna `area` (`aberta` ou `restrita:<slug>`).
- **Regra do primeiro nível:** a pasta de cima é sempre a fronteira de acesso. Na aberta, o projeto é metadado (uma foto pode servir a vários projetos); na restrita, o projeto é pasta (o conteúdo pertence a um único cliente).
- **Códigos na área restrita:**
  - o grupo (pessoa, assunto) vira um código neutro e aleatório: `r` + 6 caracteres de minúsculas e números, sem os ambíguos (0/o, 1/l/i). Ex.: `marca-exemplo_rk7m2qx-014.jpg`;
  - é estável, sem repetição, e não diz nada do setor;
  - a tradução código → nome fica em `midia/restrita/<projeto>/_chave.json`, visível só para quem tem acesso à área;
  - o catálogo, que todos veem, só mostra o código.
- **Por quê:** a foto protegida pela pasta não basta se o catálogo contar de quem ela é. O código mantém o catálogo único e legível sem identificar ninguém.
- **Atenção:**
  - a restrição depende de o seu armazenamento permitir **pasta com acesso limitado** (no Google Drive, uma pasta com acesso restrito dentro de um drive compartilhado). Teste antes de colocar material sensível;
  - não é criptografia: a proteção vem da permissão da pasta onde fica a chave.

## Legado: original antes do Figma; colunas extras no catálogo

- **Decisão:** ao trazer foto do legado (imagens que o projeto já usava antes do banco), a fonte é o **original no Drive** quando ele existe. O Figma só entra para o que não está no Drive. A origem continua `legado:figma`, e o caminho real fica numa coluna `fonte_legado`.
- **Por quê:** o Figma guarda no máximo 4096 px e às vezes só uma miniatura. Os originais costumam ser bem maiores.
- **Formato:** JPEG é copiado sem recompressão. PNG sem transparência vira JPG com qualidade 95 e o mesmo perfil de cor. PNG só fica PNG quando há transparência real.
- **Colunas extras** (preservadas pelo indexador): `arquivo_original`, `descricao`, `temas`, `tom`, `espaco_livre`, `orientacao`, `usos_legado`, `fonte_legado`.
  - "Formato" (horizontal/vertical/quadrada) vira `orientacao`, porque `formato` já é a extensão.
  - Um "usos" antigo vira `usos_legado`, porque `usos` vem do log.
- **Escopo:** entra só o que tem descrição. Imagem sem descrição fica fora até ser descrita.
- **Spread no log:** uma foto que ocupa um spread é uma linha só, com slide `02-03`, e não uma por slide.

## Versão visual do processo, atualizada em lote

- **Decisão:** o processo tem uma versão visual em `docs/fluxo.html`. Desenha as trilhas A e B e as conexões entre elas, e cada etapa abre o detalhe ao clicar (entra, sai, ferramenta, deu certo se, como funciona por dentro, estado).
- **Fonte:** os textos (`how-it-works.md` e `fluxo-producao.md`) continuam sendo a fonte. A página só desenha o que eles dizem e, se divergir, os textos valem.
- **Atualização em lote:** o visual não é refeito a cada mudança. Quem mudar o processo anota a mudança em "Pendente no visual", no fim do `how-it-works.md`. Com pendências, o Claude pergunta se já atualiza ou se espera acumular mais.
- **Lugar:** `docs/`, junto dos textos que ele desenha. Arquivo único, sem dependências: abre direto no navegador.
- **Por quê:** o mapa em texto é difícil de enxergar como fluxo. Atualizar o visual a cada detalhe daria retrabalho, e esquecer de atualizar deixaria o visual mentindo; a lista de pendências resolve as duas coisas.

## Estruturação do pedido (B2) em script; o Notion fica com o Claude

- **Decisão:** `scripts/estruturar_pedido.py` transforma a tarefa do Notion no JSON da estrutura. Quem lê o Notion é o Claude, pelo MCP e só leitura; ele salva a resposta do `notion-fetch` num arquivo temporário e o script lê esse arquivo.
- **Por quê:** o script fica sem credencial e sem dependência de API, e pode ser testado com arquivos salvos. O que importa da tarefa fica em `origem` no JSON, então o arquivo exportado não precisa ser guardado.
- **Regras escolhidas** (detalhe em `docs/fluxo-producao.md`):
  - quebra simples junta linhas no mesmo parágrafo; linha em branco separa;
  - texto colorido e blocos com link são anotação/referência para o designer: saem da arte e viram "revisar à mão";
  - o script nunca inventa título: 1ª linha longa demais vira "slide sem título";
  - viúvas: em textos de 4 palavras une 2, como diz a decisão das viúvas;
  - um spread só, no primeiro par de conteúdo diferente do último JSON do projeto; posição do texto provisória, decidida pela foto no B3/B5;
  - nunca sobrescreve um JSON existente sem `--sobrescrever`; projeto sem slug em `midia/projetos.csv` para tudo.

## Área restrita: código só quando a pasta é uma pessoa

- **Decisão:** na área restrita, o importador troca o nome da pasta por código (`r` + 6 caracteres) **quando a pasta identifica uma pessoa** (ex.: uma paciente). Quando a pasta é outra coisa (data de captação, evento, ambiente), usa `--sem-codigo` e mantém o nome (ex.: `marca-exemplo_captacao-15-10.jpg`).
- **Por quê:** o código existe para esconder **quem**. Trocar uma data por código só tira informação útil e ainda apagaria palavras comuns das descrições.
- **Atenção:** nomes de profissionais do cliente podem aparecer nas descrições; são pessoas públicas do projeto, não pacientes.

## Fotos externas no B3 (Pexels e Freepik) e direção fotográfica

**Contexto.** O banco próprio não cobre todos os temas. A busca externa usa Pexels e Freepik.

**Decisões**

1. **Fontes externas, nesta ordem, depois do banco próprio:**
   - **Pexels** (gratuito): busca manual pelo navegador do app. No máximo 2 ou 3 buscas por slide.
   - **Freepik pelo conector Magnific** (servidor oficial, com o login da sua conta): só quando o Pexels não resolve. Ferramentas: `stock_search`, `stock_get`, `stock_show`, `stock_download`, `account_balance`.
   - Script direto na API: adiado. Adobe Stock: fora por enquanto.
2. **Sem chaves:** o conector usa o seu login; o Claude nunca vê credencial. O conector só aparece em sessões abertas depois do login (às vezes é preciso reiniciar o app).
3. **Custo no Freepik:**
   - busca e detalhes: 0 crédito;
   - download: custa créditos, conforme o campo `creditCost` (a foto premium custa mais que a gratuita);
   - confira o saldo com `account_balance` antes de baixar.
4. **Download só depois da aprovação na mesa.**
   - Buscar e ver prévia é gratuito; o Claude faz sem perguntar.
   - O download, de qualquer fonte, só acontece depois que você aprova a foto no B6, e só da foto aprovada. Nunca em lote.
   - Em empate de qualidade, prefere a opção gratuita.
   - Geração, upscale, edição e vídeo no Magnific: sempre com aprovação.
5. **Como entra no B3:**
   - ordem das fontes: banco próprio → Pexels → Freepik, quando o slide fica com menos de 2 opções boas;
   - busca em inglês, orientação retrato, sem IA (filtro do Freepik);
   - ordem dos critérios: sentido → inegociáveis → coerência com a direção fotográfica → contraste → formato e usos;
   - o recorte do slide é conferido, porque o filtro "retrato" inclui 2:3.
6. **Na mesa:**
   - a foto externa entra como prévia, com selo "Pexels" ou "Freepik · prévia" (este com o custo do download);
   - a tarja do slide fica salmão;
   - aprovada, a foto é baixada e substitui a prévia pela versão em alta antes do B7.
7. **Registro da foto baixada:**
   - arquivo em `midia/aberta/foto/geral_<descricao>.jpg`;
   - catálogo: `origem = banco:pexels` (`licenca = pexels`) ou `banco:freepik` (`licenca = freepik-premium`), mais `autor`, `link_original` e ID;
   - Freepik: PDF da licença guardado junto da foto;
   - indexador e `usos.csv` no B7.
8. **Licença:** leia os termos atuais de cada banco antes do primeiro uso (uso comercial, crédito ao autor, uso para clientes diferentes, uso em logo ou marca, pessoas em contexto sensível).
9. **Fotos geradas por IA:** filtradas para pessoas em cena sensível (ex.: cena médica). Se alguma entrar, `origem = ia`.
10. **Área restrita nunca vai para o Magnific.** Upscale de foto da área aberta só com aprovação.
11. **Quando nada serve:** a lacuna vira pauta na tarja, com as saídas possíveis (produzir com o cliente ou outro banco). Gerar por IA só para objetos ou fundos, com aprovação e `origem = ia`.
12. **Direção fotográfica.** Cada projeto tem uma ficha `projetos/<slug>/direcao-fotografica.md` (A1), montada a partir das fotos reais e dos posts publicados: luz, cor, textura, profundidade, cenário, pessoas, pose, enquadramento, e o que denuncia "cara de banco".
    - **No B3:** foto externa que destoa perde para outra que conte a mesma etapa e combine com as reais.
    - **Na mesa:** a tarja diz quando a melhor opção destoa ("luz fria, cara de banco").
    - **Medição de apoio:** `scripts/medir_coerencia.py` compara cor, temperatura, saturação e brilho da candidata com as fotos de referência do projeto. Não substitui o julgamento visual.
    - **Tratamento leve opcional:** ajuste local de temperatura, saturação e granulação para aproximar uma foto externa. Não salva foto que destoa no cenário ou nas pessoas.

## Ordem das fontes de foto: reais, legado, Pexels, Freepik

- **Decisão:** no B3, as fontes são consultadas nesta ordem:
  1. **fotos reais do cliente** (`origem = decupagem:…`);
  2. **legado** (`origem = legado:figma`);
  3. **Pexels**;
  4. **Freepik** (conector Magnific).

  As duas externas só entram quando o slide fica com menos de 2 opções boas no banco.
- **Por quê:** a foto real é a mais autêntica e a que mais combina com a marca. O legado já foi usado e tende a repetir no feed. As externas custam busca, licença e às vezes créditos.
- **Os critérios não mudam:** sentido → inegociáveis → coerência → contraste → formato e usos valem para todas. A ordem das fontes decide quem é consultado primeiro e quem leva vantagem no desempate.

## Guia de criação do kit (A1)

- **Decisão:** a criação do kit de um projeto novo (etapa A1) segue `docs/guia-kit-projeto.md`: ler → extrair → ficha → Figma Fundamentos (variáveis → estilos → logos) → Figma Social Media (capa → conteúdo → final → contraste) → checklist → perguntas → registro. O arquivo de design system de cada marca (`-<slug>`) tem sempre a **mesma estrutura**: página "Design System" com os quadros "Fundamentos — <Marca>" e "Social Media — <Marca>".
- **Por quê:** a mesma estrutura deixa o B4 (montagem) igual para todas as marcas, e o guia evita repetir os erros já vistos.
- **Fontes divergentes:** para estilo de post, valem os **posts publicados e o arquivo de produção**; para regra de marca (logo, cores proibidas, tom), vale o brandguide. As diferenças ficam numa tabela "Divergências" na ficha.
- **Fonte indisponível no Figma:** usa-se a de rascunho do arquivo de produção, anotada na ficha e na descrição do estilo.
- **Degradês com hex fixo:** ligar variável a um ponto de degradê força o alfa a 100%; os degradês ficam com hex fixo e a documentação diz qual cor da marca eles usam.

## Perfil e imagem na ficha de cada projeto

- **Decisão:** toda ficha (`projetos/<slug>/projeto.md`) tem o bloco **"Perfil e imagem"**: tipo de projeto, o que o feed precisa provar, o que a imagem mostra, o que nunca mostra, cuidados com pessoas e fonte de foto preferida. Ele é a base do critério de **sentido** no B3.
- **Fonte:** um resumo do que a equipe já registrou sobre o cliente (no original, feito pelo Notion AI com um prompt que escreve "não encontrado" quando não há registro), guardado em `projetos/<slug>/guias/perfil-notion.md` com os links. O bloco da ficha resume; o arquivo é a prova.
- **Por quê:** o mesmo tema pede imagem diferente em cada projeto (numa marca, a paciente; em outra, a clínica e a equipe). Sem isso escrito, o critério de sentido vira gosto.
- **Relação com a direção fotográfica:** "Perfil e imagem" diz **o que** mostrar; a direção fotográfica (`direcao-fotografica.md`) diz **como** a foto deve parecer.

## Mesa de trabalho numa página só; entregues em outra

- **Decisão:** no Figma de cada projeto há **duas páginas** para a produção, e não uma página por conteúdo:
  - **"Mesa de trabalho":** tudo o que está em andamento. Cada conteúdo é uma **seção** com o tema e a versão (ex.: "Tema · v2"), uma embaixo da outra. As versões substituídas ficam logo abaixo da atual, marcadas.
  - **"Entregues":** quando o conteúdo é aprovado e entregue (B7), a seção sai da mesa e vai para cá, com a data de entrega no título. Teste e piloto sem entrega vão para cá marcados como "teste".
- **Por quê:** com uma página por conteúdo, o arquivo enche de páginas e fica difícil ver o que está em aberto. A mesa única mostra a fila; os entregues ficam como histórico, sem atrapalhar.

## Formato oficial: 1080 × 1440 para todos os projetos

- **Decisão:** todo carrossel, de qualquer projeto, sai em **1080 × 1440 (3:4)**.
- **Novo projeto:** os componentes já nascem em 1080 × 1440 (spread de 2160 × 1440), mesmo que posts antigos da marca usem outro tamanho.

## O pedido manda na estrutura

- **Decisão:**
  - **Nenhum slide é acrescentado** ao que o cliente mandou (ex.: slide de assinatura). O componente pode continuar no design system.
  - **A linha "+++" não entra**, nem quando traz texto: é do modelo de tabela do pedido.
  - **Negrito do cliente continua negrito**, no conteúdo e no final.
- **Por quê:** a estrutura corrigida à mão nesses pontos mostrou que eram correções que não precisavam ser feitas.

## Entrada e saída flexíveis: pedido padrão, fonte configurada e pasta de entrega

- **Decisão:**
  - **Pedido padrão.** Todo pedido vira, antes do B2, um arquivo `.md` neutro com `projeto` (slug), `tema`, `pasta_entrega` e a tabela "Sequência / Texto da Arte" (formato em `docs/fluxo-producao.md`). O `scripts/estruturar_pedido.py` lê esse arquivo e acha o projeto pelo slug, sem precisar de ID do Notion. A leitura direta de uma tarefa do Notion continua funcionando.
  - **Fonte configurada por projeto.** De onde vêm os pedidos (Notion, outra ferramenta, planilha, documentos, texto escrito pela IA), como o Claude acessa e o mapeamento dos campos para o pedido padrão ficam na ficha do projeto, seção "Pedidos e entregas". O Notion, com os campos do processo original, é documentado como exemplo.
  - **Texto gerado pela IA** é uma fonte como as outras e acontece antes do B1: o texto só vira pedido depois de aprovado pela pessoa. O B2 continua organizando sem reescrever.
  - **Saída configurável.** A pasta de entrega vem do pedido. Sem outra, o padrão é `projetos/<slug>/entregas/<tema>/`, fora do Git. O PNG continua 1080 × 1440, `01.png`…, e só é gravado com confirmação.
- **Por quê:** o Notion é a ferramenta de quem montou o processo, não uma regra dele. Cada pessoa recebe pedidos de um jeito; com um formato neutro no meio, o resto da trilha B não muda.
