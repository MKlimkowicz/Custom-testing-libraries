use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use serde::{Deserialize, Serialize};
use std::sync::Mutex;
use std::collections::HashMap;

#[derive(Serialize, Deserialize)]
struct Data {
    value: String,
}

struct AppState {
    data_store: Mutex<HashMap<String, String>>,
}

async fn get_data(data: web::Data<AppState>, key: web::Path<String>) -> impl Responder {
    let data_store = data.data_store.lock().unwrap();
    if let Some(value) = data_store.get(&*key) {
        HttpResponse::Ok().json(serde_json::json!({&*key: value}))
    } else {
        HttpResponse::NotFound().json(serde_json::json!({"error": "Key not found"}))
    }
}

async fn post_data(data: web::Data<AppState>, new_data: web::Json<HashMap<String, String>>) -> impl Responder {
    let mut data_store = data.data_store.lock().unwrap();
    for (key, value) in new_data.iter() {
        data_store.insert(key.clone(), value.clone());
    }
    HttpResponse::Created().json(new_data.into_inner())
}

async fn put_data(data: web::Data<AppState>, key: web::Path<String>, new_data: web::Json<Data>) -> impl Responder {
    let mut data_store = data.data_store.lock().unwrap();
    if data_store.contains_key(&*key) {
        data_store.insert(key.clone(), new_data.value.clone());
        HttpResponse::Ok().json(serde_json::json!({&*key: &new_data.value}))
    } else {
        HttpResponse::NotFound().json(serde_json::json!({"error": "Key not found"}))
    }
}

async fn delete_data(data: web::Data<AppState>, key: web::Path<String>) -> impl Responder {
    let mut data_store = data.data_store.lock().unwrap();
    if data_store.remove(&*key).is_some() {
        HttpResponse::Ok().json(serde_json::json!({"message": "Deleted"}))
    } else {
        HttpResponse::NotFound().json(serde_json::json!({"error": "Key not found"}))
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let data_store = web::Data::new(AppState {
        data_store: Mutex::new(HashMap::new()),
    });

    HttpServer::new(move || {
        App::new()
            .app_data(data_store.clone())
            .route("/api/data/{key}", web::get().to(get_data))
            .route("/api/data", web::post().to(post_data))
            .route("/api/data/{key}", web::put().to(put_data))
            .route("/api/data/{key}", web::delete().to(delete_data))
    })
    .bind("0.0.0.0:8080")?
    .run()
    .await
}
