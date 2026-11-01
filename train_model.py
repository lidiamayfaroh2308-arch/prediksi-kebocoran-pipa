import pandas as pd
import pickle

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report

# Membaca data
data = pd.read_csv("data/data_pipa.csv")

# Memisahkan fitur dan target
X = data[
    [
        "usia_pipa",
        "jenis_pipa",
        "diameter_mm",
        "tekanan_bar",
        "riwayat_kebocoran",
        "kondisi_pipa"
    ]
]

y = data["risiko_kebocoran"]

# Mengolah data kategori
preprocessor = ColumnTransformer(
    transformers=[
        ("kategori", OneHotEncoder(handle_unknown="ignore"),
         ["jenis_pipa", "kondisi_pipa"]),
        ("angka", "passthrough",
         ["usia_pipa", "diameter_mm", "tekanan_bar",
          "riwayat_kebocoran"])
    ]
)

# Membuat model Random Forest
model = Pipeline(
    steps=[
        ("preprocessing", preprocessor),
        ("classifier", RandomForestClassifier(
            n_estimators=100,
            random_state=42
        ))
    ]
)

# Membagi data untuk pelatihan dan pengujian
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# Melatih model
model.fit(X_train, y_train)

# Menguji model
prediksi = model.predict(X_test)

print("JUMLAH DATA:", len(data))
print("DATA LATIH:", len(X_train))
print("DATA UJI:", len(X_test))

print("\nHASIL PENGUJIAN MODEL")
print("Akurasi:", round(
    accuracy_score(y_test, prediksi) * 100, 2
), "%")

print("\nLAPORAN KLASIFIKASI:")
print(classification_report(
    y_test, prediksi, zero_division=0
))

# Menyimpan model
with open("model/random_forest.pkl", "wb") as file:
    pickle.dump(model, file)

print("MODEL BERHASIL DIPERBARUI!")