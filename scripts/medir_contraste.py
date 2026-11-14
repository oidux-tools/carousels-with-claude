#!/usr/bin/env python3
"""Mede o contraste do texto creme sobre cada foto, por posição do bloco de texto (etapa B3).

Para cada imagem, recorta como o slide recortaria (preencher, centralizado), aplica a
camada Contraste (#141414 a 10% em Linear Burn) e compara o creme do texto (#F0EBDC)
com o 95º percentil da luminância do fundo atrás do bloco (bloco + folga), em cinco
posições: sup-esq, sup-dir, inf-esq, inf-dir e centro.

Ordena posições e fotos; não elimina nada (regra não é filtro). Não vê rostos nem a
emenda do spread: essas continuam sendo checagem visual.

Uso:
    python scripts/medir_contraste.py foto1.jpg foto2.jpg
    python scripts/medir_contraste.py <pasta> --formato spread
    python scripts/medir_contraste.py <pasta> --bloco 700x400 --json

Requer Pillow; usa numpy se estiver instalado (mais rápido e com resolução cheia).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    from PIL import Image, ImageOps, ImageStat
except ImportError:
    sys.exit("Falta o Pillow. Rode:  python -m pip install -r scripts/requirements.txt")

try:
    import numpy as np
except ImportError:  # numpy é opcional
    np = None

Image.MAX_IMAGE_PIXELS = None

# ---------------------------------------------------------------- parâmetros da marca

W, H = 1080, 1350          # slide do Instagram (4:5)
MARGEM = 90                # margem do slide
BLOCO_PADRAO = (570, 480)  # bloco de texto aproximado (largura x altura)
FOLGA = 40                 # "bloco + 40 px": 20 px de cada lado
CREME = (240, 235, 220)    # #F0EBDC
CONTRASTE_RGB = 20         # #141414
CONTRASTE_OPAC = 0.10      # 10%, Linear Burn
PERCENTIL = 95

META = 4.5                 # recomendado
MINIMO = 3.0               # inegociável
LIMITE_MOVIMENTO = 40.0    # desvio-padrão do cinza (0–255) acima do qual o fundo é "movimentado"

POSICOES = ["sup-esq", "sup-dir", "inf-esq", "inf-dir", "centro"]
EXTENSOES = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff", ".bmp"}

AVISO_VISUAL = ("Rosto e emenda não são medidos: confira no screenshot da mesa "
                "(texto sobre rosto e corte seco na emenda são inegociáveis).")


# ---------------------------------------------------------------- cor

def _linear(c8: float) -> float:
    c = c8 / 255.0
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def luminancia(rgb) -> float:
    r, g, b = rgb
    return 0.2126 * _linear(r) + 0.7152 * _linear(g) + 0.0722 * _linear(b)


L_CREME = luminancia(CREME)


def razao(l_fundo: float) -> float:
    claro, escuro = max(L_CREME, l_fundo), min(L_CREME, l_fundo)
    return (claro + 0.05) / (escuro + 0.05)


def _camada_contraste(v: float) -> float:
    """Linear Burn de #141414 a 10% sobre um canal (0–255)."""
    queimado = max(0.0, v + CONTRASTE_RGB - 255)
    return (1 - CONTRASTE_OPAC) * v + CONTRASTE_OPAC * queimado


# Tabela por canal: valor 0–255 → contribuição linear já com a camada Contraste.
_TAB = [_linear(_camada_contraste(v)) for v in range(256)]
_PESOS = (0.2126, 0.7152, 0.0722)


# ---------------------------------------------------------------- imagem

def preencher(im: Image.Image, w: int, h: int) -> Image.Image:
    """Recorte tipo FILL centralizado (como a foto entra no slide)."""
    s = max(w / im.width, h / im.height)
    im = im.resize((max(w, round(im.width * s)), max(h, round(im.height * s))), Image.LANCZOS)
    x, y = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))


