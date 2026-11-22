
#!/bin/bash
set -e

CONTAINER_NAME="ml-container"

echo "Stopping existing ML application..."

if docker ps -a --format '{{.Names}}' | grep -qx "$CONTAINER_NAME"; then
    docker stop "$CONTAINER_NAME" || true
    docker rm "$CONTAINER_NAME" || true
fi

echo "Existing container stopped."
