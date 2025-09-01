# Book Recommendation RAG Demo

This is a small demo project showcasing Retrieval-Augmented Generation (RAG) and tool calling for book recommendations. The system recommends books from a limited library using semantic search and LLM-based formatting. It's rough around the edges, but demonstrates the core concepts.

## Structure

- **Python API** (`book_api/`): FastAPI backend with endpoints for book recommendations, using ChromaDB for semantic search and OpenAI for LLM responses.
- **Minimal React Frontend** (`book_ui/`): Simple UI to send prompts to the API and display responses.
- **Bruno Requests** (`Bruno-LLM-Requests/`): Minimal HTTP requests for manual API testing.
- **Handy Scripts** (`book_api/handy_scripts/`): Includes a `costs.py` script to estimate token costs for API usage.

## Running the Demo

The recommended way to run the project is via Docker Compose:

```sh
docker compose up --build
```

This will start:
- The ChromaDB service (for vector search)
- The Python API (FastAPI, on port 8000)
- The React frontend (served by Nginx, on port 80)

Access the frontend at [http://localhost](http://localhost).

## API Usage

- The main endpoint is `/book-recommendation` (POST), which accepts a prompt and returns formatted book recommendations.
- The backend uses RAG: it extracts themes from your prompt, retrieves relevant books from the library, and formats the response using the OpenAI Responses API.

## Notes

- The book library is limited and hardcoded in [`book_api/summaries.txt`](book_api/summaries.txt).
- The frontend is intentionally minimal — just a textarea and a button at the moment.
- The project is a demo and not production-ready; expect rough edges and minimal error handling.
- Requires an OpenAI API key (set via environment variable).

## Quick Start

1. Set your OpenAI API key in `.env` or your shell.
2. Run `docker compose up --build`.
3. Open [http://localhost](http://localhost) and try a prompt like "Recommend me a horror book set in Antarctica".

---

For more details, see the code in [`book_api/`](book_api) and and [`book_ui/`](book_ui).