class Luminancias:
    """Mapa de luminância do slide, com numpy (resolução cheia) ou sem (1 a cada 2 px)."""

    def __init__(self, slide: Image.Image):
        if np is not None:
            tab = np.array(_TAB)
            a = np.asarray(slide, dtype=np.uint8)
            self.mapa = (_PESOS[0] * tab[a[..., 0]] + _PESOS[1] * tab[a[..., 1]]
                         + _PESOS[2] * tab[a[..., 2]])
            self.passo = 1
        else:
            self.passo = 2
            red = slide.resize((slide.width // 2, slide.height // 2), Image.NEAREST)
            t = [[p * v for v in _TAB] for p in _PESOS]
            px = red.tobytes()  # RGB intercalado
            dados = [t[0][r] + t[1][g] + t[2][b] for r, g, b in zip(px[0::3], px[1::3], px[2::3])]
            self.largura = red.width
            self.mapa = dados

    def percentil(self, caixa, pct: float) -> float:
        x0, y0, x1, y1 = caixa
        if np is not None:
            return float(np.percentile(self.mapa[y0:y1, x0:x1], pct))
        p = self.passo
        x0, y0, x1, y1 = x0 // p, y0 // p, x1 // p, y1 // p
        vals = []
        for y in range(y0, y1):
            base = y * self.largura
            vals.extend(self.mapa[base + x0:base + x1])
        vals.sort()
        k = (len(vals) - 1) * pct / 100
        i = int(k)
        j = min(i + 1, len(vals) - 1)
        return vals[i] + (vals[j] - vals[i]) * (k - i)


def caixas(bloco: tuple[int, int]) -> dict[str, tuple[int, int, int, int]]:
    """Área medida em cada posição: o bloco encostado na margem, mais a folga, dentro do slide."""
    bw, bh = bloco
    f = FOLGA // 2
    xs = {"esq": MARGEM, "dir": W - MARGEM - bw, "meio": (W - bw) // 2}
    ys = {"sup": MARGEM, "inf": H - MARGEM - bh, "meio": (H - bh) // 2}
    pos = {"sup-esq": ("esq", "sup"), "sup-dir": ("dir", "sup"), "inf-esq": ("esq", "inf"),
           "inf-dir": ("dir", "inf"), "centro": ("meio", "meio")}
    r = {}
    for nome, (cx, cy) in pos.items():
        x, y = xs[cx], ys[cy]
        r[nome] = (max(0, x - f), max(0, y - f), min(W, x + bw + f), min(H, y + bh + f))
    return r


def nivel(r: float, movimentado: bool) -> str:
    if r < MINIMO:
        return "abaixo"
    if r < META or movimentado:
        return "revisar"
    return "ok"


ORDEM_NIVEL = {"ok": 0, "revisar": 1, "abaixo": 2}


def medir_slide(slide: Image.Image, bloco, metade: str | None, limite: float) -> list[dict]:
    lum = Luminancias(slide)
    cinza = slide.convert("L")
    res = []
    for nome, caixa in caixas(bloco).items():
        r = razao(lum.percentil(caixa, PERCENTIL))
        desvio = ImageStat.Stat(cinza.crop(caixa)).stddev[0]
        mov = desvio > limite
        notas = []
        if mov:
            notas.append("fundo movimentado")
        # No spread, o lado de dentro de cada metade fica junto da emenda.
        if (metade == "esq" and nome.endswith("dir")) or (metade == "dir" and nome.endswith("esq")):
            notas.append("junto da emenda")
        res.append({"posicao": nome, "razao": round(r, 2), "nivel": nivel(r, mov),
                    "variacao": round(desvio, 1), "notas": notas})
    # Melhor primeiro: nível, depois longe da emenda, depois razão.
    res.sort(key=lambda p: (ORDEM_NIVEL[p["nivel"]], "junto da emenda" in p["notas"], -p["razao"]))
    return res


def analisar(caminho: Path, formato: str, bloco, limite: float = LIMITE_MOVIMENTO) -> dict:
    with Image.open(caminho) as im:
        im = ImageOps.exif_transpose(im).convert("RGB")
    if formato == "spread":
        s = preencher(im, 2 * W, H)
        metades = {"esq": medir_slide(s.crop((0, 0, W, H)), bloco, "esq", limite),
                   "dir": medir_slide(s.crop((W, 0, 2 * W, H)), bloco, "dir", limite)}
    else:
        metades = {"slide": medir_slide(preencher(im, W, H), bloco, None, limite)}
    # Nota da foto: a pior das melhores posições (no spread, as duas metades precisam de texto).
    melhores = [m[0] for m in metades.values()]
    pior = min(melhores, key=lambda p: (-ORDEM_NIVEL[p["nivel"]], p["razao"]))
    return {"arquivo": str(caminho), "formato": formato, "origem_px": list(im.size),
            "nivel": pior["nivel"], "melhor_razao": pior["razao"], "metades": metades}


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


def bloco_arg(txt: str) -> tuple[int, int]:
    try:
        w, h = (int(v) for v in txt.lower().split("x"))
    except ValueError:
        raise argparse.ArgumentTypeError("use LARGURAxALTURA, ex.: 570x480")
    if not (0 < w <= W - 2 * MARGEM and 0 < h <= H - 2 * MARGEM):
        raise argparse.ArgumentTypeError(f"o bloco precisa caber na área útil ({W - 2 * MARGEM}x{H - 2 * MARGEM})")
    return w, h


def texto(resultados: list[dict], bloco, erros: list[dict]) -> str:
    l = [f"Contraste do creme #F0EBDC · camada Contraste ligada · bloco {bloco[0]}x{bloco[1]} + {FOLGA} px",
         f"ok >= {META} · revisar {MINIMO}–{META} ou fundo movimentado · abaixo < {MINIMO}", ""]
    for r in resultados:
        l.append(f"{Path(r['arquivo']).name}  ({r['formato']}, {r['origem_px'][0]}x{r['origem_px'][1]})")
        for metade, posicoes in r["metades"].items():
            pre = "  " if metade == "slide" else f"  [{metade}] "
            for p in posicoes:
                notas = f"  · {', '.join(p['notas'])}" if p["notas"] else ""
                l.append(f"{pre}{p['posicao']:<8} {p['razao']:>5.2f}:1  {p['nivel']:<8}"
                         f" variação {p['variacao']:>5.1f}{notas}")
        l.append("")
    if resultados:
        l.append("Ordem das fotos (melhor primeiro; nada é eliminado):")
        for i, r in enumerate(resultados, 1):
            onde = " / ".join(ps[0]["posicao"] if m == "slide" else f"{m} {ps[0]['posicao']}"
                              for m, ps in r["metades"].items())
            l.append(f"  {i}. {Path(r['arquivo']).name:<40} {r['melhor_razao']:>5.2f}:1  {r['nivel']:<8} {onde}")
        l.append("")
    for e in erros:
        l.append(f"não li {e['arquivo']}: {e['erro']}")
    l.append(AVISO_VISUAL)
    return "\n".join(l)


def main() -> int:
    for fluxo in (sys.stdout, sys.stderr):  # acentos no console do Windows
        try:
            fluxo.reconfigure(encoding="utf-8")
        except Exception:
            pass
    ap = argparse.ArgumentParser(description="Mede o contraste do texto creme por posição, para ordenar fotos (B3).")
    ap.add_argument("entradas", nargs="+", help="imagens ou pastas")
    ap.add_argument("--formato", choices=["slide", "spread"], default="slide",
                    help="slide 1080x1350 (padrão) ou spread 2160x1350 medido em duas metades")
    ap.add_argument("--bloco", type=bloco_arg, default=BLOCO_PADRAO,
                    help=f"tamanho aproximado do bloco de texto, LxA (padrão {BLOCO_PADRAO[0]}x{BLOCO_PADRAO[1]})")
    ap.add_argument("--json", action="store_true", help="saída em JSON, para outras etapas")
    ap.add_argument("--limite-movimento", type=float, default=LIMITE_MOVIMENTO,
                    help=f"desvio-padrão do cinza acima do qual o fundo conta como movimentado (padrão {LIMITE_MOVIMENTO:g})")
    a = ap.parse_args()

    arqs = listar(a.entradas)
    if not arqs:
        print("Nenhuma imagem encontrada.", file=sys.stderr)
        return 1
    resultados, erros = [], []
    for f in arqs:
        try:
            resultados.append(analisar(f, a.formato, a.bloco, a.limite_movimento))
        except Exception as e:  # arquivo corrompido ou formato que o Pillow não abre
            erros.append({"arquivo": str(f), "erro": str(e)})
    resultados.sort(key=lambda r: (ORDEM_NIVEL[r["nivel"]], -r["melhor_razao"]))

    if a.json:
        print(json.dumps({
            "parametros": {"creme": "#F0EBDC", "camada": "#141414 10% Linear Burn", "percentil": PERCENTIL,
                           "slide": [W, H], "margem": MARGEM, "bloco": list(a.bloco), "folga": FOLGA,
                           "meta": META, "minimo": MINIMO, "limite_movimento": a.limite_movimento,
                           "numpy": np is not None},
            "fotos": resultados, "erros": erros, "aviso": AVISO_VISUAL,
        }, ensure_ascii=False, indent=2))
    else:
        print(texto(resultados, a.bloco, erros))
    return 0


if __name__ == "__main__":
    sys.exit(main())
