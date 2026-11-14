# Projetos

Uma pasta por projeto (cliente ou marca), com tudo o que é preciso para produzir conteúdo para ele.

## Estrutura

```
projetos/
├── _modelo/              copie esta pasta para criar um projeto novo
└── <slug>/               ex.: marca-exemplo/
    ├── projeto.md        ficha: quem é, tom de voz, perfil e imagem, identidade visual, pedidos e entregas
    ├── aprendizados.md   direção de arte aprendida em pilotos e revisões desta marca
    ├── direcao-fotografica.md  como a foto deve parecer (régua do B3 e fotos de referência)
    ├── guias/            guias de aplicação, brandbook, manual de marca (como recebidos)
    ├── kit/              kit de produção: templates, logos oficiais, fontes, paletas
    ├── producao/         a estrutura de cada carrossel (<tema>.json, do B2) e tempos.csv
    └── entregas/         pasta de entrega padrão dos PNGs (<tema>/01.png…), fora do Git
```

## Três camadas, cada uma com um papel

| camada         | é o quê                                   | quem lê                              |
|----------------|-------------------------------------------|--------------------------------------|
| `guias/`       | o material original, intocado (PDFs etc.) | pessoas, quando há dúvida             |
| `projeto.md`   | o resumo prático dos guias, em texto      | pessoas e automações, no dia a dia   |
| `kit/`         | os arquivos de produção prontos para usar | quem monta as peças                  |

O `projeto.md` é a **fonte de consulta rápida**: cores em hex, fontes, regras de logo, tom de voz, o que evitar. Se algo no resumo conflitar com o guia original, o guia vence e o resumo é corrigido.

## Criar um projeto novo

1. Escolha o slug (minúsculo, sem acento, hífen entre palavras) e adicione em `midia/projetos.csv`.
2. Copie `_modelo/` para `projetos/<slug>/`.
3. Coloque os guias em `guias/` e o kit em `kit/`, do jeito que vieram.
4. Preencha o `projeto.md` a partir dos guias.

## Kit do projeto × banco de mídia

- **`kit/`**: a identidade oficial do projeto (logo, fontes, templates). Fica junto, como um pacote.
- **`midia/`**: matéria-prima reutilizável (fotos, vídeos, ícones…), ligada ao projeto pelo slug no nome do arquivo.
