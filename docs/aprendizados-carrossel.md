# Aprendizados · carrosséis em geral

Critérios que valem para **qualquer projeto**, aprendidos em pilotos e revisões. O que é só de uma marca fica em `projetos/<slug>/aprendizados.md`.

Formato: o critério, de onde veio e como aplicar. Entradas novas no fim de cada seção. Os critérios abaixo vieram das revisões do processo original; a origem foi resumida para não identificar clientes.

---

## Imagem e sentido

1. **A imagem conta a mesma etapa que o texto.** Se o texto fala de gestação, a foto mostra gestante, e não mãe com bebê. Não antecipar fases que o texto ainda não alcançou.
   *Origem: revisão de piloto.*
2. **A capa representa o tema de forma direta.** Mostrar o assunto e quem ele envolve (ex.: "vacina na gestação" → gestante sendo vacinada, ou um elemento claro de vacina). Foto genérica ou só atmosférica (silhueta, P&B artístico) não serve para tema informativo.
   *Origem: revisão de piloto.*
3. **As fotos seguem um arco.** A sequência acompanha a história do texto, e o fechamento pode mostrar o resultado (ex.: o bebê no último slide, depois de falar da gestação).
   *Origem: revisão de piloto.*
4. **Ordem dos critérios na escolha da foto:**
   1. sentido (critérios 1 a 3);
   2. inegociáveis (rosto, contraste mínimo, emenda);
   3. contraste recomendado, formato e usos.

   Contraste alto não compensa uma foto que não conta o assunto.
   *Origem: revisão de piloto.*
5. **Quando o banco não tem a foto certa, isso é um achado.** A mesa registra a lacuna (ex.: "falta gestante sendo vacinada") como pauta para produzir ou comprar a foto. Não preencher com uma foto que só "passa".

6. **Foto com marca de época perde.** Máscara da Covid e outros sinais datados fazem a foto parecer velha; ela perde para outra que conte a mesma etapa do texto.
   *Origem: revisão de piloto.*

7. **A foto conta a história de quem lê, não de quem atende.** Em tema de paciente (diagnóstico, exame, consulta), o foco da foto é a paciente e o que acontece com ela, não o médico. Médico de frente e paciente de costas, ou só a mão da paciente, perde para uma foto em que a paciente aparece.
   *Origem: revisão de piloto.*
8. **No slide final, a metade visível precisa fazer sentido sozinha.** O painel cobre a metade direita, então a foto é enquadrada para a metade esquerda: a pessoa principal inteira ali, sem cortar gente ao meio.
   *Origem: revisão de piloto.*
9. **Um carrossel, um tom de cor.** Todas as fotos do mesmo carrossel precisam conversar em temperatura, brilho e saturação; uma foto fria e clara no meio de fotos quentes e escuras quebra a direção de arte, mesmo que cada uma, sozinha, esteja certa. Na B3, comparar as fotos lado a lado (temperatura = R−B, brilho e saturação médios) e, na B4, aplicar tratamento leve (temperatura, exposição, saturação) nas que destoam. Se o tratamento leve não basta, a foto perde.
   *Origem: revisão de piloto.*
10. **As pessoas parecem do público da marca.** Foto externa (Pexels, Freepik) tende a mostrar gente de fora do Brasil; antes de aceitar, conferir se a pessoa poderia ser uma paciente brasileira. Buscar com termos como "brazilian", "latina" e conferir a prévia; na dúvida, perde.
   *Origem: revisão de piloto.*
11. **No spread, a pessoa aparece no slide em que o texto fala dela e segue no seguinte.** Se o 02 fala de quem recebe o diagnóstico, ela começa no 02 e continua no 03, não fica toda no 03 com o 02 vazio. Espelhar a foto é um recurso válido (sem texto ou marca na imagem); o rosto continua longe da emenda.
   *Origem: revisão de piloto.*

## Estrutura do carrossel

1. **Um spread pode bastar.** A regra pede pelo menos um, não um por par de slides. O último slide pode ter foto própria, sem dividir com o anterior.
   *Origem: revisão de piloto.*
2. **O carrossel tem os slides que o cliente mandou, nem mais nem menos.** Slide que o pedido não traz (assinatura, por exemplo) não é acrescentado, mesmo que o design system tenha o componente.
   *Origem: revisão de piloto.*
3. **A linha "+++" do pedido não entra.** É do modelo de tabela do cliente, não do carrossel, mesmo quando vem com texto. O script já ignora; não resgatar à mão.
   *Origem: revisão de piloto.*
4. **Negrito do cliente continua negrito**, em qualquer slide com texto (conteúdo ou final). Se o componente não tem onde pôr, a mesa decide como mostrar; a frase não se mistura ao parágrafo.
   *Origem: revisão de piloto.*

## Montagem e checagem

1. **Texto não pode ser cortado por máscara.** Descendentes (g, j, ç, p) do destaque em itálico passam da caixa do texto. Quadros com texto não recortam conteúdo; só o slide recorta. Checar no screenshot.
   *Origem: revisão de piloto.*
2. **A medição de contraste não vê rosto nem emenda.** O screenshot da mesa é obrigatório antes da revisão.
   *Origem: revisão de piloto.*

3. **Rosto precisa de respiro, não só de "não encostar".** Na capa e nos conteúdos, o título e o texto ficam longe do rosto. Primeiro tente **reenquadrar** (deslocar ou dar zoom na foto) ou **quebrar o título em mais linhas**; só depois troque a posição do texto ou a foto. Conferir a capa também: num piloto o título caiu sobre o rosto e passou pela checagem.
   *Origem: revisão de piloto.*
4. **Zoom para limpar a cena.** Quando a foto tem coisas que não somam (equipamento, chão, borda de objeto), dar zoom e reenquadrar antes de aceitar. O spread usa o mesmo recorte nas duas metades.
   *Origem: revisão de piloto.*
5. **Título de capa em até 3 linhas curtas**, quebradas à mão quando a quebra automática deixa uma linha longa ou empurra o título para cima do rosto.
   *Origem: revisão de piloto.*
6. **Viúva em coluna estreita: unir 2 palavras, não 3.** Em caixas de texto estreitas (~380 px com texto de 36 px), três palavras unidas por espaço não separável podem passar da largura, e o Figma quebra a palavra no meio ("crian-ças"). Nesses casos, unir só as 2 últimas e conferir no screenshot.
   *Origem: revisão de piloto.*

## Mesa de revisão

1. **Quem revisa olha, não lê.** O que pede decisão precisa aparecer na própria imagem ou num aviso curto e visível. Fotos alternativas e motivos longos são apoio, não o principal.
   *Origem: revisão de piloto.*
