"""Estrutura o pedido de carrossel (etapa B2).

Lê o pedido num destes dois formatos e grava `projetos/<slug>/producao/<tema>.json`:
- **pedido padrão** (.md): projeto (slug), tema, pasta de entrega e a tabela
  "Sequência / Texto da Arte". É o formato neutro: o Claude converte para ele o pedido
  que vier de qualquer fonte (planilha, documento, outra ferramenta, texto aprovado).
  Exemplo: `scripts/exemplos/pedido-padrao-exemplo.md`;
- **tarefa do Notion**: a resposta do `notion-fetch`, salva num arquivo pelo Claude.
  Exemplo: `scripts/exemplos/tarefa-notion-exemplo.md`.

O script organiza; não reescreve. O texto do cliente sai igual, só com:
- a palavra de destaque marcada com *asteriscos* (última palavra do título);
- as últimas palavras de cada parágrafo e item unidas por U+00A0 (viúvas);
- espaços sobrando nas pontas tirados.
Tudo o que pede decisão vira exceção "revisar à mão" (ou "recomendado") + motivo.

Uso (a partir da raiz do repositório):
    python scripts/estruturar_pedido.py <arquivo-do-pedido> [--tema rotina-de-cuidados]
    python scripts/estruturar_pedido.py <arquivo> --simular
Veja `scripts/README.md`.
"""

from __future__ import annotations

import argparse
import csv
import html
import json
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
# Prefixo do ID único da base de tarefas no Notion (propriedade "ID"). Troque pelo da sua base.
PREFIXO_ID = "TAREFA"
NBSP = "\u00a0"

# Palavras que não servem de destaque nem de nome de arquivo.
PALAVRAS_FRACAS = {
    "a", "o", "as", "os", "um", "uma", "uns", "umas", "de", "da", "do", "das", "dos",
    "em", "na", "no", "nas", "nos", "e", "ou", "para", "pra", "por", "pelo", "pela",
    "que", "se", "com", "sem", "ao", "aos", "à", "às", "é", "são", "ser", "ter", "isso",
    "isto", "aqui", "ali", "já", "não", "sim", "mais", "menos", "muito", "como", "seu",
    "sua", "seus", "suas", "meu", "minha", "você", "ela", "ele", "lhe", "me", "te",
}

MARCADORES_LISTA = re.compile(r"^\s*(?:[•●▪◦·\-–*]|(\d{1,2})[.)])\s+")
URL = re.compile(r"https?://\S+")

LIMITES = {
    "palavras_slide": 45,          # projeto.md: até ~45 palavras por slide
    "titulo_capa": 54,             # modelo A: até 3 linhas de ~18 caracteres
    "titulo_conteudo": 60,         # 2–3 linhas curtas
    "titulo_final": 35,            # painel creme estreito (no piloto, 42 → 4 linhas)
    "titulo_maximo": 80,           # acima disso a 1ª linha é frase, não título
    "lista_min": 3,
    "lista_max": 5,
}


# ---------------------------------------------------------------- utilidades


def excecao(nivel: str, motivo: str) -> dict:
    return {"nivel": nivel, "motivo": motivo}


