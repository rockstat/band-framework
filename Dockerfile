FROM python:3.6
LABEL maintainer="Dmitry Rodin <madiedinro@gmail.com>" band.base.version=0.7.1

RUN apt-get update && apt-get install -y --no-install-recommends \
		wget \
        curl \
		unzip \
		gzip \
        nano \
	&& rm -rf /var/lib/apt/lists/*

ENV HOST=0.0.0.0
ENV PORT=8080
EXPOSE ${PORT}
WORKDIR /usr/src/band
ADD . .
RUN python setup.py develop
RUN pip freeze
