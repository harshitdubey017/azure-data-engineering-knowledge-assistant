# Databricks notebook source
# MAGIC %pip install openai

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

# MAGIC %run ./00_setup

# COMMAND ----------

# MAGIC %run ./05_vector_search

# COMMAND ----------

CATALOG = "azure_knowledge_asistant"
SCHEMA = "azure_rag"

EMBEDDING_TABLE = "document_embeddings"

VECTOR_INDEX = "azure_knowledge_asistant.azure_rag.knowledge_chunks_index"

TOP_K = 3

# COMMAND ----------

SYSTEM_PROMPT = """
You are an Azure Data Engineering knowledge assistant.

Your job is to answer questions using ONLY the information provided
in the retrieved context.

Rules:

1. Use the retrieved context as the primary and only source of truth.
2. Do not invent information that is not present in the context.
3. If the context does not contain enough information to answer the question,
   clearly say:
   "I don't have enough information in the provided knowledge base to answer this."
4. Keep the answer technically accurate and concise.
5. Explain technical concepts in simple language when possible.
6. When the context contains multiple relevant documents, combine the
   information carefully.
7. Always provide the source document names used for the answer.
8. Do not claim that a source says something unless that information is
   actually present in the retrieved context.
9. If the question is unrelated to Azure Data Engineering documentation,
   state that the question is outside the current knowledge base.

Retrieved context will be provided separately.
"""

# COMMAND ----------

USER_PROMPT_TEMPLATE = """
Use the following retrieved context to answer the user's question.

---------------- RETRIEVED CONTEXT ----------------

{context}

---------------- END CONTEXT ----------------

USER QUESTION:
{question}

Instructions:

1. Answer the question using only the retrieved context.

2. Do not use information that is not supported by the retrieved context.

3. Every factual statement should include the citation number
   corresponding to the source that supports it.

4. Use citation format:
   [1]
   [2]
   [1][2]

5. Only use citation numbers that exist in the retrieved context.

6. Do not invent document names, chunk IDs, URLs, or citation numbers.

7. If the context is insufficient, say:
   "I don't have enough information in the provided knowledge base to answer this."

8. Do not create a Sources section.
   The application will generate the Sources section automatically.

9. Keep the answer clear, technically accurate, and concise.
"""

# COMMAND ----------

NO_CONTEXT_MESSAGE = (
    "I don't have enough information in the provided "
    "knowledge base to answer this."
)

# COMMAND ----------

def format_context(results):
    """
    Convert AI Search retrieval results into citation-aware
    context for the LLM.
    """

    context_parts = []

    rows = results.collect()

    for i, row in enumerate(rows, start=1):

        document_name = (
            row["document_name"]
            if "document_name" in row
            else "Unknown document"
        )

        chunk_id = (
            row["chunk_id"]
            if "chunk_id" in row
            else "Unknown chunk"
        )

        chunk_number = (
            row["chunk_number"]
            if "chunk_number" in row
            else "Unknown"
        )

        source_path = (
            row["source_path"]
            if "source_path" in row
            else "Unknown"
        )

        chunk_text = (
            row["chunk_text"]
            if "chunk_text" in row
            else ""
        )

        context_part = f"""
SOURCE [{i}]

Document: {document_name}
Chunk Number: {chunk_number}
Chunk ID: {chunk_id}
Source Path: {source_path}

Content:
{chunk_text}
"""

        context_parts.append(context_part)

    return "\n".join(context_parts)

# COMMAND ----------

def build_user_prompt(question, results):
    """
    Build the final prompt that will be sent to the LLM.
    """
    
    context = format_context(results)

    prompt = USER_PROMPT_TEMPLATE.format(
        context=context,
        question=question
    )

    return prompt

# COMMAND ----------

# question = "What is Delta Lake?"

# results = retrieve_context(question)

# print(format_context(results))

# COMMAND ----------

def build_citation_metadata(results):
    """
    Create application-controlled citation metadata
    for retrieved chunks.
    """

    rows = results.collect()

    citations = []

    for i, row in enumerate(rows, start=1):

        citation = {
            "citation_id": i,
            "document_name": (
                row["document_name"]
                if "document_name" in row
                else "Unknown document"
            ),
            "chunk_id": (
                row["chunk_id"]
                if "chunk_id" in row
                else "Unknown chunk"
            ),
            "chunk_number": (
                row["chunk_number"]
                if "chunk_number" in row
                else None
            ),
            "source_path": (
                row["source_path"]
                if "source_path" in row
                else None
            ),
            "chunk_text": (
                row["chunk_text"]
                if "chunk_text" in row
                else ""
            )
        }

        citations.append(citation)

    return citations

# COMMAND ----------

