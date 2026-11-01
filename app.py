
import pickle
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st


# =========================================================
# 1. KONFIGURASI
# =========================================================

st.set_page_config(
    page_title="PERUMDA AIR MINUM X",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = Path(__file__).parent
DATA_PATH = BASE_DIR / "data" / "data_pipa.csv"
MODEL_PATH = BASE_DIR / "model" / "random_forest.pkl"

NAVY = "#12365A"
BLUE = "#0878C9"
RED = "#E34B55"
ORANGE = "#E99A27"
GREEN = "#15966B"


# =========================================================
# 2. MEMUAT DATA DAN MODEL
# =========================================================

@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH)


@st.cache_resource
def load_model():
    with open(MODEL_PATH, "rb") as file:
        return pickle.load(file)


try:
    data = load_data()
    model = load_model()

except Exception as error:
    st.error(f"Gagal memuat data atau model: {error}")
    st.stop()


required_columns = [
    "id_pipa",
    "wilayah",
    "usia_pipa",
    "jenis_pipa",
    "diameter_mm",
    "tekanan_bar",
    "riwayat_kebocoran",
    "kondisi_pipa",
    "risiko_kebocoran"
]

missing_columns = [
    column for column in required_columns
    if column not in data.columns
]

if missing_columns:
    st.error(
        "Kolom dataset tidak ditemukan: "
        + ", ".join(missing_columns)
    )
    st.stop()


# =========================================================
# 3. DESAIN APLIKASI
# =========================================================

