# Dockerfile-server
FROM python:3.9-slim-buster

SHELL ["/bin/bash", "-c"]

WORKDIR /app
ENV PYTHONPATH=/app

RUN pip install --upgrade pip
# RUN python -m venv venv
# RUN source venv/bin/activate

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    libfreetype6-dev \
    libjpeg62-turbo-dev \
    libpng-dev \
    pkg-config

# Install Python dependencies
COPY ../../requirements.txt ./
RUN pip install -r requirements.txt

# Copy application code
COPY . .
COPY ../../simulation /app/simulation

# Set environment variables for freetype and libpng
ENV LIBRARY_PATH=/lib:/usr/lib
# ENV PYTHONPATH "${PYTHONPATH}:../../simulation"
EXPOSE 80

ENV FLASK_APP='ui/server/App.py'
ENV STATIC_JS='true'

RUN echo ${FLASK_APP}
RUN echo ${PYTHONPATH}
# Run the application
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]