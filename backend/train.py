import pandas as pd
import pickle
import re
import string

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import accuracy_score, classification_report

# =========================
# 🧠 TEXT CLEANING
# =========================
def clean_text(text):
    text = str(text).lower()

    # remove urls
    text = re.sub(r"http\S+|www\S+|https\S+", '', text)

    # remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))

    # remove numbers
    text = re.sub(r'\d+', '', text)

    # remove extra spaces
    text = text.strip()

    return text


# =========================
# 📦 LOAD DATA
# =========================
fake = pd.read_csv("Data/Fake.csv")
real = pd.read_csv("Data/True.csv")

fake["label"] = 0  # FAKE
real["label"] = 1  # REAL

df = pd.concat([fake, real], axis=0)

# =========================
# 🧹 CLEAN DATA
# =========================
df = df[["text", "label"]]

df.dropna(inplace=True)
df.drop_duplicates(inplace=True)

# remove very short texts (noise)
df = df[df["text"].str.split().str.len() > 5]

# clean text
df["text"] = df["text"].apply(clean_text)

print("Dataset size:", len(df))

# =========================
# ⚖️ BALANCE DATASET
# =========================
min_count = df["label"].value_counts().min()

df_fake = df[df["label"] == 0].sample(min_count)
df_real = df[df["label"] == 1].sample(min_count)

df = pd.concat([df_fake, df_real])

print("Balanced dataset:", df["label"].value_counts())

# =========================
# 🔀 SPLIT DATA
# =========================
X = df["text"]
y = df["label"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# =========================
# 🧠 TF-IDF (UPGRADED)
# =========================
vectorizer = TfidfVectorizer(
    max_features=15000,
    ngram_range=(1, 2),
    stop_words='english'
)

X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

# =========================
# 🤖 MODEL (UPGRADED)
# =========================
model = SGDClassifier(loss='log_loss', max_iter=1000)

model.fit(X_train_vec, y_train)

# =========================
# 📊 EVALUATION
# =========================
y_pred = model.predict(X_test_vec)

print("\n🔥 Accuracy:", accuracy_score(y_test, y_pred))
print("\n🔥 Classification Report:\n")
print(classification_report(y_test, y_pred))

# =========================
# 💾 SAVE MODEL
# =========================
pickle.dump(model, open("model.pkl", "wb"))
pickle.dump(vectorizer, open("vectorizer.pkl", "wb"))

print("\n✅ Model and Vectorizer saved successfully!")