def sem_acento(texto: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn")


def palavras(texto: str) -> list[str]:
    return texto.replace(NBSP, " ").split()


def unir_viuva(texto: str) -> str:
    """Une as últimas palavras com U+00A0: 3 a partir de 5 palavras, 2 com 4 (decisoes.md)."""
    p = palavras(texto)
    if len(p) >= 5:
        n = 3
    elif len(p) == 4:
        n = 2
    else:
        return " ".join(p)
    return " ".join(p[:-n]) + " " + NBSP.join(p[-n:])


def limpar_markdown(texto: str) -> str:
    """Tira escapes e links do markdown do Notion, sem mudar as palavras."""
    texto = re.sub(r"\[([^\]]*)\]\(([^)]*)\)", lambda m: m.group(2) if m.group(1).replace("\\", "") == m.group(2) else f"{m.group(1)} ({m.group(2)})", texto)
    texto = re.sub(r"\\([_*\[\]()#>`~|\\-])", r"\1", texto)
    return texto


def slug(texto: str, max_palavras: int = 4) -> str:
    base = sem_acento(texto.lower())
    base = re.sub(r"[^a-z0-9]+", " ", base)
    fracas = {sem_acento(p) for p in PALAVRAS_FRACAS}
    p = [w for w in base.split() if w not in fracas]
    return "-".join(p[:max_palavras]) or "carrossel"


# ---------------------------------------------------------------- leitura


CAMPOS_PADRAO = ("projeto", "tema", "titulo", "pasta_entrega", "id", "fonte")


def ler_pedido_padrao(bruto: str) -> tuple[dict, str] | None:
    """Pedido padrão: linhas "- campo: valor" + tabela markdown "| Sequência | Texto da Arte |".

    Na célula de texto, <br> quebra linha (<br><br> separa parágrafos) e **negrito** ou
    <b>negrito</b> marcam a frase em negrito. Devolve None se o arquivo não for um pedido padrão.
    """
    campos = {}
    for m in re.finditer(r"^[ \t]*-?[ \t]*([a-z_]+)[ \t]*:[ \t]*(.*?)[ \t]*$", bruto, re.M):
        if m.group(1) in CAMPOS_PADRAO and m.group(1) not in campos:
            campos[m.group(1)] = m.group(2)
    linhas_tabela = [l.strip() for l in bruto.splitlines() if l.strip().startswith("|")]
    if not campos.get("projeto") or not linhas_tabela:
        return None
    trs = []
    for l in linhas_tabela:
        celulas = [c.strip() for c in l.strip("|").split("|")]
        if len(celulas) < 2 or re.fullmatch(r":?-{3,}:?", celulas[0]):
            continue  # linha separadora da tabela markdown
        texto = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", "|".join(celulas[1:]))
        trs.append(f"<tr><td>{celulas[0]}</td><td>{texto}</td></tr>")
    props = {
        "_padrao": True,
        "_slug": campos["projeto"],
        "_tema": campos.get("tema") or None,
        "_fonte": campos.get("fonte") or None,
        "Name": campos.get("titulo", ""),
        "Link Location": campos.get("pasta_entrega") or None,
        "userDefined:ID": campos.get("id") or None,
    }
    return props, "<table>" + "".join(trs) + "</table>"


def ler_exportacao(caminho: Path) -> tuple[dict, str]:
    """Devolve (propriedades, html do conteúdo).

    Aceita: o pedido padrão (ver `ler_pedido_padrao`), a resposta JSON do notion-fetch
    (com o campo "text") ou o texto da página (<page>…<properties>{…}</properties>…<content>…</content>).
    """
    bruto = caminho.read_text(encoding="utf-8")
    if "<properties>" not in bruto and not bruto.lstrip().startswith("{"):
        padrao = ler_pedido_padrao(bruto)
        if padrao:
            return padrao
    try:
        dados = json.loads(bruto)
        if isinstance(dados, dict) and "text" in dados:
            bruto = dados["text"]
    except json.JSONDecodeError:
        pass

    props: dict = {}
    m = re.search(r"<properties>\s*(\{.*?\})\s*</properties>", bruto, re.S)
    if m:
        txt = m.group(1)
        # O Notion às vezes devolve escapes de markdown que não são JSON válido (ex.: "\_").
        txt = re.sub(r"\\(.)", lambda m: m.group(0) if m.group(1) in '"\\/bfnrtu' else "\\\\" + m.group(1), txt)
        props = json.loads(txt)
    m = re.search(r"<content>(.*?)</content>", bruto, re.S)
    conteudo = m.group(1) if m else bruto
    return props, conteudo


def linhas_da_tabela(conteudo: str) -> list[tuple[str, str]]:
    """(rótulo, html da célula de texto) de cada linha da tabela de slides."""
    tabela = re.search(r"<table[^>]*>(.*?)</table>", conteudo, re.S)
    if not tabela:
        raise SystemExit("Não achei a tabela \"Sequência / Texto da Arte\" no conteúdo da tarefa.")
    linhas = []
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", tabela.group(1), re.S):
        celulas = re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)
        if len(celulas) < 2:
            continue
        rotulo = texto_simples(celulas[0])
        if sem_acento(rotulo.lower()).startswith("sequencia"):
            continue  # cabeçalho
        linhas.append((rotulo, celulas[1]))
    return linhas


def texto_simples(trecho: str) -> str:
    trecho = re.sub(r"<[^>]+>", "", trecho)
    return html.unescape(limpar_markdown(trecho)).strip()


def separar_notas(celula: str) -> tuple[str, list[str]]:
    """Tira da célula o texto colorido (anotação para o designer), que não vai para a arte."""
    notas = []

    def guardar(m):
        nota = texto_simples(m.group(0).replace("<br />", " ").replace("<br/>", " "))
        if nota:
            notas.append(re.sub(r"\s+", " ", nota))
        return "<br /><br />"

    celula = re.sub(r"<i>\s*<span color=\"[^\"]+\">.*?</span>\s*</i>", guardar, celula, flags=re.S)
    celula = re.sub(r"<span color=\"[^\"]+\">.*?</span>", guardar, celula, flags=re.S)
    return celula, notas


