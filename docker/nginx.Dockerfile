FROM xthulu AS html

FROM nginx
COPY --from=html /app/xthulu/web/static/ /usr/share/nginx/html/
