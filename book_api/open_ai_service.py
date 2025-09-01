from typing import List
from openai import OpenAI
from book_api.response_monitor import record_response

client = OpenAI()


def get_response(
    input_text, *, max_output_tokens=500, model="gpt-4.1-nano"
):  # 500 tokens as sanity limit
    """
    Get a response from the OpenAI API for a given input text.

    :param input_text: The input text to send to the OpenAI API.
    :type input_text: str
    :param max_output_tokens: The maximum number of output tokens.
    :type max_output_tokens: int, optional
    :param model: The model to use for the response.
        (Defaults to "gpt-4.1-nano".)
    :type model: str, optional
    :returns: The response object from the OpenAI API.
    :rtype: OpenAIResponse
    """
    # No caching for requests shorter than 1024 tokens, unfortunately
    try:
        response = client.responses.create(
            model=model,
            input=input_text,
            max_output_tokens=max_output_tokens,
        )
        record_response(
            instructions=None,
            input=input_text,
            openai_response=response
        )
        return response
    except Exception as e:
        # Return a mocked response for development if OpenAI API fails
        class MockResponse:
            def __init__(self, text):
                self.output_text = text
        return MockResponse(
            "[MOCKED RESPONSE]"
            f"\nCould not reach OpenAI: {e}."
            f"\nInput was: {input_text}"
        )


def get_response_text(
    input_text, *, max_output_tokens=500, model="gpt-4.1-nano"
):
    """
    Get a response text from the OpenAI API for a given input text.

    :param input_text: The input text to send to the OpenAI API.
    :type input_text: str
    :param max_output_tokens: The maximum number of output tokens.
    :type max_output_tokens: int, optional
    :param model: The model to use for the response.
        (Defaults to "gpt-4.1-nano".)
    :type model: str, optional
    :returns: The response text from the OpenAI API.
    :rtype: str
    """
    response = get_response(
        input_text,
        max_output_tokens=max_output_tokens,
        model=model
    )
    return response.output_text


def get_embedding(texts):
    """
    Get an embedding for the text using OpenAI's text-embedding-3-small model.

    :param texts: The texts to embed.
    :type texts: List[str]
    :returns: The reponse object from the OpenAI API.
    :rtype: OpenAIResponse
    """
    try:
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=texts
        )
        record_response(
            instructions=None,
            input=str(texts),
            openai_response=response
        )
        return response
    except Exception:
        # Return a mocked embedding for development if OpenAI API fails
        class MockEmbedding:
            def __init__(self, embedding):
                self.data = [{'embedding': embedding}]
        return MockEmbedding([0.0] * 1536)  # Example: 1536-dim zero vector


def get_embedding_vector(texts: List[str]) -> List[List[float]]:
    """
    Get an embedding vector for the text using OpenAI's text-embedding-3-small
    model.

    :param texts: The texts to embed.
    :type texts: List[str]
    :returns: The embedding vector as a list.
    :rtype: list
    """
    response = get_embedding(texts)
    return [entry.embedding for entry in response.data]  # type: ignore
    # TODO: Type is fine, I swear! Figure why VS Code disagrees
