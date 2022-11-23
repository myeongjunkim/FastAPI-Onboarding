FROM --platform=linux/amd64 python:3.10.3-slim 
ENV PYTHONHASHSEED=random \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false \
    WORKDIR=/code 
ENV PATH="$POETRY_HOME/bin:$PATH" 
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    curl \
    build-essential
ENV POETRY_VERSION=1.2.0
RUN curl -sSL https://install.python-poetry.org | python3 -
RUN cp /usr/share/zoneinfo/Asia/Seoul /etc/localtime && \
    echo "Asia/Seoul" > /etc/timezone

WORKDIR $WORKDIR

COPY ./poetry.lock ./pyproject.toml ./
RUN poetry install
COPY . .

EXPOSE 8000

CMD ["scripts/run_server.sh"]
