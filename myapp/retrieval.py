import os
from openai import OpenAI
from pinecone import Pinecone, ServerlessSpec
from flashrank import Ranker, RerankRequest
from dotenv import load_dotenv, find_dotenv

# Load environment variables from a .env file if it exists
load_dotenv(find_dotenv())

# Api Keys
openai_api_key = os.environ.get('OPENAI_API_KEY')
pinecone_api_key = os.environ.get('PINECONE_VECTOR_DB_KEY')
llm_name = os.environ.get('LLM_NAME')
top_k_retrieval = os.environ.get('TOP_K_RETREIVAL')

pinecone = Pinecone(api_key=pinecone_api_key)

# Setup Pinecone Vectro DB
index_name = os.environ.get('PINECONE_INDEX_NAME')
def create_pinecone_index(index_name):
    if index_name not in [index.name for index in pinecone.list_indexes()]:
        # Configure the index in pinecone
        pinecone.create_index(name=index_name, dimension=1536, metric='cosine',
        spec=ServerlessSpec(cloud='aws', region='us-east-1'))
        # Create Index
        pinecone.Index(index_name)
        print("DONE")

    # If already exists    
    index = pinecone.Index(index_name)    
    return index 

# Initialize openai client
openai_client = OpenAI(api_key=openai_api_key)

# Embeddings of texts
def get_embeddings(texts, model="text-embedding-ada-002"):
   return openai_client.embeddings.create(input = texts, model=model)

index = create_pinecone_index(index_name)

# method for get top retrieval
def get_top_retrieval(user_query,namespace):
    try:
    # Query Pinecone index
        user_query_vector = get_embeddings(user_query).data[0].embedding
    
        top_k = int(os.environ.get('TOP_K_RETREIVAL'))
    

        response = index.query(
            vector=user_query_vector,
            top_k=top_k,
            include_values=True,
            include_metadata=True,
            namespace=namespace
        )
    except Exception as e:
        print(e)
    return user_query_vector, response['matches']

# Initialize Reranking feature and their method
ranker = Ranker(model_name="ms-marco-MiniLM-L-12-v2", cache_dir="/opt")
def rerank(user_query, retrieved_data):
    rerankrequest = RerankRequest(query=user_query, passages=retrieved_data)
    return ranker.rerank(rerankrequest)   

def existing_namespaces():
    return list(index.describe_index_stats()['namespaces'])    