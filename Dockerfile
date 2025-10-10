# Use a lightweight Python base image
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Copy everything from your repo into the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Streamlit default port 8501
EXPOSE 8501

# Run your Streamlit app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
