#!/usr/bin/env bash

NAMESPACE=osom-api

if kubectl get namespace "$NAMESPACE" &> /dev/null; then
    echo "The '$NAMESPACE' namespace already exists" 1>&2
    exit 1
fi

kubectl create namespace "$NAMESPACE"
