#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Function to clean up Redis container on exit
cleanup() {
    echo "Stopping and removing Redis container..."
    docker stop test-redis-stack
    docker rm test-redis-stack
}
trap cleanup EXIT

# Start the Redis container
echo "Starting Redis container..."
docker run -d --name test-redis-stack -p 6379:6379 -p 8001:8001 redis/redis-stack:latest

# Wait until Redis is ready
echo "Waiting for Redis to be ready..."
for i in {1..10}; do
    if docker exec test-redis-stack redis-cli ping | grep -q PONG; then
        echo "Redis is ready!"
        break
    else
        echo "Redis is not ready yet... ($i/10)"
        sleep 2
    fi
done

# Check if Redis is ready
if ! docker exec test-redis-stack redis-cli ping | grep -q PONG; then
    echo "Error: Redis is not ready. Exiting."
    exit 1
fi

# Set environment variables
export REDIS_URL=redis://localhost:6379
echo "Environment variables set:"
echo "REDIS_URL=$REDIS_URL"

# Navigate to the backend directory
cd ../backend

# Run the tests
echo "Running tests..."
poetry run pytest