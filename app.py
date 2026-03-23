from flask import Flask, request, jsonify
import pandas as pd
import pickle

app = Flask(__name__)

# Load model and preprocessing artifacts
model = pickle.load(open("models/model.pkl", "rb"))
encoders = pickle.load(open("models/encoders.pkl", "rb"))
features = pickle.load(open("models/features.pkl", "rb"))
target_encoder = pickle.load(open("models/target_encoder.pkl", "rb"))  # FIX 1: load target encoder


@app.route("/")
def home():
    return "Food Inspection Prediction API is running!"
@app.route("/health")
def health():
    return jsonify({
        "status":   "running",
        "model":    "RandomForestClassifier",
        "features": features,
        "classes":  list(target_encoder.classes_),
        "total_classes": len(target_encoder.classes_)
    })

@app.route("/predict", methods=["POST"])  # FIX 2: make sure Postman sends POST, not GET
def predict():
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "error": "No JSON body received. Send a POST request with JSON.",
                "required_fields": features
            }), 400

        df = pd.DataFrame([data])

        # Check all required features are present
        missing = [f for f in features if f not in df.columns]
        if missing:
            return jsonify({"error": f"Missing fields: {missing}"}), 400

        df = df[features]

        # Encode each feature using saved LabelEncoders
        for col in df.columns:
            encoder = encoders[col]
            df[col] = df[col].astype(str)
            df[col] = df[col].apply(
                lambda x: encoder.transform([x])[0] if x in encoder.classes_ else 0
            )

        prediction = model.predict(df)

        # FIX 3: decode prediction back to original label (e.g. "Pass" / "Fail")
        predicted_label = target_encoder.inverse_transform(prediction)[0]

        return jsonify({
            "prediction_code": int(prediction[0]),
            "prediction_label": str(predicted_label)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # FIX 4: bind to 0.0.0.0 so Postman can reach it reliably
    app.run(debug=True, host="0.0.0.0", port=5000)