from book_api.chroma_db_setup import get_chroma_collection


def get_book_by_themes(themes, n_results=3):
    """
    Retrieve book summaries from ChromaDB based on thematic similarity.

    :param themes: A list of strings describing the themes to search for.
    :type themes: list[str]
    :param n_results: The number of similar book summaries to retrieve.
    :type n_results: int
    :returns: A list of dictionaries containing title, author, and summary.
    :rtype: list of dict
    """
    collection = get_chroma_collection()
    results = collection.query(
        query_texts=[" ".join(themes)],
        n_results=n_results,
        include=["metadatas", "documents", "distances"],
    )
    ids = results["ids"][0]
    documents = results["documents"][0]  # type: ignore
    metadatas = results["metadatas"][0]  # type: ignore
    # distances = results["distances"][0]  # type: ignore
    # Pylance doesn't understand that we explicitly asked for these

    books = []
    for idx in range(len(ids)):
        books.append({
            "title": metadatas[idx].get("title", "Unknown Title"),
            "author": metadatas[idx].get("author", "Unknown Author"),
            "summary": documents[idx],
            # "distance": distances[idx],
        })

    return books
