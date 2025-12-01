#!/usr/bin/env python3
import argparse
import csv
import subprocess
import shlex
import glob
import os
from pathlib import Path
import sys

# ============================
# CONFIGURAÇÃO DO AMBIENTE
# ============================
# Se quiser usar um ambiente Conda específico:
CONDA_ENV = "py13"
# Se quiser usar o ambiente padrão do sistema (sem conda):
# CONDA_ENV = None
# ============================

def baixar(url, artist, title, ext="opus"):
    print(f"\n🔽 Baixando: {artist} - {title}\nURL: {url}\n")

	# Decide se usa conda ou não
    if CONDA_ENV:
        cmd = ["conda", "run", "-n", CONDA_ENV, "yt-dlp"]
    else:
        cmd = ["yt-dlp"]
    # Executa comando principal
    subprocess.run(
        cmd + [
            "-x", url,
            "--postprocessor-args",
            f"-metadata artist={shlex.quote(artist)} -metadata title={shlex.quote(title)}"
        ],
        check=True
    )

    # Encontra o arquivo .opus mais recente
    files = sorted(glob.glob("*.opus"), key=os.path.getmtime)
    if not files:
        raise RuntimeError("Nenhum arquivo .opus encontrado após o download.")

    filename_in = files[-1]
    filename_out = f"{artist} - {title}.{ext}"

    # Renomeia
    os.rename(filename_in, filename_out)

    # Move para ~/Downloads
    downloads = Path.home() / "Downloads"
    target = downloads / filename_out
    os.rename(filename_out, target)

    print(f"✅ Salvo em: {target}")


def ler_playlist_csv(path):
    itens = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row or len(row) < 3:
                continue
            url, artist, title = row[0].strip(), row[1].strip(), row[2].strip()
            itens.append((url, artist, title))
    return itens


def main():
    parser = argparse.ArgumentParser(
        description="Baixa áudios do YouTube com metadados, via CSV ou via argumentos diretos."
    )

    # Argumentos diretos
    parser.add_argument("--url", help="URL do vídeo")
    parser.add_argument("--artist", help="Artista")
    parser.add_argument("--title", help="Título")

    # CSV
    parser.add_argument(
        "--playlist",
        help="Arquivo CSV com colunas url,artist,title"
    )

    args = parser.parse_args()

    # ---- Validação de modo de operação ----
    usando_csv = args.playlist is not None
    usando_args = args.url or args.artist or args.title

    if usando_csv and usando_args:
        print("❌ Erro: não use CSV e argumentos diretos ao mesmo tempo.")
        sys.exit(1)

    # Caso 1: entrada direta
    if usando_args:
        if not (args.url and args.artist and args.title):
            print("❌ Erro: --url, --artist e --title devem ser usados juntos.")
            sys.exit(1)

        baixar(args.url, args.artist, args.title)
        return

    # Caso 2: arquivo CSV (playlist.csv padrão, se não for fornecido)
    playlist_path = args.playlist if args.playlist else "playlist.csv"

    if not os.path.exists(playlist_path):
        print(f"❌ Arquivo CSV não encontrado: {playlist_path}")
        sys.exit(1)

    itens = ler_playlist_csv(playlist_path)

    if not itens:
        print("❌ Nenhuma linha válida encontrada no CSV.")
        sys.exit(1)

    for url, artist, title in itens:
        baixar(url, artist, title)


if __name__ == "__main__":
    main()
