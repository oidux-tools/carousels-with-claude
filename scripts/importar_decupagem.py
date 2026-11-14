#!/usr/bin/env python3
"""Importa uma pasta de decupagem para o banco de mídia.

A decupagem (feita fora deste repositório) entrega:
    <origem>/<Pessoa ou assunto>/<Pessoa>_<NNN>[_destaque].<ext>
    <origem>/catalogo.csv   (separado por ;, uma linha por arquivo, coluna "arquivo" e "pasta")

O importador:
  - copia cada foto em versão otimizada (lado maior 2400 px), sem metadados além de autor e
    copyright; vídeos vão como estão;
  - área aberta (padrão): midia/aberta/<tipo>/<projeto>_<grupo>-<NNN>.<ext>, onde <grupo> é o
    nome da pasta (ex.: marca-exemplo_ensaio-praia-003.jpg);
  - área restrita (--area restrita): midia/restrita/<projeto>/<tipo>/<projeto>_<codigo>-<NNN>.<ext>,
    onde <codigo> é "r" + 6 caracteres aleatórios, estável por pasta. A tradução código → nome fica
    em midia/restrita/<projeto>/_chave.json (só quem tem acesso à área vê). O nome da pasta também
    é trocado pelo código nos textos que vão para o catálogo;
  - leva as colunas da decupagem para midia/catalogo.csv (menos as que identificam a origem);
  - roda o indexador no fim para preencher as especificações técnicas.

Os originais nunca são alterados. Reimportar é seguro: arquivos já copiados são mantidos e
as colunas vindas da decupagem são atualizadas a partir dela.

Uso:
    python scripts/importar_decupagem.py <origem> --projeto marca-exemplo --simular
    python scripts/importar_decupagem.py <origem> --projeto marca-exemplo --area restrita --pastas "Nome da Pessoa"
    python scripts/importar_decupagem.py <origem> --projeto outra-marca --area restrita --sem-codigo
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import secrets
import subprocess
import sys
import unicodedata
from datetime import date
from pathlib import Path

from PIL import Image, ImageOps

sys.path.insert(0, str(Path(__file__).resolve().parent))
from indexar_midia import COLUNAS, carregar_catalogo, carregar_projetos, gerar_csv  # noqa: E402

FOTOS = {"jpg", "jpeg", "png", "webp", "tif", "tiff", "heic"}
VIDEOS = {"mp4", "mov", "m4v"}
# colunas da decupagem que não vão para o banco: identificam a origem ou o banco já calcula
NAO_IMPORTAR = {"arquivo", "pasta", "projeto", "numero", "tipo", "orientacao"}
LADO_MAXIMO = 2400


def slug(texto: str) -> str:
    t = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def ler_decupagem(origem: Path) -> list[dict]:
    texto = (origem / "catalogo.csv").read_text(encoding="utf-8-sig")
    primeira = texto.split("\n", 1)[0]
    sep = ";" if primeira.count(";") > primeira.count(",") else ","
    return list(csv.DictReader(texto.splitlines(), delimiter=sep))


ALFABETO = "23456789abcdefghjkmnpqrstuvwxyz"  # sem 0/o, 1/l/i: não se confundem na leitura


def carregar_chave(caminho: Path) -> dict:
    """{codigo: {"nome": ..., ...}} da área restrita do projeto."""
    if not caminho.exists():
        return {}
    return json.loads(caminho.read_text(encoding="utf-8"))


def gravar_chave(caminho: Path, chave: dict) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    tmp = caminho.with_suffix(".tmp")
    tmp.write_text(json.dumps(chave, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(caminho)


def novo_codigo(usados: set) -> str:
    while True:
        codigo = "r" + "".join(secrets.choice(ALFABETO) for _ in range(6))
        if codigo not in usados:
            return codigo


def tirar_nome(valor: str, pasta: str, codigo: str) -> str:
    """Troca nome completo, nome colado (NomeSobrenome) e cada parte do nome (nome, sobrenome) pelo código."""
    partes = [pasta, pasta.replace(" ", "")] + [p for p in pasta.split() if len(p) >= 4]
    for nome in partes:
        if len(nome) >= 3:
            valor = re.sub(r"\b" + re.escape(nome) + r"\b", codigo, valor, flags=re.IGNORECASE)
    return valor


def copiar_foto(orig: Path, dest: Path) -> None:
    with Image.open(orig) as img:
        exif = img.getexif()
        img = ImageOps.exif_transpose(img)
        img.thumbnail((LADO_MAXIMO, LADO_MAXIMO), Image.LANCZOS)
        limpo = Image.Exif()
        for tag in (315, 33432):  # autor, copyright: créditos ficam; GPS, câmera e XMP saem
            if exif.get(tag):
                limpo[tag] = exif[tag]
        img.convert("RGB").save(dest, "JPEG", quality=85, optimize=True, progressive=True, exif=limpo)


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    raiz = Path(__file__).resolve().parent.parent
    ap = argparse.ArgumentParser(description="Importa uma pasta de decupagem para o banco de mídia.")
    ap.add_argument("origem", type=Path, help="pasta da decupagem (com catalogo.csv)")
    ap.add_argument("--projeto", required=True, help="slug de midia/projetos.csv")
    ap.add_argument("--area", choices=["aberta", "restrita"], default="aberta",
                    help="aberta (padrão) ou restrita: na restrita, cada pasta vira um código e o nome fica na _chave.json")
    ap.add_argument("--sem-codigo", action="store_true",
                    help="na área restrita, mantém o nome da pasta (use quando as pastas não são pessoas, ex.: datas de captação)")
    ap.add_argument("--lote", default="", help="nome do lote, guardado na chave da área restrita")
    ap.add_argument("--pastas", nargs="+", help="importa só estas pastas (para testar)")
    ap.add_argument("--origem-midia", default="", help="valor da coluna origem (propria, cliente, banco:x…)")
    ap.add_argument("--midia", type=Path, default=raiz / "midia", help="pasta do banco (padrão: midia/)")
    ap.add_argument("--simular", action="store_true", help="mostra o que faria, sem copiar nem gravar")
    args = ap.parse_args()

    origem, midia = args.origem.resolve(), args.midia.resolve()
    if args.projeto not in carregar_projetos(midia / "projetos.csv"):
        print(f"Projeto '{args.projeto}' não está em midia/projetos.csv.")
        return 1
    linhas = ler_decupagem(origem)
    if args.pastas:
        linhas = [l for l in linhas if l["pasta"] in args.pastas]

    restrita = args.area == "restrita"
    codificar = restrita and not args.sem_codigo
    base = midia / "restrita" / args.projeto if restrita else midia / "aberta"
    prefixo_rel = f"restrita/{args.projeto}" if restrita else "aberta"
    arq_chave = base / "_chave.json"
    chave = carregar_chave(arq_chave) if codificar else {}
    catalogo, extras = carregar_catalogo(midia / "catalogo.csv")
    hoje = date.today().isoformat()
    avisos, copiados, mantidos, nomes_trocados = [], 0, 0, 0
    novas_colunas = []

    # códigos estáveis: a mesma pasta mantém o código de importações anteriores
    codigo_da_pasta = {}
    if codificar:
        por_nome = {v.get("nome"): k for k, v in chave.items()}
        for pasta in sorted({l["pasta"] for l in linhas}):
            codigo = por_nome.get(pasta) or novo_codigo(set(chave))
            chave.setdefault(codigo, {"nome": pasta, "lote": args.lote, "adicionado_em": hoje})
            codigo_da_pasta[pasta] = codigo

    for l in linhas:
        pasta, nome = l["pasta"], l["arquivo"]
        orig = origem / pasta / nome
        if not orig.exists():
            avisos.append(f"{pasta}/{nome}: está no catálogo da decupagem, mas o arquivo não existe")
            continue
        ext = orig.suffix.lower().lstrip(".")
        partes = orig.stem.split("_")
        numero = partes[1] if len(partes) > 1 else slug(orig.stem)
        grupo = codigo_da_pasta[pasta] if codificar else slug(pasta)
        if ext in FOTOS:
            tipo, ext_dest = "foto", "jpg"
        elif ext in VIDEOS:
            tipo, ext_dest = "video", ext
        else:
            avisos.append(f"{pasta}/{nome}: formato .{ext} não importado")
            continue
        rel = f"{prefixo_rel}/{tipo}/{args.projeto}_{grupo}-{numero.lower()}.{ext_dest}"
        dest = midia / rel

        if dest.exists():
            mantidos += 1
        else:
            copiados += 1
            if not args.simular:
                dest.parent.mkdir(parents=True, exist_ok=True)
                if tipo == "foto":
                    copiar_foto(orig, dest)
                else:
                    dest.write_bytes(orig.read_bytes())

        linha = catalogo.setdefault(rel, {"arquivo": rel, "adicionado_em": hoje})
        linha["projetos"] = linha.get("projetos") or args.projeto
        if args.origem_midia and not linha.get("origem"):
            linha["origem"] = args.origem_midia
        linha["grupo"] = grupo
        for col, valor in l.items():
            if not col or col in NAO_IMPORTAR:
                continue
            valor = (valor or "").strip()
            if codificar and valor:
                novo = tirar_nome(valor, pasta, grupo)
                nomes_trocados += novo != valor
                valor = novo
            if col in COLUNAS:  # coluna que o banco também tem: só preenche se estiver vazia
                if valor and not linha.get(col):
                    linha[col] = valor
                continue
            linha[col] = valor
            if col not in extras and col not in novas_colunas:
                novas_colunas.append(col)

    for pasta in sorted({p.name for p in origem.iterdir() if p.is_dir()} & {l["pasta"] for l in linhas}):
        no_catalogo = {l["arquivo"] for l in linhas if l["pasta"] == pasta}
        for a in sorted((origem / pasta).iterdir()):
            if a.is_file() and a.name not in no_catalogo and a.name.lower() != "desktop.ini":
                avisos.append(f"{pasta}/{a.name}: arquivo sem linha no catálogo da decupagem (não importado)")

    colunas = COLUNAS + [c for c in extras if c != "grupo"]
    colunas += ["grupo"] + [c for c in novas_colunas if c not in colunas]

    print(f"Decupagem: {origem}")
    print(f"  {len(linhas)} linha(s) lida(s): {copiados} arquivo(s) a copiar, {mantidos} já no banco")
    print(f"  Área: {prefixo_rel}/")
    if codificar:
        print(f"  {len(codigo_da_pasta)} pasta(s) com código; chave em {arq_chave} (só a área restrita vê)")
        print(f"  {nomes_trocados} campo(s) de texto tinham o nome da pasta e receberam o código")
    if avisos:
        print(f"\nAvisos ({len(avisos)}):")
        for a in avisos[:15]:
            print(f"  ! {a}")
        if len(avisos) > 15:
            print(f"  … e mais {len(avisos) - 15}")

    if args.simular:
        print("\nSimulação: nada foi copiado nem gravado.")
        return 0
    if codificar:
        gravar_chave(arq_chave, chave)
    (midia / "catalogo.csv").write_text(gerar_csv([catalogo[k] for k in sorted(catalogo)], colunas),
                                        encoding="utf-8", newline="")
    print("\nCatálogo atualizado. Rodando o indexador…\n", flush=True)
    return subprocess.call([sys.executable, str(Path(__file__).with_name("indexar_midia.py")),
                            "--midia", str(midia)])


if __name__ == "__main__":
    sys.exit(main())
