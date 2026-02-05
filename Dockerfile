
# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.10-slim

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

# Install production dependencies.
RUN pip install --no-cache-dir -r requirements.txt

# Install Tesseract OCR
RUN apt-get update && apt-get install -y tesseract-ocr && apt-get clean

# Run the web service on container startup.
# We configure the port to default to 8080, but Cloud Run injects the PORT env var.
CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}
