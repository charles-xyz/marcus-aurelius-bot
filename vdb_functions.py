import openai
import langchain
import pinecone
import streamlit as st

OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
PINECONE_API_KEY = st.secrets["PINECONE_API_KEY"]

from openai import OpenAI
from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec

client = OpenAI(api_key=OPENAI_API_KEY)
pc = Pinecone(api_key=PINECONE_API_KEY)

index_name = "marcus-aurelius"
index = pc.Index(index_name)

def create_embedding(text):
  response = client.embeddings.create(
    input=text,
    model="text-embedding-3-large"
  )
  return response.data[0].embedding

def query_vdb(text):
  res = ""
  embedded_text = create_embedding(text)
  query_result = index.query(
      vector = embedded_text,
      top_k = 5,
      include_metadata = True
  )
  for i in query_result['matches']:
    res = res + i['metadata']['quote']
  return res


if __name__ == "__main__":
  res = query_vdb("what do i tell my kids?")
  print(res)
