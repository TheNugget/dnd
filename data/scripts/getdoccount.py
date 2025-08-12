import chromadb
from chromadb.config import Settings
import sys

def main(folder_path):
    # Initialize Chroma client with persistent storage
    client = chromadb.PersistentClient(path=folder_path)

    # List all collections
    collections = client.list_collections()

    if collections:
        # Get the first collection
        first_collection = collections[0]

        # Load the collection
        collection = client.get_collection(name=first_collection.name)

        # Get number of documents
        num_documents = len(collection.get()["ids"])

        print(f"Collection name: {collection.name}")
        print(f"Number of documents: {num_documents}")
    else:
        print("No collections found in the database.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <folder_path>")
    else:
        main(sys.argv[1])
