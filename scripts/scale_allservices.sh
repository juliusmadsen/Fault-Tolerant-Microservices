#!/bin/bash
docker service scale account=$1 stocks=$1 trader=$1
