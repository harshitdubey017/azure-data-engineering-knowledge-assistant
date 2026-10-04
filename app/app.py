
import os
import re
import logging
from typing import Any, Dict, List, Tuple

import streamlit as st
from openai import OpenAI

from databricks.ai_search.client import AISearchClient
from databricks.sdk import WorkspaceClient


# ============================================================
# APPLICATION CONFIGURATION
# ============================================================

APP_TITLE = "Azure Data Engineering Knowledge Assistant"

DEFAULT_DATABRICKS_HOST = (
    "dbc-14b82404-0ff3.cloud.databricks.com"
)

VECTOR_INDEX = os.getenv(
    "VECTOR_SEARCH_INDEX",
    "azure_knowledge_asistant.azure_rag.knowledge_chunks_index"
)

LLM_MODEL = os.getenv(
    "LLM_MODEL",
    "system.ai.gpt-oss-20b"
)

EMBEDDING_MODEL_NAME = "BAAI/bge-small-en-v1.5"

TOP_K = 3

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


# ============================================================
# STREAMLIT PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="📚",
    layout="wide"
)


# ============================================================
# DATABRICKS AUTHENTICATION
# ============================================================

def get_databricks_host() -> str:
    """
    Retrieves the Databricks workspace URL.
    """

    host = os.getenv(
        "DATABRICKS_HOST",
        DEFAULT_DATABRICKS_HOST
    ).strip()

    if not host:
        raise RuntimeError(
            "DATABRICKS_HOST is not configured."
        )

    return f"https://{os.environ['DATABRICKS_HOST']}"


def get_service_principal_credentials() -> Tuple[str, str]:
    """
    Retrieves the application service-principal credentials.

    These variables are provided by Databricks App
    authorization configuration.
    """

    client_id = os.getenv(
        "DATABRICKS_CLIENT_ID",
        ""
    ).strip()

    client_secret = os.getenv(
        "DATABRICKS_CLIENT_SECRET",
        ""
    ).strip()

    if not client_id:
        raise RuntimeError(
            "DATABRICKS_CLIENT_ID is missing from the "
            "application environment."
        )

    if not client_secret:
        raise RuntimeError(
            "DATABRICKS_CLIENT_SECRET is missing from the "
            "application environment."
        )

    return client_id, client_secret


# ============================================================
# DATABRICKS WORKSPACE CLIENT
# ============================================================

@st.cache_resource
def get_workspace_client():
    """
    Creates a Databricks SDK WorkspaceClient using
    OAuth machine-to-machine authentication.
    """

    host = get_databricks_host()

    client_id, client_secret = (
        get_service_principal_credentials()
    )

    workspace_client = WorkspaceClient(
        host=host,
        client_id=client_id,
        client_secret=client_secret
    )

    return workspace_client


# ============================================================
# AI SEARCH CLIENT
# ============================================================

@st.cache_resource
def get_ai_search_index():
    """
    Initializes Databricks AI Search using service-principal
    authentication and retrieves the configured index.
    """

    workspace_url = get_databricks_host()

    client_id, client_secret = (
        get_service_principal_credentials()
    )

    search_client = AISearchClient(
        workspace_url=workspace_url,
        service_principal_client_id=client_id,
        service_principal_client_secret=client_secret
    )

    index = search_client.get_index(
        index_name=VECTOR_INDEX
    )

    return index


# ============================================================
# LLM CLIENT
# ============================================================

@st.cache_resource
def get_llm_client():
    """
    Creates the OpenAI-compatible Databricks AI Gateway client.

    The Databricks SDK obtains OAuth credentials using the
    service principal. The current OAuth access token is
    obtained when constructing the OpenAI client.
    """

    workspace_url = get_databricks_host()

    workspace_client = get_workspace_client()

    auth_headers = workspace_client.config.authenticate()

    authorization_header = auth_headers.get(
        "Authorization",
        ""
    )

    if not authorization_header.startswith("Bearer "):
        raise RuntimeError(
            "Databricks SDK did not return a valid OAuth "
            "authorization header."
        )

    access_token = authorization_header.split(
        " ",
        1
    )[1]

    return OpenAI(
        api_key=access_token,
        base_url=f"{workspace_url}/ai-gateway/mlflow/v1"
    )


# ============================================================
# QUERY EMBEDDING
# ============================================================

@st.cache_resource
def get_embedding_model():
    """
    Loads the embedding model once per application process.
    """

    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(
        EMBEDDING_MODEL_NAME
    )

    return model


