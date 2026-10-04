# Project Results

## Overview

This document summarizes the implementation and evaluation outcomes of the Azure Data Engineering Knowledge Assistant.

The project demonstrates a Retrieval-Augmented Generation (RAG) workflow built using Databricks, Delta Lake, Unity Catalog, Databricks AI Search, an LLM, and Streamlit.

## Implementation Summary

The following project components have been implemented:

| Component                                  | Implementation Status |
| ------------------------------------------ | --------------------- |
| Technical knowledge base                   | Completed             |
| Document chunking and embedding generation | Completed             |
| Unity Catalog Delta table                  | Completed             |
| Databricks AI Search retrieval             | Completed             |
| Retrieval evaluation benchmark             | Completed             |
| Hit@1, Hit@3, and MRR calculation          | Completed             |
| RAG response generation                    | Completed             |
| Source citation generation and validation  | Completed             |
| Streamlit chatbot                          | Completed             |
| Databricks Apps deployment                 | Completed             |

## Knowledge Base

The project stores document chunks and embedding metadata in a Unity Catalog Delta table.

**Table:**

`azure_knowledge_asistant.azure_rag.document_embeddings`

The table includes the following fields:

| Field                 | Purpose                                |
| --------------------- | -------------------------------------- |
| `chunk_id`            | Unique identifier for a document chunk |
| `document_id`         | Document identifier                    |
| `document_name`       | Source document name                   |
| `chunk_number`        | Chunk sequence number                  |
| `chunk_text`          | Extracted text content                 |
| `source_path`         | Source document location               |
| `embedding`           | Vector representation of the chunk     |
| `embedding_model`     | Embedding model identifier             |
| `embedding_dimension` | Embedding vector dimension             |
| `created_at`          | Record creation timestamp              |

## Retrieval Evaluation

A benchmark of 30 technical questions was created to evaluate semantic retrieval.

The evaluation measured:

* Hit@1
* Hit@3
* Mean Reciprocal Rank (MRR)

The detailed question-level results are available in:

`evaluation/retrieval_results.csv`

### Evaluation Metrics

| Metric                     | Actual Result                      |
| -------------------------- | ---------------------------------- |
| Total evaluation questions | 30                                 |
| Hit@1                      | 96%                                |
| Hit@3                      | 100%                               |
| MRR                        | 98%                                |

### Evaluation Interpretation

Hit@1 measures whether the expected document is retrieved as the first result.

Hit@3 measures whether the expected document is present among the top three results.

MRR measures the ranking quality of the expected document across the benchmark.

The metrics should be interpreted in the context of the benchmark size and the expected-document labels.

## RAG Pipeline Results

The implemented RAG pipeline supports the following workflow:

1. Accept a user question.
2. Retrieve relevant knowledge chunks using semantic search.
3. Construct a context-grounded prompt.
4. Generate an answer using the configured LLM.
5. Extract and validate citation identifiers.
6. Resolve citations against the actual retrieved document metadata.
7. Display the answer with corresponding source information.

Citation resolution is handled by application logic using retrieved metadata rather than relying exclusively on the LLM to produce source names.

This reduces the risk of displaying unsupported document references.

## Application Results

The Streamlit chatbot was deployed as a Databricks App.

The application supports:

* Technical question submission
* Semantic retrieval
* Context-grounded answer generation
* Source citation display
* Retrieved context inspection
* Testing of valid and out-of-scope questions

Screenshots of the deployed application are available in the `screenshots/` directory.

## Key Learnings

The project provided practical experience with:

* Document ingestion and text chunking
* Embedding generation and vector storage
* Unity Catalog table management
* Semantic retrieval using Databricks AI Search
* Retrieval quality evaluation
* RAG prompt construction
* Source citation validation
* Streamlit application development
* Databricks Apps deployment

## Limitations

* The evaluation benchmark contains 30 questions.
* Retrieval metrics do not independently measure generated-answer correctness.
* Response quality depends on knowledge base coverage and retrieval relevance.
* Production-scale latency, cost, concurrency, and reliability testing have not been claimed.
* Results should be interpreted as outcomes of a portfolio project developed in Databricks Free Edition.

## Conclusion

The project demonstrates an end-to-end implementation of a document-grounded technical knowledge assistant, covering knowledge ingestion, vector retrieval, retrieval evaluation, LLM-based response generation, source validation, and application deployment.

It provides a practical foundation for further experimentation with retrieval optimization, answer-quality evaluation, monitoring, and production deployment patterns.
