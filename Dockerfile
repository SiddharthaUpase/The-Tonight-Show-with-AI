FROM python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

# Install system dependencies including ImageMagick 6
RUN apt-get update \
    && apt-get install -qq -y build-essential xvfb xdg-utils wget unzip ffmpeg libpq-dev vim \
    imagemagick libmagickwand-dev fonts-liberation sox bc gsfonts --no-install-recommends \
    && apt-get clean

# Copy and configure ImageMagick policy file
COPY imagemagick-policy.xml /etc/ImageMagick-6/policy.xml
RUN chmod 644 /etc/ImageMagick-6/policy.xml

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /workspace/temp_files

# Set environment variables
ENV PORT=8080
ENV HOST=0.0.0.0

# Command to run the application
CMD ["python", "run.py"] 