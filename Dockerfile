FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy dependencies list & install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY Data/ ./Data/
COPY src/ ./src/
COPY Api/ ./Api/
COPY static/ ./static/

# Expose port
EXPOSE 8000

# Start FastAPI Uvicorn server
CMD ["uvicorn", "Api.app:app", "--host", "0.0.0.0", "--port", "8000"]
