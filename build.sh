#!/usr/bin/env bash

DOCKER_HUB_REPO=${1:-nzolot}

VERSIONS="1.27 1.28 1.29"
IMAGE="${DOCKER_HUB_REPO}/$(basename $(git rev-parse --show-toplevel))"

BUILD_MINOR=$(curl -s https://registry.hub.docker.com/v2/repositories/${IMAGE}/tags?page_size=1000 | jq -r ".results[].name" | awk -F'.' {'print $3'} | sort -n | tail -n 1)
if [ "x${BUILD_MINOR}" == "x" ]; then
  BUILD_MINOR=0
fi
VERSION_MINOR=$((BUILD_MINOR+1))

set -e
for VERSION in ${VERSIONS}; do
  echo "Building VERSION ${VERSION}.${VERSION_MINOR}"
  docker build --build-arg="VERSION=${VERSION}" -t ${IMAGE}:${VERSION}.${VERSION_MINOR} -t ${IMAGE}:${VERSION}.x .
done

for VERSION in ${VERSIONS}; do
  echo "Pushing VERSION ${VERSION}.${VERSION_MINOR}"
  docker push ${IMAGE}:${VERSION}.${VERSION_MINOR}
  docker push ${IMAGE}:${VERSION}.x
done
