# ===============================
# Dockerfile for 11_nation_cup
# ===============================

# Use a lightweight Python base image
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Copy all project files into the container
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create Streamlit config directory and SSL settings
RUN mkdir -p /root/.streamlit && \
    printf "[server]\n\
address = \"0.0.0.0\"\n\
port = 8501\n\
enableCORS = false\n\
sslCertFile = \"/certs/fullchain.pem\"\n\
sslKeyFile = \"/certs/privkey.pem\"\n" \
    > /root/.streamlit/config.toml

# Copy start up script
COPY start.sh .
RUN chmod +x start.sh

# Streamlit default port
EXPOSE 8501

# call start up script
CMD ["./start.sh"]