def linha_em_negrito(bruta: str, aberto: bool) -> tuple[bool, bool]:
    """A linha está toda em negrito? Considera o <b> que vem aberto da linha anterior.
    Devolve (linha em negrito, negrito ainda aberto no fim da linha)."""
    tem_texto, tudo_negrito = False, True
    for pedaco in re.split(r"(</?b>)", bruta):
        if pedaco == "<b>":
            aberto = True
        elif pedaco == "</b>":
            aberto = False
        else:
            t = texto_simples(pedaco)
            if t and not re.fullmatch(r"[•●▪◦·\-–*\d.)\s]+", t):  # marcador de lista sozinho não conta
                tem_texto = True
                tudo_negrito = tudo_negrito and aberto
    return tem_texto and tudo_negrito, aberto


def blocos_da_celula(celula: str) -> list[list[dict]]:
    """Blocos separados por linha em branco; cada linha com texto, negrito e marcador."""
    celula = re.sub(r"<br\s*/?>", "\n", celula.strip())
    blocos, atual = [], []
    em_negrito = False  # o <b> do Notion pode abrir numa linha e fechar em outra
    for bruta in celula.split("\n"):
        negrito, em_negrito = linha_em_negrito(bruta, em_negrito)
        texto = texto_simples(bruta)
        if not texto:
            if atual:
                blocos.append(atual)
                atual = []
            continue
        m = MARCADORES_LISTA.match(texto)
        atual.append({
            "texto": texto[m.end():].strip() if m else texto,
            "item": bool(m),
            "numero": bool(m and m.group(1)),
            "negrito": negrito,
            "url": bool(URL.search(texto)),
        })
    if atual:
        blocos.append(atual)
    return blocos


# ---------------------------------------------------------------- estrutura


def titulo_com_destaque(titulo: str) -> tuple[str, str | None, list[dict]]:
    """Marca a última palavra com *asteriscos*; a pontuação final fica fora."""
    exc = []
    p = titulo.strip().rsplit(" ", 1)
    ultima = p[-1]
    m = re.match(r"^(.*?)([.!?:;,…\"”’)]*)$", ultima)
    nucleo, pont = m.group(1), m.group(2)
    if not nucleo:
        return titulo, None, [excecao("revisar à mão", "título sem palavra para o destaque")]
    if sem_acento(nucleo.lower()) in {sem_acento(w) for w in PALAVRAS_FRACAS} or len(nucleo) <= 2:
        exc.append(excecao("recomendado", f"destaque cai em palavra fraca (\"{nucleo}\"); a regra pede título que termine numa palavra forte"))
    marcado = (p[0] + " " if len(p) > 1 else "") + f"*{nucleo}*{pont}"
    return marcado, nucleo, exc


def checar_frases(texto: str, antes_da_lista: bool = False) -> list[dict]:
    """Sinais de frase incompleta. Heurística: marca, nunca corrige."""
    exc = []
    for frase in re.split(r"(?<=[.!?])\s+", texto):
        p = palavras(frase.rstrip(".!?"))
        if len(p) >= 2 and p[0].lower() in {"um", "uma"} and p[1].lower() in {"dos", "das"}:
            seguinte = p[2].lower() if len(p) > 2 else ""
            if seguinte not in {"mais", "principais", "maiores", "melhores", "menores", "piores", "primeiros", "primeiras", "poucos", "poucas"}:
                exc.append(excecao("revisar à mão", f"\"{frase.strip()}\" parece incompleta (falta \"mais\"?). Texto mantido; confirmar com quem escreveu"))
    for a, b in zip(palavras(texto), palavras(texto)[1:]):
        if a.lower() == b.lower() and a.isalpha():
            exc.append(excecao("revisar à mão", f"palavra repetida: \"{a} {b}\""))
    fim = texto.rstrip()
    if fim.endswith(":") and not antes_da_lista:
        exc.append(excecao("revisar à mão", f"\"{fim[-40:]}\" termina em dois-pontos e nada vem depois"))
    elif fim and fim[-1] not in ".!?…)\"”;:" and len(palavras(fim)) > 6:
        exc.append(excecao("recomendado", f"parágrafo sem pontuação final: \"…{fim[-30:]}\""))
    return exc


