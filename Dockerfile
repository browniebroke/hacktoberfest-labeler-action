FROM python:3.14-slim

# Create app directory
WORKDIR /app

# Copy file containing dependencies
COPY . .

# Install dependencies using PEP 517 Build Backend
RUN pip install .

# Run the app
CMD ["python", "/app/src/app.py"]