def generate_query_embedding(
    question: str
) -> List[float]:
    """
    Converts the user question into a normalized embedding.
    """

    model = get_embedding_model()

    embedding = model.encode(
        question,
        normalize_embeddings=True
    )

    return embedding.tolist()


# ============================================================
# VECTOR SEARCH
# ============================================================

def search_knowledge_base(
    question: str,
    top_k: int = TOP_K
) -> List[Dict[str, Any]]:
    """
    Performs semantic retrieval against the AI Search index.

    Converts the SDK response into a list of Python dictionaries,
    avoiding a Spark session dependency inside the app.
    """

    query_vector = generate_query_embedding(
        question
    )

    index = get_ai_search_index()

    results = index.similarity_search(
        query_vector=query_vector,
        columns=[
            "chunk_id",
            "document_id",
            "document_name",
            "chunk_number",
            "chunk_text",
            "source_path"
        ],
        num_results=top_k
    )

    manifest_columns = results.get(
        "manifest",
        {}
    ).get(
        "columns",
        []
    )

    column_names = [
        column["name"]
        for column in manifest_columns
    ]

    data_rows = results.get(
        "result",
        {}
    ).get(
        "data_array",
        []
    )

    documents = []

    for row in data_rows:

        document = dict(
            zip(column_names, row)
        )

        if document.get("chunk_text"):
            documents.append(document)

    return documents


# ============================================================
# CONTEXT FORMATTING
# ============================================================

def format_retrieved_context(
    documents: List[Dict[str, Any]]
) -> str:
    """
    Formats retrieved knowledge chunks and assigns
    sequential citation identifiers.
    """

    context_parts = []

    for index, document in enumerate(
        documents,
        start=1
    ):

        document_name = document.get(
            "document_name",
            "Unknown document"
        )

        chunk_text = document.get(
            "chunk_text",
            ""
        )

        source_path = document.get(
            "source_path",
            ""
        )

        chunk_number = document.get(
            "chunk_number",
            ""
        )

        context_parts.append(
            f"""
[SOURCE {index}]

Document: {document_name}
Chunk: {chunk_number}
Source Path: {source_path}

Content:
{chunk_text}
"""
        )

    return "\n\n".join(context_parts)


# ============================================================
# CITATION EXTRACTION
# ============================================================

def extract_citation_ids(
    answer: str
) -> List[int]:
    """
    Extracts unique numeric citations such as [1], [2], [3].
    """

    citation_ids = re.findall(
        r"\[(\d+)\]",
        answer
    )

    return list(
        dict.fromkeys(
            int(citation_id)
            for citation_id in citation_ids
        )
    )


