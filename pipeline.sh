#!/bin/bash

docker build -t asdfry/watching-pod:20230613 .
docker push asdfry/watching-pod:20230613
yes | docker system prune -a
docker system df
