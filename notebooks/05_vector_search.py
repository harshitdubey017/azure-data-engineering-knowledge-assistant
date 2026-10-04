# Databricks notebook source
# MAGIC %pip install databricks-ai-search

# COMMAND ----------

# MAGIC %pip install sentence-transformers

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

from sentence_transformers import SentenceTransformer

embedding_model = SentenceTransformer("BAAI/bge-small-en-v1.5")

# COMMAND ----------

def generate_query_embedding(question):
    embedding = embedding_model.encode(
        question,
        normalize_embeddings=True
    )

    return embedding.tolist()

# COMMAND ----------

from databricks.ai_search.client import AISearchClient

client = AISearchClient()

INDEX_NAME = "azure_knowledge_asistant.azure_rag.knowledge_chunks_index"

index = client.get_index(
    index_name=INDEX_NAME
)

print("Connected to index:")
print(INDEX_NAME)

# COMMAND ----------

import time

while True:
    status = index.describe()

    print(status)

    detailed_state = status.get("status", {}).get("detailed_state", "")

    if detailed_state.startswith("ONLINE"):
        print("Index is ONLINE")
        break

    time.sleep(10)

# COMMAND ----------

def search_knowledge_base(question, top_k=3):

    query_vector = generate_query_embedding(question)

    results = index.similarity_search(
        query_vector=query_vector,
        columns=[
            "chunk_id",
            "document_id",
            "document_name",
            "chunk_number",
            "chunk_text",
            "source_path"
        ],
        num_results=top_k
    )

    return results

# COMMAND ----------



def retrieve_context(question, top_k=3):
    
    results = search_knowledge_base(
        question,
        top_k
    )

    columns = [
        column["name"]
        for column in results["manifest"]["columns"]
    ]

    rows = results["result"]["data_array"]

    results_df = spark.createDataFrame(
        rows,
        schema=columns
    )

    #print(f"Question: {question}")
    #print(f"Top {top_k} results:")

    #display(results_df)

    return results_df

# COMMAND ----------

print(retrieve_context)

# COMMAND ----------

# retrieve_context(
#     "What is Delta Lake?",
#     top_k=3
# )

# COMMAND ----------

# test_questions = [
#     "What is Delta Lake?",
#     "How does incremental loading work in Azure Data Factory?",
#     "How does data skew affect Spark performance?",
#     "What is Unity Catalog?",
#     "How can Azure DevOps be used for ADF CI/CD?"
# ]

# for question in test_questions:

#     print("=" * 100)

#     retrieve_context(
#         question,
#         top_k=3
#     )

# COMMAND ----------

# display_search_results(
#     "Why can a Spark job become slow when the data is distributed unevenly?",
#     top_k=3
# )

# COMMAND ----------

# display_search_results(
#     "What is the capital of France?",
#     top_k=3
# )