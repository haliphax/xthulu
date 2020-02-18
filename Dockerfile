FROM python:3.7-alpine
WORKDIR /app
VOLUME /app/data
VOLUME /app/xthulu
VOLUME /app/userland
EXPOSE 8022
ADD ./xthulu /app/xthulu
RUN sh -c "\
	apk add -U gcc libffi libffi-dev musl-dev openssl openssl-dev; \
	pip install -e xthulu; \
	apk del gcc libffi-dev musl-dev openssl-dev"
ENTRYPOINT ["/usr/local/bin/python3", "-m", "xthulu"]
