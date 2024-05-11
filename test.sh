#!/usr/bin/env bash

set +x

if [ -z ${KUBECONFIG} ]; then
  echo "Not connected to kube"
  exit 1
fi

docker build . -t $(basename $(git rev-parse --show-toplevel)):test

docker run -ti --rm --privileged \
  -v ${KUBECONFIG}:/kubeconfig.yaml \
  -e KUBECONFIG=/kubeconfig.yaml \
  -e LOG_LEVEL=INFO \
  $(basename $(git rev-parse --show-toplevel)):test
