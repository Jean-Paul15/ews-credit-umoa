FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml ./
COPY src ./src
RUN pip install --no-cache-dir ".[api]"

ENV EWS_DATA_SYNTHETIC=/data/synthetic
EXPOSE 8000

CMD ["uvicorn", "ews_credit.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
