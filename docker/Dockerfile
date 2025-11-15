# syntax = docker/dockerfile-upstream:1-labs

FROM python:3.12-alpine
WORKDIR /app
STOPSIGNAL SIGTERM
ENV ENV=/app/.profile
RUN \
	--mount=type=cache,target=/var/cache/apk,sharing=locked \
	--mount=type=cache,target=/app/.cache/pip,uid=1000,gid=1000,sharing=locked \
	<<-EOF
	apk add -U cargo gcc g++ libffi-dev musl-dev openssl openssl-dev
	addgroup --gid 1000 xthulu
	adduser --disabled-password --home /app --uid 1000 --ingroup xthulu xthulu
	chown -R xthulu:xthulu /app
	pip install -U 'pip<25.3' setuptools
EOF

COPY --chown=xthulu:xthulu ./pyproject.toml /app/pyproject.toml
COPY --chown=xthulu:xthulu ./requirements /app/requirements
COPY --chown=xthulu:xthulu ./xthulu /app/xthulu
USER xthulu
RUN --mount=type=cache,target=/app/.cache/pip,uid=1000,gid=1000,sharing=locked \
	pip install --no-warn-script-location -Ue .
ENTRYPOINT ["/usr/local/bin/python3", "-m", "xthulu"]
