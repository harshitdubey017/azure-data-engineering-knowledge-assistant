# Notebooks

This directory contains the notebooks used to implement the Azure Data Engineering Knowledge Assistant.

## Execution Flow

1. Document ingestion
2. Document chunking
3. Embedding generation
4. Embedding evaluation
5. Vector Search setup
6. Retrieval evaluation
7. RAG pipeline
8. Citation extraction and validation

Notebook filenames should follow the actual implementation order.

## Execution Requirements

* Databricks workspace
* Appropriate Unity Catalog permissions
* Required model endpoints
* Configured vector search resources
* Required Python dependencies

Execute notebooks in the documented order, subject to the resource dependencies of each notebook.

Do not include workspace credentials, personal access tokens, or secret values in notebook source files.
