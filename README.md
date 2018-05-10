# About Band

Microservice framework for Rockstat platform. Used for serving custom user services.
Built on top of asyncio, for communication uses JSON-RPC2 over Redis PubSub so that incredible fast!


## Components

#### director

Занимается оркестрацией микросервисов сервисов.
Может запускаться на хосте или в контейнере

#### service (one of many)

содержит бизнес логику и необходимые данные. 
Каждый сервис запускается в своем отдельном контейнере

#### Фичи

Автоматическая аллокация портов на хостовой машине


## Running (DEV host)

add dev .env file containg

    ...


host.docker.internal is internal host machine alias at docker for mac

running band (by default starting on 10000 port)

    ./run_band

run service

    http get http://localhost:10000/run/tg_hellobot

check

    http get http://localhost:10000/list

call

    http get http://localhost:10000/call/tg_hellobot/<method>

`http` is executable of httpie library

## Run in docker

    docker run -d \
        --name=band --hostname=band \
        --restart=unless-stopped \
        --network custom \
        -p 127.0.0.1:10000:8080 \
        -v /Users/user/projects/rockstat/band_images:/images \
        -v /Users/user/projects/rockstat/band:/images/band-base \
        -v /var/run/docker.sock:/var/run/docker.sock \
        -e REDIS_HOST=redis \
        -e BAND_URL=http://band:8080 \
        -e BAND_IMAGES=/images \
        rst/band

## Maintain

Prune unused docker containers

    docker container prune
    
and images

    docker image prune --all

