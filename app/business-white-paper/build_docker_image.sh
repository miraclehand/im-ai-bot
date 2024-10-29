ARCH=$(uname -m)
if [ "$ARCH" = "x86_64" ]; then
    PLATFORM="amd64"
elif [ "$ARCH" = "aarch64" ]; then
    PLATFORM="arm64"
else
    PLATFORM=$ARCH
fi

docker build --build-arg PLATFORM=$PLATFORM -t localhost:32000/business-white-paper:latest .
docker push localhost:32000/business-white-paper:latest
microk8s kubectl rollout restart deployment business-white-paper