st.markdown("""
<style>

/* LATAR UTAMA */

.stApp {
    background-color: #F3F6FA;
}

.block-container {
    max-width: 1450px;
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}

header[data-testid="stHeader"] {
    background: transparent;
}


/* SIDEBAR */

section[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #12365A 0%,
        #174C78 100%
    );
}

section[data-testid="stSidebar"] * {
    color: white;
}

section[data-testid="stSidebar"] [data-testid="stRadio"] label {
    background: rgba(255,255,255,0.08);
    padding: 11px 13px;
    border-radius: 9px;
    margin-bottom: 7px;
}

section[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    background: rgba(255,255,255,0.17);
}


/* PEMBUKA DASHBOARD */

.hero {
    background: linear-gradient(
        115deg,
        #12365A 0%,
        #075B9C 55%,
        #0878C9 100%
    );
    padding: 32px;
    border-radius: 17px;
    color: white;
    margin-bottom: 28px;
    box-shadow: 0 9px 25px rgba(18,54,90,0.15);
}

.hero-brand {
    display: flex;
    align-items: center;
    gap: 15px;
    margin-bottom: 20px;
}

.hero-drop {
    font-size: 45px;
    line-height: 1;
}

.hero-name {
    font-size: 14px;
    color: #FFFFFF;
    font-weight: 800;
    letter-spacing: 1.5px;
}

.hero-caption {
    color: #D5E9FA;
    font-size: 10px;
    letter-spacing: 1px;
    margin-top: 5px;
}

.hero h1 {
    color: white;
    font-size: 28px;
    font-weight: 800;
    line-height: 1.35;
    margin: 0 0 12px 0;
}

.hero p {
    color: #E5F2FC;
    font-size: 13px;
    line-height: 1.8;
    margin: 0;
    max-width: 1050px;
}


/* JUDUL BAGIAN */

.section-title,
.page-title {
    color: #183B5C;
    font-size: 25px;
    font-weight: 800;
    margin-bottom: 5px;
}

.section-subtitle,
.page-subtitle {
    color: #71849A;
    font-size: 13px;
    line-height: 1.7;
    margin-bottom: 20px;
}


/* KARTU STATISTIK */

.metric-card {
    background: #FFFFFF;
    border: 1px solid #E3EAF1;
    border-radius: 13px;
    padding: 19px;
    min-height: 125px;
    box-shadow: 0 3px 12px rgba(20,50,80,0.04);
}

.metric-label {
    color: #71849A;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.5px;
}

.metric-value {
    font-size: 30px;
    font-weight: 800;
    margin-top: 12px;
    line-height: 1.2;
}

.metric-note {
    color: #8A9BAD;
    font-size: 11px;
    margin-top: 7px;
}


/* PANEL GRAFIK */

.chart-card {
    background: white;
    border: 1px solid #E3EAF1;
    border-radius: 13px;
    padding: 17px;
    box-shadow: 0 3px 12px rgba(20,50,80,0.04);
}

.chart-card h3 {
    color: #183B5C;
    font-size: 16px;
}

.chart-card p {
    color: #8A9BAD;
    font-size: 11px;
}


/* TABEL */

div[data-testid="stDataFrame"] {
    border: 1px solid #E3EAF1;
    border-radius: 10px;
    overflow: hidden;
}


/* TOMBOL */

.stButton button,
.stDownloadButton button {
    background-color: #0878C9;
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 600;
}

.stButton button:hover,
.stDownloadButton button:hover {
    background-color: #12365A;
    color: white;
}


/* TAMPILAN HP */

@media (max-width: 700px) {

    .block-container {
        padding: 1rem 0.8rem 1.5rem;
    }

    .hero {
        padding: 22px 18px;
        border-radius: 14px;
    }

    .hero-drop {
        font-size: 36px;
    }

    .hero-name {
        font-size: 11px;
    }

    .hero-caption {
        font-size: 8px;
    }

    .hero h1 {
        font-size: 21px;
    }

    .hero p {
        font-size: 12px;
    }

    .section-title,
    .page-title {
        font-size: 21px;
    }

    .metric-card {
        padding: 13px;
        min-height: 105px;
    }

    .metric-value {
        font-size: 25px;
    }
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# 4. SIDEBAR DAN NAVIGASI
# =========================================================

with st.sidebar:

    st.markdown(
        '<h2 style="color:white;">💧 PERUMDA X</h2>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<p style="font-size:10px;color:#D5E9FA;">SISTEM MONITORING JARINGAN AIR BERSIH</p>',
        unsafe_allow_html=True
    )

    st.divider()

    st.markdown(
        '<p style="font-size:11px;letter-spacing:1.5px;font-weight:700;">MENU UTAMA</p>',
        unsafe_allow_html=True
    )

    menu = st.radio(
        "Navigasi",
        [
            "Dashboard",
            "Data Pipa",
            "Prediksi Risiko",
            "Laporan"
        ],
        label_visibility="collapsed"
    )


# =========================================================
# 5. PERHITUNGAN DATA
# =========================================================

total = len(data)

tinggi = int(
    (data["risiko_kebocoran"] == "Tinggi").sum()
)

sedang = int(
    (data["risiko_kebocoran"] == "Sedang").sum()
)

rendah = int(
    (data["risiko_kebocoran"] == "Rendah").sum()
)


# =========================================================
# 6. HALAMAN DASHBOARD
# =========================================================

if menu == "Dashboard":

    # HEADER DASHBOARD

    st.markdown(
        '<div class="hero">'
        '<div class="hero-brand">'
        '<span class="hero-drop">💧</span>'
        '<div>'
        '<div class="hero-name">PERUMDA AIR MINUM X</div>'
        '<div class="hero-caption">SISTEM MONITORING JARINGAN DISTRIBUSI AIR BERSIH</div>'
        '</div>'
        '</div>'
        '<h1>Sistem Monitoring dan Prediksi Risiko Kebocoran Pipa</h1>'
        '<p>'
        'Sistem ini dikembangkan untuk menyajikan informasi mengenai '
        'kondisi jaringan distribusi air bersih serta mengidentifikasi '
        'tingkat risiko kebocoran berdasarkan karakteristik pipa. '
        'Proses klasifikasi menggunakan metode Random Forest. '
        'Hasil pengolahan ditampilkan melalui dashboard berbasis web '
        'untuk membantu proses pemantauan dan penentuan prioritas pemeriksaan.'
        '</p>'
        '</div>',
        unsafe_allow_html=True
    )


    # RINGKASAN MONITORING

    st.markdown(
        '<div class="section-title">Ringkasan Monitoring Jaringan</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-subtitle">'
        'Gambaran jumlah pipa berdasarkan kategori tingkat risiko '
        'kebocoran pada jaringan distribusi air bersih.'
        '</div>',
        unsafe_allow_html=True
    )


    # KARTU STATISTIK

    columns = st.columns(4)

    metrics = [
        ("TOTAL PIPA", total, NAVY, "Seluruh data jaringan"),
        ("RISIKO TINGGI", tinggi, RED, "Prioritas pemeriksaan"),
        ("RISIKO SEDANG", sedang, ORANGE, "Perlu pemantauan"),
        ("RISIKO RENDAH", rendah, GREEN, "Pemeriksaan rutin")
    ]

    for column, item in zip(columns, metrics):

        label, value, color, note = item

        with column:

            st.markdown(
                '<div class="metric-card">'
                f'<div class="metric-label">{label}</div>'
                f'<div class="metric-value" style="color:{color};">{value:,}</div>'
                f'<div class="metric-note">{note}</div>'
                '</div>',
                unsafe_allow_html=True
            )


    st.write("")


    # DUA GRAFIK

    left, right = st.columns(2)


    # GRAFIK BATANG

    with left:

        with st.container(border=True):

            st.subheader("Distribusi Tingkat Risiko")

            st.caption(
                "Jumlah pipa berdasarkan kategori risiko kebocoran."
            )

            fig, ax = plt.subplots(figsize=(6, 3.5))

            fig.patch.set_facecolor("white")
            ax.set_facecolor("white")

            categories = ["Tinggi", "Sedang", "Rendah"]
            values = [tinggi, sedang, rendah]
            colors = [RED, ORANGE, GREEN]

            bars = ax.barh(
                categories,
                values,
                color=colors,
                height=0.48
            )

            ax.invert_yaxis()

            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.spines["left"].set_visible(False)
            ax.spines["bottom"].set_color("#E5EBF2")

            ax.tick_params(
                axis="y",
                length=0,
                labelsize=9,
                colors=NAVY
            )

            ax.tick_params(
                axis="x",
                labelsize=8,
                colors="#8797A8"
            )

            ax.grid(
                axis="x",
                color="#EAF0F5",
                linewidth=0.8
            )

            ax.set_axisbelow(True)

            max_value = max(values) if max(values) > 0 else 1

            for bar in bars:

                ax.text(
                    bar.get_width() + max_value * 0.02,
                    bar.get_y() + bar.get_height() / 2,
                    str(int(bar.get_width())),
                    va="center",
                    fontsize=9,
                    color=NAVY,
                    fontweight="bold"
                )

            ax.set_xlim(0, max_value * 1.2)

            plt.tight_layout()

            st.pyplot(fig, use_container_width=True)

            plt.close(fig)


    # GRAFIK LINGKARAN

    with right:

        with st.container(border=True):

            st.subheader("Komposisi Tingkat Risiko")

            st.caption(
                "Persentase kategori risiko terhadap seluruh data pipa."
            )

            fig, ax = plt.subplots(figsize=(6, 3.5))

            fig.patch.set_facecolor("white")

            values = [tinggi, sedang, rendah]
            labels = ["Tinggi", "Sedang", "Rendah"]
            colors = [RED, ORANGE, GREEN]

            if sum(values) > 0:

                ax.pie(
                    values,
                    labels=labels,
                    colors=colors,
                    startangle=90,
                    counterclock=False,
                    autopct="%1.1f%%",
                    pctdistance=0.78,
                    labeldistance=1.12,
                    wedgeprops={
                        "width": 0.36,
                        "edgecolor": "white",
                        "linewidth": 3
                    },
                    textprops={
                        "fontsize": 9,
                        "color": NAVY
                    }
                )

                ax.text(
                    0,
                    0,
                    f"{total}\nPIPA",
                    ha="center",
                    va="center",
                    fontsize=16,
                    fontweight="bold",
                    color=NAVY
                )

            else:

                ax.text(
                    0,
                    0,
                    "Belum ada data",
                    ha="center",
                    va="center"
                )

            ax.axis("equal")

            plt.tight_layout()

            st.pyplot(fig, use_container_width=True)

            plt.close(fig)


# =========================================================
# 7. HALAMAN DATA PIPA
# =========================================================

elif menu == "Data Pipa":

    st.markdown(
        '<div class="page-title">Data Jaringan Pipa</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="page-subtitle">'
        'Halaman ini menyajikan informasi karakteristik jaringan '
        'pipa distribusi air bersih. Pengguna dapat melakukan '
        'pencarian berdasarkan ID pipa atau wilayah serta '
        'menyaring data berdasarkan kategori tingkat risiko.'
        '</div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns([2, 1])

    with col1:

        search_text = st.text_input(
            "Cari ID Pipa atau Wilayah",
            placeholder="Contoh: P001 atau Wilayah A"
        )

    with col2:

        risk_filter = st.selectbox(
            "Filter Risiko",
            ["Semua", "Tinggi", "Sedang", "Rendah"]
        )

    shown = data.copy()

    if search_text:

        by_id = shown["id_pipa"].astype(str).str.contains(
            search_text,
            case=False,
            na=False
        )

        by_area = shown["wilayah"].astype(str).str.contains(
            search_text,
            case=False,
            na=False
        )

        shown = shown[by_id | by_area]

    if risk_filter != "Semua":

        shown = shown[
            shown["risiko_kebocoran"] == risk_filter
        ]

    st.dataframe(
        shown,
        hide_index=True,
        use_container_width=True,
        height=480
    )

    st.caption(
        f"Jumlah data ditampilkan: {len(shown)} dari {total} data."
    )


# =========================================================
# 8. HALAMAN PREDIKSI RISIKO
# =========================================================

elif menu == "Prediksi Risiko":

    st.markdown(
        '<div class="page-title">Prediksi Risiko Kebocoran Pipa</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="page-subtitle">'
        'Masukkan karakteristik pipa untuk memperoleh perkiraan '
        'kategori risiko menggunakan model klasifikasi Random Forest.'
        '</div>',
        unsafe_allow_html=True
    )

    with st.container(border=True):

        st.subheader("Informasi Karakteristik Pipa")

        with st.form("form_prediksi"):

            col1, col2 = st.columns(2)

            with col1:

                usia = st.number_input(
                    "Usia Pipa (tahun)",
                    min_value=0,
                    max_value=100,
                    value=10
                )

                jenis = st.selectbox(
                    "Jenis Pipa",
                    ["PVC", "Besi", "HDPE"]
                )

                diameter = st.number_input(
                    "Diameter Pipa (mm)",
                    min_value=1,
                    max_value=1000,
                    value=100
                )

            with col2:

                tekanan = st.number_input(
                    "Tekanan Air (bar)",
                    min_value=0.0,
                    max_value=20.0,
                    value=3.0,
                    step=0.1
                )

                riwayat = st.number_input(
                    "Jumlah Riwayat Kebocoran",
                    min_value=0,
                    max_value=100,
                    value=0
                )

                kondisi = st.selectbox(
                    "Kondisi Pipa",
                    ["Baik", "Sedang", "Buruk"]
                )

            submitted = st.form_submit_button(
                "Prediksi Risiko Sekarang",
                type="primary",
                use_container_width=True
            )

    if submitted:

        new_pipe = pd.DataFrame([{
            "usia_pipa": usia,
            "jenis_pipa": jenis,
            "diameter_mm": diameter,
            "tekanan_bar": tekanan,
            "riwayat_kebocoran": riwayat,
            "kondisi_pipa": kondisi
        }])

        try:

            result = model.predict(new_pipe)[0]

            st.subheader("Hasil Prediksi")

            if result == "Tinggi":

                st.error("RISIKO TINGGI")

                st.write(
                    "Pipa disarankan menjadi prioritas pemeriksaan "
                    "dan pemantauan lapangan."
                )

            elif result == "Sedang":

                st.warning("RISIKO SEDANG")

                st.write(
                    "Pipa disarankan mendapatkan pemantauan "
                    "dan pemeriksaan secara berkala."
                )

            else:

                st.success("RISIKO RENDAH")

                st.write(
                    "Pipa tetap perlu menjalani pemeriksaan rutin "
                    "untuk menjaga kondisi jaringan."
                )

            st.caption(
                "Hasil prediksi berasal dari model latihan yang "
                "menggunakan data simulasi dan bukan pengganti "
                "pemeriksaan langsung di lapangan."
            )

        except Exception as error:

            st.error(f"Prediksi gagal dilakukan: {error}")


# =========================================================
# 9. HALAMAN LAPORAN
# =========================================================

elif menu == "Laporan":

    st.markdown(
        '<div class="page-title">Laporan Data Jaringan Pipa</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="page-subtitle">'
        'Halaman ini menyajikan ringkasan data jaringan berdasarkan '
        'kategori risiko serta menyediakan fasilitas untuk '
        'mengunduh data dalam format CSV.'
        '</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Data Pipa", total)
    col2.metric("Risiko Tinggi", tinggi)
    col3.metric("Risiko Rendah", rendah)

    st.subheader("Pratinjau Data")

    st.dataframe(
        data.head(10),
        hide_index=True,
        use_container_width=True
    )

    csv_data = data.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="Unduh Laporan Data Pipa (CSV)",
        data=csv_data,
        file_name="laporan_data_pipa.csv",
        mime="text/csv",
        use_container_width=True
    )
