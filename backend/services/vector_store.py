import os
import pandas as pd
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings
import random
load_dotenv()

_vector_store = None  # singleton


def _load_documents(csv_path: str) -> list[Document]:
    
    df = pd.read_csv(csv_path)
    documents = []
    for _, row in df.iterrows():
        content = (
            f"Role: {row['role']}\n"
            f"Topic: {row['topic']}\n"
            f"Difficulty: {row['difficulty']}\n"
            f"Question: {row['question']}"
        )
        documents.append(Document(
            page_content=content,
            metadata={
                "role": row["role"],
                "topic": row["topic"],
                "difficulty": row["difficulty"],
                "question": row["question"],
                "answer": row["answer"],
            }
        ))
    return documents


def get_vector_store() -> FAISS:

    global _vector_store
    if _vector_store is not None:
        return _vector_store

    print("Building FAISS index from QnA.csv ...")
    csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "QnA.csv")
    documents = _load_documents(csv_path)

    embeddings_gem = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=os.getenv("GEMINI_API_KEY"),
    )
    embeddings_ol = OllamaEmbeddings(
        model="embeddinggemma"
    )

    _vector_store = FAISS.from_documents(documents, embeddings_ol)
    print(f"✅ FAISS index built with {len(documents)} documents.")
    return _vector_store


def retrieve_question(k: int, role: str, topic: str, difficulty: str, exclude_questions: list[str] = []) -> dict:

    store = get_vector_store()

    query = f"Role: {role}\n Difficulty: {difficulty}"
    results = store.similarity_search(query, k=k)

    for i in range (0,k*2):
        doc_no = random.randint(0,k)
        q = results[doc_no].metadata["question"]
        if q not in exclude_questions:
            return results[doc_no].metadata

    return results[0].metadata