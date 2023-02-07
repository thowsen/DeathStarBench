#!/usr/bin/bash
PARAMS=(
    -D 
    exp 
    -t 20 # time
    -c 50 # connections
    -R 1250 # requests per second 
    -L 
    -s ./wrk2/scripts/social-network/register-user.lua
    http://localhost:8080/wrk2-api/user/register # test to be run
)

../wrk2/wrk ${PARAMS[@]}