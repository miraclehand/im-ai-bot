docker build -t localhost:32000/api-gateway:latest .
docker push localhost:32000/api-gateway:latest
microk8s kubectl rollout restart deployment api-gateway


