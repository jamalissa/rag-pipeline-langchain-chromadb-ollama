import os
import json
from sentence_transformers import SentenceTransformer
from langchain.vectorstores import Chroma
from langchain.embeddings.base import Embeddings
from langchain.schema import Document

class SentenceTransformersEmbeddings(Embeddings):
    """
    A custom embedding class using sentence-transformers for generating embeddings.
    """
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def embed_documents(self, texts):
        # Convert NumPy array to Python list to avoid truth value ambiguity
        return self.model.encode(texts, convert_to_numpy=True).tolist()

    def embed_query(self, text):
        return self.embed_documents([text])[0]

def ingest_data():
    # Load the JSON file
    json_file = "./data.json"
    if not os.path.exists(json_file):
        print("JSON file not found. Exiting.")
        return

    with open(json_file, "r") as f:
        data = json.load(f)

    # Initialize SentenceTransformers embeddings
    embeddings = SentenceTransformersEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = Chroma(persist_directory="./chroma_data", embedding_function=embeddings)

    # Convert JSON documents to LangChain Document objects
    documents = [Document(page_content=doc["content"], metadata={"title": doc["title"]}) for doc in data["documents"]]

    # Add documents to the vector store
    vectorstore.add_documents(documents)
    vectorstore.persist()
    print("Documents have been successfully ingested into ChromaDB.")

if __name__ == "__main__":
    ingest_data()
