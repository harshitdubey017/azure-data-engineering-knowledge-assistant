# Retrieval Evaluation Report

## Objective

Evaluate whether the semantic retrieval system returns relevant technical documentation for Azure Data Engineering questions.

## Evaluation Dataset

* Total evaluation questions: 30
* Evaluation categories: Azure Data Factory, Databricks, Spark, Delta Lake, Unity Catalog, SQL, and Azure DevOps
* Retrieval depth: Top 3

## Evaluation Metrics

### Hit@1

Measures whether the expected document appears as the first retrieved result.

### Hit@3

Measures whether the expected document appears anywhere in the top three retrieved results.

### Mean Reciprocal Rank (MRR)

Measures the ranking quality of the expected document.

For a question whose expected document appears at rank r, the reciprocal rank is 1/r. If it is not retrieved within the evaluated ranking, its reciprocal rank is zero.

## Results

The detailed per-question results are available in `retrieval_results.csv`.

Insert the actual aggregate Hit@1, Hit@3, and MRR values calculated by the evaluation notebook.

## Interpretation

Use the evaluation results to identify:

* Questions with poor retrieval
* Documents that are frequently missed
* Differences in retrieval performance across categories
* Potential improvements to chunking, embeddings, and retrieval configuration

## Limitations

Retrieval metrics measure document ranking against the defined expected-document labels. They do not independently establish factual correctness of generated answers.

LLM answer quality and citation correctness should be evaluated separately.
