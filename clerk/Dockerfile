FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY clerk/ ./clerk/
COPY verify/ ./verify/
COPY switch/ ./switch/
COPY warrant.py .

EXPOSE 8000

CMD ["python", "warrant.py", "serve", "--host", "0.0.0.0", "--port", "8000"]
