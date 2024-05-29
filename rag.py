import os
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
from utility import debug_print

# Get the Pinecone API key from the environment
pc_api_key = os.getenv("PINECONE_API_KEY")

pc = Pinecone(
    api_key=pc_api_key)

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
#   What are these sparse values for?
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
def get_relevant_chat_history(message, namespace, top_k=6):
    query_embedding = get_embedding(message)
    results = index.query(
                namespace=namespace,
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
                # include_values=True
    )

#    debug_print(f"RAG retrieved {top_k} closest messages", results)

    #closest_messages = [match["metadata"]["message"] for match in results.matches]

    # Retrieve messages and vector_ids from results
    closest_messages = [(match["metadata"]["message"], int(match["id"])) for match in results.matches]
    # Sort messages by vector_id
    closest_messages.sort(key=lambda x: x[1])
    # Extract sorted messages
    sorted_messages = [message for message, _ in closest_messages]

    for message in sorted_messages:
        debug_print("RAG closest message", message)

    return sorted_messages

# Delete all messages in namespace
def delete_all_namespace_messages(namespace):
    index.delete(delete_all=True, namespace=namespace)
