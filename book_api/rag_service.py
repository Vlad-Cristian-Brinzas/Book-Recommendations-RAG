import json
from book_api.open_ai_service import get_response, get_response_text
from book_api.chroma_db_service import get_book_by_themes


# Define callable tools
tools = [
    {
        "type": "function",
        "name": "get_books_by_themes",
        "description": "Get book summaries based on thematic similarity.",
        "parameters": {
            "type": "object",
            "properties": {
                "themes": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": (
                        "A list of themes to search for."
                    ),
                    # Note: probably works without description too
                },
                "n_results": {
                    "type": "integer",
                    "description": (
                        "The number of book summaries to retrieve (default 3)."
                    ),
                    # Note: probably works without description too
                },
            },
            "required": ["themes"],
        },
    },
]


def get_book_recommendation(user_input):
    """
    Get formatted book recommendations based on user input.
    """
    input_list = [user_input]

    # Step 1: Send user input to OpenAI and get tool call
    instructions_identify_themes = (
        "Based on the user's input, identify relevant themes"
        " and call the appropriate tool to get book summaries."
    )
    response = get_response(
        input=input_list,
        instructions=instructions_identify_themes,
        tools=tools,
        max_output_tokens=100,  # Can it fit in 100 tokens?
    )
    input_list.append(response.output)
    # TODO: do we need *all* the output?
    # (If not, we could save tokens by passing only relevant bits.)

    # Step 2: Parse the tool call from the response
    for item in response.output:
        if item.type == "function_call":
            function_name = item.name
            if not function_name == "get_books_by_themes":
                # We only handle this one function for now
                raise ValueError(
                    f"Unexpected function call: {function_name}"
                )
            arguments = json.loads(item.arguments)
            themes = arguments.themes  # Has to be there!
            n_results = arguments.get("n_results")

            # Step 3: Call the function to get book summaries
            kwargs = {}
            if n_results is not None:
                kwargs["n_results"] = n_results
            recommended_books = get_book_by_themes(
                themes, **kwargs
            )

            input_list.append({
                "type": "function_call_output",
                "call_id": item.call_id,
                "output": json.dumps({
                    "recommended_books": recommended_books
                })
            })

    # Step 4: Pass summaries back to OpenAI for formatting
    instructions_format_recommendations = (
        "Format the book recommendations into a user-friendly"
        " format. Include title, author, and summary for each book."
        " Do not change the content of the summaries."
    )
    final_response_text = get_response_text(
        input=input_list,
        instructions=instructions_format_recommendations,
        max_output_tokens=1000,
    )

    return final_response_text