def montar_slide(numero: int, rotulo: str, papel: str, celula: str) -> dict:
    celula, notas = separar_notas(celula)
    blocos = blocos_da_celula(celula)
    exc: list[dict] = []
    slide = {"slide": f"{numero:02d}", "papel": papel, "origem_notion": rotulo}

    # Bloco com link: referência para o designer (produto, ícone…), não texto da arte.
    referencias = []
    texto_blocos = []
    for b in blocos:
        if any(l["url"] for l in b):
            referencias.append(" · ".join(l["texto"] for l in b))
        else:
            texto_blocos.append(b)
    blocos = texto_blocos

    # Título: 1ª linha do 1º bloco, se ela não for item de lista e tiver cara de título.
    comeca_com_item = bool(blocos) and blocos[0][0]["item"]
    titulo = None
    if blocos and not blocos[0][0]["item"]:
        candidata = blocos[0][0]["texto"]
        so_ela = len(blocos) == 1 and len(blocos[0]) == 1
        if len(candidata) <= LIMITES["titulo_maximo"] or papel == "capa" or (papel == "final" and so_ela):
            titulo = candidata
            blocos[0] = blocos[0][1:]
            blocos = [b for b in blocos if b]
    # Frase em negrito do cliente (conteúdo e final): sai do corpo e continua negrito.
    # Antes, linha em negrito colada a outra linha era juntada ao parágrafo sem aviso.
    usa_negrito = papel in ("conteudo", "final")
    negrito_cliente = [l for b in blocos for l in b if l["negrito"] and not l["item"]] if usa_negrito else []
    linhas = [l for b in blocos for l in b]
    texto_depois_do_negrito = bool(negrito_cliente) and any(
        not l["negrito"] for l in linhas[linhas.index(negrito_cliente[0]) + 1:])

    # Corpo: parágrafos (linhas seguidas viram um parágrafo) e listas, na ordem.
    corpo: list[tuple[str, object]] = []
    for b in blocos:
        par: list[str] = []
        lista: list[dict] = []
        for l in b:
            if usa_negrito and l["negrito"] and not l["item"]:
                if par:
                    corpo.append(("paragrafo", " ".join(par)))
                    par = []
                if lista:
                    corpo.append(("lista", lista))
                    lista = []
                continue
            if l["item"]:
                if par:
                    corpo.append(("paragrafo", " ".join(par)))
                    par = []
                lista.append(l)
            else:
                if lista:
                    corpo.append(("lista", lista))
                    lista = []
                par.append(l["texto"])
        if par:
            corpo.append(("paragrafo", " ".join(par)))
        if lista:
            corpo.append(("lista", lista))

    # No Notion é comum separar os itens com linha em branco ("• a<br><br>• b"): cada item cai num bloco.
    # Itens seguidos, só separados por linha em branco, são uma lista só (aprendido em piloto).
    juntos: list[tuple[str, object]] = []
    for tipo, valor in corpo:
        if tipo == "lista" and juntos and juntos[-1][0] == "lista":
            juntos[-1] = ("lista", juntos[-1][1] + valor)
        else:
            juntos.append((tipo, valor))
    corpo = juntos

    # Lista de 1 item vira parágrafo (o componente pede 3 a 5).
    final_corpo = []
    for tipo, valor in corpo:
        if tipo == "lista" and len(valor) == 1:
            final_corpo.append(("paragrafo", valor[0]["texto"]))
            exc.append(excecao("revisar à mão", f"\"{valor[0]['texto']}\" é uma lista de 1 item no Notion; o componente pede {LIMITES['lista_min']} a {LIMITES['lista_max']}. Virou parágrafo; decidir se vira negrito ou subtítulo"))
        else:
            final_corpo.append((tipo, valor))
    corpo = final_corpo

    paragrafos = [v for t, v in corpo if t == "paragrafo"]
    listas = [v for t, v in corpo if t == "lista"]

    # Frase em negrito: a marcada em negrito pelo cliente; senão, o 3º parágrafo (regra do piloto).
    negrito = None
    if negrito_cliente:
        negrito = " ".join(l["texto"] for l in negrito_cliente)
        if texto_depois_do_negrito:
            exc.append(excecao("revisar à mão", f"frase em negrito \"{negrito}\" vem antes de outro texto no pedido; o componente mostra o negrito no fim. Conferir a ordem"))

    if titulo is not None:
        slide["titulo"], destaque, e = titulo_com_destaque(titulo)
        slide["destaque"] = destaque
        exc += e
    elif papel != "final":  # o final sem título tem exceção própria (modelo A)
        if comeca_com_item:
            exc.append(excecao("revisar à mão", "slide sem título: começa direto na lista, que continua a do slide anterior. Decidir com quem escreveu se repete o título ou se os dois slides viram um spread (não inventar)"))
        else:
            exc.append(excecao("revisar à mão", "slide sem título: a 1ª linha é longa demais para título. Todo o texto ficou como corpo; decidir o título com quem escreveu (não inventar)"))

    if papel == "capa":
        slide["componente"] = "Social/Capa"
        if paragrafos or listas:
            slide["modelo"] = "B"
            slide["subtitulo"] = unir_viuva(" ".join(paragrafos + [i["texto"] for l in listas for i in l]))
            exc.append(excecao("revisar à mão", "capa com mais de uma linha: o resto virou subtítulo (modelo B); conferir"))
        else:
            slide["modelo"] = "A"
        if titulo and len(titulo) > LIMITES["titulo_capa"]:
            exc.append(excecao("recomendado", f"título da capa com {len(titulo)} caracteres; o modelo A comporta ~3 linhas de 18"))

    elif papel == "final":
        slide["componente"] = "Social/Final"
        textos = paragrafos + [i["texto"] for l in listas for i in l]
        if titulo and len(titulo) <= LIMITES["titulo_maximo"] and not (len(textos) == 0 and len(titulo) > LIMITES["titulo_conteudo"]):
            slide["modelo"] = "B"
            if textos:
                slide["texto"] = unir_viuva(" ".join(textos))
            if len(titulo) > LIMITES["titulo_final"]:
                exc.append(excecao("recomendado", f"título de {len(titulo)} caracteres no painel do final: pode passar de 3 linhas; conferir altura"))
            if not textos:
                exc.append(excecao("revisar à mão", "final só com uma frase: usada como título; o painel fica sem texto de apoio"))
        elif titulo:
            # Só uma frase longa: título grande demais para o painel.
            slide["modelo"] = "B"
            exc.append(excecao("revisar à mão", f"final só com uma frase de {len(titulo)} caracteres, usada como título; longa para o painel. Decidir se vira texto (modelo A) e qual seria a frase de fechamento"))
        else:
            # Sem título: modelo A (apoio em cima, fechamento grande embaixo).
            slide["modelo"] = "A"
            if len(paragrafos) >= 2:
                slide["texto"] = unir_viuva(" ".join(paragrafos[:-1]))
                slide["fechamento"] = paragrafos[-1]
                exc.append(excecao("revisar à mão", "final sem título: modelo A, com o último parágrafo como frase de fechamento (grande) e o resto como apoio. Conferir se é essa a frase de destaque"))
                f, d, e = titulo_com_destaque(paragrafos[-1])
                slide["fechamento"], slide["destaque"] = f, d
                exc += e
            else:
                slide["texto"] = unir_viuva(" ".join(textos))
        if negrito:
            slide["negrito"] = unir_viuva(negrito)
        for t in textos + ([negrito] if negrito else []):
            exc += checar_frases(t)

    else:
        slide["componente"] = "Social/Conteúdo"
        if len(paragrafos) == 3 and negrito is None:
            negrito = paragrafos.pop()
            exc.append(excecao("revisar à mão", f"3 blocos de texto e o componente tem 2 parágrafos: \"{negrito}\" foi para a frase em negrito, o que muda a ênfase"))
        elif len(paragrafos) > 3 or (len(paragrafos) > 2 and negrito is not None):
            exc.append(excecao("revisar à mão", f"{len(paragrafos)} parágrafos; o componente tem 2 + frase em negrito. Nada foi cortado: decidir o que junta ou vai para outro slide"))
        if paragrafos:
            slide["paragrafos"] = [unir_viuva(p) for p in paragrafos]
        if listas:
            itens = listas[0]
            slide["lista"] = {
                "marcador": "Número" if all(i["numero"] for i in itens) else "Ponto",
                "itens": [unir_viuva(i["texto"]) for i in itens],
            }
            n = len(itens)
            if not LIMITES["lista_min"] <= n <= LIMITES["lista_max"]:
                exc.append(excecao("revisar à mão", f"lista com {n} itens; o componente pede {LIMITES['lista_min']} a {LIMITES['lista_max']}"))
            if len(listas) > 1:
                slide["listas_extras"] = [[unir_viuva(i["texto"]) for i in l] for l in listas[1:]]
                exc.append(excecao("revisar à mão", f"{len(listas)} listas no slide; o componente tem 1"))
            if paragrafos:
                slide["ordem"] = [t for t, _ in corpo]
        if negrito:
            slide["negrito"] = unir_viuva(negrito)
        if titulo and len(titulo) > LIMITES["titulo_conteudo"]:
            exc.append(excecao("recomendado", f"título com {len(titulo)} caracteres; o padrão são 2–3 linhas curtas"))
        if titulo and titulo.rstrip().endswith(":"):
            exc.append(excecao("revisar à mão", "título termina em dois-pontos: parece a introdução da lista, não um título"))
        elif titulo and titulo.rstrip().endswith(".") and not titulo.rstrip().endswith("..."):
            exc.append(excecao("recomendado", "título termina em ponto final: conferir se é título ou frase"))
        apresenta_lista = {v for (t, v), (t2, _) in zip(corpo, corpo[1:]) if t == "paragrafo" and t2 == "lista"}
        for t in paragrafos + ([negrito] if negrito else []) + [i["texto"] for l in listas for i in l]:
            exc += checar_frases(t, antes_da_lista=t in apresenta_lista)
        total = len(palavras(" ".join(paragrafos + ([negrito] if negrito else []) + [i["texto"] for l in listas for i in l])))
        if total > LIMITES["palavras_slide"]:
            exc.append(excecao("recomendado", f"{total} palavras no corpo (padrão: até ~{LIMITES['palavras_slide']})"))

    if notas:
        slide["notas_producao"] = notas
        exc.append(excecao("revisar à mão", "anotação para o designer no Notion (texto colorido), fora da arte: " + " / ".join(notas)))
    if referencias:
        slide["referencias"] = referencias
        exc.append(excecao("revisar à mão", f"{len(referencias)} referência(s) com link (produto, imagem) fora da arte: " + "; ".join(r.split(" · ")[0] for r in referencias)))

    slide["excecoes"] = exc
    return slide


