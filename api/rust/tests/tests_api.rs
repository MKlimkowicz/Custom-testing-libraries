use reqwest::Client;
use serde_json::Value;

async fn assert_response_status_and_json(
    response: reqwest::Response,
    expected_status: u16,
    expected_json: Value,
) {
    let status = response.status().as_u16();
    let json: Value = response.json().await.unwrap();
    assert_eq!(status, expected_status, "Expected status: {}, but got: {}. Response body: {:?}", expected_status, status, json);
    assert_eq!(json, expected_json, "Expected JSON: {}, but got: {}", expected_json, json);
}

async fn post_data(client: &Client, url: &str, data: Value) -> reqwest::Response {
    client
        .post(url)
        .json(&data)
        .send()
        .await
        .unwrap()
}

async fn get_data(url: &str) -> reqwest::Response {
    reqwest::get(url)
        .await
        .unwrap()
}

async fn put_data(client: &Client, url: &str, data: Value) -> reqwest::Response {
    client
        .put(url)
        .json(&data)
        .send()
        .await
        .unwrap()
}

async fn delete_data(client: &Client, url: &str) -> reqwest::Response {
    client
        .delete(url)
        .send()
        .await
        .unwrap()
}

#[tokio::test]
async fn test_crud_operations() {
    let client = reqwest::Client::new();
    let base_url = "http://localhost:8080/api/data";

    // Test POST
    let post_data_value = serde_json::json!({"test_key": "test_value"});
    let post_response = post_data(&client, base_url, post_data_value.clone()).await;
    assert_response_status_and_json(post_response, 201, post_data_value.clone()).await;

    // Test GET
    let get_response = get_data(&format!("{}/test_key", base_url)).await;
    assert_response_status_and_json(get_response, 200, post_data_value).await;

    // Test PUT
    let put_data_value = serde_json::json!({"value": "new_value"});
    let put_response = put_data(&client, &format!("{}/test_key", base_url), put_data_value.clone()).await;
    let expected_put_response = serde_json::json!({"test_key": "new_value"});
    assert_response_status_and_json(put_response, 200, expected_put_response.clone()).await;

    // Test DELETE
    let delete_response = delete_data(&client, &format!("{}/test_key", base_url)).await;
    assert_response_status_and_json(delete_response, 200, serde_json::json!({"message": "Deleted"})).await;

    let get_response_after_delete = get_data(&format!("{}/test_key", base_url)).await;
    assert_response_status_and_json(get_response_after_delete, 404, serde_json::json!({"error": "Key not found"})).await;
}
