from flask import Flask, jsonify, request

app = Flask(__name__)

data_store = {}


@app.route("/api/data/<string:key>", methods=["GET"])
def get_data(key):
    if key in data_store:
        return jsonify({key: data_store[key]})
    else:
        return jsonify({"error": "Key not found"}), 404


@app.route("/api/data", methods=["POST"])
def post_data():
    data = request.json
    data_store.update(data)
    return jsonify(data), 201


@app.route("/api/data/<string:key>", methods=["PUT"])
def put_data(key):
    data = request.json
    if key in data_store:
        data_store[key] = data["value"]
        return jsonify({key: data_store[key]})
    else:
        return jsonify({"error": "Key not found"}), 404


@app.route("/api/data/<string:key>", methods=["DELETE"])
def delete_data(key):
    if key in data_store:
        del data_store[key]
        return jsonify({"message": "Deleted"}), 200
    else:
        return jsonify({"error": "Key not found"}), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
