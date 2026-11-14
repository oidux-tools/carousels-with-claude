# Carrosséis com Claude

**Para começar:**
1. Baixe esta pasta (no GitHub: **Code → Download ZIP**, ou `git clone`).
2. Abra a pasta no **Claude Code** (app ou terminal).
3. Escreva: **"me ajuda a implementar"**. O Claude mostra as fases e conduz uma por vez.

---

## O que é

Um processo para produzir carrosséis de Instagram com o Claude, do pedido até a entrega dos PNGs. Ele foi montado e usado em produção real; aqui está o método, sem dados de clientes.

O processo tem **duas trilhas** que rodam juntas:

- **Trilha A · Preparação do terreno** (A1–A4): a ficha da marca (tom de voz, perfil e imagem, identidade visual), o design system no Figma, o banco de fotos catalogado e as regras.
- **Trilha B · Produção** (B1–B7): a cada pedido, o Claude estrutura o texto em slides, escolhe as fotos, monta uma **mesa de revisão** no Figma e checa contraste e rosto. Você revisa olhando, aprova, e só então ele entrega.

O mapa completo está em [`docs/how-it-works.md`](docs/how-it-works.md). A versão visual, com as etapas clicáveis, é [`docs/fluxo.html`](docs/fluxo.html) (abre no navegador).

## Como pedir um carrossel

Depois de implementar (a fase 7 da skill combina de onde vêm os seus pedidos):

1. **Diga ao Claude qual é o pedido.** Exemplos: "faz o carrossel da tarefa <link>", "pega o próximo pedido pronto da planilha", "faz o pedido do arquivo <caminho>" ou "escreve um carrossel sobre <tema> para <marca>".
2. Se a IA escreveu o texto, **você aprova antes**. Daí em diante, o texto não é reescrito.
3. O Claude converte o pedido para o **pedido padrão** (projeto, tema, pasta de entrega e o texto por slide) e segue a trilha B:
   - **B2** organiza o texto em slides (capa, conteúdos, final, pelo menos um spread), sem reescrever;
   - **B3** escolhe 1 foto principal e 2 alternativas por slide;
   - **B4** monta a mesa de revisão no Figma;
   - **B5** confere contraste, rosto e emenda e marca o que pede decisão sua.

Formato do pedido padrão e exemplos: [`docs/fluxo-producao.md`](docs/fluxo-producao.md) ("Pedido padrão") e `scripts/exemplos/`.

## Como você recebe

1. **Para revisar:** uma seção nova na página **"Mesa de trabalho"** do Figma do projeto, com o carrossel em cima, uma tarja por slide (salmão = decisão sua) e as fotos sugeridas embaixo. Você olha, aprova ou dá o feedback; cada ponto do feedback vira regra escrita antes da nova versão.
2. **Depois de aprovado e só com a sua confirmação:** os PNGs **1080 × 1440**, `01.png`, `02.png`…, na pasta de entrega do pedido. Se você não tiver outro lugar, o padrão é `projetos/<slug>/entregas/<tema>/`. Se a fonte do pedido tiver status (ex.: Notion), ele só muda com a sua confirmação.

## O que você precisa

- **Claude Code** e uma conta do Claude.
- **Python 3.10+** (para os scripts de catálogo, contraste e estrutura).
- **Figma**, com o conector do Figma ligado no Claude (design system e mesa de revisão).
- **Uma fonte de pedidos**: a que você já usa (Notion, outra ferramenta, planilha, documentos) ou nenhuma, se a IA for escrever o texto a partir de um tema. Ferramenta com conector precisa do conector ligado no Claude.
- Para fotos externas (opcional): **Pexels** (pelo navegador) e **Freepik** pelo conector Magnific.

A skill `implementar` confere tudo isso na primeira fase.

## Mapa

| pasta      | para quê                                          |
|------------|---------------------------------------------------|
| `projetos/`| uma pasta por projeto (marca): ficha, aprendizados, direção fotográfica, guias, kit e produção. Comece copiando `projetos/_modelo/` |
| `midia/`   | banco de mídia: fotos e vídeos brutos, catálogo e log de usos. O material novo entra em `midia/_entrada/` |
| `docs/`    | o processo, as decisões, os aprendizados gerais e o diário |
| `scripts/` | automações (catálogo, importação, estrutura do pedido, contraste, coerência de cor) |
| `.claude/skills/implementar/` | o guia passo a passo que o Claude usa para te ajudar a implementar |

Toda pasta principal tem um `README.md` dizendo o que entra nela.

## Convenções gerais

- **Nomes** de pasta e arquivo: minúsculo, sem acento, sem espaço. `_` separa campos, `-` separa palavras.
- **Pastas com `_` na frente** são de uso especial (ex.: `midia/_entrada/`).
- **Datas** dentro de arquivos: `AAAA-MM-DD`.
- **Listas e catálogos** em CSV (UTF-8, vírgula): abrem no Sheets/Excel e são lidos por qualquer script.
- **Decisões de estrutura** ficam registradas em [`docs/decisoes.md`](docs/decisoes.md).
- **A história do seu processo** (o que foi feito, o que deu errado, o que aprendeu) fica em [`docs/diario.md`](docs/diario.md).

## Git

- O Git versiona só texto: processos, fichas, catálogos e scripts. Mídia, guias e kits ficam fora (`.gitignore`); guarde-os num drive que faça backup.
- Se o repositório ficar dentro de uma pasta sincronizada (Google Drive, OneDrive), funciona bem com uma pessoa rodando Git por vez.
- **Cuidado ao publicar o seu:** fichas, catálogos e o log de usos podem ter nomes de clientes e de pessoas. Se for compartilhar a sua versão, mantenha o repositório privado.
