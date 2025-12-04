#!/usr/bin/env python3
import csv
from yt_dlp import YoutubeDL

def extrair_artista_titulo(nome):
    if " - " in nome:
        artista, titulo = nome.split(" - ", 1)
    else:
        artista = ""
        titulo = nome
    return artista.strip(), titulo.strip()

def salvar_playlist_csv(url_playlist, arquivo_saida="playlist.csv"):
    ydl_opts = {
        "quiet": True,
        "extract_flat": True,   # não baixa nada, só lista vídeos
        "skip_download": True
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url_playlist, download=False)

    entries = info.get("entries", [])

    with open(arquivo_saida, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        #writer.writerow(["url", "artista", "titulo"])

        for item in entries:
            url = f"https://www.youtube.com/watch?v={item['id']}"
            artista, titulo = extrair_artista_titulo(item.get("title", ""))
            writer.writerow([url, artista, titulo])

    print(f"Arquivo salvo com sucesso: {arquivo_saida}")


# ---------- Exemplo de uso ----------
url = "COLE_A_URL_DA_PLAYLIST_AQUI"
salvar_playlist_csv(url)
