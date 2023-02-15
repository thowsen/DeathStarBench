#!/usr/bin/bash
PARAMS=(
    -D 
    exp 
    -t 4 # threads 
    -d 1m
    -c 4 # connections
    -R 200 # requests per second 
    -L 
    -s ./wrk2/scripts/social-network/register-user.lua
    http://localhost:8080/wrk2-api/user/register # test to be run
)

../wrk2/wrk ${PARAMS[@]}