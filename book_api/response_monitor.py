from book_api.persistence import persist_response


def get_response_stats(openai_response):
    """
    Extracts and returns the statistics from an OpenAI response object.

    :param openai_response: The response object from OpenAI API.
    :type openai_response: OpenAIResponse
    :returns: A dictionary containing model used,
        cached input tokens, uncached input tokens,
        reasoning output tokens, non-reasoning output tokens.
    :rtype: dict
    """
    stats = {"model": openai_response.model}
    usage_data = openai_response.usage
    if (
        hasattr(usage_data, 'input_tokens_details')
        and hasattr(usage_data, 'output_tokens_details')
    ):
        # Regular Responses API data
        cached_input_tokens = (
            usage_data.input_tokens_details.cached_tokens
        )
        uncached_input_tokens = (
            usage_data.input_tokens - cached_input_tokens
        )
        reasoning_output_tokens = (
            usage_data.output_tokens_details.reasoning_tokens
        )
        nonreasoning_output_tokens = (
            usage_data.output_tokens - reasoning_output_tokens
        )

        stats.update({
            "cached_input_tokens": cached_input_tokens,
            "uncached_input_tokens": uncached_input_tokens,
            "reasoning_output_tokens": reasoning_output_tokens,
            "nonreasoning_output_tokens": nonreasoning_output_tokens,
        })
    else:
        # Embeddings API data (currently only alternative)
        input_tokens = usage_data.prompt_tokens
        stats.update({"uncached_input_tokens": input_tokens})

    return stats


def record_response(instructions, input, openai_response, *, batch=False):
    """
    Records the response statistics for a given OpenAI response.

    :param instructions: Instructions for the response.
    :type instructions: str
    :param input: Input text sent to the OpenAI API.
    :type input: str
    :param openai_response: The response object from OpenAI API.
    :type openai_response: OpenAIResponse
    :param batch: Whether the request used the Batch API.
    :type batch: bool
    :returns: None
    """
    response_data = get_response_stats(openai_response)
    response_data["instructions"] = instructions
    response_data["input"] = input
    response_data["output"] = openai_response.output_text
    persist_response(response_data)
    print("[INFO] Response recorded in the database.")
