# Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy your requirements.txt
COPY requirements.txt .

# Install system dependencies needed for asyncpg
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        g++ \
        libpq-dev \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your app
COPY . .

# Expose port 8080 (Railway uses this by default)
EXPOSE 8080

# Run the Streamlit app
CMD ["streamlit", "run", "app.py", \
     "--server.port=8080", \
     "--server.address=0.0.0.0", \
     "--browser.gatherUsageStats=false"]