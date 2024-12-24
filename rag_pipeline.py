from langchain_chroma.vectorstores import Chroma
from langchain_ollama.llms import OllamaLLM
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from sentence_transformers import SentenceTransformer
from langchain.embeddings.base import Embeddings

class SentenceTransformersEmbeddings(Embeddings):
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def embed_documents(self, texts):
        return self.model.encode(texts, convert_to_numpy=True).tolist()

    def embed_query(self, text):
        return self.embed_documents([text])[0]

def initialize_vector_db():
    embeddings = SentenceTransformersEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = Chroma(persist_directory="./chroma_data", embedding_function=embeddings)
    return vectorstore

def initialize_ollama_model():
    llm = OllamaLLM(model="llama2:7b-chat", server_url="http://localhost:11434")
    return llm

def main():
    vectorstore = initialize_vector_db()
    retriever = vectorstore.as_retriever()

    llm = initialize_ollama_model()

    prompt_template = """You are a helpful assistant. Use the following retrieved information to answer the user's question.

Retrieved Information:
{context}

Question:
{question}

Answer:
"""
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])

    print("Welcome to the RAG Pipeline. Type 'exit' to quit.")
    while True:
        user_query = input("Enter your question: ")
        if user_query.lower() == 'exit':
            print("Goodbye!")
            break

        # Retrieve relevant documents
        docs = retriever.invoke({"query": user_query})  # Updated to use invoke

        # Combine retrieved documents into context
        context = "\n".join([doc.page_content for doc in docs])

        # Prepare the final input for the LLM
        llm_input = prompt.format(context=context, question=user_query)

        # Get the response from the LLM
        response = llm.invoke(llm_input)  # Pass string directly

        print("\nResponse:")
        print(response)

        print("\nSource Documents:")
        for doc in docs:
            print(f"- {doc.page_content}")


if __name__ == "__main__":
    main()
