#!/usr/bin/env python3
"""Mede a coerência de cor de fotos candidatas com as fotos reais do projeto (etapa B3).

A "régua" é a assinatura de cor do projeto, tirada das fotos de referência:
  1. a lista de fotos em projetos/<slug>/direcao-fotografica.md, se existir;
  2. senão, as fotos do projeto no catálogo com destaque = sim e origem real
     (decupagem ou legado).

Para cada foto mede seis coisas simples, no espaço Lab:
  brilho (média de L*), contraste (desvio de L*), saturação (croma médio),
  temperatura (b* médio: + quente/amarelo, - fria/azul), tom (a* médio: + rosado,
  - esverdeado) e paleta (distribuição de matiz das áreas com cor).

Cada medida vira um desvio em relação à régua (mediana das referências, em unidades
da variação normal do projeto). A distância é a média quadrática desses desvios.
Ordena as candidatas; não elimina nenhuma (regra não é filtro).

Não vê cenário, pessoas nem "cara de banco": isso continua sendo checagem visual.

Uso:
    python scripts/medir_coerencia.py <foto ou pasta> --projeto marca-exemplo
    python scripts/medir_coerencia.py prévias/ --projeto outra-marca --json
    python scripts/medir_coerencia.py foto.jpg --projeto marca-exemplo --referencias <pasta>

Requer Pillow; usa numpy se estiver instalado (mais rápido, mesmo resultado).
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import sys
import tempfile
from pathlib import Path

try:
    from PIL import Image, ImageOps
except ImportError:
    sys.exit("Falta o Pillow. Rode:  python -m pip install -r scripts/requirements.txt")

try:
    import numpy as np
except ImportError:  # numpy é opcional
    np = None

Image.MAX_IMAGE_PIXELS = None

RAIZ = Path(__file__).resolve().parent.parent
MIDIA = RAIZ / "midia"
CATALOGO = MIDIA / "catalogo.csv"
VERSAO = 1                 # muda quando o cálculo muda (invalida o cache)

LADO = 256                 # lado maior da miniatura medida
CROMA_COR = 8.0            # croma mínimo para um pixel "ter cor" (entra na paleta)
EXTENSOES = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff", ".bmp"}

# Medidas, na ordem de exibição: chave, nome, unidade de "variação mínima" (piso do
# desvio, para um projeto muito homogêneo não transformar diferença pequena em grande),
# e as palavras para acima / abaixo da régua.
MEDIDAS = [
    ("temperatura", "temperatura", 3.0, "{p}mais quente que o projeto", "{p}mais fria que o projeto"),
    ("saturacao", "saturação", 3.0, "saturação {p}acima", "saturação {p}abaixo (mais lavada)"),
    ("brilho", "brilho", 4.0, "{p}mais clara que o projeto", "{p}mais escura que o projeto"),
    ("contraste", "contraste", 2.5, "contraste {p}acima", "contraste {p}abaixo (mais chapada)"),
    ("tom", "tom", 2.0, "tom {p}puxado para o rosado", "tom {p}puxado para o verde"),
]
PISO_PALETA = 0.06
LIMITE_Z = 4.0             # um desvio enorme não domina sozinho a distância

# Faixas: |desvio| ≤ 1 dentro; ≤ 2 um pouco fora; > 2 fora.
FAIXAS = [(1.0, "dentro"), (2.0, "um pouco fora"), (math.inf, "fora")]
# Distância geral (média quadrática dos desvios).
NIVEIS = [(1.0, "coerente"), (2.0, "perto"), (math.inf, "destoa")]

# Matiz no Lab (graus, 0 = +a*, 90 = +b*). Faixas aproximadas, para explicar a paleta.
MATIZES = [(0, 30, "vermelho/rosa"), (30, 70, "laranja/pele"), (70, 110, "amarelo"),
           (110, 170, "verde"), (170, 230, "ciano"), (230, 290, "azul"),
           (290, 330, "roxo"), (330, 360, "magenta")]

AVISO_VISUAL = ("Mede só cor e luz. Cenário, pessoas (brasileiras, reais), naturalidade e "
                "\"cara de banco\" continuam sendo checagem visual, contra a direção fotográfica.")


# ---------------------------------------------------------------- cor

def _linear(c8: int) -> float:
    c = c8 / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


_LIN = [_linear(v) for v in range(256)]
# sRGB linear → XYZ (D65), já dividido pelo branco de referência.
_M = [(0.4124 / 0.95047, 0.3576 / 0.95047, 0.1805 / 0.95047),
      (0.2126, 0.7152, 0.0722),
      (0.0193 / 1.08883, 0.1192 / 1.08883, 0.9505 / 1.08883)]
_E = (6 / 29) ** 3


def _f(t: float) -> float:
    return t ** (1 / 3) if t > _E else t / (3 * (6 / 29) ** 2) + 4 / 29


def miniatura(caminho: Path) -> Image.Image:
    with Image.open(caminho) as im:
        im.draft("RGB", (LADO * 2, LADO * 2))  # JPEG decodifica já reduzido
        im = ImageOps.exif_transpose(im).convert("RGB")
        im.thumbnail((LADO, LADO), Image.BILINEAR)
        return im.copy()


def _lab_numpy(im: Image.Image):
    a = np.asarray(im, dtype=np.uint8).reshape(-1, 3)
    lin = np.array(_LIN)[a]
    xyz = lin @ np.array(_M).T
    f = np.where(xyz > _E, np.cbrt(xyz), xyz / (3 * (6 / 29) ** 2) + 4 / 29)
    L = 116 * f[:, 1] - 16
    A = 500 * (f[:, 0] - f[:, 1])
    B = 200 * (f[:, 1] - f[:, 2])
    return L, A, B


def _lab_puro(im: Image.Image):
    px = im.tobytes()
    L, A, B = [], [], []
    for r, g, b in zip(px[0::3], px[1::3], px[2::3]):
        lr, lg, lb = _LIN[r], _LIN[g], _LIN[b]
        fx = _f(_M[0][0] * lr + _M[0][1] * lg + _M[0][2] * lb)
        fy = _f(_M[1][0] * lr + _M[1][1] * lg + _M[1][2] * lb)
        fz = _f(_M[2][0] * lr + _M[2][1] * lg + _M[2][2] * lb)
        L.append(116 * fy - 16)
        A.append(500 * (fx - fy))
        B.append(200 * (fy - fz))
    return L, A, B


def assinatura(caminho: Path) -> dict:
    """As seis medidas de uma foto."""
    im = miniatura(caminho)
    if np is not None:
        L, A, B = _lab_numpy(im)
        croma = np.hypot(A, B)
        ang = np.degrees(np.arctan2(B, A)) % 360
        com_cor = croma > CROMA_COR
        hist, _ = np.histogram(ang[com_cor], bins=[m[0] for m in MATIZES] + [360],
                               weights=croma[com_cor])
        med = {"brilho": float(L.mean()), "contraste": float(L.std()),
               "saturacao": float(croma.mean()), "temperatura": float(B.mean()),
               "tom": float(A.mean())}
        hist = [float(h) for h in hist]
    else:
        L, A, B = _lab_puro(im)
        n = len(L)
        mL = sum(L) / n
        hist = [0.0] * len(MATIZES)
        croma_total = 0.0
        for a, b in zip(A, B):
            c = math.hypot(a, b)
            croma_total += c
            if c > CROMA_COR:
                ang = math.degrees(math.atan2(b, a)) % 360
                for i, (ini, fim, _) in enumerate(MATIZES):
                    if ini <= ang < fim:
                        hist[i] += c
                        break
        med = {"brilho": mL, "contraste": math.sqrt(sum((v - mL) ** 2 for v in L) / n),
               "saturacao": croma_total / n, "temperatura": sum(B) / n, "tom": sum(A) / n}
    total = sum(hist)
    med["paleta"] = [h / total for h in hist] if total else [0.0] * len(MATIZES)
    med["px"] = [im.width, im.height]
    return med


def dist_paleta(p: list[float], q: list[float]) -> float:
    """0 = mesma distribuição de matiz; 1 = nada em comum (1 - interseção)."""
    if not sum(p) or not sum(q):
        return 0.0  # foto quase sem cor: a paleta não diz nada
    return 1.0 - sum(min(a, b) for a, b in zip(p, q))


# ---------------------------------------------------------------- estatística

def mediana(v: list[float]) -> float:
    s = sorted(v)
    n = len(s)
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2


def espalhamento(v: list[float], piso: float) -> float:
    """Variação normal do projeto: 1,4826 × desvio absoluto mediano (robusto), com piso."""
    m = mediana(v)
    return max(1.4826 * mediana([abs(x - m) for x in v]), piso)


def nome_paleta(p: list[float], n: int = 2) -> str:
    top = sorted(range(len(p)), key=lambda i: -p[i])[:n]
    return " e ".join(f"{MATIZES[i][2]} {p[i] * 100:.0f}%" for i in top if p[i] > 0.05) or "quase sem cor"


def montar_regua(fotos: list[Path], fonte: str) -> dict:
    sigs, erros = [], []
    for f in fotos:
        try:
            sigs.append((f, assinatura(f)))
        except Exception as e:
            erros.append({"arquivo": str(f), "erro": str(e)})
    if not sigs:
        raise SystemExit("Nenhuma foto de referência pôde ser lida.")
    regua = {"fonte": fonte, "n": len(sigs), "medidas": {}, "erros": erros}
    for chave, _, piso, _, _ in MEDIDAS:
        v = [s[chave] for _, s in sigs]
        regua["medidas"][chave] = {"mediana": mediana(v), "variacao": espalhamento(v, piso),
                                   "min": min(v), "max": max(v)}
    k = len(MATIZES)
    centro = [sum(s["paleta"][i] for _, s in sigs) / len(sigs) for i in range(k)]
    tot = sum(centro) or 1.0
    centro = [c / tot for c in centro]
    dp = [dist_paleta(s["paleta"], centro) for _, s in sigs]
    regua["paleta"] = {"centro": centro, "mediana": mediana(dp), "variacao": espalhamento(dp, PISO_PALETA)}
    # Distância de cada referência à própria régua: calibra o que é "normal" no projeto.
    regua["dist_referencias"] = sorted(comparar(s, regua)["distancia"] for _, s in sigs)
    regua["referencias"] = [str(f) for f, _ in sigs]
    return regua


def faixa(z: float) -> str:
    for lim, nome in FAIXAS:
        if abs(z) <= lim:
            return nome
    return FAIXAS[-1][1]


def comparar(sig: dict, regua: dict) -> dict:
    itens, zs = [], []
    for chave, nome, _, acima, abaixo in MEDIDAS:
        r = regua["medidas"][chave]
        z = (sig[chave] - r["mediana"]) / r["variacao"]
        zs.append(max(-LIMITE_Z, min(LIMITE_Z, z)))
        f = faixa(z)
        if f == "dentro":
            frase = f"{nome} dentro"
        else:
            frase = (acima if z > 0 else abaixo).format(p="um pouco " if f == "um pouco fora" else "")
        itens.append({"medida": chave, "valor": round(sig[chave], 1), "regua": round(r["mediana"], 1),
                      "desvio": round(z, 2), "faixa": f, "frase": frase})
    rp = regua["paleta"]
    d = dist_paleta(sig["paleta"], rp["centro"])
    zp = max(0.0, (d - rp["mediana"]) / rp["variacao"])  # só "mais diferente que o normal" conta
    zs.append(min(LIMITE_Z, zp))
    fp = faixa(zp)
    frase = ("paleta dentro" if fp == "dentro"
             else f"paleta {'um pouco ' if fp == 'um pouco fora' else ''}diferente "
                  f"({nome_paleta(sig['paleta'])}; projeto: {nome_paleta(rp['centro'])})")
    itens.append({"medida": "paleta", "valor": round(d, 3), "regua": round(rp["mediana"], 3),
                  "desvio": round(zp, 2), "faixa": fp, "frase": frase})
    dist = math.sqrt(sum(z * z for z in zs) / len(zs))
    return {"distancia": round(dist, 2), "itens": itens}


def nivel(d: float) -> str:
    for lim, nome in NIVEIS:
        if d <= lim:
            return nome
    return NIVEIS[-1][1]


# ---------------------------------------------------------------- referências

PADRAO_CAMINHO = re.compile(r"(?:midia/)?((?:aberta|restrita)/[^\s`'\"()\[\]<>|,;]+?\.(?:jpe?g|png|webp|tiff?|bmp))",
                            re.IGNORECASE)


def refs_da_direcao(slug: str) -> tuple[list[Path], list[str]] | None:
    """Caminhos de midia/ citados em direcao-fotografica.md (na seção de referências, se houver)."""
    arq = RAIZ / "projetos" / slug / "direcao-fotografica.md"
    if not arq.exists():
        return None
    txt = arq.read_text(encoding="utf-8")
    # Se houver uma seção cujo título fala em "referência", lê só ela.
    secoes = re.split(r"(?m)^(#{1,6} .*)$", txt)
    trecho = ""
    for i in range(1, len(secoes) - 1, 2):
        if "refer" in secoes[i].lower():
            trecho += secoes[i + 1]
    achados = PADRAO_CAMINHO.findall(trecho or txt)
    vistos, fotos, faltam = set(), [], []
    for c in achados:
        if c in vistos:
            continue
        vistos.add(c)
        p = MIDIA / c
        (fotos if p.is_file() else faltam).append(p if p.is_file() else c)
    return fotos, faltam


def refs_do_catalogo(slug: str) -> list[Path]:
    with open(CATALOGO, encoding="utf-8-sig", newline="") as f:
        amostra = f.read(4096)
        f.seek(0)
        linhas = list(csv.DictReader(f, delimiter=";" if amostra.count(";") > amostra.count(",") else ","))
    fotos = []
    for l in linhas:
        projetos = {p.strip() for p in re.split(r"[,;]", l.get("projetos", ""))}
        origem = l.get("origem", "").split(":")[0].strip()
        if (slug in projetos and l.get("tipo") == "foto" and origem in ("decupagem", "legado")
                and l.get("destaque", "").strip().lower() == "sim"):
            p = MIDIA / l["arquivo"]
            if p.is_file():
                fotos.append(p)
    return fotos


def chave_cache(fotos: list[Path], fonte: str) -> str:
    h = hashlib.sha1(f"v{VERSAO}|{LADO}|{CROMA_COR}|{fonte}".encode())
    for f in sorted(fotos):
        st = f.stat()
        h.update(f"{f}|{st.st_size}|{int(st.st_mtime)}".encode())
    return h.hexdigest()[:16]


def obter_regua(slug: str, referencias: list[str] | None, pasta_cache: Path | None) -> tuple[dict, list[str]]:
    avisos = []
    if referencias:
        fotos, fonte = listar(referencias), "--referencias"
    else:
        d = refs_da_direcao(slug)
        fotos = []
        if d is not None:
            fotos, faltam = d
            for c in faltam:
                avisos.append(f"referência citada em direcao-fotografica.md não encontrada: {c}")
            if not fotos:
                avisos.append("direcao-fotografica.md existe, mas não cita fotos de midia/; usei o catálogo")
        fonte = f"projetos/{slug}/direcao-fotografica.md"
        if not fotos:
            fotos, fonte = refs_do_catalogo(slug), "catálogo: destaque = sim, origem decupagem/legado"
    if not fotos:
        raise SystemExit(f"Sem fotos de referência para o projeto '{slug}'.")
    if len(fotos) < 8:
        avisos.append(f"só {len(fotos)} fotos de referência: a régua é frágil")
    regua = None
    arq_cache = None
    if pasta_cache is not None:
        arq_cache = pasta_cache / f"{slug}-{chave_cache(fotos, fonte)}.json"
        if arq_cache.exists():
            try:
                regua = json.loads(arq_cache.read_text(encoding="utf-8"))
            except Exception:
                regua = None
    if regua is None:
        regua = montar_regua(fotos, fonte)
        if arq_cache is not None:
            try:
                arq_cache.parent.mkdir(parents=True, exist_ok=True)
                arq_cache.write_text(json.dumps(regua, ensure_ascii=False), encoding="utf-8")
            except OSError:
                pass
    else:
        regua["cache"] = str(arq_cache)
    for e in regua.get("erros", []):
        avisos.append(f"não li a referência {e['arquivo']}: {e['erro']}")
    return regua, avisos


# ---------------------------------------------------------------- entrada e saída

def listar(entradas: list[str]) -> list[Path]:
    arqs = []
    for e in entradas:
        p = Path(e)
        if p.is_dir():
            arqs += sorted(f for f in p.iterdir() if f.suffix.lower() in EXTENSOES)
        elif p.is_file():
            arqs.append(p)
        else:
            print(f"aviso: não encontrei {e}", file=sys.stderr)
    return arqs


def percentil_ref(d: float, dists: list[float]) -> int:
    """Que parte das próprias fotos do projeto fica mais perto da régua que a candidata."""
    return round(100 * sum(1 for x in dists if x < d) / len(dists)) if dists else 0


def resumo(itens: list[dict]) -> str:
    fora = [i for i in itens if i["faixa"] != "dentro"]
    fora.sort(key=lambda i: -abs(i["desvio"]))
    dentro = [i["medida"].replace("saturacao", "saturação") for i in itens if i["faixa"] == "dentro"]
    partes = [i["frase"] for i in fora]
    if dentro:
        partes.append(("dentro: " if fora else "tudo dentro: ") + ", ".join(dentro))
    return "; ".join(partes)


def texto(slug: str, regua: dict, resultados: list[dict], erros: list[dict], avisos: list[str]) -> str:
    m = regua["medidas"]
    l = [f"Coerência de cor com o projeto {slug} · régua: {regua['n']} fotos ({regua['fonte']})"
         + (" · do cache" if regua.get("cache") else ""),
         "Régua (mediana ± variação normal): "
         + " · ".join(f"{nome} {m[k]['mediana']:.1f}±{m[k]['variacao']:.1f}" for k, nome, *_ in MEDIDAS)
         + f" · paleta {nome_paleta(regua['paleta']['centro'], 3)}",
         "Distância: média quadrática dos desvios. <= 1 coerente · 1–2 perto · > 2 destoa", ""]
    for i, r in enumerate(resultados, 1):
        l.append(f"{i}. {Path(r['arquivo']).name}  distância {r['distancia']:.2f}  {r['nivel']}"
                 f"  (mais longe que {r['percentil_ref']}% das fotos do projeto)")
        l.append(f"   {r['resumo']}")
        l.append("   " + "  ".join(f"{it['medida'][:5]} {it['desvio']:+.1f}" for it in r["itens"]))
    l.append("")
    for e in erros:
        l.append(f"não li {e['arquivo']}: {e['erro']}")
    for a in avisos:
        l.append(f"aviso: {a}")
    l.append("Ordem, não filtro: nenhuma candidata é eliminada. " + AVISO_VISUAL)
    return "\n".join(l)


def main() -> int:
    for fluxo in (sys.stdout, sys.stderr):  # acentos no console do Windows
        try:
            fluxo.reconfigure(encoding="utf-8")
        except Exception:
            pass
    ap = argparse.ArgumentParser(description="Mede a coerência de cor das candidatas com as fotos do projeto (B3).")
    ap.add_argument("entradas", nargs="+", help="fotos candidatas ou pastas")
    ap.add_argument("--projeto", required=True, help="slug do projeto (ex.: marca-exemplo)")
    ap.add_argument("--referencias", nargs="+", metavar="FOTO_OU_PASTA",
                    help="usa estas fotos como régua, no lugar da direção fotográfica e do catálogo")
    ap.add_argument("--json", action="store_true", help="saída em JSON, para outras etapas")
    ap.add_argument("--cache", default=str(Path(tempfile.gettempdir()) / "coerencia-carrosseis"),
                    help="pasta do cache da régua (padrão: pasta temporária do sistema)")
    ap.add_argument("--sem-cache", action="store_true", help="recalcula a régua sem ler nem gravar cache")
    a = ap.parse_args()

    if not (RAIZ / "projetos" / a.projeto).is_dir():
        print(f"aviso: não existe projetos/{a.projeto}/", file=sys.stderr)
    regua, avisos = obter_regua(a.projeto, a.referencias, None if a.sem_cache else Path(a.cache))

    arqs = listar(a.entradas)
    if not arqs:
        print("Nenhuma imagem encontrada.", file=sys.stderr)
        return 1
    resultados, erros = [], []
    for f in arqs:
        try:
            sig = assinatura(f)
        except Exception as e:
            erros.append({"arquivo": str(f), "erro": str(e)})
            continue
        c = comparar(sig, regua)
        resultados.append({"arquivo": str(f), "distancia": c["distancia"], "nivel": nivel(c["distancia"]),
                           "percentil_ref": percentil_ref(c["distancia"], regua["dist_referencias"]),
                           "resumo": resumo(c["itens"]), "itens": c["itens"]})
    resultados.sort(key=lambda r: r["distancia"])

    if a.json:
        print(json.dumps({
            "projeto": a.projeto,
            "regua": {"fonte": regua["fonte"], "n": regua["n"], "cache": regua.get("cache"),
                      "medidas": {k: {kk: round(vv, 2) for kk, vv in v.items()} for k, v in regua["medidas"].items()},
                      "paleta": nome_paleta(regua["paleta"]["centro"], 3)},
            "parametros": {"lado": LADO, "croma_cor": CROMA_COR, "limite_desvio": LIMITE_Z,
                           "faixas": {"dentro": 1, "um pouco fora": 2}, "niveis": {"coerente": 1, "perto": 2},
                           "numpy": np is not None},
            "fotos": resultados, "erros": erros, "avisos": avisos, "aviso": AVISO_VISUAL,
        }, ensure_ascii=False, indent=2))
    else:
        print(texto(a.projeto, regua, resultados, erros, avisos))
    return 0


if __name__ == "__main__":
    sys.exit(main())
