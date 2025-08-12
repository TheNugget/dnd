import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from concurrent.futures import ThreadPoolExecutor
import threading
import hashlib
import chromadb
from chromadb.config import Settings
import argparse


parser = argparse.ArgumentParser(description="Web crawler for indexing pages.")
parser.add_argument('--root-url', type=str, required=True, help='The root URL to start crawling from.')
parser.add_argument('--max-depth', type=int, default=3, help='Maximum crawl depth.')
parser.add_argument('--max-threads', type=int, default=10, help='Number of concurrent threads.')
parser.add_argument('--chroma-path', type=str, default="../chroma/dnd", help='Path to ChromaDB storage.')
parser.add_argument('--collection-name', type=str, default="dnd_web_crawl", help='Name of the ChromaDB collection.')
args = parser.parse_args()



# 🧠 Thread-safe visited set
visited = set()
visited_lock = threading.Lock()

# 🚀 ChromaDB setup
client = chromadb.PersistentClient(path=args.chroma_path)

try:
    client.delete_collection(name=args.collection_name)
except chromadb.errors.NotFoundError:
    print(f"⚠️ Collection '{args.collection_name}' does not exist. Skipping deletion.")

collection = client.get_or_create_collection(name=args.collection_name)

# 🧠 Utility functions
def get_page_title(soup):
    return soup.title.string.strip() if soup.title and soup.title.string else "Untitled"

def get_text_content2(soup):
    for tag in soup(["script", "style", "noscript", "nav", "footer", "header", ".sidebar"]):
        tag.decompose()
    return soup.get_text(separator="\n", strip=True)

def get_text_content(soup):
    soup_clone = BeautifulSoup(str(soup), "html.parser")
    for tag in soup_clone(["script", "style", "noscript", "nav", "footer", "header", "aside"]):
        tag.decompose()
    return soup_clone.get_text(separator="\n", strip=True)

def generate_filename(url):
    return hashlib.md5(url.encode("utf-8")).hexdigest()

# 🕸️ Crawl function
def crawl(url, depth, root_url, executor):
    parsed_root = urlparse(root_url)
    root_domain = parsed_root.netloc

    normalized_url = urljoin(root_url, url)
    parsed_url = urlparse(normalized_url)

    if parsed_url.scheme not in ["http", "https"]:
        return
    if parsed_url.netloc != root_domain:
        return

    with visited_lock:
        if normalized_url in visited or depth <= 0:
            return
        visited.add(normalized_url)

    try:
        response = requests.get(normalized_url, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"❌ Failed to fetch {normalized_url}: {e}")
        return

    soup = BeautifulSoup(response.text, "html.parser")
    title = get_page_title(soup)
    text = get_text_content(soup)
    filename = generate_filename(normalized_url)
    path = parsed_url.path + ("?" + parsed_url.query if parsed_url.query else "")

    # Extract root URL (scheme + netloc)
    parsed_url = urlparse(normalized_url)
    root_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    full_url = normalized_url  # already normalized



    collection.add(
        documents=[text],
        metadatas=[{
            "filename": filename,
            "title": title,
            "path": path,
            "url": normalized_url
        }],
        ids=[filename]
    )
    print(f"✅ Indexed: {title} ({normalized_url})")

    for link in soup.find_all("a", href=True):
        href = link['href']
        next_url = urljoin(normalized_url, href)
        executor.submit(crawl, next_url, depth - 1, root_url, executor)

# 🏁 Run the crawler
if __name__ == "__main__":

    ROOT_URL = args.root_url
    MAX_DEPTH = args.max_depth
    MAX_THREADS = args.max_threads

    executor = ThreadPoolExecutor(max_workers=MAX_THREADS)
    crawl(ROOT_URL, MAX_DEPTH, ROOT_URL, executor)
    executor.shutdown(wait=True)
