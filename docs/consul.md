https://gliderlabs.com/registrator/latest/


## Dev server

    docker run --name=socat -d \
      -v /var/run/docker.sock:/var/run/docker.sock \
      -p 192.168.65.1:1234:1234 bobrik/socat \
      TCP-LISTEN:1234,fork UNIX-CONNECT:/var/run/docker.sock



    consul agent -ui -dev -advertise 127.0.0.1
    -bootstrap-expect=3 
    -advertise 127.0.0.1
      -bind=192.168.1.42
      --net=host 
      
    docker rm -f consul;
    docker run \
      -d --name=consul \
      --group-add $(stat -f '%g' /var/run/docker.sock) \
      -p 8300-8302:8300-8302 -p 8500:8500 -p 8600:8600 \
      -e DOCKER_HOST=tcp://192.168.65.2:1234 \
      -e CONSUL_LOCAL_CONFIG='{
        "datacenter":"us_west",
        "server":true,
        "enable_debug":true,
        "enable_script_checks":true
        }' \
      consul agent -server -ui -dev  -client=0.0.0.0
    


