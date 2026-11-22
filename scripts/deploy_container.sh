
#!/bin/bash
set -e

# Update these values for each AWS project
AWS_REGION="ap-southeast-2"
AWS_ACCOUNT_ID="YOUR_AWS_ACCOUNT_ID"
ECR_REPOSITORY="YOUR_ECR_REPOSITORY"

IMAGE_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPOSITORY}:latest"

CONTAINER_NAME="ml-container"
HOST_PORT="8000"
CONTAINER_PORT="8000"

echo "Logging into Amazon ECR..."

aws ecr get-login-password --region "$AWS_REGION" | \
docker login --username AWS --password-stdin \
"${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

echo "Pulling latest Docker image..."

docker pull "$IMAGE_URI"

echo "Starting ML application..."

docker run -d \
    --name "$CONTAINER_NAME" \
    --restart unless-stopped \
    -p "${HOST_PORT}:${CONTAINER_PORT}" \
    "$IMAGE_URI"

echo "ML application deployment completed."
