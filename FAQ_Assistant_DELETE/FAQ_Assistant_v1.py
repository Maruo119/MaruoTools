import json
import pandas as pd
from haystack.document_stores import FAISSDocumentStore
from haystack.nodes import DensePassageRetriever
from haystack.pipelines import DocumentSearchPipeline
from haystack.utils import clean_wiki_text
from haystack.schema import Document
from fastapi import FastAPI
from pydantic import BaseModel

# FAQデータのロード（CSV/JSONから）
def load_faq_data(filepath: str):
    df = pd.read_csv(filepath)  # FAQデータはCSVと仮定
    documents = [Document(content=row['answer'], meta={"question": row['question']}) for _, row in df.iterrows()]
    return documents

# Document Storeのセットアップ
def setup_document_store(documents):
    document_store = FAISSDocumentStore(embedding_dim=768)
    retriever = DensePassageRetriever(document_store=document_store)
    document_store.write_documents(documents)
    document_store.update_embeddings(retriever)
    return document_store, retriever

# FAQ検索用API
documents = load_faq_data("faq.csv")
document_store, retriever = setup_document_store(documents)
pipeline = DocumentSearchPipeline(retriever)

app = FastAPI()

class QueryRequest(BaseModel):
    query: str

@app.post("/search")
def search_faq(request: QueryRequest):
    results = pipeline.run(query=request.query, params={"Retriever": {"top_k": 3}})
    return {"answers": [{"question": doc.meta["question"], "answer": doc.content} for doc in results["documents"]]}

# サーバー起動コマンド（ターミナルで実行）
# uvicorn main:app --reload
