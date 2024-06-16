#!/usr/bin/env bash

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" || exit; pwd)
ENV_NAME="osom-api-env"
ENV_PATH="$ROOT_DIR/../../.env.local"
NAMESPACE=osom-api

if kubectl get secret "$ENV_NAME" -n "$NAMESPACE" &> /dev/null; then
    echo "The '$ENV_NAME' secret already exists" 1>&2
    exit 1
fi

if [[ ! -f "$ENV_PATH" ]]; then
    echo "Not found '$ENV_PATH' env file" 1>&2
    exit 1
fi

kubectl create secret generic "$ENV_NAME" \
    --namespace "$NAMESPACE" \
    --from-env-file "$ENV_PATH"
