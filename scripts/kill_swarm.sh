#!/bin/bash
docker-machine kill $(docker-machine ls --filter "driver=virtualbox" -q)
