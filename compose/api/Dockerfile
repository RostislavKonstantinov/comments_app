FROM python:3.6
ENTRYPOINT ["dumb-init", "--"]


ENV PYTHONUNBUFFERED 1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        jq \
        dumb-init \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade \
        pip \
        setuptools

COPY compose/api/deps /deps
COPY compose/api/scripts /usr/local/bin
COPY compose/api/envs /envs
COPY . /code
COPY .git .git

RUN pip install -r /deps/requirements.txt

WORKDIR /code

EXPOSE 8000
CMD ["api.sh"]