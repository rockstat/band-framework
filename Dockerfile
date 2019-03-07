FROM python:3.6-alpine3.9
LABEL maintainer="Dmitry Rodin <madiedinro@gmail.com>"
LABEL band.base-py.version="0.17.8"

RUN apk add --no-cache \
		wget curl \
		unzip gzip \
        nano git \
    make gcc g++ coreutils \
    libffi-dev


ENV HOST=0.0.0.0
ENV PORT=8080
EXPOSE ${PORT}
WORKDIR /usr/src/band
ADD . .
RUN pip install -U 'git+https://github.com/madiedinro/simple-clickhouse#egg=simplech'
RUN python setup.py develop
RUN pip freeze
