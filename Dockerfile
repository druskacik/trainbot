FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Install system dependencies (Uncomment if using PostgreSQL, etc.)
RUN apt-get update && \
    apt-get install -y libpq-dev gcc && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy the pyproject.toml first for caching layer
COPY pyproject.toml ./

# Install dependencies using standard pip
# --no-cache-dir keeps the image size small
RUN pip install --no-cache-dir .

# Copy the rest of the application
COPY . .

# Expose the port Django runs on
EXPOSE 80

CMD ["python", "manage.py", "runserver", "0.0.0.0:80"]