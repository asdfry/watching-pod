#!/bin/bash

docker compose down
yes | docker image prune
yes | docker builder prune
yes | docker volume prune
# yes | docker system prune -a
docker system df
