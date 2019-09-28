FROM python:3.7-alpine
LABEL maintainer="Dmitry Rodin <madiedinro@gmail.com>"
LABEL band.base-py.version="0.21.1"

RUN apk add --no-cache \
		wget curl \
		unzip gzip \
        nano git \
    make gcc g++ coreutils \
    libffi libffi-dev \
    openssl openssl-dev


ENV HOST=0.0.0.0
ENV PORT=8080
EXPOSE ${PORT}
WORKDIR /usr/src/band
ADD . .
RUN python setup.py develop
RUN echo -e "Installed python packages:\n$(pip freeze)"
