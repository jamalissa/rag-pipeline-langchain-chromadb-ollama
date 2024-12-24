# Use the official Python image as a base
FROM python:3.9

# Set the working directory inside the container
WORKDIR /app

# Copy the Streamlit app and requirements from the current directory
COPY requirements.txt ./requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
COPY streamlit_chatbot.py ./streamlit_chatbot.py
COPY chatbot.py ./chatbot.py



# Expose the Streamlit port
EXPOSE 8501

# Command to run the Streamlit app
CMD ["streamlit", "run", "streamlit_chatbot.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
