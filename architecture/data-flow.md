# Project Data Flow

## Overview

The application consists of a document processing pipeline and a retrieval-augmented generation pipeline.

## Document Processing

1. Read technical documentation files.
2. Extract document content.
3. Generate document identifiers.
4. Split content into manageable chunks.
5. Attach document and chunk metadata.
6. Generate embeddings.
7. Store the processed data in Delta Lake.
8. Synchronize the vector index.

## Query Processing

1. Accept a user question.
2. Generate a query embedding.
3. Retrieve semantically relevant document chunks.
4. Construct context using retrieved results.
5. Pass context and question to the LLM.
6. Generate a grounded response.
7. Extract and validate citation identifiers.
8. Resolve citations to actual document metadata.
9. Display the answer, sources, and retrieved context.

## Reliability Considerations

* Handle empty retrieval results.
* Prevent unsupported answers when context is unavailable.
* Validate citation identifiers.
* Resolve sources using retrieved metadata rather than model-generated source names.
* Handle structured LLM responses.
* Keep credentials outside source code.
