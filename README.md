# 🧙‍♂️ DND Web Assistant

**DND Web Assistant** is a powerful tool designed to scrape websites and build a ChromaDB for use with your existing [Ollama](https://ollama.com/) server. It enables semantic querying and reasoning over structured documentation — ideal for developers, researchers, and dungeon masters alike. 

---

## 🚀 Features

- Scrapes sites and extracts structured content
- Builds a ChromaDB for fast semantic search
- Integrates seamlessly with Ollama for advanced querying
- Dockerized for easy deployment and portability

---

## 🛠 Installation

Clone the repository:
    git clone https://github.com/TheNugget/dnd.git
    cd dnd

Build the Docker image:

```bash
docker build -t chroma-backend .

Run the container: you can remove --rm if you want it to be static.

docker run -it --rm \
  -p 6022:22 \
  -p 6001:6001 \
  -p 6002:6002 \
  -p 6003:6003 \
  -p 6004:6004 \
  -v "$(pwd)/data:/data" \
  --name chroma-backend \
  chroma-backend

## 🧾 Scripts Overview

### `data/scripts/populatechroma.py`

This script is the core web crawler that scrapes sites and populates a ChromaDB collection with the extracted content. My recommendation is to use the defaults and just pass it a url to start crawling. Once you have it working you can adjust.  By default is does recreate the db so it will overwrite the existing chromadb.

#### 🔧 Arguments

| Argument            | Type   | Description                                                                 |
|---------------------|--------|-----------------------------------------------------------------------------|
| `--root-url`        | `str`  | **Required.** The root URL to begin crawling from.                          |
| `--max-depth`       | `int`  | Maximum depth to crawl. Default is `3`.                                     |
| `--max-threads`     | `int`  | Number of concurrent threads for crawling. Default is `10`.                 |
| `--chroma-path`     | `str`  | Path to store ChromaDB data. Default is `../chroma`.                        |
| `--collection-name` | `str`  | Name of the ChromaDB collection to populate. Default is `"web_crawl"`.     |

#### 🏃‍♂️ Example Usage

```bash
python data/scripts/populatechroma.py \
  --root-url https://example-mkdocs-site.com \
  --max-depth 2 \
  --max-threads 5 \
  --chroma-path ./data/chroma \
  --collection-name mkdocs_docs

### `data/scripts/getdoccount.py`

This utility script connects to a ChromaDB instance and reports the number of documents in the first available collection.

#### 🔧 Arguments

| Argument        | Type   | Description                                      |
|-----------------|--------|--------------------------------------------------|
| `<folder_path>` | `str`  | **Required.** Path to the ChromaDB storage folder.|

#### 🏃‍♂️ Example Usage

```bash
python data/scripts/getdoccount.py /app/data/chroma

#### 📋 Output Example

Collection name: mkdocs_docs
Number of documents: 128

If no collections are found, the script will print:
No collections found in the database.

### `data/website/appdev.py`

This script launches a Streamlit-based web app that serves as a Dungeons & Dragons 5e SRD assistant. It uses a local Ollama LLM and ChromaDB to answer user questions based strictly on SRD-compliant content. Make sure that the ollama server is accessible from this container or location.  Also make sure that the model is available on the ollama server.

#### 🧠 Features

- Streamlit UI for interactive querying
- Embedding-based document retrieval using HuggingFace and ChromaDB
- LLM-powered responses via Ollama
- Debug mode for inspecting vector search results
- SRD-compliant prompt enforcement

#### 🔧 Arguments

| Argument             | Type    | Description                                                                 |
|----------------------|---------|-----------------------------------------------------------------------------|
| `--ollama_url`       | `str`   | URL of the Ollama server. Defaults to auto-detected host IP.               |
| `--model_name`       | `str`   | Name of the LLM model to use. Default is `"llama3:8b"`.                     |
| `--vectorstore_dir`  | `str`   | Path to ChromaDB vectorstore. Defaults to `../chroma`.                      |
| `--collection_name`  | `str`   | Name of the ChromaDB collection. Default is `"web_crawl"`.                  |
| `--temperature`      | `float` | LLM temperature setting. Default is `0`.                                    |

#### 🏃‍♂️ Example Usage

```bash
python data/website/appdev.py \
  --ollama_url http://localhost:11434 \
  --model_name llama3:8b \
  --vectorstore_dir ./data/chroma \
  --collection_name mkdocs_docs \
  --temperature 0.7


### 🛠️ `supervisor.conf`

This configuration file is used to manage the Streamlit-based D&D SRD Assistant via **Supervisor**, ensuring it runs continuously and restarts automatically if it crashes.

#### ⚙️ Configuration Overview

```ini
[supervisord]
nodaemon=true

[program:streamlit]
command=streamlit run /app/data/website/appdev.py --server.port 6001
directory=/app
autostart=true
autorestart=true
stderr_logfile=/var/log/streamlit.err.log
stdout_logfile=/var/log/streamlit.out.log

### 🚪 `entrypoint.sh`

This shell script serves as the container entrypoint, launching **Supervisor** to manage the Streamlit app and then opening an interactive shell.

#### 📄 Script Contents

```bash
#!/bin/bash

# Start supervisord in the background, fully detached
nohup /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf > /var/log/supervisord.out 2>&1 &

# Optional: wait a moment to ensure it's started
sleep 1

# Drop into interactive shell
exec bash




