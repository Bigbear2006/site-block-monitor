FROM python:3.11-alpine

RUN apk update && apk add --no-cache postgresql-dev

WORKDIR app

COPY pyproject.toml .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir uv \
    && uv pip install -e . --system --no-cache-dir

COPY . .
RUN chmod +x entrypoint.sh
