# Databricks notebook source
from datetime import datetime, timezone 
import os
import uuid

volume_path = "/Volumes/azure_knowledge_asistant/azure_rag/raw_documents"

# COMMAND ----------

md_files = sorted([
    file
    for file in os.listdir(volume_path)
    if file.lower().endswith(".md")
])

print(f"Found {len(md_files)} Markdown files")

for file in md_files:
    print(file)

# COMMAND ----------

documents = []
for file_name in md_files:

    file_path = os.path.join(volume_path, file_name)

    with open(file_path, "r", encoding="utf-8") as f:
        document_text = f.read()

    document_id = os.path.splitext(file_name)[0]

    documents.append({
        "document_id": document_id,
        "document_name": file_name,
        "document_text": document_text,
        "source_path": file_path,
        "ingestion_timestamp": datetime.now(timezone.utc)
    })

# COMMAND ----------

df_documents = spark.createDataFrame(documents)
display(df_documents)

# COMMAND ----------

df_documents.printSchema()

# COMMAND ----------

from pyspark.sql.functions import length

display(
    df_documents
    .select(
        "document_id",
        "document_name",
        length("document_text").alias("character_count")
    )
    .orderBy("character_count")
)

# COMMAND ----------

df_documents.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable("azure_knowledge_asistant.azure_rag.documents_raw")

# COMMAND ----------

# MAGIC %sql
# MAGIC
# MAGIC SELECT COUNT(*) AS document_count
# MAGIC FROM azure_knowledge_asistant.azure_rag.documents_raw;

# COMMAND ----------

# MAGIC %sql
# MAGIC
# MAGIC DESCRIBE TABLE azure_knowledge_asistant.azure_rag.documents_raw;