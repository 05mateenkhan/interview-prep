from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
import pandas as pd

df = pd.read_csv("data/QnA.csv")

documents = []

for _, row in df.iterrows():
    documents.append(
        Document(
            page_content=f"""
            Role: {row['role']}
            Topic: {row['topic']}
            Difficulty: {row['difficulty']}
            Question: {row['question']}
            """,
            metadata=row.to_dict()
        )
    )

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vector_store = FAISS.from_documents(documents, embeddings)

vector_store.save_local("faiss_index")

print("FAISS index saved!")