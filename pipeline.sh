#!/bin/bash

docker build -t asdfry/watching-pod:20230629 .
docker push asdfry/watching-pod:20230629
yes | docker system prune -a
docker system df
