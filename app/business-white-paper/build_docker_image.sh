docker build -t localhost:32000/business-white-paper:latest .
docker push localhost:32000/business-white-paper:latest
microk8s kubectl rollout restart deployment business-white-paper


