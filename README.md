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

    ... plz ask me to take actual version


host.docker.internal is internal host machine alias in the docker for mac


running band (by default starting on 10000 port)

    ./run_band

run service

    http get http://localhost:10000/run/tg_hellobot

check

    http get http://localhost:10000/list

call

    http get http://localhost:10000/call/tg_hellobot/<method>

`http` is executable of httpie library

### Maintain

Prune unused docker containers

    docker container prune
    
and images

    docker image prune --all

