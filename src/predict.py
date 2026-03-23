import pickle
import pandas as pd

# FIX: Load ALL required artifacts, not just the model
model          = pickle.load(open("models/model.pkl",          "rb"))
encoders       = pickle.load(open("models/encoders.pkl",       "rb"))
features       = pickle.load(open("models/features.pkl",       "rb"))
target_encoder = pickle.load(open("models/target_encoder.pkl", "rb"))


def predict_food(data: dict) -> dict:
    """
    Predict food inspection result from a dict of raw string values.

    Example input:
        {
            "businessname": "Pizza Palace",
            "city": "Chicago",
            "address": "123 Main St"
        }

    Returns:
        {
            "prediction_code": 0,
            "prediction_label": "Pass"
        }
    """
    df = pd.DataFrame([data])
    df = df[features]

    # Encode each column using saved LabelEncoders
    for col in df.columns:
        encoder = encoders[col]
        df[col] = df[col].astype(str)
        df[col] = df[col].apply(
            lambda x: encoder.transform([x])[0] if x in encoder.classes_ else 0
        )

    prediction = model.predict(df)
    label = target_encoder.inverse_transform(prediction)[0]

    return {
        "prediction_code": int(prediction[0]),
        "prediction_label": str(label)
    }


# Quick test when run directly
if __name__ == "__main__":
    sample = {
        "businessname": "Test Restaurant",
        "city": "Chicago",
        "address": "456 Unknown Ave"
    }
    result = predict_food(sample)
    print("Prediction:", result)