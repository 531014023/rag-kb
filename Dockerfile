FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src/
COPY scripts ./scripts/
RUN pip install -e .

ENV PYTHONPATH=/app

ENTRYPOINT ["rag-server"]