# citations = build_citation_metadata(results)

# for citation in citations:
#     print(citation)

# COMMAND ----------

import re
def extract_citation_ids(answer):
    """
    Extract citation numbers such as [1], [2], [3]
    from the generated answer.
    """

    citation_numbers = re.findall(
        r"\[(\d+)\]",
        answer
    )

    citation_ids = sorted(
        set(int(number) for number in citation_numbers)
    )

    return citation_ids

# COMMAND ----------

test_answer = """
Delta Lake provides ACID transactions [1].
It also supports schema enforcement [1][2].
"""

print(extract_citation_ids(test_answer))

# COMMAND ----------

def validate_citation_ids(citation_ids, citations):
    """
    Validate that every citation generated by the LLM
    corresponds to an actual retrieved source.
    """

    valid_ids = {
        citation["citation_id"]
        for citation in citations
    }

    valid_citations = [
        citation_id
        for citation_id in citation_ids
        if citation_id in valid_ids
    ]

    invalid_citations = [
        citation_id
        for citation_id in citation_ids
        if citation_id not in valid_ids
    ]

    return valid_citations, invalid_citations

# COMMAND ----------

# citation_ids = [1, 2, 5]

# valid, invalid = validate_citation_ids(
#     citation_ids,
#     citations
# )

# print("Valid:", valid)
# print("Invalid:", invalid)

# COMMAND ----------

def resolve_citations(citation_ids, citations):
    """
    Resolve citation IDs generated by the LLM
    to the actual retrieved source metadata.
    """

    citation_lookup = {
        citation["citation_id"]: citation
        for citation in citations
    }

    resolved_sources = []

    for citation_id in citation_ids:

        if citation_id in citation_lookup:

            resolved_sources.append(
                citation_lookup[citation_id]
            )

    return resolved_sources

# COMMAND ----------

# resolved_sources = resolve_citations(
#     [1, 2],
#     citations
# )

# for source in resolved_sources:

#     print(
#         source["citation_id"],
#         source["document_name"],
#         source["chunk_id"]
#     )

# COMMAND ----------

def build_sources_section(resolved_sources):
    """
    Build the final Sources section from verified
    application-controlled citation metadata.
    """

    if not resolved_sources:
        return ""

    lines = ["\nSources:"]

    for source in resolved_sources:

        citation_id = source["citation_id"]
        document_name = source["document_name"]
        chunk_number = source["chunk_number"]
        source_path = source["source_path"]

        lines.append(
            f"[{citation_id}] {document_name} "
            f"(Chunk {chunk_number})"
        )

        if source_path:
            lines.append(
                f"    Path: {source_path}"
            )

    return "\n".join(lines)

# COMMAND ----------

def has_context(results):
    """
    Check whether retrieval returned useful context.
    """
    
    if results is None:
        return False

    if len(results) == 0:
        return False

    return True

# COMMAND ----------

import os

host = os.environ.get("DATABRICKS_HOST")
token_exists = bool(os.environ.get("DATABRICKS_TOKEN"))

print("Host:", host)
print("Token configured:", token_exists)

# COMMAND ----------

from openai import OpenAI

client = OpenAI(
    api_key=databricks_token,
    base_url="https://dbc-14b82404-0ff3.cloud.databricks.com/ai-gateway/mlflow/v1"
)

# COMMAND ----------

def generate_answer(system_prompt, user_prompt):
    """
    Send system and user prompts to the LLM
    and return only the final text answer.
    """

    response = client.chat.completions.create(
        model="system.ai.gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        max_tokens=500
    )

    content = response.choices[0].message.content

    # If the model returns structured content
    if isinstance(content, list):

        text_parts = []

        for item in content:

            if isinstance(item, dict):

                if item.get("type") == "text":
                    text_parts.append(
                        item.get("text", "")
                    )

        return "\n".join(text_parts).strip()

    # Normal string response
    return content.strip()

# COMMAND ----------

