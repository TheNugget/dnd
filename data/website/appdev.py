import streamlit as st
import requests
import argparse
#from langchain.vectorstores import Chroma
from langchain_chroma import Chroma

#from langchain.embeddings import HuggingFaceEmbeddings
#from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings


import os

# 🧠 Dynamically get host IP (fallback to localhost if it fails)
import subprocess

def get_host_ip():
    commands = [
        "ip route | awk '/default/ { print $3 }'",
        "route -n | awk '/^0.0.0.0/ { print $2 }'"
    ]
    for cmd in commands:
        try:
            result = subprocess.run(
                ["sh", "-c", cmd],
                capture_output=True,
                text=True,
                check=True
            )
            ip = result.stdout.strip()
            if ip:
                return f"http://{ip}:11434"
        except Exception:
            continue
    return "http://localhost:11434"

# 🎛️ Argument Parsing

default_vectorstore_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "chroma", "dnd"))


parser = argparse.ArgumentParser(description="D&D SRD Assistant Configuration")
parser.add_argument("--ollama_url", default=get_host_ip(), help="Ollama server URL")
parser.add_argument("--model_name", default="llama3:8b", help="LLM model name")
parser.add_argument("--vectorstore_dir", default=default_vectorstore_dir, help="Path to Chroma vectorstore")
parser.add_argument("--collection_name", default="dnd_web_crawl", help="Chroma collection name")
parser.add_argument("--temperature", type=float, default=0, help="LLM temperature")

args = parser.parse_args()

# 🔧 Configs from arguments
OLLAMA_URL = args.ollama_url
MODEL_NAME = args.model_name
VECTORSTORE_DIR = args.vectorstore_dir
COLLECTION_NAME = args.collection_name
TEMP = args.temperature

# 🧠 Prompt Template
SYSTEM_PROMPT = """You are an expert Dungeon Master AI assistant.
You respond accurately and concisely, strictly within the bounds of 
SRD (System Reference Document) legal Dungeons & Dragons 5e content.
Do not speculate or provide unofficial information. If unsure, say you don't know.
Always begin your answer with a summary of the SRD section it comes from. Use numbered steps if describing mechanics."""

# 🧠 Embedding + Vector Store
embedder = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
db = Chroma(embedding_function=embedder, persist_directory=VECTORSTORE_DIR, collection_name=COLLECTION_NAME)

# 🔍 Search functions
def search_chroma_debug(query, top_k=5):
    st.markdown("#### 🧪 Debug: Searching Chroma")
    try:
        results = db.similarity_search_with_score(query, k=top_k)
        st.write(f"🔍 Found {len(results)} results.")
        for i, (doc, score) in enumerate(results):
            st.markdown(f"**Result {i+1}:**")
            st.write(f"- Score: `{score:.2f}`")
            st.write(f"- Metadata: `{doc.metadata}`")
            st.write(f"- Content preview: `{doc.page_content[:200]}...`")
        return [{
            "text": doc.page_content,
            "meta": doc.metadata,
            "score": score
        } for doc, score in results]
    except Exception as e:
        st.error(f"❌ Error during Chroma search: {e}")
        return []

def search_chroma(query, top_k=5):
    results = db.similarity_search_with_score(query, k=top_k)
    return [{
        "text": doc.page_content,
        "meta": doc.metadata,
        "score": score
    } for doc, score in results]

# 🧠 Ollama call
def query_ollama(system_prompt, user_prompt):
    payload = {
        "model": MODEL_NAME,
        "prompt": f"<|system|>\n{system_prompt}\n<|user|>\n{user_prompt}",
        "temperature": TEMP,
        "stream": False
    }
    response = requests.post(f"{OLLAMA_URL}/api/generate", json=payload)
    response.raise_for_status()
    return response.json()["response"]

# 🎨 Streamlit UI
st.set_page_config(page_title="D&D SRD Assistant", layout="centered")
st.title("🧙 D&D 5e SRD Assistant")
st.markdown("Ask me anything about the official Dungeons & Dragons 5e System Reference Document.")

query = st.text_input("🗨️ Your question", placeholder="e.g. How does grappling work?")
top_k = st.slider("🔍 Number of relevant documents", min_value=1, max_value=10, value=5)

if st.button("Ask"):
    if query.strip() == "":
        st.warning("Please enter a question.")
    else:
        with st.spinner("Searching ChromaDB..."):
            results = search_chroma(query, top_k=top_k)
            context = "\n\n".join([r["text"] for r in results])
            metadata = results[0]["meta"] if results else {}

        with st.spinner("Querying LLM..."):
            full_prompt = f"{context}\n\nQuestion: {query}"
            answer = query_ollama(SYSTEM_PROMPT, full_prompt)

        st.markdown("### 🧠 Answer")
        st.write(answer)

        st.markdown("### 📚 Sources")
        for i, r in enumerate(results):
            url = r["meta"].get("url", "#")
            title = r["meta"].get("title", f"Document {i+1}")
            score = r["score"]
            content = r["text"]

            with st.expander(f"📄 {title} — Score: `{score:.2f}`"):
                st.markdown(f"[🔗 Source Link]({url})")
                st.write(content)
