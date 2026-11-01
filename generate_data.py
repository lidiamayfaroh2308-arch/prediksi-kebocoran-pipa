
import pandas as pd
import random

random.seed(42)

jumlah_data = 500
data_pipa = []

jenis_pipa = ["PVC", "Besi", "HDPE"]
kondisi_pipa = ["Baik", "Sedang", "Buruk"]

wilayah = [
    "Wilayah A",
    "Wilayah B",
    "Wilayah C",
    "Wilayah D",
    "Wilayah E"
]

for i in range(1, jumlah_data + 1):

    usia = random.randint(1, 30)
    jenis = random.choice(jenis_pipa)
    diameter = random.choice([50, 75, 100, 150, 200])
    tekanan = round(random.uniform(1.5, 5.0), 2)
    riwayat = random.randint(0, 5)
    kondisi = random.choices(
        kondisi_pipa,
        weights=[40, 35, 25]
    )[0]

    # Skor simulasi untuk menentukan label risiko
    skor = 0

    if usia >= 15:
        skor += 2
    elif usia >= 8:
        skor += 1

    if kondisi == "Buruk":
        skor += 2
    elif kondisi == "Sedang":
        skor += 1

    if riwayat >= 3:
        skor += 2
    elif riwayat >= 1:
        skor += 1

    if tekanan >= 4.0:
        skor += 1

    if skor >= 5:
        risiko = "Tinggi"
    elif skor >= 3:
        risiko = "Sedang"
    else:
        risiko = "Rendah"

    data_pipa.append({
        "id_pipa": f"P{i:03d}",
        "wilayah": random.choice(wilayah),
        "usia_pipa": usia,
        "jenis_pipa": jenis,
        "diameter_mm": diameter,
        "tekanan_bar": tekanan,
        "riwayat_kebocoran": riwayat,
        "kondisi_pipa": kondisi,
        "risiko_kebocoran": risiko
    })

df = pd.DataFrame(data_pipa)

df.to_csv("data/data_pipa.csv", index=False)

print("DATA BERHASIL DIBUAT!")
print("Jumlah data:", len(df))
print("\nContoh data:")
print(df.head())

print("\nJumlah kategori risiko:")
print(df["risiko_kebocoran"].value_counts())
