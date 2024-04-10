# syntax = docker/dockerfile-upstream:1-labs
# asdf

FROM python:3.11-alpine
WORKDIR /app
STOPSIGNAL SIGTERM
ENV ENV=/app/.profile
RUN \
	--mount=type=cache,target=/var/cache/apk,sharing=locked \
	--mount=type=cache,target=/app/.cache/pip,uid=1000,gid=1000,sharing=locked \
	<<-EOF
	apk add -U \
		cargo=1.71.1-r0 \
		gcc=12.2.1_git20220924-r10 \
		g++=12.2.1_git20220924-r10 \
		libffi-dev=3.4.4-r2 \
		musl-dev=1.2.4-r2 \
		openssl=3.1.3-r0 \
		openssl-dev=3.1.3-r0
	addgroup --gid 1000 xthulu
	adduser --disabled-password --home /app --uid 1000 --ingroup xthulu xthulu
	chown -R xthulu:xthulu /app
	pip install -U pip==24.0 setuptools==69.2.0
EOF

COPY --chown=xthulu:xthulu ./pyproject.toml /app/pyproject.toml
COPY --chown=xthulu:xthulu ./requirements /app/requirements
COPY --chown=xthulu:xthulu ./xthulu /app/xthulu
USER xthulu
RUN --mount=type=cache,target=/app/.cache/pip,uid=1000,gid=1000,sharing=locked \
	pip install --no-warn-script-location -Ue ".[hiredis]"
ENTRYPOINT ["/usr/local/bin/python3", "-m", "xthulu"]
