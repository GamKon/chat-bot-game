import os
import pinecone
from sentence_transformers import SentenceTransformer

# Get the Pinecone API key from the environment
pc_api_key = os.getenv("PINECONE_API_KEY")

# Initialize Pinecone DB
pinecone.init(api_key=pc_api_key)
index = pinecone.Index("chat-bot-history")

# Choose an Embedding Model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Convert to embeddings
def get_embedding(text):
    return model.encode(text).tolist()

# Store the chat history in Pinecone
def store_chat_history(chat_history):
    embeddings = [get_embedding(chat) for chat in chat_history]
    index.upsert(items=embeddings, item_ids=range(len(chat_history)))

# Retrieve relevant chat history from Pinecone
def get_relevant_chat_history(query):
    query_embedding = get_embedding(query)
    results = index.query(queries=[query_embedding], top_k=5)
#    return [chat_history[result.id] for result in results[0].ids]
    return results
