#!/bin/bash
NODES=($(docker node ls -q))

for node in "${NODES[@]}"
do
	docker node ps $node
	echo
done
