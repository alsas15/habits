FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml poetry.lock* /app/
RUN apt-get update && apt-get install -y build-essential libpq-dev
RUN pip install --upgrade pip
RUN pip install poetry
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi
COPY app /app/app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
