# Databricks notebook source
import re
from datetime import datetime

# COMMAND ----------

df_documents = spark.table("azure_knowledge_asistant.azure_rag.documents_raw")
print("Number of documents:", df_documents.count())

# COMMAND ----------

# DBTITLE 1,Chunk Function
def chunk_text(text, chunk_size=150, overlap=30):
    if text is None:
        return []
    
    text = str(text).strip()
    if not text:
        return []

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)
    words = text.split()

    if len(words) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk_words = words[start:end]
        chunk = " ".join(chunk_words)
        chunks.append(chunk)

        if end >= len(words):
            break
        start = end - overlap

    return chunks

# COMMAND ----------

from pyspark.sql.functions import udf
from pyspark.sql.types import ArrayType, StringType

chunk_text_udf = udf(
    chunk_text,
    ArrayType(StringType())
)

# COMMAND ----------

df_with_chunks = df_documents.withColumn(
    "chunks",
    chunk_text_udf("document_text")
)

# COMMAND ----------

display(df_with_chunks)

# COMMAND ----------

from pyspark.sql.functions import explode, col
df_chunks = df_with_chunks.select(
    "document_id",
    "document_name",
    "source_path",
    "ingestion_timestamp",
    explode("chunks").alias("chunk_text")
)

# COMMAND ----------

display(df_chunks)

# COMMAND ----------

# MAGIC %md
# MAGIC Generating a chunk ID

# COMMAND ----------

from pyspark.sql.functions import row_number
from pyspark.sql.window import Window

window_spec = Window.partitionBy(
    "document_id"
).orderBy(
    "chunk_text"
)

df_chunks = df_chunks.withColumn(
    "chunk_number",
    row_number().over(window_spec)
)

# COMMAND ----------

from pyspark.sql.functions import concat_ws

df_chunks = df_chunks.withColumn(
    "chunk_id",
    concat_ws(
        "_",
        col("document_id"),
        col("chunk_number")
    )
)

# COMMAND ----------

df_chunks = df_chunks.select(
    "chunk_id",
    "document_id",
    "document_name",
    "chunk_number",
    "chunk_text",
    "source_path",
    "ingestion_timestamp"
)

display(df_chunks)

# COMMAND ----------

from pyspark.sql.functions import size, split

df_chunks = df_chunks.withColumn(
    "word_count",
    size(split(col("chunk_text"), " "))
)

display(
    df_chunks.select(
        "chunk_id",
        "document_name",
        "word_count"
    )
)

# COMMAND ----------

df_chunks.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable("azure_knowledge_asistant.azure_rag.document_chunks")

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC     document_name,
# MAGIC     chunk_number,
# MAGIC     word_count,
# MAGIC     LEFT(chunk_text, 100) AS chunk_preview
# MAGIC FROM azure_knowledge_asistant.azure_rag.document_chunks
# MAGIC ORDER BY
# MAGIC     document_name,
# MAGIC     chunk_number;

# COMMAND ----------

# MAGIC %sql
# MAGIC DESCRIBE TABLE EXTENDED azure_knowledge_asistant.azure_rag.document_chunks;