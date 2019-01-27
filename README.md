# Required images colection for Rockstat platform

Rockstat platform has own microservice management tool call `director` (on of images in this repo). For interraction whith other services used special framework [Band](/rockstat/band) for python and [Rock-me-ts](/rockstat/rock-me-ts) for TypeScript/JavaScript services running in node.js.

## Rockstat architecture

![Rockstat sheme](https://rockstat.ru/media/rockstat_v3_arch.png?3)

[Read more](https://rockstat.ru/about)

## Components (Band collection)

### Director 

Director is the Chief serivice officer. It manages all other services built on provided frameworks. Runs by setup software.

### SxGeo: Sypes Geo ip to location service

Enriches requests with geo data. 
At first execution service download fresh database from library servers.
To run make http call:

```
 ❯❯❯ http GET http://127.0.0.1:10000/run/sxgeo --timeout 300 -v
HTTP/1.1 200 OK
{
    "name": "sxgeo",
    "short_id": "c9e202d9a535",
    "state": "running"
}
```

In last example used [httpie](/jakubroztocil/httpie) console HTTP client

### MmGeo: MaxMind ip to location service

Enriches requests with geo data. 
At first execution service download fresh database from library servers.
To run make http call:

```
 ❯❯❯ http GET http://127.0.0.1:10000/run/mmgeo --timeout 300 -v
HTTP/1.1 200 OK
{
    "name": "mmgeo",
    "short_id": "363ef60fe68c",
    "state": "running"
}
```

### UaParser: extract usefull data from User-Agent string

Enriches requests with client device type and software versions.
To run make http call:

```
 ❯❯❯ http GET http://127.0.0.1:10000/run/uaparser --timeout 300 -v

HTTP/1.1 200 OK
{
    "name": "mmgeo",
    "short_id": "363ef60fe68c",
    "state": "running"
}
```

### Send Mixpanel: service for batch uploading data to Mixpanel warehouse

By default upload data every second.
To run make http call:

```
 ❯❯❯ http --timeout 300 -v POST http://127.0.0.1:10000/run/send_mixpanel env:='{"MIXPANEL_TOKEN":"31fecdd83ab66bbd2de1fd098a704e00","MIXPANEL_API_SECRET":"06e0d599bced1abe8c56cc162842a44f"'
HTTP/1.1 200 OK
{
    "name": "send_mixpanel",
    "short_id": "d1c2c3153e8d",
    "state": "running"
}
```




_________________________________________________

Closed area / Проход закрыт. Очень сыро
===========

Автоматическая аллокация портов на хостовой машине

## Running (DEV host)

add dev .env file containg

    ...


host.docker.internal is internal host machine alias at docker for mac

running band (by default starting on 10000 port)

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
