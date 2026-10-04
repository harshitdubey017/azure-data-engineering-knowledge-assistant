# Azure Data Engineering Knowledge Assistant

A Retrieval-Augmented Generation (RAG) application for semantic search and question answering across Azure Data Engineering technical documentation.

Built using Python, Azure Databricks, PySpark, Delta Lake, Databricks AI Search, embeddings, an LLM, and Streamlit.

## Project Overview

The Azure Data Engineering Knowledge Assistant enables users to ask technical questions related to Azure Data Factory, Azure Databricks, Apache Spark, Delta Lake, Unity Catalog, SQL optimization, and Azure DevOps.

The application retrieves relevant document chunks using semantic search and supplies the retrieved context to an LLM to generate grounded answers with verified source citations.

The project demonstrates the integration of data engineering pipelines with Generative AI and Retrieval-Augmented Generation.

## Business Problem

Data engineers frequently need to search technical documentation to understand implementation patterns, troubleshoot pipeline failures, investigate Spark performance issues, and identify platform best practices.

Traditional keyword-based searches may not retrieve the most relevant information when questions are phrased differently from the source documentation.

This project addresses that problem using semantic retrieval and LLM-based question answering.

## Objectives

* Build a document ingestion and processing pipeline.
* Extract and chunk technical documentation.
* Store processed document chunks and embeddings in Delta Lake.
* Implement semantic retrieval using Databricks AI Search.
* Develop a RAG pipeline for contextual answer generation.
* Provide verified source citations.
* Evaluate retrieval quality using Hit@1, Hit@3, and Mean Reciprocal Rank (MRR).
* Deploy an interactive chatbot using Streamlit and Databricks Apps.

## Technology Stack

| Category        | Technologies                         |
| --------------- | ------------------------------------ |
| Programming     | Python, PySpark                      |
| Data Platform   | Azure Databricks                     |
| Storage         | Delta Lake                           |
| Retrieval       | Databricks AI Search / Vector Search |
| GenAI           | Embeddings, LLM, RAG                 |
| Frontend        | Streamlit                            |
| Evaluation      | Hit@1, Hit@3, MRR                    |
| Governance      | Unity Catalog                        |
| Version Control | GitHub                               |

## Architecture

The solution consists of the following components:

1. Technical documentation sources
2. Document ingestion
3. Text extraction and preprocessing
4. Document chunking and metadata extraction
5. Delta Lake storage
6. Embedding generation
7. Vector index
8. Semantic retrieval
9. Context construction and prompt generation
10. LLM-based answer generation
11. Citation extraction and validation
12. Streamlit chatbot interface

## Data Pipeline

Technical Documents
→ Document Ingestion
→ Text Extraction
→ Chunking
→ Metadata Enrichment
→ Delta Lake
→ Embedding Generation
→ Vector Index

## RAG Pipeline

User Question
→ Query Embedding
→ Semantic Retrieval
→ Top-K Relevant Chunks
→ Context Construction
→ LLM
→ Generated Answer
→ Citation Validation
→ Answer with Sources

## Data Storage

The embedding dataset is stored in the Unity Catalog table:

`azure_knowledge_asistant.azure_rag.document_embeddings`

The table contains document identifiers, chunk identifiers, source metadata, chunk text, embedding vectors, embedding model information, embedding dimensions, and creation timestamps.

## Retrieval Evaluation

A 30-question evaluation dataset was created to assess retrieval performance.

Evaluation metrics:

* Hit@1
* Hit@3
* Mean Reciprocal Rank (MRR)

The evaluation output includes the expected document, retrieved document rankings, and metric results for each question.

Detailed results are available in the `evaluation/` directory.

## RAG Capabilities

* Semantic search over technical documentation
* Context-aware answer generation
* Citation-aware prompting
* Python-based citation extraction and validation
* Source resolution to document, chunk, and source path
* Retrieved-context transparency
* Out-of-scope question handling
* No-context response handling

## Application

The chatbot is deployed using Databricks Apps and provides an interactive interface for technical questions.

Application screenshots are available in the `screenshots/` directory.

## Repository Structure

```text
azure-data-engineering-knowledge-assistant/
├── README.md
├── LICENSE
├── .gitignore
├── requirements.txt
├── architecture/
├── docs/
├── notebooks/
├── app/
├── evaluation/
├── screenshots/
└── results/
```

## Setup and Reproducibility

The project uses Databricks-hosted resources for data storage, embeddings, vector retrieval, and application deployment.

Refer to the notebook files and project documentation for implementation details.

Required workspace resources, model endpoints, vector indexes, and application configuration must be provisioned in the target Databricks environment.

Credentials, tokens, and secrets must be configured securely and must never be committed to GitHub.

## Key Engineering Concepts

* Document ingestion and processing
* Data chunking
* Metadata management
* Delta Lake
* Embedding generation
* Semantic search
* Vector retrieval
* Retrieval-Augmented Generation
* Prompt engineering
* Citation validation
* Retrieval evaluation
* Source-grounded generation
* Databricks application deployment

## Future Enhancements

* Incremental document ingestion
* Hybrid search
* Reranking
* Automated RAG evaluation
* Retrieval latency monitoring
* Unity Catalog governance enhancements
* Improved document update and deletion handling

## Disclaimer
This is a personal learning and portfolio project. All documentation and sample data included in the repository are intended for demonstration and educational purposes.

This is a personal learning and portfolio project. All documentation and sample data included in the repository are intended for demonstration and educational purposes.
