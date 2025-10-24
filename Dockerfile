# python:3.10-slim-bookworm is modern, small, and secure
FROM python:3.10-slim-bookworm

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


COPY main.py .
COPY src/ /app/src/


CMD ["python", "main.py"]

