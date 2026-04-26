# Use a slim Python image for a smaller footprint
FROM python:3.11-slim

# Set environment variables to prevent Python from writing .pyc and buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies if needed (e.g., for some network tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY core/ ./core/
COPY data/ ./data/
COPY main.py .

# Create directory for reports (will be mapped via volume)
RUN mkdir -p /app/reports /app/data /app/logs

# Default command: basic scan.
# Users can override this to run with --advanced or --daemon
ENTRYPOINT ["python", "main.py"]
CMD ["--help"]