def resolve_citations(
    answer: str,
    documents: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Resolves citation numbers against the retrieved documents.
    """

    citation_ids = extract_citation_ids(
        answer
    )

    resolved_sources = []

    for citation_id in citation_ids:

        if citation_id < 1:
            continue

        if citation_id > len(documents):
            continue

        document = documents[citation_id - 1]

        resolved_sources.append({
            "citation_id": citation_id,
            "document_name": document.get(
                "document_name",
                "Unknown document"
            ),
            "source_path": document.get(
                "source_path",
                ""
            ),
            "chunk_number": document.get(
                "chunk_number",
                ""
            )
        })

    return resolved_sources


# ============================================================
# RAG PROMPT
# ============================================================

def build_rag_prompt(
    question: str,
    context: str
) -> str:
    """
    Builds the context-grounded RAG prompt.
    """

    return f"""
You are an Azure Data Engineering Knowledge Assistant.

Your task is to answer questions using the retrieved
knowledge-base context.

Follow these rules strictly:

1. Use the supplied context as the primary source of truth.
2. Do not invent technical facts, configurations, commands,
   documentation references, or implementation details.
3. If the context does not contain enough information,
   clearly state that the available knowledge base does not
   provide sufficient information.
4. Explain technical concepts clearly and accurately.
5. Use numbered steps for procedures when appropriate.
6. Include citations in the format [1], [2], etc.
7. Only cite source numbers present in the retrieved context.
8. Do not fabricate citations.
9. Distinguish source-supported facts from assumptions.
10. Keep the answer relevant to the user's question.

Retrieved Knowledge Base Context:

{context}

User Question:

{question}

Provide a clear, structured answer with citations.
"""


# ============================================================
# GENERATE ANSWER
# ============================================================

def generate_answer(
    question: str,
    context: str
) -> str:
    """
    Generates an answer using the Databricks model endpoint.
    """

    client = get_llm_client()

    prompt = build_rag_prompt(
        question=question,
        context=context
    )

    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a precise Azure Data Engineering "
                    "assistant. Ground your answers in the "
                    "retrieved context and cite sources."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.1,
        max_tokens=1500
    )

    answer = response.choices[0].message.content
    logger.info(f"Answer type: {type(answer)}")
    logger.info(f"Answer: {answer}")

    if not answer:
        return (
            "The model returned an empty response. "
            "Please try again."
        )
    
    if isinstance(answer, list):
        text_parts = []
        
        for item in answer:
            if isinstance(item, dict):
                text_parts.append(item.get("text", ""))
            else:
                text_parts.append(str(item))
        
        answer = " ".join(text_parts)

    return str(answer).strip()


# ============================================================
# SOURCE DISPLAY
# ============================================================

def display_sources(
    sources: List[Dict[str, Any]]
):
    """
    Displays the source documents associated with an answer.
    """

    if not sources:
        st.caption(
            "No valid source citations were returned."
        )
        return

    with st.expander(
        "📚 Retrieved Sources",
        expanded=False
    ):

        for source in sources:

            st.markdown(
                f"**[{source['citation_id']}] "
                f"{source['document_name']}**"
            )

            if source.get("chunk_number") is not None:

                st.caption(
                    f"Chunk: {source['chunk_number']}"
                )

            if source.get("source_path"):

                st.caption(
                    f"Source: {source['source_path']}"
                )

            st.divider()


# ============================================================
# END-TO-END RAG PIPELINE
# ============================================================

def process_question(
    question: str
) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Executes the complete RAG workflow.

    Question
        -> Embedding
        -> AI Search
        -> Context formatting
        -> LLM generation
        -> Citation resolution
        -> Answer
    """

    documents = search_knowledge_base(
        question=question,
        top_k=TOP_K
    )

    if not documents:

        return (
            "I could not retrieve relevant information "
            "from the knowledge base for this question.",
            []
        )

    context = format_retrieved_context(
        documents
    )

    answer = generate_answer(
        question=question,
        context=context
    )

    sources = resolve_citations(
        answer=answer,
        documents=documents
    )

    return answer, sources


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("📚 Knowledge Assistant")

    st.markdown(
        """
        Ask questions about Azure Data Engineering topics
        covered by the indexed knowledge base.

        **Capabilities**
        - Semantic retrieval
        - Context-grounded answers
        - Source citations
        - Conversational interface
        """
    )

    st.divider()

    st.markdown("**Configuration**")

    st.caption(
        f"Vector Index: `{VECTOR_INDEX}`"
    )

    st.caption(
        f"Model: `{LLM_MODEL}`"
    )

    if st.button(
        "Clear Chat",
        use_container_width=True
    ):

        st.session_state.messages = []

        st.rerun()


# ============================================================
# MAIN APPLICATION
# ============================================================

st.title(
    "📚 Azure Data Engineering Knowledge Assistant"
)

st.markdown(
    """
    Ask technical questions about Azure Data Factory,
    Azure Databricks, PySpark, SQL, Delta Lake, data pipelines,
    and related data engineering concepts.

    Answers are generated using retrieved knowledge-base
    content and include source references where available.
    """
)

st.divider()


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:

    st.session_state.messages = []


# ============================================================
# DISPLAY CHAT HISTORY
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(
            message["content"]
        )

        if message["role"] == "assistant":

            sources = message.get(
                "sources",
                []
            )

            if sources:
                display_sources(sources)


# ============================================================
# CHAT INPUT
# ============================================================

user_question = st.chat_input(
    "Ask an Azure Data Engineering question..."
)


if user_question:

    user_question = user_question.strip()

    if user_question:

        st.session_state.messages.append({
            "role": "user",
            "content": user_question
        })

        with st.chat_message("user"):

            st.markdown(
                user_question
            )

        with st.chat_message("assistant"):

            with st.spinner(
                "Searching the knowledge base and generating an answer..."
            ):

                try:

                    answer, sources = process_question(
                        user_question
                    )

                    st.markdown(answer)

                    if sources:
                        display_sources(sources)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources
                    })

                except Exception:

                    logger.exception(
                        "RAG application request failed."
                    )

                    error_message = (
                        "The application encountered an error "
                        "while processing your question.\n\n"
                        "Check the Databricks App logs for "
                        "technical details. Verify service-principal "
                        "authentication, AI Search permissions, "
                        "index availability, and model endpoint access."
                    )

                    st.error(
                        error_message
                    )

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_message,
                        "sources": []
                    })