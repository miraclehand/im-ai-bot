docker pull ollama/ollama && sleep 5
docker run -d --name ollama-container ollama/ollama && sleep 5
docker exec ollama-container ollama pull phi3.5
docker commit ollama-container localhost:32000/ollama-phi3.5:latest
docker push localhost:32000/ollama-phi3.5:latest
docker stop ollama-container
docker rm ollama-container
microk8s kubectl rollout restart deployment ollama-phi3.5


