# Nome do Projeto

- **slug:** `slug-do-projeto` (o mesmo de `midia/projetos.csv`)
- **status:** ativo
- **responsável:**
- **links:** Instagram, site…

## Sobre

O que é, o que faz ou vende, em 2–3 linhas.

## Público

Para quem fala: quem é, o que busca, o que incomoda.

## Tom de voz

- Como fala:
- Como não fala:
- Palavras e expressões da marca:

## Perfil e imagem

O que este projeto é e **o que a imagem deve mostrar e nunca mostrar**. O critério de **sentido** do B3 (escolha das fotos) parte daqui. Fonte: `guias/perfil-notion.md` (resumo do Notion) e conversas com quem conhece a marca.

- **Tipo de projeto:** profissional individual, clínica, marca…
- **O feed precisa provar:**
- **Imagem mostra (prioridade):**
- **Imagem nunca mostra:**
- **Cuidados com pessoas:**
- **Fonte de foto preferida:** (ex.: captações reais → legado → bancos externos)
- **Em aberto:**

## Identidade visual

Resumo prático dos guias. Fonte: `guias/…`.

- **Cores:** nome — `#000000` — onde usa
- **Fontes:** títulos / textos / destaques
- **Logo:** versões, área de respiro, tamanho mínimo, fundos permitidos
- **Elementos gráficos:** grafismos, ícones, estilo de foto
- **O que evitar:**

## Conteúdo

- **Redes e formatos:** ex.: Instagram, carrossel 3:4 (1080 × 1440, formato oficial), até 10 slides
- **Pilares / temas:**
- **Estrutura padrão do carrossel:** capa → desenvolvimento → fechamento/CTA
- **CTA padrão:**

## Pedidos e entregas

Configurado uma vez (fase de pedidos da skill `implementar`). Na produção, o Claude lê a fonte daqui e converte o pedido para o **pedido padrão** (`docs/fluxo-producao.md`) antes do B2.

- **Fonte dos pedidos:** (ex.: Notion, outra ferramenta, planilha, documentos, texto escrito pela IA a partir de um tema)
- **Como o Claude acessa:** (ex.: conector do Notion, pasta, arquivo)
- **Quando um pedido está pronto para começar:** (ex.: status "pronto para começar" na base)
- **Mapeamento para o pedido padrão:**

  | pedido padrão | na fonte |
  |---|---|
  | `projeto` | sempre este projeto (`slug`), ou o campo que identifica a marca |
  | `tema` | |
  | `titulo` | |
  | `pasta_entrega` | |
  | tabela "Sequência / Texto da Arte" | onde está o texto por slide |
  | `id` | |

- **Pasta de entrega padrão:** `projetos/<slug>/entregas/<tema>/` (se a fonte não disser outra)
- **Status na fonte depois da entrega:** (se houver; sempre com confirmação)
- **Texto gerado pela IA:** só vira pedido depois de aprovado por você.

## Arquivos

- `guias/`: o que tem lá
- `kit/`: o que tem lá
