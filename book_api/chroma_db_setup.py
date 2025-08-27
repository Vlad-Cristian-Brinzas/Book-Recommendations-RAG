# Plan:
# Start from some hard-coded summaries (we could put them in a file)
# Embed via OpenAI text-embedding-3-small
# SAVE those embeddings to a file or something (embedding is expensive-ish)
# Or, more sensibly, save them to ChromaDB or some similar vector database
# (Make sure to actually persist the data on disk, not just in memory)
from chromadb import PersistentClient
