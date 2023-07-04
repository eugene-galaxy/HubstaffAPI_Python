#!/bin/bash

if ! [[ -f "settings.yaml" ]]; then
    echo "ERROR: There should be file settings.yaml with the API credentials defined. See file 'settings_example.yaml'" >&2
    exit 1
fi

docker container remove hubstafftimelog

docker build \
    -t hubstafftimelog \
    .

docker create --name hubstafftimelog hubstafftimelog $*
