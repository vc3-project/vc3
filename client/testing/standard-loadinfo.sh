#!/bin/bash -e

./standard-users.sh "$@"
./standard-projects.sh "$@"
./standard-resources.sh "$@"
./standard-environments.sh "$@"
./standard-clusters.sh "$@"
./standard-allocations.sh "$@"
./standard-headnodes.sh "$@"

