# TODO: make endpoints
# We do need to figure out what we want to return
# from these endpoints (how much detail, what format)
# and get the service to do that.
from fastapi import FastAPI
from pydantic import BaseModel
from book_api.open_ai_service import get_response_text


class PromptRequest(BaseModel):
    prompt: str


app = FastAPI()


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/book-recommendation")
async def book_recommendation(request: PromptRequest):
    response_text = get_response_text(request.prompt)
    return {"response": response_text}
