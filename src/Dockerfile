FROM python:3.12

ENV PYTHONUNBUFFERED=1

WORKDIR /src

RUN pip install --upgrade pip "poetry==2.1.3"
ENV POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR='/var/cache/pypoetry'

COPY ./pyproject.toml /src/
COPY ./poetry.lock /src/

RUN poetry install --no-root

COPY ./src /src
