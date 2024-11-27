FROM python:3.12

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ENV DJANGO_SETTINGS_MODULE "config.settings"
ENV PATH="/scripts:$PATH"

COPY ./scripts /scripts
RUN chmod +x /scripts/*

COPY ./movies_admin .
COPY ./uwsgi/uwsgi.ini uwsgi.ini

COPY ./requirements.txt requirements.txt
RUN  pip install --upgrade pip \
     && pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /vol/web/static

VOLUME /vol/web

CMD [ "entrypoint.sh" ]
