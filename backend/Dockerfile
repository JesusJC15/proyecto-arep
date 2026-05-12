FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY backend/pyproject.toml ./
COPY backend/app ./app
COPY backend/scripts ./scripts
COPY knowledge-base ./knowledge-base
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -e .

RUN mkdir -p /app/runtime && adduser --disabled-password --gecos "" arep && chown -R arep:arep /app
USER arep

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
