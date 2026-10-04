# Databricks notebook source
# MAGIC %pip install sentence-transformers

# COMMAND ----------

from sentence_transformers import SentenceTransformer

model = SentenceTransformer(
    "BAAI/bge-small-en-v1.5"
)

# COMMAND ----------

import numpy as np
from pyspark.sql import functions as F

embeddings_df = spark.table(
    "azure_knowledge_asistant.azure_rag.document_embeddings"
)

# COMMAND ----------

def semantic_search(query, top_k=5):
    
    # Generate embedding for the query
    query_embedding = model.encode(
        query,
        normalize_embeddings=True
    )

    # Collect stored embeddings
    rows = embeddings_df.select(
        "chunk_id",
        "document_id",
        "document_name",
        "chunk_number",
        "chunk_text",
        "source_path",
        "embedding"
    ).collect()

    results = []

    for row in rows:
        
        stored_embedding = np.array(
            row["embedding"],
            dtype=np.float32
        )

        # Because both vectors are normalized,
        # dot product = cosine similarity
        similarity = float(
            np.dot(
                query_embedding,
                stored_embedding
            )
        )

        results.append({
            "chunk_id": row["chunk_id"],
            "document_id": row["document_id"],
            "document_name": row["document_name"],
            "chunk_number": row["chunk_number"],
            "chunk_text": row["chunk_text"],
            "source_path": row["source_path"],
            "similarity": similarity
        })

    # Sort highest similarity first
    results = sorted(
        results,
        key=lambda x: x["similarity"],
        reverse=True
    )

    return results[:top_k]

# COMMAND ----------

query = "How does Azure Data Factory perform incremental loading?"

results = semantic_search(
    query,
    top_k=5
)

for i, result in enumerate(results, start=1):
    print(f"\n{'=' * 80}")
    print(f"Rank: {i}")
    print(f"Similarity: {result['similarity']:.4f}")
    print(f"Document: {result['document_name']}")
    print(f"Chunk: {result['chunk_number']}")
    print(f"Source: {result['source_path']}")
    print("\nChunk:")
    print(result["chunk_text"][:1000])

# COMMAND ----------


queries = [
    "How does Azure Data Factory perform incremental loading?",
    "How can Spark performance be improved?",
    "What is Delta Lake?",
    "How does Unity Catalog manage data access?",
    "How can Azure DevOps be used for CI/CD?"
]

# COMMAND ----------

all_results = []

for query in queries:

    results = semantic_search(
        query,
        top_k=5
    )

    for rank, result in enumerate(results, start=1):

        all_results.append({
            "query": query,
            "rank": rank,
            "similarity": result["similarity"],
            "document_name": result["document_name"],
            "chunk_id": result["chunk_id"],
            "chunk_number": result["chunk_number"],
            "source_path": result["source_path"]
        })

results_df = spark.createDataFrame(
    all_results
)

# COMMAND ----------

top_results = (
    results_df
    .filter(F.col("rank") == 1)
    .orderBy("query")
)

display(top_results)

# COMMAND ----------

# MAGIC %sql
# MAGIC
# MAGIC SELECT
# MAGIC     embedding_dimension,
# MAGIC     COUNT(*) AS records
# MAGIC FROM azure_knowledge_asistant.azure_rag.document_embeddings
# MAGIC GROUP BY embedding_dimension;

# COMMAND ----------

# MAGIC %sql
# MAGIC
# MAGIC SHOW TBLPROPERTIES azure_knowledge_asistant.azure_rag.document_embeddings;

# COMMAND ----------

# MAGIC %sql
# MAGIC
# MAGIC ALTER TABLE azure_knowledge_asistant.azure_rag.document_embeddings
# MAGIC SET TBLPROPERTIES (
# MAGIC     delta.enableChangeDataFeed = true
# MAGIC );