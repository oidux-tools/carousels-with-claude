#!/usr/bin/env python3
"""Indexador do banco de mídia.

Percorre midia/, lê as especificações técnicas de cada arquivo e atualiza
midia/catalogo.csv. As colunas manuais (projetos, tags, origem) nunca são
sobrescritas; `projetos` só é sugerido pelo nome do arquivo quando está vazio.
As colunas `usos` e `ultimo_uso` são sempre recalculadas a partir do log
midia/usos.csv (uma linha por imagem usada em peça entregue).

Uso:
    python scripts/indexar_midia.py             atualiza o catálogo
    python scripts/indexar_midia.py --simular   mostra o que mudaria, sem gravar
    python scripts/indexar_midia.py --limpar    também tira do catálogo arquivos que não existem mais

Requer Pillow:  python -m pip install -r scripts/requirements.txt
"""
from __future__ import annotations

import argparse
import csv
import io
import os
import re
import struct
import sys
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    sys.exit("Falta o Pillow. Rode:  python -m pip install -r scripts/requirements.txt")

Image.MAX_IMAGE_PIXELS = None  # fotos grandes de banco são normais; só lemos o cabeçalho

COLUNAS = ["arquivo", "area", "tipo", "formato", "largura", "altura", "proporcao",
           "duracao_s", "tamanho_mb", "projetos", "tags", "origem", "adicionado_em",
           "usos", "ultimo_uso"]
COLUNAS_USOS = ["data", "arquivo", "projeto", "peca", "tarefa_notion", "slide", "tema"]
DATA_VALIDA = re.compile(r"^\d{4}-\d{2}-\d{2}$")

IGNORAR = {".gitkeep", "desktop.ini", "thumbs.db", ".ds_store"}
NOME_VALIDO = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*_[a-z0-9]+(?:-[a-z0-9]+)*(?:_\d{2})?\.[a-z0-9]+$")

PROPORCOES = {"1:1": 1.0, "4:5": 0.8, "5:4": 1.25, "3:4": 0.75, "4:3": 4 / 3, "2:3": 2 / 3,
              "3:2": 1.5, "9:16": 9 / 16, "16:9": 16 / 9, "1.91:1": 1.91}

MINIMOS = {"foto": "lado menor >= 1080 px", "fundo": ">= 1080 x 1350 px"}


def abaixo_do_minimo(tipo: str, w: int, h: int) -> bool:
    if tipo == "foto":
        return min(w, h) < 1080
    if tipo == "fundo":
        return min(w, h) < 1080 or max(w, h) < 1350
    return False


def proporcao(w, h) -> str:
    """Encaixa na proporção comum mais próxima (tolerância de 2%); senão, devolve decimal."""
    if not w or not h:
        return ""
    r = w / h
    for nome, alvo in PROPORCOES.items():
        if abs(r - alvo) / alvo <= 0.02:
            return nome
    return f"{r:.2f}:1"


# ---------------------------------------------------------------- leitores

def ler_imagem(caminho: Path) -> dict:
    with Image.open(caminho) as img:
        w, h = img.size
        try:
            if img.getexif().get(0x0112) in (5, 6, 7, 8):  # foto de celular girada via EXIF
                w, h = h, w
        except Exception:
            pass
    return {"largura": w, "altura": h}


def _px(valor):
    m = re.fullmatch(r"\s*(\d+(?:\.\d+)?|\.\d+)\s*(?:px)?\s*", valor or "")
    return float(m.group(1)) if m else None


def ler_svg(caminho: Path) -> dict:
    with open(caminho, "rb") as f:
        for _, raiz in ET.iterparse(f, events=("start",)):
            w, h = _px(raiz.get("width")), _px(raiz.get("height"))
            if not (w and h) and raiz.get("viewBox"):
                partes = re.split(r"[\s,]+", raiz.get("viewBox").strip())
                if len(partes) == 4:
                    w, h = float(partes[2]), float(partes[3])
            return {"largura": round(w), "altura": round(h)} if w and h else {}
    return {}


