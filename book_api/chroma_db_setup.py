from chromadb import HttpClient
from chromadb.api.types import EmbeddingFunction, Embeddable, Metadata
from book_api.open_ai_service import get_embedding_vector
from book_api.chroma_db_config import (
    CHROMA_HOST,
    CHROMA_PORT,
    CHROMA_COLLECTION_NAME,
)


_client = None  # Must setup first
_collection = None


def get_chroma_collection():
    """Get the ChromaDB collection (after setup)."""
    if _collection is None:
        raise ValueError(
            "ChromaDB collection not set up."
            " Call setup_chroma_db() first."
        )
    return _collection


def get_id_for_title_author(title, author):
    """Get the ChromaDB ID for a given title and author."""
    return (
        f"summary_{title.lower().replace(' ', '_')}"
        f"_{author.lower().replace(' ', '_')}"
    )


def parse_summaries_txt():
    """
    Parse summaries.txt into a list of (title, author, summary) tuples.
    """
    summaries_path = "book_api/summaries.txt"  # Note: currently hardcoded

    summaries = []
    with open(summaries_path, "r", encoding="utf-8") as summaries_file:
        content = summaries_file.read()

        entries = content.strip().split("\n\n")
        for entry in entries:
            lines = entry.strip().split("\n")
            if len(lines) >= 3:
                title = lines[0].replace("## Title: ", "").strip()
                author = lines[1].replace("# Author: ", "").strip()
                summary = "\n".join(lines[2:]).strip()
                summaries.append((title, author, summary))

    return summaries


def ensure_summaries_up_to_date():
    """Ensure that the summaries are loaded into the ChromaDB collection."""
    # Step 0: Ensure setup has been done
    collection = get_chroma_collection()

    # Note: currently we're only checking that there ARE summaries in there
    # A more complete solution would also check whether these are up-to-date
    # (e.g. that they haven't been updated in summaries.txt), and if not
    # update only the changed ones.
    # Step 1: Check if there are already summaries in the collection
    existing_count = collection.count()
    if existing_count > 0:
        print(
            "ChromaDB collection already has"
            f" {existing_count} summaries. Skipping load."
        )
        return

    # Step 2: If not, load summaries from summaries.txt
    print(
        "ChromaDB collection is empty."
        " Loading summaries from summaries.txt..."
    )
    summaries = parse_summaries_txt()
    ids = [
        get_id_for_title_author(title, author)
        for title, author, _ in summaries
    ]
    metadatas: list[Metadata] = [
        {"title": title, "author": author}
        for title, author, _ in summaries
    ]
    documents = [summary for _, _, summary in summaries]

    collection.add(
        ids=ids,
        metadatas=metadatas,
        documents=documents
    )


def setup_chroma_db():
    """Set up the ChromaDB persistent client."""
    global _client, _collection

    # Set up the ChromaDB persistent client
    if _client is None:
        if CHROMA_HOST is None:
            raise ValueError("CHROMA_HOST environment variable not set")
        _client = HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)

    # Set up embedding callable
    # (Consider getting a cleverer name)
    class MyEmbedder(EmbeddingFunction[Embeddable]):
        def __call__(self, texts):
            return get_embedding_vector(texts)

    # Set up a collection (like a table) for book summaries
    _collection = _client.get_or_create_collection(
        name=CHROMA_COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
        # FIXME: What's this metadata above even say?
        embedding_function=MyEmbedder()
    )
