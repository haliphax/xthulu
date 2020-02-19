FROM python:3.7-alpine
WORKDIR /app
VOLUME /app/data
VOLUME /app/xthulu
VOLUME /app/userland
EXPOSE 8022
ADD ./setup.py /app/
ADD ./requirements.txt /app/
ADD ./xthulu /app/xthulu
RUN sh -c "\
	apk add -U gcc libffi libffi-dev musl-dev openssl openssl-dev; \
	pip install -e .; \
	apk del gcc libffi-dev musl-dev openssl-dev; \
	printf 'from xthulu.__main__ import main; main()' > /app/entrypoint.py; \
	printf '#!/bin/ash\n/usr/local/bin/python3 /app/entrypoint.py \$@' \
		> /usr/local/bin/xt; \
	chmod a+x /usr/local/bin/xt; \
	addgroup --gid 1000 xthulu \
		&& adduser --disabled-password --home /app --uid 1000 \
			--ingroup xthulu xthulu \
		&& chown -R xthulu:xthulu /app"
USER xthulu
ENTRYPOINT ["/usr/local/bin/xt"]
