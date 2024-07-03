# Python API Project

This is a simple Python API project using Flask.

## Requirements

- Python 3.7+
- Docker
- Docker Compose

## Setup

1. **Clone the repository:**

    ```sh
    git clone https://github.com/yourusername/Custom-testing-libraries.git
    cd Custom-testing-libraries/api/python
    ```

2. **Build and run the Docker container:**

    ```sh
    docker compose up --build -d
    ```

3. **Run tests:**

    ```sh
    docker compose run web pytest
    ```

**API Endpoints**

- POST /api/data
- GET /api/data/{key}
- PUT /api/data/{key}
- DELETE /api/data/{key}

**Example Usage**

Create data (POST):

```sh
curl -X POST -H "Content-Type: application/json" -d '{"test_key":"test_value"}' http://localhost:5000/api/data
```

Retrieve data (GET):

```sh
curl http://localhost:5000/api/data/test_key
```

Update data (PUT):

```sh
curl -X PUT -H "Content-Type: application/json" -d '{"value":"new_value"}' http://localhost:5000/api/data/test_key
```

Delete data (DELETE):

```sh
curl -X DELETE http://localhost:5000/api/data/test_key
```

Clean up:

Stop the Docker container:

```sh
docker compose down
```

