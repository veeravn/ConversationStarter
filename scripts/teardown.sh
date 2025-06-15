#!/bin/bash
set -e

kubectl delete -f k8s/ingress.yaml
kubectl delete -f k8s/convo-ui-lb.yaml
kubectl delete -f k8s/convo-api-lb.yaml
kubectl delete -f k8s/react-deployment.yaml
kubectl delete -f k8s/python-deployment.yaml
kubectl delete -f k8s/configmap.yaml
