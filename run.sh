#!/bin/bash

kubectl apply -f "APIGetaway/config-map.yaml"
kubectl apply -f "APIGetaway/configmap-reader-role.yaml"
kubectl apply -f "APIGetaway/configmap-reader-rolebinding.yaml"
kubectl apply -f "APIGetaway/service.yaml"
kubectl apply -f "db_manager_service/pv_and_pvc.yaml"
kubectl apply -f "db_manager_service/service.yaml"

# Build the DB module Docker image
IMAGE_NAME="stikeyrs/scraper:db-api"
DOCKERFILE_PATH="db_manager_service/Dockerfile"
docker build -t $IMAGE_NAME -f $DOCKERFILE_PATH .

# Build the API Getaway Drivers module Docker image
IMAGE_NAME="stikeyrs/scraper:api_getaway_chrome_driver"
DOCKERFILE_PATH="APIGetaway/Dockerfile"
docker build -t $IMAGE_NAME -f $DOCKERFILE_PATH .

# Build the Driver module Docker image
IMAGE_NAME="stikeyrs/scraper:driver-container"
DOCKERFILE_PATH="chrome_driver_menager/Dockerfile"
docker build -t $IMAGE_NAME -f $DOCKERFILE_PATH .

kubectl apply -f "APIGetaway/deployment.yaml"
kubectl apply -f "chrome_driver_menager/deployment.yaml"
kubectl apply -f "db_manager_service/deployment.yaml"

# Build the Parser module Docker image
IMAGE_NAME="stikeyrs/scraper:parser"
DOCKERFILE_PATH="parsers/parser/Dockerfile"
docker build -t $IMAGE_NAME -f $DOCKERFILE_PATH .

deployment_status=$(kubectl rollout status deployment "api-getaway-deployment ")
echo 'APIGetaway Deployment is running'
deployment_status=$(kubectl rollout status deployment "chrome-driver-deployment")
echo 'Chrome Drive Deployment is running'
deployment_status=$(kubectl rollout status deployment "db-api-deployment")
echo 'DB Deployment is running'

export PGPASSWORD='123456i'
psql -h localhost -p 30007 -U postgres -d realestatedb -a -f create_db.sql

kubectl apply -f "parsers/deployment.yaml"
deployment_status=$(kubectl rollout status deployment "parser")
echo 'Parser Deployment is running'


