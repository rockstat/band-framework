FROM python:3.6
LABEL maintainer="Dmitry Rodin <madiedinro@gmail.com>"

RUN apt-get update && apt-get install -y --no-install-recommends \
		wget \
        curl \
		unzip \
		gzip \
        nano \
	&& rm -rf /var/lib/apt/lists/*


WORKDIR /usr/src/band

ENV HOST=0.0.0.0
ENV PORT=8080

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE ${PORT}
COPY . .
RUN python setup.py develop
