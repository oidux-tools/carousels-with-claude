# How It Works · como a automação funciona

O mapa de referência do processo. Quando falamos de uma etapa ("isso é B3", "isso é trilha A"), é deste mapa que estamos falando. O detalhe de cada etapa da produção (entra, sai, critério) está em [`fluxo-producao.md`](fluxo-producao.md).

**Versão visual:** [`fluxo.html`](fluxo.html), que abre no navegador e tem as etapas clicáveis.

---

## Duas trilhas, a mesma importância

O processo não é uma fila única. São duas trilhas que rodam juntas:

- **Trilha A · Preparação do terreno:** contínua, independente de pedido. Deixa sistema, mídia e regras prontos.
- **Trilha B · Produção:** roda a cada pedido, apoiada na trilha A.

### Trilha A · Preparação do terreno

| código | etapa | quem | o que é |
|---|---|---|---|
| A1 | Sistema e estilo | você + Claude | ficha do projeto, design system, componentes, regras e aprendizados (da marca e gerais, alimentados pelas revisões). Passo a passo para marca nova: [`guia-kit-projeto.md`](guia-kit-projeto.md) |
| A2 | Decupagem | você + Claude | organizar e catalogar o material bruto; processo à parte, entrega um ZIP |
| A3 | Importação | Claude | do ZIP da decupagem para o banco de mídia e o catálogo: área **aberta** (equipe toda) ou **restrita** por projeto, com código no lugar do nome |
| A4 | Curadoria | você + Claude | destaques, contraste, histórico: o banco fica pronto para escolha. Os usos de cada imagem vêm do log `midia/usos.csv` |

### Trilha B · Produção

| código | etapa | quem | o que é |
|---|---|---|---|
| B1 | Pedido | cliente ou você | o pedido chega da **fonte configurada no projeto** (Notion, outra ferramenta, planilha, documento ou texto escrito pela IA e aprovado por você) com o texto **já separado por slide**, e o Claude o converte no **pedido padrão** (projeto, tema, pasta de entrega e a tabela "Sequência / Texto da Arte"). No processo original, a fonte é uma tarefa no Notion e o projeto vem da relação `Project` |
| B2 | Estruturação | Claude | o texto vira a estrutura do carrossel (capa, conteúdos, final, posição, destaque, viúvas) e é distribuído em slides, com **pelo menos um spread** (não todos). Organiza, **não reescreve** |
| B3 | Escolha das fotos | Claude | 1 principal + 2 alternativas por slide, nesta ordem: **sentido** (segue o "Perfil e imagem" da ficha do projeto; a foto conta a mesma etapa do texto, a capa mostra o tema direto, as fotos seguem um arco) → inegociáveis (rosto, contraste mínimo, emenda) → **coerência com a direção fotográfica** do projeto → contraste medido → formato e usos. Falta de foto certa vira **pauta**, não foto que "só passa". Consulta catálogo + log de usos e prefere as menos usadas e não usadas recentemente no projeto. Fontes, nesta ordem: **fotos reais do cliente** (decupagem) → **legado** (`legado:figma`) → **Pexels** (navegador) → **Freepik** (conector Magnific); as externas só quando o slide tem menos de 2 opções boas no banco. Externa entra na mesa como **prévia**; só é baixada depois da aprovação no B6 e entra no `midia/` com origem e licença |
| B4 | Montagem | Claude | a **mesa** no Figma: uma página única **"Mesa de trabalho"** por projeto, com uma seção por conteúdo em andamento; com os componentes `Social/*`, em três faixas alinhadas por slide: carrossel em cima, **tarja de decisão** (salmão = decisão sua, branca = nada pendente) e as sugestões de foto embaixo |
| B5 | Checagem | Claude | contraste medido + screenshot (rosto, emenda, texto cortado); exceções com nível, motivo e sugestão |
| B6 | Ajuste e aprovação | você + cliente | revisão humana da mesa. Quem revisa **olha, não lê**: o que pede decisão aparece na imagem ou na tarja |
| B6.1 | Ciclo de revisão | Claude | cada ponto do feedback vira **critério escrito** (da marca ou geral) **antes** de refazer; a mesa ganha v2, v3… e a anterior fica embaixo, marcada como substituída |
| B7 | Entrega | você + Claude | PNGs **1080 × 1440** (formato oficial de todos os projetos) nomeados `01.png`, `02.png`… na **pasta de entrega do pedido** (padrão: `projetos/<slug>/entregas/<tema>/`; no Notion, a pasta do `Link Location`), status na fonte do pedido quando houver e registro (uma linha em `midia/usos.csv` por foto usada, histórico, tempos). Só com confirmação |

