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


##########################################################################################################################################################
# Convert to embeddings
def get_embedding(message):
    return model.encode(message).tolist()

# Store the chat history in Pinecone
def store_vector_chat_message(chat_history, vector_id, namespace):
    embeddings = [get_embedding(message) for message in chat_history]
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


##########################################################################################################################################################
# Retrieve closest messages in chat history from Pinecone
def get_relevant_chat_history(message, namespace, top_k):

    # To fix error: Invalid value for `top_k`, must be a value greater than or equal to `1`
    if top_k == 0: top_k = 1

    query_embedding = get_embedding(message)
    results = index.query(
                namespace=namespace,
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
                # include_values=True
    )

    # Retrieve messages and vector_ids from results
    closest_messages = [(match["metadata"]["message"], int(match["id"])) for match in results.matches]

    # Sort messages by vector_id
    closest_messages.sort(key=lambda x: x[1])

    # Extract sorted messages
    sorted_messages = [message for message, _ in closest_messages]

#    for message in sorted_messages:
#        debug_print("RAG closest message", message)

    return sorted_messages


##########################################################################################################################################################
# Delete all messages in namespace
def delete_all_namespace_messages(namespace):
    index.delete(delete_all=True, namespace=namespace)


##########################################################################################################################################################
# Extract the number of vectors in the specified namespace
def get_num_vectors(namespace):
    # Get the index statistics
    index_stats = index.describe_index_stats()
    namespace_stats = index_stats.get('namespaces', {}).get(namespace, {})
    num_vectors = namespace_stats.get('vector_count', 0)
    return num_vectors


##########################################################################################################################################################
# Extract vector metadata message by vector ID
def get_vector_metadata(namespace, vector_id):
    # Get the vector metadata
    response = index.fetch(ids=[vector_id], namespace=namespace)
    # Check if the vector is found and has metadata
    if vector_id in response.vectors:
        vector_metadata = response.vectors[vector_id].metadata
        return vector_metadata.get("message", None)
    else:
        return None


##########################################################################################################################################################
# Delete a vector from the specified namespace
def delete_vector_from_namespace(namespace, vector_id):
    vector_message = get_vector_metadata(namespace, vector_id)
    index.delete(ids=[vector_id], namespace=namespace)
    debug_print(f"Deleted vector {vector_id} from namespace {namespace}", vector_message)
