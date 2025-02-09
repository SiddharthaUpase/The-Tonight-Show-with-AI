FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    imagemagick \
    libmagick++-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Configure ImageMagick policy
RUN sed -i 's/rights="none" pattern="PDF"/rights="read|write" pattern="PDF"/' /etc/ImageMagick-6/policy.xml

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /workspace/temp_files

# Set environment variables
ENV PORT=8080
ENV HOST=0.0.0.0

# Command to run the application
CMD ["python", "run.py"] 