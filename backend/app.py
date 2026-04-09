from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
from urllib.parse import urlparse

# =========================
# 🔥 INIT
# =========================
app = Flask(__name__)
CORS(app)

# =========================
# 🔥 LOAD MODEL
# =========================
model = pickle.load(open("model.pkl", "rb"))
vectorizer = pickle.load(open("vectorizer.pkl", "rb"))

# =========================
# 🧠 TRUSTED SOURCES
# =========================
TRUSTED_SOURCES = [
    "bbc", "reuters", "cnn", "ndtv", "thehindu", "aljazeera"
]

# =========================
# 🧠 SUSPICIOUS WORDS
# =========================
SUSPICIOUS_WORDS = [
    "shocking", "unbelievable", "miracle", "secret",
    "exposed", "viral", "conspiracy", "aliens"
]

# =========================
# 🚨 EXTREME FAKE DETECTOR
# =========================
EXTREME_FAKE_PATTERNS = [
    "aliens", "time travel", "immortal", "zombie",
    "teleport", "mind control", "miracle cure overnight",
    "world ending tomorrow"
]

def extreme_fake_detector(text):
    text = text.lower()
    for pattern in EXTREME_FAKE_PATTERNS:
        if pattern in text:
            return True
    return False

# =========================
# 🧠 SOURCE SCORE
# =========================
def get_source_score(url):
    if not url:
        return 0.5

    try:
        domain = urlparse(url).netloc.lower()
        for source in TRUSTED_SOURCES:
            if source in domain:
                return 0.9
        return 0.4
    except:
        return 0.5

# =========================
# 🧠 KEYWORD SIGNAL
# =========================
def keyword_signal(text):
    found = []
    for word in SUSPICIOUS_WORDS:
        if word in text.lower():
            found.append(word)

    score = 0.5 - (len(found) * 0.05)
    score = max(score, 0.2)

    return score, found

# =========================
# 🧠 HEALTH CHECK
# =========================
@app.route("/")
def home():
    return "API Running"

# =========================
# 🧠 MAIN PREDICT API
# =========================
@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data received"}), 400

        text = data.get("text", "")
        url = data.get("url", "")

        if not text.strip():
            return jsonify({"error": "Empty text"}), 400

        # =========================
        # 🚨 HARD FAKE OVERRIDE
        # =========================
        if extreme_fake_detector(text):
            return jsonify({
                "prediction": "FAKE",
                "confidence": 0.95,
                "probabilities": {
                    "fake": 0.95,
                    "real": 0.05
                },
                "signals": {
                    "reason": "Extreme fake pattern detected"
                },
                "credibility": 0.1
            })

        # =========================
        # 🤖 ML PREDICTION
        # =========================
        vectorized = vectorizer.transform([text])

        if hasattr(model, "predict_proba"):
            probs = model.predict_proba(vectorized)[0]
            fake_prob = float(probs[0])
            real_prob = float(probs[1])
        else:
            pred = model.predict(vectorized)[0]
            fake_prob = 1.0 if pred == 0 else 0.0
            real_prob = 1.0 if pred == 1 else 0.0

        model_confidence = max(fake_prob, real_prob)

        # 🔥 Confidence boost
        model_confidence = min(1.0, model_confidence + 0.05)

        # =========================
        # 🔍 SIGNALS
        # =========================
        source_score = get_source_score(url)
        keyword_score, keywords_found = keyword_signal(text)

        # =========================
        # 🔥 FINAL SCORE (IMPROVED)
        # =========================
        final_score = (
            (model_confidence * 0.75) +
            (source_score * 0.15) +
            (keyword_score * 0.10)
        )

        # =========================
        # 🎯 FINAL DECISION
        # =========================
        if final_score >= 0.6:
            prediction = "REAL"
        elif final_score <= 0.4:
            prediction = "FAKE"
        else:
            prediction = "UNCERTAIN"

        # =========================
        # 📤 RESPONSE
        # =========================
        return jsonify({
            "prediction": prediction,
            "confidence": round(final_score, 2),
            "probabilities": {
                "fake": fake_prob,
                "real": real_prob
            },
            "signals": {
                "model_confidence": model_confidence,
                "source_score": source_score,
                "keyword_score": keyword_score,
                "keywords_triggered": keywords_found
            },
            "credibility": source_score,
            "explanation": {
                "reason": "Hybrid decision using ML + source + keyword signals",
                "advice": "Cross-check with trusted sources if uncertain"
            }
        })

    except Exception as e:
        print("🔥 BACKEND ERROR:", str(e))

        return jsonify({
            "error": "Internal server error",
            "details": str(e)
        }), 500

# =========================
# 🚀 RUN
# =========================
if __name__ == "__main__":
    import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)