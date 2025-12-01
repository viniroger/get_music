# Processador de Músicas com yt-dlp

O script Python aqui desenvolvido serve para automatizar o download e tratamento de arquivos de áudio a partir de URLs (principalmente YouTube), usando o utilitário [yt-dlp](https://www.monolitonimbus.com.br/extraindo-audio-de-videos-com-tags/). O código foi projetado para ser executado tanto em ambiente padrão do sistema quanto em ambientes isolados via **Conda**, quando necessário.

## 1. Visão Geral do Sistema

O script implementa uma **interface de linha de comando (CLI)** que permite dois modos principais de execução:

1. **Modo A** – Processamento manual de um único item:
   O usuário fornece um `url`, `artist` e `title` diretamente pelos argumentos da CLI.

2. **Modo B** – Processamento múltiplo a partir de playlist:
   O script lê um arquivo `playlist.csv` contendo colunas `url,artist,title` e processa cada linha de forma independente.

O objetivo central é garantir que o **yt-dlp** seja executado de forma segura e isolada, impedindo que falhas gerem arquivos erroneamente movidos, sobrescritos ou processados parcialmente.

## 2. Módulos e Dependências

O script depende exclusivamente da biblioteca padrão do Python. As chamadas externas (como `yt-dlp`) são feitas através de:

```python
subprocess.run(...)
```

A leitura do arquivo CSV utiliza:

```python
import csv
```

Opcionalmente, o usuário pode definir um ambiente virtual:

```python
CONDA_ENV = "py13"
```

Quando definida, o script executa os comandos dentro do ambiente Conda correspondente; quando `None`, o sistema usa o Python padrão.

## 3. Fluxo de Execução

### 3.1 Entrada da Linha de Comando

A CLI é definida com `argparse`, oferecendo três grupos de parâmetros:

* Argumentos diretos (`--url`, `--artist`, `--title`)
* Argumento de arquivo (`--playlist`)

O código garante que pelo menos uma fonte de dados seja informada:

```
python process.py --url <URL> --artist "Queen" --title "Bohemian Rhapsody"
python process.py --playlist playlist.csv
```

### 3.2 Construção do Comando yt-dlp

O script constrói dinamicamente a lista de argumentos a ser executada por `subprocess.run`:

```python
cmd = [
    "yt-dlp",
    "-x", "--audio-format", "mp3",
    "--embed-metadata",
    "--embed-thumbnail",
    "-o", f"{artist} - {title}.%(ext)s",
    url
]
```

Esse comando nunca é concatenado como string — ele é passado como **lista**, eliminando problemas de escape de shell e aumentando a segurança.

### 3.3 Execução via subprocess.run

O código usa:

```python
result = subprocess.run(cmd, check=True, capture_output=True, text=True)
```

As opções permitem:

* `check=True` → se `yt-dlp` falhar, é levantada uma `CalledProcessError`
  → **o processamento da música é abortado imediatamente**, impedindo efeitos colaterais.

* `capture_output=True` e `text=True`
  → logs ficam disponíveis em `result.stdout` e `result.stderr`

Esse comportamento é crucial para evitar que:

* arquivos incorretos sejam movidos
* arquivos parcialmente gerados sejam tratados como válidos
* o processamento continue com dados inválidos

### 3.4 Execução com ou sem ambiente Conda

O script detecta automaticamente se deve envolver o comando dentro de um ambiente Conda:

#### **Caso 1: sem Conda (`conda_env=None`)**

O comando é executado diretamente:

```python
subprocess.run(cmd, ...)
```

#### **Caso 2: com Conda**

O comando é envolvido em uma chamada a `conda run`:

```python
full_cmd = ["conda", "run", "-n", conda_env] + cmd
subprocess.run(full_cmd, ...)
```

Isso permite:

* trocar rapidamente o ambiente Conda em uma única variável
* usar diferentes ambientes em diferentes máquinas
* evitar problemas com `conda activate` dentro de scripts

## 4. Processamento em Lote (playlist.csv)

O arquivo `playlist.csv` deve conter:

```csv
url,artist,title
https://youtube.com/... , Artist1 , Title1
https://youtube.com/... , Artist2 , Title2
```

O loop:

```python
for row in reader:
    process_item(row["url"], row["artist"], row["title"])
```

Cada linha é tratada isoladamente e independentemente.

* Se um item falhar, ele é ignorado e o script segue para o próximo
* Logs são agrupados item por item
* Não há interferência cruzada entre downloads

Isso evita que um erro interrompa toda a lista.

## 5. Robustez e Tratamento de Erros

### 5.1 Falhas do yt-dlp

Qualquer erro no download levanta uma exceção:

```python
except subprocess.CalledProcessError as e:
```

Isso impede execução posterior indevida.

### 5.2 Falhas de metadados

O script sempre valida:

* existência de URL
* existência de artist e title
* formato do CSV
* número de colunas correto

### 5.3 Falhas de ambiente

Se o ambiente Conda especificado não existir, o erro será claramente exibido pelo Conda.

## 6. Layout Geral do Código

Um resumo da arquitetura:

```
get_music.py
 ├── parse_args()
 ├── main()
 ├── process_item(url, artist, title)
 ├── run_yt_dlp(cmd)
 ├── load_csv(playlist_path)
 └── build_command(url, artist, title)
```

Cada função tem uma única responsabilidade, seguindo boas práticas de:

* modularização
* clareza
* testabilidade
* reuso

## 7. Extensões Futuras

O design atual permite facilmente adicionar:

* saída em formatos diferentes (flac, opus, wav)
* tratamento posterior (ex.: normalização, renomeação, mover para pastas)
* integração com bases externas (Spotify API, MusicBrainz)
* paralelização com `concurrent.futures`
* logging detalhado para auditoria

Disclaimer: O uso do yt-dlp deve ser sempre realizado em conformidade com as leis de direitos autorais e com os termos de serviço das plataformas de origem. O software em si é uma ferramenta legítima de código aberto, mas baixar ou distribuir conteúdo protegido sem autorização pode violar a legislação aplicável ou os termos de uso dos serviços acessados. Utilize-o apenas para conteúdos de sua autoria, de domínio público, licenciados para download ou cuja permissão explícita tenha sido concedida. O usuário é o único responsável por assegurar que seu uso esteja em plena conformidade legal.

