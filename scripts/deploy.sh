#!/bin/bash
set -e

kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/python-deployment.yaml
kubectl apply -f k8s/react-deployment.yaml
kubectl apply -f k8s/convo-api-lb.yaml
kubectl apply -f k8s/convo-ui-lb.yaml
kubectl apply -f k8s/ingress.yaml