def rag_answer(question, top_k=3):

    # --------------------------------------------------
    # 1. Retrieve context
    # --------------------------------------------------

    results = retrieve_context(question, top_k=top_k)

    if results is None:

        return {
            "question": question,
            "answer": NO_CONTEXT_MESSAGE,
            "raw_answer": NO_CONTEXT_MESSAGE,
            "sources": [],
            "citations": [],
            "citation_ids": [],
            "valid_citations": [],
            "invalid_citations": [],
            "retrieved_chunks": []
        }

    rows = results.collect()

    if len(rows) == 0:

        return {
            "question": question,
            "answer": NO_CONTEXT_MESSAGE,
            "raw_answer": NO_CONTEXT_MESSAGE,
            "sources": [],
            "citations": [],
            "citation_ids": [],
            "valid_citations": [],
            "invalid_citations": [],
            "retrieved_chunks": []
        }

    # --------------------------------------------------
    # 2. Build citation metadata
    # --------------------------------------------------

    citations = build_citation_metadata(
        results
    )

    # --------------------------------------------------
    # 3. Build citation-aware context
    # --------------------------------------------------

    context = format_context(
        results
    )

    user_prompt = USER_PROMPT_TEMPLATE.format(
        context=context,
        question=question
    )

    # --------------------------------------------------
    # 4. Generate answer
    # --------------------------------------------------

    answer = generate_answer(
        SYSTEM_PROMPT,
        user_prompt
    )

    # --------------------------------------------------
    # 5. Extract citation IDs
    # --------------------------------------------------

    citation_ids = extract_citation_ids(
        answer
    )

    # --------------------------------------------------
    # 6. Validate citations
    # --------------------------------------------------

    valid_citations, invalid_citations = (
        validate_citation_ids(
            citation_ids,
            citations
        )
    )

    # --------------------------------------------------
    # 7. Resolve citations
    # --------------------------------------------------

    resolved_sources = resolve_citations(
        valid_citations,
        citations
    )

    # --------------------------------------------------
    # 8. Build Sources section
    # --------------------------------------------------

    sources_section = build_sources_section(
        resolved_sources
    )

    # --------------------------------------------------
    # 9. Final answer
    # --------------------------------------------------

    final_answer = (
        answer +
        sources_section
    )

    # --------------------------------------------------
    # 10. Return result
    # --------------------------------------------------

    return {
        "question": question,
        "answer": final_answer,
        "raw_answer": answer,
        "citation_ids": citation_ids,
        "valid_citations": valid_citations,
        "invalid_citations": invalid_citations,
        "sources": resolved_sources,
        "citations": citations,
        "retrieved_chunks": rows,
        "top_k": top_k
    }

# COMMAND ----------

# result = rag_answer(
#     "What is Delta Lake?"
# )

# print(result["answer"])

# COMMAND ----------

def display_rag_result(result):
    """
    Display a citation-aware RAG result.
    """

    print("=" * 80)
    print("QUESTION")
    print("=" * 80)

    print(result["question"])

    print("\n" + "=" * 80)
    print("ANSWER")
    print("=" * 80)

    print(result["answer"])

    print("\n" + "=" * 80)
    print("CITATION VALIDATION")
    print("=" * 80)

    print(
        "Generated citations:",
        result.get("citation_ids", [])
    )

    print(
        "Valid citations:",
        result.get("valid_citations", [])
    )

    print(
        "Invalid citations:",
        result.get("invalid_citations", [])
    )

    print("\n" + "=" * 80)
    print("VERIFIED SOURCES")
    print("=" * 80)

    if result["sources"]:

        for source in result["sources"]:

            print(
                f"[{source['citation_id']}] "
                f"{source['document_name']}"
            )

            print(
                f"    Chunk: {source['chunk_number']}"
            )

            print(
                f"    Chunk ID: {source['chunk_id']}"
            )

            print(
                f"    Path: {source['source_path']}"
            )

    else:
        print("No verified sources.")

    print("\n" + "=" * 80)
    print("RETRIEVED CONTEXT")
    print("=" * 80)

    for i, chunk in enumerate(
        result["retrieved_chunks"],
        start=1
    ):

        if hasattr(chunk, "asDict"):
            chunk = chunk.asDict()

        print(f"\nSOURCE [{i}]")
        print("-" * 80)

        print(
            "Document:",
            chunk.get(
                "document_name",
                "Unknown document"
            )
        )

        print(
            "Chunk ID:",
            chunk.get(
                "chunk_id",
                "Unknown chunk"
            )
        )

        print(
            "Chunk Number:",
            chunk.get(
                "chunk_number",
                "Unknown"
            )
        )

        print(
            "\nText:",
            chunk.get(
                "chunk_text",
                ""
            )
        )

# COMMAND ----------

def citation_consistency_check(result):

    invalid = result.get(
        "invalid_citations",
        []
    )

    if invalid:
        return {
            "status": "FAIL",
            "reason": f"Invalid citations: {invalid}"
        }

    if result.get("citation_ids") and not result.get(
        "valid_citations"
    ):
        return {
            "status": "FAIL",
            "reason": "Generated citations could not be resolved."
        }

    return {
        "status": "PASS",
        "reason": "All generated citations are resolvable."
    }

# COMMAND ----------

# result = rag_answer(
#     "How do I configure Apache Kafka?"
# )

# display_rag_result(result)

# COMMAND ----------

# check = citation_consistency_check(result)

# print(check)