#!/bin/bash
SERVICES=($(docker service ls -q))

for service in "${SERVICES[@]}"
do
	docker service rm $service
done
