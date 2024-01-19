FROM python:3.11-alpine

ADD jonochen.net/requirements.txt /app/requirements.txt

RUN set -ex \
    && python -m venv /env \
    && apk add --no-cache --virtual .build-deps build-base \
    && /env/bin/pip install --upgrade pip \
    && /env/bin/pip install --no-cache-dir -r /app/requirements.txt \
    && runDeps="$(scanelf --needed --nobanner --recursive /env \
        | awk '{ gsub(/,/, "\nso:", $2); print "so:" $2 }' \
        | sort -u \
        | xargs -r apk info --installed \
        | sort -u)" \
    && apk add --virtual rundeps $runDeps \
    && apk del .build-deps

ADD jonochen.net /app
WORKDIR /app

COPY ./startup.sh /

ENV VIRTUAL_ENV /env
ENV PATH /env/bin:$PATH

EXPOSE 8000

ENTRYPOINT ["sh", "/startup.sh"]