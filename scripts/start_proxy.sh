#!/bin/bash
# NGINX Proxy
docker service create \
	--network swarm_net \
	--name proxy \
	--replicas 1 \
	--publish 80:80 \
	sthordall/traderproxy:latest

