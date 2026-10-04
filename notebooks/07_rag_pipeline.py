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

1. Answer the question using the retrieved context.
2. Do not use information that is not supported by the context.
3. If the context is insufficient, say:
   "I don't have enough information in the provided knowledge base to answer this."
4. Keep the answer clear and technically accurate.
5. At the end of the answer, provide a short "Sources" section.
6. List only the document names that were actually provided in the context.
"""

# COMMAND ----------

NO_CONTEXT_MESSAGE = (
    "I don't have enough information in the provided "
    "knowledge base to answer this."
)

# COMMAND ----------

def format_context(results):
    """
    Convert AI Search retrieval results into text
    that can be provided to the LLM.
    """

    context_parts = []

    rows = results.collect()

    for i, row in enumerate(rows, start=1):

        document_name = row["document_name"] if "document_name" in row else "Unknown document"
        chunk_id = row["chunk_id"] if "chunk_id" in row else "Unknown chunk"
        chunk_text = row["chunk_text"] if "chunk_text" in row else ""

        context_part = f"""
SOURCE {i}

Document: {document_name}
Chunk ID: {chunk_id}

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

question = "What is Delta Lake?"
results = retrieve_context(question)
user_prompt = build_user_prompt(
    question,
    results
)

print(user_prompt)

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

def rag_answer(question):

    # 1. Retrieve context
    results = retrieve_context(question)

    # 2. Check context
    if results.count() == 0:
        return {
            "question": question,
            "answer": NO_CONTEXT_MESSAGE,
            "sources": [],
            "retrieved_chunks": []
        }

    # 3. Build prompt
    user_prompt = build_user_prompt(
        question,
        results
    )

    # 4. Generate answer
    answer = generate_answer(
        SYSTEM_PROMPT,
        user_prompt
    )

    # 5. Extract sources
    sources = []

    rows = results.collect()

    for row in rows:

        document_name = row["document_name"]

        if document_name not in sources:
            sources.append(document_name)

    # 6. Return result
    return {
        "question": question,
        "answer": answer,
        "sources": sources,
        "retrieved_chunks": rows
    }

# COMMAND ----------

result = rag_answer(
    "What is Delta Lake?"
)

print("QUESTION:")
print(result["question"])

print("\nANSWER:")
print(result["answer"])

print("\nSOURCES:")
for source in result["sources"]:
    print("-", source)

# COMMAND ----------

def display_rag_result(result):
    """
    Display a RAG result in a readable format.
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
    print("SOURCES")
    print("=" * 80)

    if result["sources"]:
        for source in result["sources"]:
            print("-", source)
    else:
        print("No sources retrieved.")

    print("\n" + "=" * 80)
    print("RETRIEVED CONTEXT")
    print("=" * 80)

    for i, chunk in enumerate(
        result["retrieved_chunks"],
        start=1
    ):

        # Handle Spark Row objects
        if hasattr(chunk, "asDict"):
            chunk = chunk.asDict()

        print(f"\nCHUNK {i}")
        print("-" * 80)

        print(
            "Document:",
            chunk.get("document_name", "Unknown document")
        )

        print(
            "Chunk ID:",
            chunk.get("chunk_id", "Unknown chunk")
        )

        print(
            "\nText:",
            chunk.get("chunk_text", "")
        )

# COMMAND ----------

result = rag_answer(
    "How do I configure Apache Kafka?"
)

display_rag_result(result)