microk8s kubectl apply -f api-gateway/deployment.yaml
microk8s kubectl apply -f api-gateway/service.yaml
microk8s kubectl apply -f business-white-paper/deployment.yaml
microk8s kubectl apply -f business-white-paper/service.yaml
microk8s kubectl apply -f ollama/deployment.yaml
microk8s kubectl apply -f ollama/service.yaml

microk8s kubectl rollout restart deployment api-gateway
microk8s kubectl rollout restart deployment business-white-paper
microk8s kubectl rollout restart deployment ollama-tinyllama
microk8s kubectl rollout restart deployment zookeeper
microk8s kubectl rollout restart deployment kafka
