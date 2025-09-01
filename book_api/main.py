# TODO: make endpoints
# We do need to figure out what we want to return
# from these endpoints (how much detail, what format)
# and get the service to do that.
from contextlib import asynccontextmanager
from fastapi import FastAPI
from pydantic import BaseModel
from book_api.open_ai_service import get_response_text
from book_api.persistence import setup_database


class PromptRequest(BaseModel):
    prompt: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    # Setup persistence (SQLite DB)
    setup_database()

    yield

    # Shutdown
    # (Nothing to do here currently)
    # (Could consider closing connections if needed)


app = FastAPI(lifespan=lifespan)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/book-recommendation")
async def book_recommendation(request: PromptRequest):
    response_text = get_response_text(request.prompt)
    return {"response": response_text}
