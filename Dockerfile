# Use an official Python runtime as the base image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Install system-level dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    wget \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN wget -qO- https://ollama.ai/install.sh | bash

# Set the working directory
WORKDIR /app

# Copy application files
COPY . /app/

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Ensure ChromaDB persistence directory exists
RUN mkdir -p /app/chroma_data

# Expose ports for Ollama and application
EXPOSE 8000 11434

# Run Ollama and the RAG pipeline together
CMD bash -c "ollama serve & uvicorn rag_pipeline:app --host 0.0.0.0 --port 8000"
