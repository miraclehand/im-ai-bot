ARCH=$(uname -m)
if [ "$ARCH" = "x86_64" ]; then
    PLATFORM="amd64"
elif [ "$ARCH" = "aarch64" ]; then
    PLATFORM="arm64"
else
    PLATFORM=$ARCH
fi

docker build --build-arg PLATFORM=$PLATFORM -t localhost:32000/api-gateway:latest .
docker push localhost:32000/api-gateway:latest
microk8s kubectl rollout restart deployment api-gateway