def _caixas(dados: bytes, inicio: int = 0, fim: int | None = None):
    """Itera (tipo, início do conteúdo, fim) das caixas MP4/MOV dentro de `dados`."""
    fim = len(dados) if fim is None else fim
    pos = inicio
    while pos + 8 <= fim:
        tam, tipo = struct.unpack(">I4s", dados[pos:pos + 8])
        cab = 8
        if tam == 1:
            tam, cab = struct.unpack(">Q", dados[pos + 8:pos + 16])[0], 16
        elif tam == 0:
            tam = fim - pos
        if tam < cab:
            return
        yield tipo, pos + cab, min(pos + tam, fim)
        pos += tam


def _ler_moov(f) -> bytes | None:
    """Acha a caixa 'moov' (metadados) sem carregar o vídeo inteiro."""
    f.seek(0, 2)
    total, pos = f.tell(), 0
    while pos + 8 <= total:
        f.seek(pos)
        cab = f.read(16)
        tam, tipo = struct.unpack(">I4s", cab[:8])
        n = 8
        if tam == 1:
            tam, n = struct.unpack(">Q", cab[8:16])[0], 16
        elif tam == 0:
            tam = total - pos
        if tam < n:
            return None
        if tipo == b"moov":
            f.seek(pos + n)
            return f.read(tam - n)
        pos += tam
    return None


def ler_mp4(caminho: Path) -> dict:
    with open(caminho, "rb") as f:
        moov = _ler_moov(f)
    if not moov:
        return {}
    info = {}
    for tipo, ini, fim in _caixas(moov):
        if tipo == b"mvhd":
            if moov[ini] == 1:
                escala, dur = struct.unpack(">IQ", moov[ini + 20:ini + 32])
            else:
                escala, dur = struct.unpack(">II", moov[ini + 12:ini + 20])
            if escala:
                info["duracao_s"] = dur / escala
        elif tipo == b"trak" and "largura" not in info:
            for t2, i2, _ in _caixas(moov, ini, fim):
                if t2 != b"tkhd":
                    continue
                m = i2 + (52 if moov[i2] == 1 else 40)  # início da matriz de transformação
                a, _b, _u, _c, d = struct.unpack(">5i", moov[m:m + 20])
                w, h = (v >> 16 for v in struct.unpack(">II", moov[m + 36:m + 44]))
                if w and h:  # trilha de áudio tem 0 x 0
                    if a == 0 and d == 0:  # vídeo gravado em pé (rotação 90°/270°)
                        w, h = h, w
                    info["largura"], info["altura"] = w, h
    return info


def ler_wav(caminho: Path) -> dict:
    with open(caminho, "rb") as f:
        riff, _, wave = struct.unpack("<4sI4s", f.read(12))
        if riff != b"RIFF" or wave != b"WAVE":
            return {}
        bytes_por_s = None
        while True:
            cab = f.read(8)
            if len(cab) < 8:
                return {}
            cid, tam = struct.unpack("<4sI", cab)
            if cid == b"data":
                return {"duracao_s": tam / bytes_por_s} if bytes_por_s else {}
            if cid == b"fmt ":
                bytes_por_s = struct.unpack("<I", f.read(tam)[8:12])[0]
            else:
                f.seek(tam, 1)
            if tam % 2:
                f.seek(1, 1)


_KBPS = {1: [0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320],
         2: [0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160]}
_HZ = [44100, 48000, 32000]


