FROM python:3.11-slim

# Create app directory
WORKDIR /app

# Copy file containing dependencies
COPY pyproject.toml ./

# Install dependencies using PEP 517 Build Backend
RUN pip install .

# Copy source code
COPY src /app

# Run the app
ENTRYPOINT ["python", "/app/app.py"]
