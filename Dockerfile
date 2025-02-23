FROM python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

# Install system dependencies including ImageMagick 6
RUN apt-get update \
    && apt-get install -qq -y build-essential xvfb xdg-utils wget unzip ffmpeg libpq-dev vim \
    imagemagick libmagickwand-dev fonts-liberation sox bc gsfonts --no-install-recommends \
    && apt-get clean

# Create and configure ImageMagick policy file
RUN mv /etc/ImageMagick-6/policy.xml /etc/ImageMagick-6/policy.xml.backup && \
    echo '<?xml version="1.0" encoding="UTF-8"?>\
    <policymap>\
    <policy domain="resource" name="memory" value="256MiB"/>\
    <policy domain="resource" name="map" value="512MiB"/>\
    <policy domain="resource" name="width" value="16KP"/>\
    <policy domain="resource" name="height" value="16KP"/>\
    <policy domain="resource" name="area" value="128MP"/>\
    <policy domain="resource" name="disk" value="1GiB"/>\
    <policy domain="delegate" rights="read|write" pattern="URL"/>\
    <policy domain="delegate" rights="read|write" pattern="HTTPS"/>\
    <policy domain="delegate" rights="read|write" pattern="HTTP"/>\
    <policy domain="path" rights="read|write" pattern="@*"/>\
    <policy domain="path" rights="read|write" pattern="*"/>\
    <policy domain="cache" name="shared-secret" value="passphrase" stealth="true"/>\
    </policymap>' > /etc/ImageMagick-6/policy.xml

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /workspace/temp_files

# Set environment variables
ENV PORT=8080
ENV HOST=0.0.0.0

# Command to run the application
CMD ["python", "run.py"] 