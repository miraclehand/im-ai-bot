docker pull bitnami/zookeeper:latest
docker image tag bitnami/zookeeper:latest localhost:32000/bitnami/zookeeper:latest
docker push localhost:32000/bitnami/zookeeper:latest
microk8s kubectl rollout restart deployment zookeeper


docker pull bitnami/kafka:latest
docker image tag bitnami/kafka:latest localhost:32000/bitnami/kafka:latest
docker push localhost:32000/bitnami/kafka:latest
microk8s kubectl rollout restart deployment kafka
