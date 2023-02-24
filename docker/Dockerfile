# syntax = docker/dockerfile-upstream:1-labs

FROM golang:alpine AS go-mmproxy
RUN go install github.com/path-network/go-mmproxy@latest

FROM python:3.11-alpine
WORKDIR /app
STOPSIGNAL SIGTERM
EXPOSE 8022
ENV ENV=/app/.profile
RUN --mount=type=cache,target=/var/cache/apk,sharing=locked \
<<-EOF
	set -eo pipefail
	apk add -U gcc g++ libffi libffi-dev musl-dev openssl openssl-dev cargo
	addgroup --gid 1000 xthulu
	adduser --disabled-password --home /app --uid 1000 --ingroup xthulu xthulu
	echo "from xthulu.__main__ import main; main()" > entrypoint.py
	chown -R xthulu:xthulu /app
	pip install -U pip setuptools
EOF
COPY --from=go-mmproxy /go/bin/go-mmproxy /go-mmproxy
COPY --chown=xthulu:xthulu ./pyproject.toml /app/pyproject.toml
COPY --chown=xthulu:xthulu ./requirements /app/requirements
COPY --chown=xthulu:xthulu ./xthulu /app/xthulu
RUN --mount=type=cache,target=/app/.cache/pip,uid=1000,gid=1000,sharing=locked \
	pip install -e .
COPY ./docker/entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
