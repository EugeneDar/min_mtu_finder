#!/bin/bash

if [ -z "$1" ]; then
  echo "Usage: $0 <destination_address>"
  exit 1
fi

DESTINATION_ADDRESS=$1

echo "Building Docker image..."
docker build -t mtu-finder .

if [ $? -ne 0 ]; then
  echo "Failed to build Docker image."
  exit 1
fi

#docker network rm mynetwork
docker network create --driver bridge --opt com.docker.network.driver.mtu=1500 mynetwork

echo "Running Docker container to find MTU for $DESTINATION_ADDRESS ..."
docker run --net=mynetwork --rm mtu-finder "$DESTINATION_ADDRESS"
#docker run --rm mtu-finder "$DESTINATION_ADDRESS"

if [ $? -ne 0 ]; then
  echo "Failed to run Docker container."
  exit 1
fi

echo "MTU discovery completed."
