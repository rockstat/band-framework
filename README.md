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

    IMG_PATH=/Users/user/projects/rockstat/band_images
    docker run -d \
        --name=band --hostname=band \
        --restart=unless-stopped \
        --network custom \
        -p 127.0.0.1:10000:8080 \
        -v $IMG_PATH/band_collection:/images/band_collection:ro \
        -v $IMG_PATH/band:/images/band_base:ro \
        -v /var/run/docker.sock:/var/run/docker.sock \
        -e REDIS_HOST=redis \
        -e BAND_URL=http://band:8080 \
        -e BAND_IMAGES=/images \
        rst/band

## Deps

in pypi old version of `jsonrpcclient` and should be installed from git `pip install -U git+https://github.com/bcb/jsonrpcclient.git@master#egg=jsonrpcclient`

## Maintain

Prune unused docker containers

    docker container prune
    
and images

    docker image prune --all

