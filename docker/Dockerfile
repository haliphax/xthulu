# syntax = docker/dockerfile-upstream:1-labs

FROM python:3.11-alpine
WORKDIR /app
STOPSIGNAL SIGTERM
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
COPY --chown=xthulu:xthulu ./pyproject.toml /app/pyproject.toml
COPY --chown=xthulu:xthulu ./requirements /app/requirements
COPY --chown=xthulu:xthulu ./xthulu /app/xthulu
USER xthulu
RUN --mount=type=cache,target=/app/.cache/pip,uid=1000,gid=1000,sharing=locked \
	pip install -e .[hiredis]
ENTRYPOINT ["/usr/local/bin/python3", "/app/entrypoint.py"]