def ler_mp3(caminho: Path) -> dict:
    tamanho = caminho.stat().st_size
    with open(caminho, "rb") as f:
        cab = f.read(10)
        inicio = 0
        if cab[:3] == b"ID3":  # pula a tag ID3v2 (capa, título…)
            inicio = 10 + ((cab[6] & 0x7F) << 21 | (cab[7] & 0x7F) << 14 | (cab[8] & 0x7F) << 7 | (cab[9] & 0x7F))
            if cab[5] & 0x10:
                inicio += 10
        f.seek(inicio)
        bloco = f.read(64 * 1024)
    for i in range(len(bloco) - 4):
        if bloco[i] != 0xFF or (bloco[i + 1] & 0xE0) != 0xE0:
            continue
        versao = (bloco[i + 1] >> 3) & 3  # 3 = MPEG1, 2 = MPEG2, 0 = MPEG2.5
        camada = (bloco[i + 1] >> 1) & 3  # 1 = Layer III
        br, hz = bloco[i + 2] >> 4, (bloco[i + 2] >> 2) & 3
        if versao == 1 or camada != 1 or br in (0, 15) or hz == 3:
            continue
        mpeg1 = versao == 3
        taxa = _HZ[hz] // (1 if mpeg1 else 2 if versao == 2 else 4)
        mono = (bloco[i + 3] >> 6) == 3
        xing = i + 4 + ((17 if mono else 32) if mpeg1 else (9 if mono else 17))
        if bloco[xing:xing + 4] in (b"Xing", b"Info"):  # VBR: o cabeçalho traz o nº de quadros
            if struct.unpack(">I", bloco[xing + 4:xing + 8])[0] & 1:
                quadros = struct.unpack(">I", bloco[xing + 8:xing + 12])[0]
                return {"duracao_s": quadros * (1152 if mpeg1 else 576) / taxa}
        kbps = _KBPS[1 if mpeg1 else 2][br]  # CBR: estimativa por tamanho
        return {"duracao_s": (tamanho - inicio - i) * 8 / (kbps * 1000)}
    return {}


LEITORES = {
    **dict.fromkeys(["jpg", "jpeg", "png", "webp", "gif", "bmp", "tif", "tiff", "psd"], ler_imagem),
    "svg": ler_svg,
    **dict.fromkeys(["mp4", "mov", "m4v", "m4a"], ler_mp4),
    "wav": ler_wav,
    "mp3": ler_mp3,
}


# ---------------------------------------------------------------- catálogo

def carregar_catalogo(caminho: Path) -> tuple[dict, list]:
    """Devolve (linhas por arquivo, colunas extras que alguém tenha criado à mão)."""
    if not caminho.exists():
        return {}, []
    texto = caminho.read_text(encoding="utf-8-sig")  # tolera BOM do Excel
    primeira = texto.split("\n", 1)[0]
    sep = ";" if primeira.count(";") > primeira.count(",") else ","  # Excel pt-BR salva com ;
    leitor = csv.DictReader(io.StringIO(texto), delimiter=sep)
    extras = [c for c in (leitor.fieldnames or []) if c and c not in COLUNAS]
    linhas = {}
    for linha in leitor:
        chave = (linha.get("arquivo") or "").strip().replace("\\", "/")
        if chave:
            linha["arquivo"] = chave
            linhas[chave] = linha
    return linhas, extras


def carregar_projetos(caminho: Path) -> set:
    if not caminho.exists():
        return set()
    with open(caminho, encoding="utf-8-sig", newline="") as f:
        return {(l.get("slug") or "").strip() for l in csv.DictReader(f)} - {""}


def carregar_usos(caminho: Path, projetos_validos: set, avisos: list) -> dict:
    """Lê o log de usos e devolve {arquivo: (quantidade, data mais recente)}."""
    if not caminho.exists():
        return {}
    texto = caminho.read_text(encoding="utf-8-sig")
    primeira = texto.split("\n", 1)[0]
    sep = ";" if primeira.count(";") > primeira.count(",") else ","
    leitor = csv.DictReader(io.StringIO(texto), delimiter=sep)
    faltando = [c for c in COLUNAS_USOS if c not in (leitor.fieldnames or [])]
    if faltando:
        avisos.append(f"usos.csv: faltam as colunas {', '.join(faltando)}")
    contagem, vistos = {}, set()
    for n, l in enumerate(leitor, start=2):  # linha 1 é o cabeçalho
        arquivo = (l.get("arquivo") or "").strip().replace("\\", "/")
        data = (l.get("data") or "").strip()
        projeto = (l.get("projeto") or "").strip()
        if not any((v or "").strip() for v in l.values()):
            continue
        if not arquivo:
            avisos.append(f"usos.csv linha {n}: sem arquivo (ignorada)")
            continue
        if not DATA_VALIDA.match(data):
            avisos.append(f"usos.csv linha {n}: data '{data}' fora do formato AAAA-MM-DD")
        if projetos_validos and projeto and projeto not in projetos_validos:
            avisos.append(f"usos.csv linha {n}: projeto '{projeto}' não está em projetos.csv")
        chave = (arquivo, (l.get("peca") or "").strip(), (l.get("slide") or "").strip())
        if chave in vistos:
            avisos.append(f"usos.csv linha {n}: repete arquivo + peça + slide de uma linha anterior")
        vistos.add(chave)
        qtd, ultima = contagem.get(arquivo, (0, ""))
        ultima = max(ultima, data) if DATA_VALIDA.match(data) else ultima
        contagem[arquivo] = (qtd + 1, ultima)
    return contagem


