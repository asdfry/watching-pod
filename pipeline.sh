#!/bin/bash

docker build -t asdfry/watching-pod:20230625 .
docker push asdfry/watching-pod:20230625
yes | docker system prune -a
docker system df
