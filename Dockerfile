# Use official Python slim image
FROM python:3.11-slim

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    nano \
    openssh-server \
    wget \
    curl \
    iproute2 \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Create SSH directory and set up basic config
RUN mkdir /var/run/sshd

# Install Python packages
RUN pip install --no-cache-dir \
    chromadb \
    langchain \
    openai \
    Beautifulsoup4 \
    streamlit \
    langchain-chroma \
    langchain-community \
    langchain-huggingface \
    sentence-transformers 

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY entrypoint.sh /entrypoint.sh

# Set working directory
WORKDIR /app

# Optional: expose SSH port
EXPOSE 22 6000 6001 6002 6003

# Optional: default command
#CMD ["bash"]

#CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]

ENTRYPOINT ["/entrypoint.sh"]






