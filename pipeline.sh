#!/bin/bash

docker build -t asdfry/watching-pod:20230616 .
docker push asdfry/watching-pod:20230616
yes | docker system prune -a
docker system df