POSICOES = ["sup-esq", "inf-dir", "sup-dir", "inf-esq"]


def spread_anterior(pasta: Path, ignorar_id: str | None, ignorar_arquivo: Path | None) -> str | None:
    """Slides do 1º spread do carrossel mais recente do projeto (para variar a posição)."""
    candidatos = []
    for arq in pasta.glob("*.json") if pasta.is_dir() else []:
        if ignorar_arquivo and arq.resolve() == ignorar_arquivo.resolve():
            continue
        try:
            d = json.loads(arq.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        if not isinstance(d, dict) or not d.get("spreads"):
            continue
        if ignorar_id and d.get("origem", {}).get("id") == ignorar_id:
            continue
        quando = (d.get("entrega") or {}).get("data") or d.get("gerado_em") or ""
        candidatos.append((quando, arq.stat().st_mtime, d["spreads"][0]["slides"]))
    if not candidatos:
        return None
    return max(candidatos)[2]


def distribuir(slides: list[dict], anterior: str | None) -> tuple[list[dict], list[dict]]:
    """Um spread entre slides de conteúdo, em posição diferente do carrossel anterior."""
    exc = []
    conteudo = [s for s in slides if s["papel"] == "conteudo"]
    pares = [(a, b) for a, b in zip(conteudo, conteudo[1:]) if int(b["slide"]) == int(a["slide"]) + 1]
    escolhido = None
    for a, b in pares:
        if f"{a['slide']}-{b['slide']}" != anterior:
            escolhido = (a, b)
            break
    if escolhido is None and pares:
        escolhido = pares[0]
        exc.append(excecao("recomendado", f"só cabe o spread {anterior}, igual ao do carrossel anterior"))
    if escolhido is None:
        exc.append(excecao("revisar à mão", "menos de 2 slides de conteúdo seguidos: não dá para ter o spread obrigatório. Considerar o spread com o final"))

    i = 0
    for s in slides:
        if s["papel"] != "conteudo":
            s["spread"] = None
            continue
        s["spread"] = None
        s["metade"] = None
        if escolhido and s in escolhido:
            s["spread"] = f"{escolhido[0]['slide']}-{escolhido[1]['slide']}"
            s["metade"] = "esquerda" if s is escolhido[0] else "direita"
        s["posicao"] = POSICOES[i % len(POSICOES)]
        i += 1

    # Chaves na mesma ordem do piloto.
    ordem = ("slide", "papel", "spread", "metade", "componente", "modelo", "posicao", "origem_notion",
             "titulo", "destaque", "subtitulo", "paragrafos", "lista", "listas_extras", "ordem", "negrito",
             "texto", "fechamento", "notas_producao", "referencias", "excecoes")
    for n, s in enumerate(slides):
        slides[n] = {k: s[k] for k in ordem if k in s} | {k: v for k, v in s.items() if k not in ordem}

    spreads = []
    if escolhido:
        spreads.append({"slides": f"{escolhido[0]['slide']}-{escolhido[1]['slide']}", "fotos": [], "excecoes": []})
    return spreads, exc


def resumo_estrutura(slides: list[dict]) -> str:
    partes, vistos = [], set()
    for s in slides:
        if s["slide"] in vistos:
            continue
        if s.get("spread"):
            a, b = s["spread"].split("-")
            partes.append(f"{a}–{b} spread")
            vistos.update({a, b})
        elif s["papel"] == "capa":
            partes.append(f"{s['slide']} capa")
        elif s["papel"] == "final":
            partes.append(f"{s['slide']} final (foto própria)")
        else:
            partes.append(f"{s['slide']} foto única")
        vistos.add(s["slide"])
    return " · ".join(partes)


def achar_projeto(props: dict) -> tuple[str, str, str]:
    """(slug, id da página do projeto no Notion, nome).

    Pedido padrão: pelo slug, que precisa estar em midia/projetos.csv.
    Tarefa do Notion: pela relação Project, comparada com a coluna notion_projeto.
    """
    if props.get("_padrao"):
        with open(RAIZ / "midia" / "projetos.csv", encoding="utf-8-sig", newline="") as f:
            for linha in csv.DictReader(f):
                if linha.get("slug") == props["_slug"]:
                    return linha["slug"], "", linha.get("nome", "")
        raise SystemExit(
            f"PARADO: o projeto '{props['_slug']}' do pedido não está em midia/projetos.csv (coluna slug).\n"
            "  Cadastre o projeto (veja projetos/README.md) e rode de novo."
        )
    projeto = props.get("Project") or []
    if isinstance(projeto, str):
        try:
            projeto = json.loads(projeto)
        except json.JSONDecodeError:
            projeto = [projeto]
    ids = [re.sub(r"[^0-9a-f]", "", p.lower())[-32:] for p in projeto]
    with open(RAIZ / "midia" / "projetos.csv", encoding="utf-8-sig", newline="") as f:
        for linha in csv.DictReader(f):
            alvo = re.sub(r"[^0-9a-f]", "", (linha.get("notion_projeto") or "").lower())
            if alvo and alvo in ids:
                obs = linha.get("observacao") or ""
                nome = obs.split("Notion:", 1)[1].strip() if "Notion:" in obs else linha.get("nome", "")
                return linha["slug"], alvo, nome
    raise SystemExit(
        "PARADO: o projeto da tarefa não está em midia/projetos.csv (coluna notion_projeto).\n"
        f"  Project no Notion: {projeto or '(vazio)'}\n"
        "  Cadastre o projeto (veja projetos/README.md) e rode de novo."
    )


def estruturar(props: dict, conteudo: str, anterior_pasta: Path | None, saida: Path | None) -> dict:
    slug_proj, id_proj, nome_proj = achar_projeto(props)
    linhas = linhas_da_tabela(conteudo)
    gerais: list[dict] = []

    validas = []
    for rotulo, celula in linhas:
        if rotulo.strip() == "+++":
            gerais.append(excecao("recomendado", "linha \"+++\" da tabela do pedido ignorada"))
            continue
        if not texto_simples(re.sub(r"<br\s*/?>", " ", celula)):
            gerais.append(excecao("recomendado", f"\"{rotulo}\" vazio na tabela do pedido: ignorado"))
            continue
        validas.append((rotulo, celula))
    if len(validas) < 3:
        raise SystemExit(f"PARADO: a tabela tem {len(validas)} slide(s) com texto; um carrossel precisa de capa, conteúdo e final.")
    if len(validas) > 10:
        gerais.append(excecao("revisar à mão", f"{len(validas)} slides; o máximo do carrossel é 10"))

    slides = []
    for i, (rotulo, celula) in enumerate(validas, start=1):
        papel = "capa" if i == 1 else "final" if i == len(validas) else "conteudo"
        esperado = f"slide {i}"
        if rotulo.lower().strip() != esperado:
            gerais.append(excecao("recomendado", f"slide {i:02d} veio da linha \"{rotulo}\" do pedido (fora da sequência)"))
        slides.append(montar_slide(i, rotulo, papel, celula))

    # Destaque repetido em slides diferentes.
    vistos: dict[str, str] = {}
    for s in slides:
        d = (s.get("destaque") or "").lower()
        if d and d in vistos:
            s["excecoes"].append(excecao("recomendado", f"'{s['destaque']}' repete o destaque do slide {vistos[d]}"))
        elif d:
            vistos[d] = s["slide"]

    tarefa_id = props.get("userDefined:ID")
    if not props.get("_padrao") and (isinstance(tarefa_id, int) or (isinstance(tarefa_id, str) and tarefa_id.isdigit())):
        tarefa_id = f"{PREFIXO_ID}-{tarefa_id}"
    anterior = spread_anterior(anterior_pasta, tarefa_id, saida) if anterior_pasta else None
    spreads, exc_spread = distribuir(slides, anterior)
    gerais += exc_spread

    asset = props.get("Asset Type")
    if asset and asset != "Social Media Carousel":
        gerais.append(excecao("recomendado", f"Asset Type da tarefa no Notion é \"{asset}\", não \"Social Media Carousel\""))

    url = (props.get("url") or "").split("?")[0]
    origem = {
        "fonte": props.get("_fonte") or ("pedido padrão" if props.get("_padrao") else "notion"),
        "notion_tarefa": url,
        "id": tarefa_id,
        "notion_projeto": nome_proj,
        "notion_projeto_id": id_proj,
        "prazo_final": props.get("date:Final Due Date:start"),
        "entrega_cliente": props.get("date:Client Delivery Date:start"),
        "pasta_entrega": props.get("Link Location"),
    }
    regras = [
        "texto do cliente sem reescrita",
        "destaque = última palavra do título (pontuação fora), marcado com *asteriscos*",
        "viúvas: últimas 3 palavras de cada parágrafo e item unidas por U+00A0 (2 em textos de 4 palavras)",
        "pelo menos um spread, em posição diferente do carrossel anterior" + (f" ({anterior})" if anterior else " (sem carrossel anterior registrado)"),
        "posição do texto provisória (alternada); a foto decide no B3/B5",
        "regra não é filtro: dúvidas como exceção",
    ]
    return {
        "nome": limpar_markdown(props.get("Name") or ""),
        "projeto": slug_proj,
        "origem": origem,
        "regras_aplicadas": regras,
        "estrutura": resumo_estrutura(slides),
        "slides": slides,
        "spreads": spreads,
        "excecoes_gerais": gerais,
        "status": "estruturado (B2); falta B3 em diante",
        "versao": 1,
        "gerado_por": "scripts/estruturar_pedido.py",
        "gerado_em": date.today().isoformat(),
    }


# ---------------------------------------------------------------- saída


def relatorio(d: dict) -> str:
    linhas = [f"{d['origem']['id'] or d['origem']['fonte']} · {d['nome']} → {d['projeto']}", f"  {d['estrutura']}"]
    for s in d["slides"]:
        cab = s.get("titulo") or s.get("fechamento") or "(sem título)"
        extra = []
        if s.get("paragrafos"):
            extra.append(f"{len(s['paragrafos'])} par.")
        if s.get("lista"):
            extra.append(f"lista {len(s['lista']['itens'])}")
        if s.get("negrito"):
            extra.append("negrito")
        if s.get("texto"):
            extra.append("texto")
        marca = sum(1 for e in s["excecoes"] if e["nivel"] == "revisar à mão")
        linhas.append(f"  {s['slide']} {s['papel']:<8} {cab[:50]:<52} {', '.join(extra):<22} revisar: {marca}")
        for e in s["excecoes"]:
            linhas.append(f"       - [{e['nivel']}] {e['motivo']}")
    for e in d["excecoes_gerais"]:
        linhas.append(f"  geral [{e['nivel']}] {e['motivo']}")
    return "\n".join(linhas)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Estrutura o pedido (B2) em projetos/<slug>/producao/<tema>.json")
    ap.add_argument("tarefa", type=Path, help="pedido padrão (.md) ou arquivo com a resposta do notion-fetch da tarefa")
    ap.add_argument("--tema", help="nome do arquivo (sem .json); padrão: o tema do pedido ou o título da capa")
    ap.add_argument("--saida", type=Path, help="grava neste caminho em vez de projetos/<slug>/producao/<tema>.json")
    ap.add_argument("--sobrescrever", action="store_true", help="permite substituir um JSON que já existe")
    ap.add_argument("--simular", action="store_true", help="mostra o JSON e o relatório, sem gravar")
    args = ap.parse_args(argv)

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    props, conteudo = ler_exportacao(args.tarefa)
    previa = estruturar(props, conteudo, None, None)  # só para saber slug e tema
    slug_proj = previa["projeto"]
    capa = next((s.get("titulo") for s in previa["slides"] if s["papel"] == "capa"), None) or previa["nome"]
    tema_pedido = re.sub(r"[^a-z0-9]+", "-", sem_acento((props.get("_tema") or "").lower())).strip("-")
    tema = args.tema or tema_pedido or slug(capa.replace("*", ""))
    pasta_proj = RAIZ / "projetos" / slug_proj / "producao"
    destino = args.saida or (pasta_proj / f"{tema}.json")

    d = estruturar(props, conteudo, pasta_proj, destino)
    texto = json.dumps(d, ensure_ascii=False, indent=2)

    if args.simular:
        print(texto)
        print()
        print(relatorio(d))
        print(f"\n(simulação) gravaria em {destino}")
        return 0
    if destino.exists() and not args.sobrescrever:
        print(f"PARADO: {destino} já existe. Use --tema, --saida ou --sobrescrever.", file=sys.stderr)
        return 1
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(texto + "\n", encoding="utf-8")
    print(relatorio(d))
    print(f"\ngravado: {destino}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
