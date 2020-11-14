FROM python:3.8-slim

# Create app directory
WORKDIR /app

# Install poetry
RUN pip install poetry

# Copy config files
COPY pyproject.toml poetry.lock ./

# Install only main dependencies
RUN poetry install --no-root --no-dev

# Copies source code
COPY src /app

# Run the app
ENTRYPOINT ["poetry", "run", "python", "/app/app.py"]
