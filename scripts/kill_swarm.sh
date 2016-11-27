#!/bin/bash
docker-machine kill $(docker-machine ls --filter "driver=virtualbox" -q)
docker-machine rm --force $(docker-machine ls --filter "driver=virtualbox" -q)
