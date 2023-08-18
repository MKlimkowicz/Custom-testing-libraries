#!/bin/bash

POSTGRES_IMAGE=${1:-postgres:15}
INITIAL_WAIT=${2:-10}
CHECK_INTERVAL=${3:-5}

docker pull $POSTGRES_IMAGE
if [ $? -ne 0 ]; then
    echo "Error pulling Docker image $POSTGRES_IMAGE."
    exit 1
fi

docker-compose down
if [ $? -ne 0 ]; then
    echo "Error shutting down containers."
    exit 1
fi

docker-compose up --build > /dev/null 2>&1 &
if [ $? -ne 0 ]; then
    echo "Error starting Docker Compose."
    exit 1
fi

sleep $INITIAL_WAIT

web_container_id=$(docker-compose ps -q web)

if [ -z "$web_container_id" ]; then
    echo "Error initializing the containers."
    exit 1
fi

while [ "$(docker inspect -f '{{.State.Running}}' $web_container_id)" == "true" ]
do
    sleep $CHECK_INTERVAL
done

echo "Fetching logs from web service container..."
docker-compose logs web

echo "Bringing down the services..."

TMP_OUTPUT=$(mktemp)
docker-compose down --volumes --rmi local > $TMP_OUTPUT 2>&1

network_name=$(docker network ls | grep $(basename $(pwd)) | awk '{print $2}')
volume_name=$(docker volume ls | grep $(basename $(pwd)) | awk '{print $2}')

awk '
    /Stopping/ && !seen_stop[$2]++ {print "Stopping and removing " $2 " ..."}
    /Removing/ && /done/ && !seen_remove[$2]++ {print $2 " removed successfully."}
' $TMP_OUTPUT

rm $TMP_OUTPUT

echo "Removing network $network_name"
echo "Removing volume $volume_name"

echo "Run is completed"

exit 0
