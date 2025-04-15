FROM python:3.11-slim

WORKDIR /app

# Install dependencies first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install the package in development mode
COPY . .
RUN pip install -e .

# Use verbose exception logging in Python
ENV PYTHONFAULTHANDLER=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONASYNCIODEBUG=1

# App-specific environment settings will be loaded from .env through docker-compose

# Run the server
EXPOSE 8000
CMD ["uvicorn", "memory_agent.web:app", "--host", "0.0.0.0", "--port", "8000"]