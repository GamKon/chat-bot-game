import os
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
from utility import debug_print
import json

# Get the Pinecone API key from the environment
pc_api_key = os.getenv("PINECONE_API_KEY")

pc = Pinecone(
    api_key=pc_api_key)

# Now do stuff
debug_print("Indexes: ", pc.list_indexes().names())

if 'chat-bot-history' not in pc.list_indexes().names():

    # Creates an index using the API key stored in the client 'pc'.
    pc.create_index(
        name='chat-bot-history',
        dimension=384,
        metric='euclidean',
        spec=ServerlessSpec(
            cloud='aws',
            region='us-east-1'
        )
    )

index = pc.Index("chat-bot-history")

# Choose an Embedding Model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Convert to embeddings
def get_embedding(message):
    return model.encode(message).tolist()

# def get_text(embedding):
#     return model.decode(embedding).tolist()

# Store the chat history in Pinecone
def store_vector_chat_message(chat_history, vector_id, namespace):
    embeddings = [get_embedding(message) for message in chat_history]
#    debug_print("Embeddings: ", embeddings)
    for i in range(len(chat_history)):
        index.upsert(
            vectors=[
                {
                    "id": vector_id[i],
                    "values": embeddings[i],
                    # "sparse_values": {
                    #     "indices": [1, 5],
                    #     "values": [0.5, 0.5]
                    # },
                    "metadata": {
                        "author": str(i),
                        "message": chat_history[i]
                    }
                }
            ],
            namespace=namespace
        )


# Retrieve closest messages in chat history from Pinecone
def get_relevant_chat_history(message, namespace, top_k=2):
    query_embedding = get_embedding(message)
    results = index.query(
                namespace=namespace,
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
                # include_values=True
    )
    debug_print("results", results)

    closest_messages = [match["metadata"]["message"] for match in results.matches]

#    debug_print("closest_messages", closest_messages)

    return closest_messages
