# Rust API Project

This is a simple Rust API project using Actix-web.

## Requirements

- Rust
- Docker
- Docker Compose

## Setup

### Docker Setup

1. **Clone the repository:**

    ```sh
    git clone https://github.com/yourusername/Custom-testing-libraries.git
    cd Custom-testing-libraries/api/rust
    ```

2. **Build and run the Docker container:**

    ```sh
    docker compose up --build -d
    ```

3. **Run tests:**

    ```sh
    docker compose exec web cargo test
    ```

### Local Setup

1. **Clone the repository:**

    ```sh
    git clone https://github.com/yourusername/Custom-testing-libraries.git
    cd Custom-testing-libraries/api/rust
    ```

2. **Build the application:**

    ```sh
    cargo build --release
    ```

3. **Run the application:**

    ```sh
    ./target/release/my_rust_api
    ```

## API Endpoints

- POST /api/data
- GET /api/data/{key}
- PUT /api/data/{key}
- DELETE /api/data/{key}

## Example Usage

- Create data (POST):

  ```sh
  curl -X POST -H "Content-Type: application/json" -d '{"test_key":"test_value"}' http://localhost:8080/api/data
  ```

- Retrieve data (GET):

  ```sh
  curl http://localhost:8080/api/data/test_key
  ```

- Update data (PUT):

  ```sh
  curl -X PUT -H "Content-Type: application/json" -d '{"value":"new_value"}' http://localhost:8080/api/data/test_key
  ```

- Delete data (DELETE):

  ```sh
  curl -X DELETE http://localhost:8080/api/data/test_key
  ```

## Clean up

- Stop the Docker container:

  ```sh
  docker compose down
  ```

