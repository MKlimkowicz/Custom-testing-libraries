#!/bin/bash

host="$1"
port="$2"
shift 2  # shift off the first two arguments
cmd="$@"

success="false"
for i in `seq 1 30`; do
    echo "Attempt $i: Trying to connect to $host:$port..."
    
    # Check for successful connection
    if PGPASSWORD=$POSTGRES_PASSWORD psql -h "$host" -p "$port" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q' 2>/dev/null; then
        success="true"
        echo "Connected successfully on attempt $i."
        break
    else
        echo "Failed to connect on attempt $i."
    fi
    
    sleep 2
done

# If the connection was not successful, exit
if [ "$success" != "true" ]; then
    >&2 echo "Failed to connect to $host:$port after 30 attempts."
    exit 1
fi

echo "Postgres is up - executing command"
exec $cmd
