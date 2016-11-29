#!/bin/bash
SERVICES=($(docker service ls -q))

for service in "${SERVICES[@]}"
do
	docker service scale $service=$1
done
