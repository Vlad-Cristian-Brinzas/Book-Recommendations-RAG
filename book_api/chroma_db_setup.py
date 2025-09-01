from os import getenv
from chromadb import HttpClient
from chromadb.api.types import EmbeddingFunction, Embeddable, Metadata
from book_api.open_ai_service import get_embedding_vector


_client = None  # Must setup first
_collection = None


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
    global _client, _collection

    # Step 0: Ensure setup has been done
    if _client is None or _collection is None:
        raise ValueError(
            "ChromaDB client or collection not set up."
            " Call setup_chroma_db() first."
        )

    # Note: currently we're only checking that there ARE summaries in there
    # A more complete solution would also check whether these are up-to-date
    # (e.g. that they haven't been updated in summaries.txt), and if not
    # update only the changed ones.
    # Step 1: Check if there are already summaries in the collection
    existing_count = _collection.count()
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

    _collection.add(
        ids=ids,
        metadatas=metadatas,
        documents=documents
    )


def setup_chroma_db():
    """Set up the ChromaDB persistent client."""
    global _client, _collection

    # Set up the ChromaDB persistent client
    if _client is None:
        # get CHROMA_HOST, else throw error if not set
        chroma_host = getenv("CHROMA_HOST")
        if chroma_host is None:
            raise ValueError("CHROMA_HOST environment variable not set")
        chroma_port = int(getenv("CHROMA_PORT", "8000"))

        _client = HttpClient(host=chroma_host, port=chroma_port)

    # Set up embedding callable
    # (Consider getting a cleverer name)
    class MyEmbedder(EmbeddingFunction[Embeddable]):
        def __call__(self, texts):
            return get_embedding_vector(texts)

    # Set up a collection (like a table) for book summaries
    _collection = _client.get_or_create_collection(
        name="book_summaries",
        metadata={"hnsw:space": "cosine"},
        embedding_function=MyEmbedder()
    )
