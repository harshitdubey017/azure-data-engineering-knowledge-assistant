# Databricks notebook source
# MAGIC %pip install sentence-transformers

# COMMAND ----------

from sentence_transformers import SentenceTransformer

model = SentenceTransformer(
    "BAAI/bge-small-en-v1.5"
)

# COMMAND ----------

from pyspark.sql import functions as F

chunks_table = "azure_knowledge_asistant.azure_rag.document_chunks"

df_chunks = spark.table(chunks_table)

df_chunks.select(
    F.count("*").alias("total_chunks"),
    F.countDistinct("chunk_id").alias("unique_chunk_ids"),
    F.sum(F.when(F.col("chunk_text").isNull(), 1).otherwise(0)).alias("null_chunk_text"),
    F.sum(F.when(F.trim(F.col("chunk_text")) == "", 1).otherwise(0)).alias("empty_chunk_text")
).show()

# COMMAND ----------

test_text = df_chunks.select("chunk_text").first()["chunk_text"]

print(test_text[:500])

test_embedding = model.encode(
    test_text,
    normalize_embeddings=True
)

print(type(test_embedding))
print("Embedding dimension:", len(test_embedding))
print("First 10 values:", test_embedding[:10])

# COMMAND ----------

spark.sql("""
CREATE TABLE IF NOT EXISTS azure_knowledge_asistant.azure_rag.document_embeddings (
    chunk_id STRING,
    document_id STRING,
    document_name STRING,
    chunk_number INT,
    chunk_text STRING,
    source_path STRING,
    embedding ARRAY<FLOAT>,
    embedding_model STRING,
    embedding_dimension INT,
    created_at TIMESTAMP
)
USING DELTA
""")

# COMMAND ----------

display(spark.table("azure_knowledge_asistant.azure_rag.document_embeddings"))

# COMMAND ----------

existing_embeddings = spark.table(
    "azure_knowledge_asistant.azure_rag.document_embeddings"
)

pending_chunks = (
    df_chunks.alias("c")
    .join(
        existing_embeddings.select("chunk_id").alias("e"),
        F.col("c.chunk_id") == F.col("e.chunk_id"),
        "left_anti"
    )
)

print("Chunks waiting for embedding:", pending_chunks.count())

# COMMAND ----------

embedded_rows = []

for row in pending_rows:

    vector = model.encode(
        row["chunk_text"],
        normalize_embeddings=True
    )

    embedded_rows.append({
        "chunk_id": row["chunk_id"],
        "document_id": row["document_id"],
        "document_name": row["document_name"],
        "chunk_number": row["chunk_number"],
        "chunk_text": row["chunk_text"],
        "source_path": row["source_path"],
        "embedding": vector.tolist(),
        "embedding_model": "BAAI/bge-small-en-v1.5",
        "embedding_dimension": len(vector),
    })

print("Generated embeddings:", len(embedded_rows))

# COMMAND ----------

from datetime import datetime

embedding_rows = [
    (
        r["chunk_id"],
        r["document_id"],
        r["document_name"],
        r["chunk_number"],
        r["chunk_text"],
        r["source_path"],
        r["embedding"],
        r["embedding_model"],
        r["embedding_dimension"],
        datetime.now()
    )
    for r in embedded_rows
]

embedding_df = spark.createDataFrame(
    embedding_rows,
    schema=[
        "chunk_id",
        "document_id",
        "document_name",
        "chunk_number",
        "chunk_text",
        "source_path",
        "embedding",
        "embedding_model",
        "embedding_dimension",
        "created_at"
    ]
)

display(embedding_df.limit(5))

# COMMAND ----------

from delta.tables import DeltaTable

target_table = "azure_knowledge_asistant.azure_rag.document_embeddings"

target = DeltaTable.forName(spark, target_table)

(
    target.alias("t")
    .merge(
        embedding_df.alias("s"),
        "t.chunk_id = s.chunk_id"
    )
    .whenMatchedUpdateAll()
    .whenNotMatchedInsertAll()
    .execute()
)

# COMMAND ----------

spark.table("azure_knowledge_asistant.azure_rag.document_embeddings").printSchema()

# COMMAND ----------

display(spark.table("azure_knowledge_asistant.azure_rag.document_embeddings"))