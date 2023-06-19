#!/bin/bash

docker build -t asdfry/watching-pod:20230619 .
docker push asdfry/watching-pod:20230619
yes | docker system prune -a
docker system df
