FROM python:3.13.3-slim-bookworm AS python-base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.8.2 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv" \
    PROJECT_PATH="/server"
ENV PATH="$VENV_PATH/bin:$PATH"

FROM python-base AS builder-base

WORKDIR $PYSETUP_PATH
COPY poetry.lock pyproject.toml ./

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    build-essential \
    curl \
    git \
    libpq-dev \
    libseccomp2 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


RUN --mount=type=cache,target=/root/.cache/pip \
    pip install "poetry==$POETRY_VERSION";

RUN --mount=type=cache,target=/root/.cache/poetry \
    poetry install --only main --no-root --no-interaction


FROM python-base AS production

WORKDIR $PROJECT_PATH
COPY --from=builder-base $VENV_PATH $VENV_PATH

RUN adduser --disabled-password --gecos '' appuser
COPY --chown=appuser:appuser app app
USER appuser
EXPOSE 8000

ENTRYPOINT ["uvicorn"]
CMD ["app.main:app", "--host", "0.0.0.0", "--port", "8000", "--lifespan", "on"]


FROM builder-base AS development

WORKDIR $PYSETUP_PATH

RUN poetry install --no-root --no-interaction

WORKDIR $PROJECT_PATH
COPY app app
COPY tests tests

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--lifespan", "on"]


FROM builder-base AS scanapi-test

WORKDIR $PYSETUP_PATH

RUN poetry install --no-root --no-interaction

WORKDIR $PROJECT_PATH

COPY poetry.lock pyproject.toml ./

COPY app app
COPY scanapi scanapi
COPY scanapi.conf ./

CMD ["poetry", "run", "scanapi", "run"]
