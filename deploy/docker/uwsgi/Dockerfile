FROM docker-registry-test.di.unistra.fr/docker_django_base:3.6

EXPOSE 8080
WORKDIR /app 

COPY . /app
# TODO: rm deploy ?
COPY deploy/docker/uwsgi/uwsgi.ini /etc/uwsgi/uwsgi.ini
COPY deploy/docker/uwsgi/prestart.sh /prestart.sh

RUN chmod +x /prestart.sh

# DEBUG
RUN echo "Creation date: $(date)"

RUN set -ex \
    pip install --upgrade pip \
    && cd /app \
    && pip install --trusted-host pypi.python.org -r requirements/dev.txt \
    && apk del build-dependencies \
    && apk add gettext-dev \
    && pip install uwsgi

ENTRYPOINT ["sh", "/prestart.sh"]

CMD ["uwsgi", "--ini", "/etc/uwsgi/uwsgi.ini", "--protocol", "http"]
