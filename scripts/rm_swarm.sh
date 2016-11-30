#!/bin/bash
docker-machine rm --force $(docker-machine ls --filter "driver=virtualbox" -q)