## Como as trilhas se ligam

- **B3 puxa de A** o catálogo e as fotos.
- **B4 puxa de A** os componentes do design system.
- **B7 devolve para A4** os usos das fotos, o histórico do carrossel e os tempos. Isso fecha o ciclo: cada entrega melhora a próxima.
- **B6.1 devolve para A1** os critérios aprendidos na revisão (`aprendizados.md`). Cada revisão deixa a próxima mesa melhor desde a primeira versão.

## O que já vem pronto neste repositório

- **Modelo de projeto (A1):** `projetos/_modelo/` (ficha com Tom de voz e Perfil e imagem, aprendizados, direção fotográfica). Passo a passo para montar o kit de uma marca: `docs/guia-kit-projeto.md`.
- **Banco de mídia (A3, A4):** estrutura em `midia/` (área aberta e restrita, catálogo, log de usos).
- **Pedido padrão:** o formato neutro que o B2 lê, descrito em `docs/fluxo-producao.md` ("Pedido padrão"), com exemplo em `scripts/exemplos/pedido-padrao-exemplo.md`.
- **Já é script:** importação (A3, `importar_decupagem.py`), catálogo (A4, `indexar_midia.py`), estruturação do pedido (B2, `estruturar_pedido.py`, que lê o pedido padrão ou uma tarefa do Notion), contraste (B3/B5, `medir_contraste.py`) e coerência de cor (B3, `medir_coerencia.py`).
- **Fotos externas (B3):** Pexels pelo navegador e Freepik pelo conector Magnific, só com prévia até a aprovação.
- **Ainda não é script:** montagem da mesa (B4; o Claude monta no Figma seguindo `fluxo-producao.md`) e registro do B7.

## Princípios que atravessam tudo

- **Regra não é filtro:** só o inegociável bloqueia; o resto vira exceção com motivo para decisão humana.
- **Nada sai sem uma pessoa:** publicar, entregar e alterar o Notion (ou outra fonte de pedidos) só com confirmação.
- **O texto do pedido não é reescrito:** o B2 organiza. Se o texto foi escrito pela IA a partir de um tema, isso acontece **antes** do B1 e ele só vira pedido depois que você aprova.
- **Tempo se mede:** toda mesa registra seus marcos em `projetos/<slug>/producao/tempos.csv`.
- **Feedback vira aprendizado:** vai para `projetos/<slug>/aprendizados.md` ou `docs/aprendizados-carrossel.md`.

## Versão visual

[`fluxo.html`](fluxo.html) desenha este mapa e o [`fluxo-producao.md`](fluxo-producao.md): as duas trilhas, as conexões e, ao clicar numa etapa, como ela funciona por dentro. Abre direto no navegador; `fluxo.html#B3` já abre o B3. Os textos são a fonte: se o visual divergir, eles valem.

**Atualização em lote.** O visual não é refeito a cada mudança. Quem mudar este mapa ou o `fluxo-producao.md` anota a mudança na lista abaixo. Quando a lista tiver algo, o Claude pergunta se já pode atualizar o visual ou se espera mais mudanças. Ao atualizar, a lista é esvaziada e a data muda.

- **Visual atualizado em:** 2026-11-14
- **Pendente no visual:** nada.
