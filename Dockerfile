FROM python:3.11-slim

WORKDIR /app

# System deps (optional, slim image hygiene)
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*
    
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

# Expose and run
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Excel file: prefer volume mount at runtime
# e.g., docker run -v $(pwd)/data/constituent.xlsx:/app/app/data/constituent.xlsx ...
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
