from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

from config import settings

SYSTEM_PROMPT = """You are an HR assistant helping recruiters find information about candidates from their resumes.

Use the following context to answer the question. If you don't know the answer, say so — don't make up information.

Context:
{context}"""


def get_embeddings() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(
        model=settings.embedding_model,
        openai_api_key=settings.openrouter_api_key,
        openai_api_base=settings.openrouter_base_url,
    )


def get_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model=settings.llm_model,
        openai_api_key=settings.openrouter_api_key,
        openai_api_base=settings.openrouter_base_url,
        temperature=0,
    )


def get_text_splitter() -> RecursiveCharacterTextSplitter:
    return RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )


def build_vector_store(chunks: list[str], metadatas: list[dict] | None = None):
    embeddings = get_embeddings()
    return Chroma.from_texts(
        texts=chunks,
        embedding=embeddings,
        metadatas=metadatas,
        persist_directory="./chroma_db",
    )


def load_vector_store():
    embeddings = get_embeddings()
    return Chroma(
        embedding_function=embeddings,
        persist_directory="./chroma_db",
    )


def build_rag_chain(vector_store):
    llm = get_llm()
    retriever = vector_store.as_retriever(search_kwargs={"k": settings.top_k})

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "{input}"),
    ])

    combine_chain = create_stuff_documents_chain(llm, prompt)
    return create_retrieval_chain(retriever, combine_chain)
