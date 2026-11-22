
#!/bin/bash
set -e

CONTAINER_NAME="ml-container"
HOST_PORT="8000"

echo "Checking container status..."

if ! docker ps --format '{{.Names}}' | grep -qx "$CONTAINER_NAME"; then
    echo "ERROR: ML container is not running."
    docker logs "$CONTAINER_NAME" || true
    exit 1
fi

echo "Checking application health..."

for i in {1..15}; do
    if curl -fsS "http://127.0.0.1:${HOST_PORT}/docs" >/dev/null; then
        echo "ML application is healthy."
        exit 0
    fi

    sleep 4
done

echo "ERROR: ML application health check failed."
docker logs "$CONTAINER_NAME" || true
exit 1
