FROM python:3.6
LABEL maintainer="Dmitry Rodin <madiedinro@gmail.com>"

RUN apt-get update && apt-get install -y --no-install-recommends \
		wget \
        curl \
		unzip \
		gzip \
        nano \
	&& rm -rf /var/lib/apt/lists/*

ENV HOST=0.0.0.0
ENV PORT=8080
#cachebust
ARG RELEASE=master

WORKDIR /usr/src/band
ADD requirements.txt .
RUN echo "Release: ${RELEASE}" && pip install --no-cache-dir -r requirements.txt

EXPOSE ${PORT}
ADD . .
RUN python setup.py develop
