microk8s kubectl get all --all-namespaces

microk8s kubectl apply -f im-ai-service.yaml
microk8s kubectl delete pod white-paper-pod
microk8s kubectl describe pod white-paper-pod
microk8s kubectl logs white-paper-pod


docker run -d localhost:32000/api-gateway:registry
docker logs -f localhost:32000/api-gateway
docker exec -it api-gateway /bin/bash
docker rmi $(docker images -f "dangling=true" -q)


curl http://localhost:32000/v2/_catalog
curl http://localhost:32000/v2/business-white-paper/tags/list

curl --max-time 6000 -d '{"query":"안녕"}'  -H "Content-Type: application/json"  -X POST http://127.0.0.1:8080/api/llm-query

curl -i --header    "Accept: application/vnd.docker.distribution.manifest.v2+json" http://localhost:32000/v2/api-gateway/manifests/registry 2>&1 | grep Docker-Content-Digest

curl -X DELETE -v http://localhost:32000/v2/api-gateway/manifests/sha256:11d59aef548beece3bc51169e431c4804ba04a798779093ff022c4ee082341e6

gunicorn -w 4 -b 0.0.0.0:8080 --log-level info --access-logfile '-' --error-logfile '-' 'src.app:create_app()'

microk8s disable registry
microk8s disable hostpath-storage:destroy-storage
microk8s enable registry


docker pull ollama/ollama
docker run -d --name ollama-container ollama/ollama
docker exec ollama-container ollama pull qwen2
docker commit ollama-container localhost:32000/ollama-qwen2:latest
docker push localhost:32000/ollama-qwen2:latest
docker stop ollama-container
docker rm ollama-container


kctl exec -it kafka-796d5f9749-mbnpt -- bash
I have no name!@kafka-796d5f9749-mbnpt:/$ kafka-topics.sh --create --topic query-business --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
I have no name!@kafka-796d5f9749-mbnpt:/$ kafka-topics.sh --list --bootstrap-server localhost:9092

