# Use this file to check that we can get OpenAI responses
# (You have to run this manually - it's just a temp file of sorts)
# (Run via `python -m book_api.handy_scripts.api_test`)
# (Since VS Code / IDEs might launch you too deep in, and imports will fail)
from book_api.persistence import setup_database
from book_api.open_ai_service import get_response_text  # ,get_embedding_vector

setup_database()
response = get_response_text("Send me ONE unicorn emoji")
print("Response from OpenAI API:\n", response)
# embedding = get_embedding_vector("I like trains!")
# print("Embedding for 'I like trains!':", embedding)
