# Databricks notebook source
# MAGIC %run ./05_vector_search

# COMMAND ----------

questions_df = spark.read \
    .option("header", True) \
    .option("inferSchema", True) \
    .csv("/Volumes/azure_knowledge_asistant/azure_rag/evaluation/retrieval_questions.csv")

display(questions_df)

# COMMAND ----------

questions_df.groupBy("category").count().display()

# COMMAND ----------

# questions = questions_df.collect()

# evaluation_results = []

# for row in questions:

#     question = row["question"]
#     expected = row["expected_document"]

#     results = display_search_results(question)

#     # Extract top 3 documents from your existing retrieval function
#     rank_1 = results[0]["document_name"]
#     rank_2 = results[1]["document_name"]
#     rank_3 = results[2]["document_name"]

#     evaluation_results.append({
#         "question": question,
#         "expected_document": expected,
#         "rank_1": rank_1,
#         "rank_2": rank_2,
#         "rank_3": rank_3
#     })
# evaluation_df = spark.createDataFrame(evaluation_results)

# display(evaluation_df)

# COMMAND ----------

from pyspark.sql.types import StructType, StructField, StringType

questions = questions_df.collect()

evaluation_results = []

for row in questions:

    question = row["question"]
    expected = row["expected_document"]
    category = row["category"]
    difficulty = row["difficulty"]

    results = retrieve_context(question)

    # Get top 3 results as Python rows
    result_rows = results.limit(3).collect()

    rank_1 = (
        str(result_rows[0]["document_name"])
        if len(result_rows) > 0
        else None
    )

    rank_2 = (
        str(result_rows[1]["document_name"])
        if len(result_rows) > 1
        else None
    )

    rank_3 = (
        str(result_rows[2]["document_name"])
        if len(result_rows) > 2
        else None
    )

    evaluation_results.append(
        (
            str(question),
            str(expected),
            str(category),
            str(difficulty),
            rank_1,
            rank_2,
            rank_3
        )
    )

schema = StructType([
    StructField("question", StringType(), True),
    StructField("expected_document", StringType(), True),
    StructField("category", StringType(), True),
    StructField("difficulty", StringType(), True),
    StructField("rank_1", StringType(), True),
    StructField("rank_2", StringType(), True),
    StructField("rank_3", StringType(), True)
])

evaluation_df = spark.createDataFrame(
    evaluation_results,
    schema=schema
)



# COMMAND ----------

display(evaluation_df)

# COMMAND ----------

from pyspark.sql.functions import col, when

evaluation_df = evaluation_df.withColumn(
    "hit_at_1",
    when(
        col("expected_document") == col("rank_1"),
        1
    ).otherwise(0)
)

evaluation_df = evaluation_df.withColumn(
    "hit_at_3",
    when(
        (col("expected_document") == col("rank_1")) |
        (col("expected_document") == col("rank_2")) |
        (col("expected_document") == col("rank_3")),
        1
    ).otherwise(0)
)

evaluation_df = evaluation_df.withColumn(
    "reciprocal_rank",
    when(col("expected_document") == col("rank_1"), 1.0)
    .when(col("expected_document") == col("rank_2"), 0.5)
    .when(col("expected_document") == col("rank_3"), 1.0 / 3.0)
    .otherwise(0.0)
)

# COMMAND ----------

from pyspark.sql.functions import avg

metrics = evaluation_df.select(
    avg("hit_at_1").alias("hit_at_1"),
    avg("hit_at_3").alias("hit_at_3"),
    avg("reciprocal_rank").alias("mrr")
)

display(metrics)

# COMMAND ----------

# MAGIC %md
# MAGIC 96% of questions:
# MAGIC correct document was Rank 1
# MAGIC
# MAGIC 100%:
# MAGIC correct document was within Top 3
# MAGIC
# MAGIC 98%:
# MAGIC average ranking quality

# COMMAND ----------

rank1_failures = evaluation_df.filter(
    col("hit_at_1") == 0
)

display(rank1_failures)

# COMMAND ----------

# DBTITLE 1,category-level evaluation
category_metrics = evaluation_df.groupBy("category").agg(
    avg("hit_at_1").alias("Hit@1")*100,
    avg("hit_at_3").alias("Hit@3")*100,
    avg("reciprocal_rank").alias("MRR")*100
)

display(category_metrics)

# COMMAND ----------

difficulty_metrics = evaluation_df.groupBy("difficulty").agg(
    avg("hit_at_1").alias("Hit@1"),
    avg("hit_at_3").alias("Hit@3"),
    avg("reciprocal_rank").alias("MRR")
)

display(difficulty_metrics)

# COMMAND ----------

display(evaluation_df)

# COMMAND ----------

# MAGIC %md
# MAGIC # Retrieval Evaluation Summary
# MAGIC
# MAGIC ## Dataset
# MAGIC
# MAGIC - Total questions: 30
# MAGIC - Domains: ADF, Databricks, Spark, Delta Lake,
# MAGIC   Unity Catalog, PySpark, SQL, Azure DevOps
# MAGIC - Retrieval depth: Top 3
# MAGIC
# MAGIC ## Metrics
# MAGIC
# MAGIC - Hit@1: 96%
# MAGIC - Hit@3: 100%
# MAGIC - reciprocal_rank: 98%
# MAGIC
# MAGIC ## Retrieval Failures
# MAGIC
# MAGIC - question	expected_document	category	difficulty	rank_1	rank_2	rank_3	hit_at_1	hit_at_3	reciprocal_rank
# MAGIC How can PySpark workloads be optimized?	spark_performance.md	Spark	Medium	pyspark.md	spark_performance.md	spark_performance.md	0	1	0.5
# MAGIC
# MAGIC ## Next Steps
# MAGIC
# MAGIC - Build RAG generation pipeline
# MAGIC - Add LLM
# MAGIC - Add source attribution
# MAGIC - Evaluate answer quality