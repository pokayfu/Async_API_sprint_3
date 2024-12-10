# Use a lightweight Python image
FROM python:3.12-slim

# Set working directory inside the container
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH="/app"

# Install dependencies
COPY ./tests/unit/requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r /app/requirements.txt --no-cache-dir

# Copy only necessary parts
COPY ./file_api /app/file_api
COPY ./src/core /app/src/core
COPY ./tests/unit /app/tests/unit

# Run pytest
CMD ["pytest", "/app/tests/unit"]
