# Use the official Ollama image as the base
FROM ollama/ollama:latest

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Install Python and pip if not already available
RUN apt-get update && apt-get install -y --no-install-recommends \
    sudo\
    wget \
    curl\
    python3 \
    python3-pip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install necessary Python dependencies
RUN pip3 install --upgrade pip

# Set the working directory
WORKDIR /app

# Copy application files into the container
COPY . /app/

# Install application dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Ensure ChromaDB persistence directory exists
RUN mkdir -p /app/chroma_data

# Expose application and Ollama ports
EXPOSE 8000 11434

# Override the default entrypoint to allow shell commands
ENTRYPOINT ["/bin/bash", "-c"]

# Run Ollama and the RAG pipeline together
CMD bash -c "ollama pull llama2:7b-chat && ollama serve & python ingest_data.py && python rag_pipeline.py"

