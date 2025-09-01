# Use a slim Python image
FROM python:3.13.5-slim

# Set working directory
WORKDIR /app

# Copy requirements file
COPY book_api/requirements.txt book_api/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r book_api/requirements.txt

# Copy rest of the project files
COPY book_api/ book_api/

# Expose the port that the app runs on
EXPOSE 8000

# Start the FastAPI application using Uvicorn
CMD ["uvicorn", "book_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
