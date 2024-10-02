This is an AI bot service.
It has been built for Ubuntu on a Raspberry Pi5.

* install microk8s
    1. add options
        $ sudo vi /boot/firmware/cmdline.txt
        - add the following options
            cgroup_enable=memory cgroup_memory=1
    2. $ sudo reboot
    3. $ sudo snap install microk8s --classic
    4. $ microk8s.start
    5. $ sudo reboot
    6. $ sudo usermod -a -G microk8s $USER
    7. $ sudo chown -f -R $USER ~/.kube
    8. $ microk8s enable dns
    9. $ microk8s enable registry
   10. $ microk8s enable storage
   11. test
        ref. https://www.skyer9.pe.kr/wordpress/?p=7173

* install docker
    1. ref. https://docs.docker.com/engine/install/ubuntu/
    2. $ sudo groupadd docker
    3. $ sudo usermod -aG docker $USER
    4. $ sudo vi /etc/docker/daemon.json
        {
          "insecure-registries" : ["localhost:32000"]
        }
    5. $ sudo systemctl restart docker

* install helm
    1. $ sudo snap install helm --classic
    2. $ sudo microk8s config > ~/.kube/config
    3. $ chmod 600 ~/.kube/config
    4. $ helm repo add bitnami https://charts.bitnami.com/bitnami
    5. $ helm repo update

* install kafka
    1. $ helm install kafka bitnami/kafka  -f values.yaml
       $ helm install kafka --set volumePermissions.enabled=true,replicaCount=3,listeners.client.protocol=PLAINTEXT oci://registry-1.docker.io/bitnamicharts/kafka -f values.yaml

        === values.yaml
        topics:
          - name: query-business
            partitions: 3
            replicationFactor: 1
          - name: query-business-response
            partitions: 3
            replicationFactor: 1

* install mongodb
    0. ref. https://artifacthub.io/packages/helm/groundhog2k/mongodb/0.1.0
    1. $ helm repo add groundhog2k https://groundhog2k.github.io/helm-charts/
    2. $ helm install mongodb groundhog2k/mongodb
    3. connect uri=mongodb.default.svc.cluster.local

* install redis
    1. $ helm install redis-server oci://registry-1.docker.io/bitnamicharts/redis
    2. $ export REDIS_PASSWORD=$(kubectl get secret --namespace default redis-server  -o jsonpath="{.data.redis-password}" | base64 -d)



* Unorganized command

docker run -d localhost:32000/api-gateway:registry
docker logs -f localhost:32000/api-gateway
docker exec -it api-gateway /bin/bash
docker rmi $(docker images -f "dangling=true" -q)

curl http://localhost:32000/v2/_catalog
curl http://localhost:32000/v2/business-white-paper/tags/list

curl --max-time 6000 -d '{"query":"안녕"}'  -H "Content-Type: application/json"  -X POST http://127.0.0.1:8080/api/llm-query
curl -i --header    "Accept: application/vnd.docker.distribution.manifest.v2+json" http://localhost:32000/v2/api-gateway/manifests/registry 2>&1 | grep Docker-Content-Digest
curl -X DELETE -v http://localhost:32000/v2/api-gateway/manifests/sha256:11d59aef548beece3bc51169e431c4804ba04a798779093ff022c4ee082341e6

microk8s disable registry
microk8s disable hostpath-storage:destroy-storage
microk8s enable registry

kctl exec -it kafka-796d5f9749-mbnpt -- bash
I have no name!@kafka-796d5f9749-mbnpt:/$ kafka-topics.sh --create --topic query-business --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
I have no name!@kafka-796d5f9749-mbnpt:/$ kafka-topics.sh --list --bootstrap-server localhost:9092

