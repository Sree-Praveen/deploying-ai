import chromadb
import os
import requests
from dotenv import load_dotenv
from openai import OpenAI

# Load API gateway key 
load_dotenv('../../05_src/.secrets')


client_openai = OpenAI(
    base_url='https://k7uffyg03f.execute-api.us-east-1.amazonaws.com/prod/openai/v1',
    api_key='any value',
    default_headers={"x-api-key": os.getenv('API_GATEWAY_KEY')}
)


# Service 2: Semantic Search

client = chromadb.PersistentClient(path="./chroma_store")

collection = client.get_or_create_collection(
    name="data_science_collection"
)

def get_embedding(text):
    response = client_openai.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding


# Load documents
def load_documents():
    if collection.count() > 0:
        return

    base_dir = os.path.dirname(__file__)
    file_path = os.path.join(base_dir, "data", "data_science_faq.txt")

    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    documents = [doc.strip() for doc in text.split("\n\n") if doc.strip()]
    ids = [f"id_{i}" for i in range(len(documents))]

    embeddings = [get_embedding(doc) for doc in documents]

    collection.add(
        documents=documents,
        embeddings=embeddings,
        ids=ids
    )


def semantic_search(query):
    query_embedding = get_embedding(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=1
    )

    if results["documents"] and results["documents"][0]:
        return results["documents"][0][0]
    else:
        return "I couldn't find a relevant answer."



# Service 1: API Call 


def get_joke():
    try:
        response = requests.get("https://official-joke-api.appspot.com/random_joke")
        data = response.json()

        setup = data.get("setup", "")
        punchline = data.get("punchline", "")

        rewritten = (
            f"Here’s something fun for you\n\n"
            f"{setup}\n...\n{punchline}\n\n"
            f"Hope that made you smile!"
        )

        return rewritten

    except Exception:
        return " I couldn't fetch a joke right now. Please try again later."


# Load documents
load_documents()