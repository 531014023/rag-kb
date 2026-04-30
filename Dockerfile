FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src/
COPY scripts ./scripts/
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -e .

ENV PYTHONPATH=/app

ENTRYPOINT ["rag-server"]