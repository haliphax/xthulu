# syntax = docker/dockerfile-upstream:1-labs

FROM python:3.11-alpine
WORKDIR /app
STOPSIGNAL SIGTERM
VOLUME ["/app/data", "/app/xthulu", "/app/userland"]
EXPOSE 8022
ENV ENV=/app/.profile
COPY ./requirements /app/requirements
COPY ./pyproject.toml /app/pyproject.toml
COPY ./xthulu /app/xthulu
RUN --mount=type=cache,target=/var/cache/apk \
<<-EOF
	set -eo pipefail
	apk add -U gcc g++ libffi libffi-dev musl-dev openssl openssl-dev cargo
	addgroup --gid 1000 xthulu
	adduser --disabled-password --home /app --uid 1000 --ingroup xthulu xthulu
	chown -R xthulu:xthulu /app
EOF
USER xthulu
RUN --mount=type=cache,target=/app/.cache/pip \
<<-EOF
	pip install -U pip setuptools
	pip install -e .
EOF
ENTRYPOINT ["/usr/local/bin/python3", "-m", "xthulu"]
