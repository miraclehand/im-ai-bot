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
    1. $ helm install kafka oci://registry-1.docker.io/bitnamicharts/kafka -f kafka-values.yaml
    2. $ kubectl delete pods,svc,configmap,pvc -l app.kubernetes.io/instance=kafka



* install kafka-connect
    1. $ kubectl apply -f kafka-connect-deployment.yaml
    2. $ kubectl apply -f kafka-connect-service.yaml
    3. $ curl http://localhost:31083/


* install elasticseaach
    1. $ helm install elasticsearch bitnami/elasticsearch -f elasticsearch-values.yaml
    2. $ curl -X POST http://localhost:31083/connectors \
            -H "Content-Type: application/json" \
            -d '{
              "name": "elasticsearch-sink-connector",
              "config": {
                "connector.class": "io.confluent.connect.elasticsearch.ElasticsearchSinkConnector",
                "tasks.max": "1",
                "topics": "query-business,query-business-response",
                "connection.url": "http://elasticsearch:9200",
                "type.name": "_doc",
                "key.ignore": "true",
                "schema.ignore": "true",
                "key.converter": "org.apache.kafka.connect.storage.StringConverter",
                "value.converter": "org.apache.kafka.connect.json.JsonConverter",
                "value.converter.schemas.enable": "false",
                "errors.tolerance": "all",
                "errors.deadletterqueue.topic.name": "dlq-topic",
                "errors.log.enable": true,
                "errors.log.include.messages": true
              }
            }'
    6. $ curl http://localhost:31084/
    7. $ curl -X PUT http://localhost:31084/tests
    8. $ curl -X POST -H "Content-Type: application/json" -d '{"test1": "value1"}' http://localhost:31084/tests/_doc
    9. $ helm uninstall elasticsearch
       $ kubectl delete pvc -l app=elasticsearch-master
       $ kubectl delete configmap -l app=elasticsearch-master
       $ kubectl delete secret -l app=elasticsearch-master
       $ kubectl delete all,pvc,configmap,secret -l app=elasticsearch-master
       $ kubectl get pv
       $ kubectl delete pv <pv-name>


* install kibana
    1. $ helm install kibana bitnami/kibana -f kibana-values.yaml
    2. $ kubectl port-forward --address 0.0.0.0 service/kibana  5601:5601
    3. $ helm uninstall kibana
       $ kubectl delete service kibana
       $ kubectl delete configmap kibana-kibana-helm-scripts
       $ kubectl delete serviceaccounts pre-install-kibana-kibana
       $ kubectl delete serviceaccounts post-delete-kibana-kibana
       $ kubectl delete roles pre-install-kibana-kibana
       $ kubectl delete roles post-delete-kibana-kibana
       $ kubectl delete rolebindings pre-install-kibana-kibana
       $ kubectl delete rolebindings post-delete-kibana-kibana
       $ kubectl delete jobs pre-install-kibana-kibana
       $ kubectl delete jobs post-delete-kibana-kibana
       $ kubectl delete secret kibana-kibana-es-token


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



#helm repo add confluentinc https://packages.confluent.io/helm
#helm repo update
#helm install confluent-kafka confluentinc/confluent-for-kubernetes -f values.yaml -f connect-values.yaml

helm install elasticsearch elastic/elasticsearch -f elasticsearch-values.yaml

kubectl apply -f elasticsearch-connector.yaml





kubectl expose deployment elasticsearch-master --type=ClusterIP --port=9200
kubectl port-forward service/elasticsearch 9200:9200
kubectl port-forward service/elasticsearch-master 9200:9200
kubectl port-forward service/kafka-connect 8083:8083

helm show values elastic/elasticsearch > values.yml

    1. $ helm repo add elastic https://helm.elastic.co
    2. $ helm repo update
    3. $ helm install elasticsearch elastic/elasticsearch -f elasticsearch-values.yaml
    4. $ kubectl exec -it elasticsearch-master-0 -- curl -u "elastic:elastic" -k "https://elasticsearch-master:9200/_cat/nodes?v"

    6. $ curl -k -u elastic:elastic https://localhost:31084/
    7. $ curl -k -X PUT -u elastic:elastic https://localhost:31084/tests
    8. $ curl -k -X POST -u elastic:elastic -H "Content-Type: application/json" -d '{"test1": "value1"}' https://localhost:31084/tests/_doc
$ curl -X POST http://localhost:31083/connectors \
-H "Content-Type: application/json" \
-d '{
  "name": "elasticsearch-sink-connector",
  "config": {
    "connector.class": "io.confluent.connect.elasticsearch.ElasticsearchSinkConnector",
    "tasks.max": "1",
    "topics": "query-business,query-business-response",
    "connection.url": "http://elasticsearch:9200",
    "type.name": "_doc",
    "key.ignore": "true",
    "schema.ignore": "true",
    "connection.username": "elastic",
    "connection.password": "elastic",
    "key.converter": "org.apache.kafka.connect.storage.StringConverter",
    "value.converter": "org.apache.kafka.connect.json.JsonConverter",
    "value.converter.schemas.enable": "false"
  }
}'

    1. $ helm install kibana elastic/kibana \
          --set elasticsearchHosts=https://elasticsearch-master:9200 \
          --set resources.requests.cpu=50m \
          --set resources.requests.memory=256Mi \
          --set resources.limits.cpu=100m \
          --set resources.limits.memory=512Mi \
          --set readinessProbe.timeoutSeconds=60 \
          --set readinessProbe.initialDelaySeconds=120

curl -X GET http://localhost:31083/connectors/elasticsearch-sink-connector | jq .

    4. $ kubectl get secrets --namespace=default kibana-kibana-es-token -ojsonpath='{.data.token}' | base64 -d
    3. $ kubectl patch svc kibana-kibana -p '{"spec": {"type": "NodePort"}}'













$ kubectl exec -it business-white-paper-58f69f65c7-4vzzl -- cat /var/log/pip_install.log
Collecting redis
  Downloading redis-5.1.1-py3-none-any.whl.metadata (9.1 kB)
Downloading redis-5.1.1-py3-none-any.whl (261 kB)
Installing collected packages: redis
Successfully installed redis-5.1.1
