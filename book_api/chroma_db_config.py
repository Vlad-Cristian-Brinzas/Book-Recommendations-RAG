from os import getenv

CHROMA_HOST = getenv("CHROMA_HOST")  # No default, must be set
CHROMA_PORT = int(getenv("CHROMA_PORT", "8000"))
CHROMA_COLLECTION_NAME = getenv("CHROMA_COLLECTION_NAME", "book_summaries")