def gerar_csv(linhas: list, colunas: list) -> str:
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=colunas, extrasaction="ignore", lineterminator="\n")
    w.writeheader()
    for linha in linhas:
        w.writerow({c: linha.get(c) or "" for c in colunas})
    return buf.getvalue()


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    ap = argparse.ArgumentParser(description="Atualiza midia/catalogo.csv a partir dos arquivos do banco.")
    ap.add_argument("--midia", type=Path, default=Path(__file__).resolve().parent.parent / "midia",
                    help="pasta do banco (padrão: midia/ do repositório)")
    ap.add_argument("--simular", action="store_true", help="mostra o resultado sem gravar o catálogo")
    ap.add_argument("--limpar", action="store_true", help="tira do catálogo arquivos que não existem mais")
    args = ap.parse_args()

    midia = args.midia.resolve()
    if not midia.is_dir():
        print(f"Pasta não encontrada: {midia}")
        return 1
    arq_catalogo = midia / "catalogo.csv"
    catalogo, extras = carregar_catalogo(arq_catalogo)
    projetos_validos = carregar_projetos(midia / "projetos.csv")
    colunas = COLUNAS + extras
    hoje = date.today().isoformat()

    novos, alterados, avisos, vistos = [], [], [], set()
    na_entrada = 0
    usos = carregar_usos(midia / "usos.csv", projetos_validos, avisos)

    def listar(pasta: Path) -> list:
        return sorted(a for a in pasta.rglob("*")
                      if a.is_file() and a.name.lower() not in IGNORAR
                      and not a.name.startswith(("~$", "_")))

    def subpastas(pasta: Path) -> list:
        return sorted(p for p in pasta.iterdir() if p.is_dir() and not p.name.startswith((".", "_")))

    # duas áreas: aberta/<tipo>/ e restrita/<projeto>/<tipo>/ (decisão de 2026-11-14)
    grupos = []  # (area, tipo, arquivos)
    for pasta in sorted(p for p in midia.iterdir() if p.is_dir() and not p.name.startswith(".")):
        if pasta.name.startswith("_"):  # _entrada/ e afins não entram no catálogo
            na_entrada += len(listar(pasta))
        elif pasta.name == "aberta":
            grupos += [("aberta", t.name, listar(t)) for t in subpastas(pasta)]
        elif pasta.name == "restrita":
            for proj in subpastas(pasta):
                if projetos_validos and proj.name not in projetos_validos:
                    avisos.append(f"restrita/{proj.name}/: projeto não está em projetos.csv")
                grupos += [(f"restrita:{proj.name}", t.name, listar(t)) for t in subpastas(proj)]
        else:
            avisos.append(f"{pasta.name}/: pasta fora do padrão (use aberta/ ou restrita/<projeto>/); não catalogada")

    for area, tipo, arquivos in grupos:
        for arq in arquivos:
            rel = arq.relative_to(midia).as_posix()
            vistos.add(rel)
            ext = arq.suffix.lower().lstrip(".")

            tec = {}
            if ext in LEITORES:
                try:
                    tec = LEITORES[ext](arq) or {}
                except Exception as e:
                    avisos.append(f"{rel}: não consegui ler as especificações ({e.__class__.__name__})")
            w, h, dur = tec.get("largura"), tec.get("altura"), tec.get("duracao_s")

            linha = catalogo.get(rel)
            eh_novo = linha is None
            if eh_novo:
                linha = {"arquivo": rel, "adicionado_em": hoje}
                catalogo[rel] = linha
                novos.append(rel)
            antes = {c: linha.get(c) or "" for c in colunas}

            linha.update({
                "area": area,
                "tipo": tipo,
                "formato": ext,
                "largura": str(w) if w else "",
                "altura": str(h) if h else "",
                "proporcao": proporcao(w, h),
                "duracao_s": f"{dur:.1f}" if dur else "",
                "tamanho_mb": f"{arq.stat().st_size / 1_048_576:.2f}",
                "usos": str(usos.get(rel, (0, ""))[0]),
                "ultimo_uso": usos.get(rel, (0, ""))[1],
            })

            prefixo = arq.name.split("_", 1)[0] if "_" in arq.name else ""
            if not (linha.get("projetos") or "").strip():
                if area.startswith("restrita:"):
                    linha["projetos"] = area.split(":", 1)[1]  # na restrita, o projeto é a pasta
                elif prefixo in projetos_validos:
                    linha["projetos"] = prefixo  # sugestão pelo nome; quem edita à mão manda

            if not eh_novo and antes !={c: linha.get(c) or "" for c in colunas}:
                alterados.append(rel)

            if not NOME_VALIDO.match(arq.name):
                avisos.append(f"{rel}: nome fora da convenção <projeto>_<descricao>_<nn>.<ext>")
            elif projetos_validos and prefixo not in projetos_validos:
                avisos.append(f"{rel}: projeto '{prefixo}' não está em projetos.csv")
            desconhecidos = [s for s in (linha.get("projetos") or "").split("|")
                             if s.strip() and s.strip() not in projetos_validos]
            if projetos_validos and desconhecidos:
                avisos.append(f"{rel}: coluna projetos tem slug desconhecido: {', '.join(desconhecidos)}")
            if w and h and abaixo_do_minimo(tipo, w, h):
                avisos.append(f"{rel}: {w}x{h} px, abaixo do mínimo para {tipo} ({MINIMOS[tipo]})")

    ausentes = sorted(set(catalogo) - vistos)
    if args.limpar:
        for rel in ausentes:
            del catalogo[rel]
    for rel in ausentes:  # linha mantida sem arquivo: os usos continuam vindo do log
        if rel in catalogo:
            catalogo[rel]["usos"] = str(usos.get(rel, (0, ""))[0])
            catalogo[rel]["ultimo_uso"] = usos.get(rel, (0, ""))[1]
    for arquivo in sorted(set(usos) - set(catalogo)):
        avisos.append(f"usos.csv: '{arquivo}' não está no catálogo ({usos[arquivo][0]} uso(s) sem imagem correspondente)")

    texto_novo = gerar_csv([catalogo[k] for k in sorted(catalogo)], colunas)
    texto_atual = arq_catalogo.read_text(encoding="utf-8-sig") if arq_catalogo.exists() else ""

    # ---- relatório
    print(f"Banco de mídia: {midia}")
    print(f"  {len(vistos)} arquivo(s) catalogado(s): {len(novos)} novo(s), {len(alterados)} alterado(s)")
    for rel in novos:
        print(f"    + {rel}")
    for rel in alterados:
        print(f"    ~ {rel}")
    if na_entrada:
        print(f"  {na_entrada} arquivo(s) em _entrada/ esperando triagem")
    if ausentes:
        acao = "removido(s) do catálogo" if args.limpar else "no catálogo sem arquivo (use --limpar para tirar)"
        print(f"  {len(ausentes)} {acao}:")
        for rel in ausentes:
            print(f"    - {rel}")
    if avisos:
        print(f"\nAvisos ({len(avisos)}):")
        for a in avisos:
            print(f"  ! {a}")

    if args.simular:
        print("\nSimulação: nada foi gravado.")
    elif texto_novo == texto_atual:
        print("\nCatálogo já estava em dia.")
    else:
        tmp = arq_catalogo.with_name("catalogo.csv.tmp")
        try:
            tmp.write_text(texto_novo, encoding="utf-8", newline="")
            os.replace(tmp, arq_catalogo)
        except PermissionError:
            tmp.unlink(missing_ok=True)
            print("\nNão consegui gravar: o catálogo está aberto em outro programa (Excel?). Feche e rode de novo.")
            return 1
        print("\nCatálogo atualizado.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
