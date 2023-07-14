#!/usr/bin/env bash

docker run \
    -d \
    --restart unless-stopped \
    -e TZ=Asia/Seoul \
    -p 6379:6379 \
    redis:7 \
    redis-server
