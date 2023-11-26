#!/usr/bin/env bash

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" || exit; pwd)

CODE="import osom_api; print(osom_api.__version__)"
if ! VERSION=$("$ROOT_DIR/python" -c "$CODE"); then
    echo "Python code execution failed ($?)" 1>&2
    exit 1
fi

NAME="ghcr.io/osom8979/osom-api"
TAG="$NAME:$VERSION"
LATEST="$NAME:latest"

if ! docker build -f "$ROOT_DIR/Dockerfile" --tag "$TAG" "$ROOT_DIR"; then
    echo "Dockerfile build failed ($?)" 1>&2
    exit 1
fi

docker tag "$TAG" "$LATEST"
