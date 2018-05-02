# About Band

Microservice framework for Rockstat platform. Used for serving custom user services.
Built on top of asyncio, for communication uses JSON-RPC2 over Redis PubSub so that incredible fast!


## Components

#### band director

Занимается оркестрацией микросервисов сервисов.
Может запускаться на хосте или в контейнере

#### band serivce (set)

содержит бизнес логику и необходимые данные. 
Каждый сервис запускается в своем отдельном контейнере

## Running (DEV host)

add dev .env file containg

    TZ=UTC
    REDIS_DSN=redis://host.docker.internal:6379
    CLICKHOUSE_DSN=http://localhost


    BAND_IMAGES_PATH=.

    HOST_BIND_ADDR=127.0.0.1

    CONTAINER_HTTP_PORT=8080

    BAND_HTTP_PORT=10000
    KERNEL_HTTP_PORT=10001
    KERNEL_WS_PORT=10002
    KERNEL_WSS_PORT=10003

    STATSD_HOST=127.0.0.1

    # host.docker.internal // mac os
    BAND_URL=http://host.docker.internal:10000

    LOG_LEVEL=debug


host.docker.internal is internal host machine alias in the docker for mac


running band (by default starting on 10000 port)

    ./run_band

service 

    http get http://localhost:10000/run/tg_hellobot

`http` is executable of httpie library

### Maintain

Prune unused docker containers

    docker container prune
    
and images

    docker image prune --all

