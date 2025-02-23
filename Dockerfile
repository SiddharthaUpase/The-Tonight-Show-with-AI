FROM python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

# Install system dependencies
RUN apt-get update \
    && apt-get install -qq -y build-essential xvfb xdg-utils wget unzip ffmpeg libpq-dev vim libmagick++-dev fonts-liberation sox bc gsfonts --no-install-recommends\
    && apt-get clean

# ImageMagick Installation 
RUN mkdir -p /tmp/distr && \
    cd /tmp/distr && \
    wget https://download.imagemagick.org/ImageMagick/download/releases/ImageMagick-7.0.11-2.tar.xz && \
    tar xvf ImageMagick-7.0.11-2.tar.xz && \
    cd ImageMagick-7.0.11-2 && \
    ./configure --enable-shared=yes --disable-static --without-perl && \
    make && \
    make install && \
    ldconfig /usr/local/lib && \
    cd /tmp && \
    rm -rf distr

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /workspace/temp_files

# Set environment variables
ENV PORT=8080
ENV HOST=0.0.0.0

# Command to run the application
CMD ["python", "run.py"] 