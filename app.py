
import pickle
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

# 1. KONFIGURASI
st.set_page_config(
    page_title="PERUMDA AIR MINUM X",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded",
)
BASE_DIR = Path(__file__).parent
DATA_PATH = BASE_DIR / "data" / "data_pipa.csv"
MODEL_PATH = BASE_DIR / "model" / "random_forest.pkl"
NAVY, BLUE = "#12365A", "#0878C9"
RED, ORANGE, GREEN = "#E34B55", "#E99A27", "#15966B"

# 2. MEMUAT DATA DAN MODEL
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
    "id_pipa", "wilayah", "usia_pipa", "jenis_pipa", "diameter_mm",
    "tekanan_bar", "riwayat_kebocoran", "kondisi_pipa", "risiko_kebocoran"
]
missing_columns = [c for c in required_columns if c not in data.columns]
if missing_columns:
    st.error("Kolom dataset tidak ditemukan: " + ", ".join(missing_columns))
    st.stop()

# 3. DESAIN
st.markdown("""
<style>
.stApp{background:#F3F6FA;color:#183B5C}
.block-container{max-width:1450px;padding-top:1.5rem;padding-bottom:2rem}
header[data-testid="stHeader"]{background:transparent}
section[data-testid="stSidebar"]{background:linear-gradient(180deg,#12365A 0%,#174C78 100%)}
section[data-testid="stSidebar"] *{color:white}
section[data-testid="stSidebar"] [data-testid="stRadio"] label{background:rgba(255,255,255,.08);padding:11px 13px;border-radius:9px;margin-bottom:7px}
section[data-testid="stSidebar"] [data-testid="stRadio"] label:hover{background:rgba(255,255,255,.17)}
.hero{background:linear-gradient(115deg,#12365A 0%,#075B9C 55%,#0878C9 100%);padding:32px;border-radius:17px;color:white;margin-bottom:28px;box-shadow:0 9px 25px rgba(18,54,90,.15)}
.hero-brand{display:flex;align-items:center;gap:15px;margin-bottom:20px}
.hero-drop{font-size:45px;line-height:1}
.hero-name{font-size:14px;color:white;font-weight:800;letter-spacing:1.5px}
.hero-caption{color:#D5E9FA;font-size:10px;letter-spacing:1px;margin-top:5px}
.hero h1{color:white;font-size:28px;font-weight:800;line-height:1.35;margin:0 0 12px}
.hero p{color:#E5F2FC;font-size:13px;line-height:1.8;margin:0;max-width:1050px}
.section-title,.page-title{color:#183B5C;font-size:25px;font-weight:800;margin-bottom:5px}
.section-subtitle,.page-subtitle{color:#71849A;font-size:13px;line-height:1.7;margin-bottom:20px}
.metric-card{background:white;border:1px solid #E3EAF1;border-radius:13px;padding:19px;min-height:125px;box-shadow:0 3px 12px rgba(20,50,80,.04)}
.metric-label{color:#71849A;font-size:11px;font-weight:700;letter-spacing:.5px}
.metric-value{font-size:30px;font-weight:800;margin-top:12px;line-height:1.2}
.metric-note{color:#8A9BAD;font-size:11px;margin-top:7px}
div[data-testid="stDataFrame"]{border:1px solid #E3EAF1;border-radius:10px;overflow:hidden}
div[data-testid="stMain"] [data-testid="stWidgetLabel"]{color:#183B5C!important}
div[data-testid="stMain"] input{background:white!important;color:#183B5C!important;border-color:#CBD5E1!important}
div[data-testid="stMain"] [data-baseweb="select"]>div{background:white!important;color:#183B5C!important;border-color:#CBD5E1!important}
div[data-testid="stMain"] [data-baseweb="select"] span{color:#183B5C!important}
div[data-testid="stFormSubmitButton"] button{background:#0878C9!important;color:white!important;border:0!important;border-radius:8px!important;min-height:45px}
.stButton button,.stDownloadButton button{background:#0878C9;color:white;border:0;border-radius:8px;font-weight:600}
.stButton button:hover,.stDownloadButton button:hover{background:#12365A;color:white}
@media(max-width:700px){.block-container{padding:1rem .8rem 1.5rem}.hero{padding:22px 18px;border-radius:14px}.hero-drop{font-size:36px}.hero-name{font-size:11px}.hero-caption{font-size:8px}.hero h1{font-size:21px}.hero p{font-size:12px}.section-title,.page-title{font-size:21px}.metric-card{padding:13px;min-height:105px}.metric-value{font-size:25px}}
</style>
""", unsafe_allow_html=True)

# 4. SIDEBAR
with st.sidebar:
    st.markdown('<h2 style="color:white;">💧 PERUMDA X</h2>', unsafe_allow_html=True)
    st.markdown('<p style="font-size:10px;color:#D5E9FA;">SISTEM MONITORING JARINGAN AIR BERSIH</p>', unsafe_allow_html=True)
    st.divider()
    st.markdown('<p style="font-size:11px;letter-spacing:1.5px;font-weight:700;">MENU UTAMA</p>', unsafe_allow_html=True)
    menu = st.radio("Navigasi", ["Dashboard", "Data Pipa", "Prediksi Risiko", "Laporan"], label_visibility="collapsed")

# 5. RINGKASAN
total = len(data)
tinggi = int((data["risiko_kebocoran"] == "Tinggi").sum())
sedang = int((data["risiko_kebocoran"] == "Sedang").sum())
rendah = int((data["risiko_kebocoran"] == "Rendah").sum())

# 6. DASHBOARD
if menu == "Dashboard":
    st.markdown(
        '<div class="hero"><div class="hero-brand"><span class="hero-drop">💧</span>'
        '<div><div class="hero-name">PERUMDA AIR MINUM X</div>'
        '<div class="hero-caption">SISTEM MONITORING JARINGAN DISTRIBUSI AIR BERSIH</div></div></div>'
        '<h1>Sistem Monitoring dan Prediksi Risiko Kebocoran Pipa</h1>'
        '<p>Sistem ini menyajikan informasi mengenai kondisi jaringan distribusi air bersih serta mengidentifikasi tingkat risiko kebocoran berdasarkan karakteristik pipa. Proses klasifikasi menggunakan metode Random Forest. Hasil pengolahan ditampilkan melalui dashboard berbasis web untuk membantu pemantauan dan penentuan prioritas pemeriksaan.</p></div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="section-title">Ringkasan Monitoring Jaringan</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Gambaran jumlah pipa berdasarkan kategori tingkat risiko kebocoran pada jaringan distribusi air bersih.</div>', unsafe_allow_html=True)
    cards = st.columns(4)
    metrics = [
        ("TOTAL PIPA", total, NAVY, "Seluruh data jaringan"),
        ("RISIKO TINGGI", tinggi, RED, "Prioritas pemeriksaan"),
        ("RISIKO SEDANG", sedang, ORANGE, "Perlu pemantauan"),
        ("RISIKO RENDAH", rendah, GREEN, "Pemeriksaan rutin")
    ]
    for col, (label, value, color, note) in zip(cards, metrics):
        with col:
            st.markdown(
                f'<div class="metric-card"><div class="metric-label">{label}</div>'
                f'<div class="metric-value" style="color:{color};">{value:,}</div>'
                f'<div class="metric-note">{note}</div></div>',
                unsafe_allow_html=True
            )
    st.write("")
    left, right = st.columns(2)
    with left:
        with st.container(border=True):
            st.subheader("Distribusi Tingkat Risiko")
            st.caption("Jumlah pipa berdasarkan kategori risiko kebocoran.")
            fig, ax = plt.subplots(figsize=(6, 3.5))
            fig.patch.set_facecolor("white")
            ax.set_facecolor("white")
            cats, vals = ["Tinggi", "Sedang", "Rendah"], [tinggi, sedang, rendah]
            bars = ax.barh(cats, vals, color=[RED, ORANGE, GREEN], height=.48)
            ax.invert_yaxis()
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.spines["left"].set_visible(False)
            ax.spines["bottom"].set_color("#E5EBF2")
            ax.tick_params(axis="y", length=0, labelsize=9, colors=NAVY)
            ax.tick_params(axis="x", labelsize=8, colors="#8797A8")
            ax.grid(axis="x", color="#EAF0F5", linewidth=.8)
            ax.set_axisbelow(True)
            max_val = max(vals) if max(vals) > 0 else 1
            for bar in bars:
                ax.text(
                    bar.get_width()+max_val*.02,
                    bar.get_y()+bar.get_height()/2,
                    str(int(bar.get_width())),
                    va="center", fontsize=9, color=NAVY, fontweight="bold"
                )
            ax.set_xlim(0, max_val*1.2)
            plt.tight_layout()
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)
    with right:
        with st.container(border=True):
            st.subheader("Komposisi Tingkat Risiko")
            st.caption("Persentase setiap kategori risiko terhadap seluruh data pipa.")
            fig, ax = plt.subplots(figsize=(6, 3.5))
            fig.patch.set_facecolor("white")
            vals = [tinggi, sedang, rendah]
            if sum(vals) > 0:
                ax.pie(
                    vals,
                    labels=["Tinggi", "Sedang", "Rendah"],
                    colors=[RED, ORANGE, GREEN],
                    startangle=90,
                    counterclock=False,
                    autopct="%1.1f%%",
                    pctdistance=.78,
                    labeldistance=1.12,
                    wedgeprops={"width":.36, "edgecolor":"white", "linewidth":3},
                    textprops={"fontsize":9, "color":NAVY}
                )
                ax.text(0, 0, f"{total}\nPIPA", ha="center", va="center", fontsize=16, fontweight="bold", color=NAVY)
            else:
                ax.text(0, 0, "Belum ada data", ha="center", va="center")
            ax.axis("equal")
            plt.tight_layout()
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)

# 7. DATA PIPA
elif menu == "Data Pipa":
    st.markdown('<div class="page-title">Data Jaringan Pipa</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Halaman ini menyajikan informasi karakteristik jaringan pipa distribusi air bersih. Pengguna dapat mencari data berdasarkan ID pipa atau wilayah serta menyaring data berdasarkan kategori tingkat risiko.</div>', unsafe_allow_html=True)
    c1, c2 = st.columns([2, 1])
    with c1:
        search_text = st.text_input("Cari ID Pipa atau Wilayah", placeholder="Contoh: P001 atau Wilayah A")
    with c2:
        risk_filter = st.selectbox("Filter Risiko", ["Semua", "Tinggi", "Sedang", "Rendah"])
    shown = data.copy()
    if search_text:
        by_id = shown["id_pipa"].astype(str).str.contains(search_text, case=False, na=False)
        by_area = shown["wilayah"].astype(str).str.contains(search_text, case=False, na=False)
        shown = shown[by_id | by_area]
    if risk_filter != "Semua":
        shown = shown[shown["risiko_kebocoran"] == risk_filter]
    st.dataframe(shown, hide_index=True, use_container_width=True, height=480)
    st.caption(f"Jumlah data ditampilkan: {len(shown)} dari {total} data.")

# 8. PREDIKSI RISIKO
elif menu == "Prediksi Risiko":
    st.markdown('<div class="page-title">Prediksi Risiko Kebocoran Pipa</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Masukkan karakteristik pipa untuk memperoleh klasifikasi tingkat risiko dan rekomendasi pemeriksaan.</div>', unsafe_allow_html=True)

    with st.container(border=True):
        st.subheader("Informasi Karakteristik Pipa")
        with st.form("form_prediksi"):
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**1. Usia Pipa (tahun)**")
                st.caption("Lama pipa telah digunakan sejak pertama kali dipasang.")
                usia = st.number_input("Usia pipa", min_value=0, max_value=100, value=10, label_visibility="collapsed")

                st.markdown("**2. Jenis Material Pipa**")
                st.caption("Bahan utama yang digunakan untuk membuat pipa.")
                jenis = st.selectbox("Material pipa", ["PVC", "Besi", "HDPE"], label_visibility="collapsed")

                st.markdown("**3. Diameter Pipa (mm)**")
                st.caption("Ukuran garis tengah pipa dalam satuan milimeter.")
                diameter = st.number_input("Diameter pipa", min_value=1, max_value=1000, value=100, label_visibility="collapsed")

            with c2:
                st.markdown("**4. Tekanan Air (bar)**")
                st.caption("Besarnya tekanan air di dalam jaringan pipa.")
                tekanan = st.number_input("Tekanan air", min_value=0.0, max_value=20.0, value=3.0, step=.1, label_visibility="collapsed")

                st.markdown("**5. Riwayat Kebocoran (kali)**")
                st.caption("Jumlah kejadian kebocoran yang pernah tercatat.")
                riwayat = st.number_input("Riwayat kebocoran", min_value=0, max_value=100, value=0, label_visibility="collapsed")

                st.markdown("**6. Kondisi Fisik Pipa**")
                st.caption("Kondisi berdasarkan hasil pemeriksaan atau pengamatan.")
                kondisi = st.selectbox("Kondisi fisik", ["Baik", "Sedang", "Buruk"], label_visibility="collapsed")

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
            result = str(model.predict(new_pipe)[0])
            st.session_state["hasil_prediksi_pipa"] = {
                "hasil": result,
                "usia": usia,
                "jenis": jenis,
                "diameter": diameter,
                "tekanan": tekanan,
                "riwayat": riwayat,
                "kondisi": kondisi
            }
        except Exception as error:
            st.error(f"Prediksi gagal dilakukan: {error}")
            st.stop()

    if "hasil_prediksi_pipa" in st.session_state:
        h = st.session_state["hasil_prediksi_pipa"]
        kategori = h["hasil"]
        st.divider()
        st.header("Hasil Analisis Prediksi")

        if kategori == "Tinggi":
            st.error("RISIKO TINGGI")
            penjelasan = (
                "Model mengelompokkan karakteristik pipa ke kategori risiko tinggi. "
                "Pipa sebaiknya diprioritaskan untuk pemeriksaan lapangan dan pemantauan."
            )
            dampak = [
                "Kehilangan air bersih akibat air keluar dari jaringan pipa.",
                "Penurunan tekanan yang dapat mengganggu distribusi kepada pelanggan.",
                "Gangguan pelayanan selama proses pemeriksaan atau perbaikan.",
                "Peningkatan kebutuhan biaya perbaikan dan pemeliharaan."
            ]
            rekomendasi = [
                "Prioritaskan pemeriksaan badan pipa, sambungan, dan fitting.",
                "Periksa kembali lokasi yang pernah mengalami kebocoran.",
                "Pantau perubahan tekanan dan aliran air pada jaringan.",
                "Lakukan pemeriksaan kebocoran di lapangan jika ditemukan indikasi."
            ]

        elif kategori == "Sedang":
            st.warning("RISIKO SEDANG")
            penjelasan = (
                "Model mengelompokkan karakteristik pipa ke kategori risiko sedang. "
                "Pipa perlu dipantau secara berkala untuk mengetahui perubahan kondisi "
                "yang dapat meningkatkan kebutuhan pemeliharaan."
            )
            dampak = [
                "Kemungkinan munculnya rembesan atau kebocoran pada bagian pipa.",
                "Perubahan tekanan yang dapat memengaruhi kelancaran distribusi air.",
                "Peningkatan kebutuhan pemeriksaan dan pemeliharaan jaringan."
            ]
            rekomendasi = [
                "Jadwalkan pemeriksaan kondisi fisik pipa secara berkala.",
                "Periksa sambungan dan lokasi yang pernah diperbaiki.",
                "Bandingkan tekanan air dengan standar operasional jaringan.",
                "Catat setiap perubahan kondisi untuk menentukan tindak lanjut."
            ]

        elif kategori == "Rendah":
            st.success("RISIKO RENDAH")
            penjelasan = (
                "Model mengelompokkan karakteristik pipa ke kategori risiko rendah. "
                "Pipa dapat mengikuti jadwal pemeriksaan rutin, dengan tetap memperhatikan "
                "perubahan kondisi di lapangan."
            )
            dampak = [
                "Risiko gangguan distribusi tetap dapat muncul apabila kondisi pipa berubah.",
                "Kerusakan yang tidak terdeteksi dapat berkembang apabila pemeriksaan diabaikan."
            ]
            rekomendasi = [
                "Lanjutkan pemeriksaan rutin sesuai jadwal pemeliharaan.",
                "Pastikan badan pipa dan sambungan tetap dalam kondisi baik.",
                "Pantau tekanan dan aliran air secara berkala.",
                "Catat perubahan kondisi sebagai bahan evaluasi berikutnya."
            ]
        else:
            st.error(f"Kategori hasil model tidak dikenali: {kategori}")
            st.stop()

        st.subheader("Penjelasan Hasil")
        st.write(penjelasan)

        st.subheader("Faktor yang Perlu Diperhatikan")
        faktor = []

        if h["kondisi"] == "Buruk":
            faktor.append(
                "Kondisi fisik tercatat buruk. Periksa retakan, korosi, deformasi, "
                "kerusakan permukaan, dan sambungan pipa."
            )
        elif h["kondisi"] == "Sedang":
            faktor.append(
                "Kondisi fisik tercatat sedang. Perhatikan perubahan permukaan, "
                "sambungan, serta tanda penurunan kondisi."
            )
        else:
            faktor.append(
                "Kondisi fisik tercatat baik. Pemeriksaan rutin tetap diperlukan "
                "untuk memastikan kondisi sebenarnya."
            )

        if h["riwayat"] > 0:
            faktor.append(
                f"Terdapat riwayat kebocoran {h['riwayat']} kali. "
                "Periksa kembali lokasi dan sambungan yang pernah diperbaiki."
            )
        else:
            faktor.append(
                "Tidak ada riwayat kebocoran yang dimasukkan. Pastikan catatan "
                "pemeriksaan sebelumnya telah diperiksa."
            )

        faktor.append(
            f"Usia pipa tercatat {h['usia']} tahun. Bandingkan dengan "
            "umur rencana dan spesifikasi material pipa."
        )

        if h["jenis"] == "Besi":
            faktor.append(
                "Material besi: periksa kemungkinan korosi, karat, dan kerusakan sambungan."
            )
        elif h["jenis"] == "PVC":
            faktor.append(
                "Material PVC: periksa kemungkinan retakan, kerusakan fisik, dan sambungan."
            )
        else:
            faktor.append(
                "Material HDPE: periksa kondisi sambungan, fitting, deformasi, dan permukaan pipa."
            )

        faktor.append(
            f"Diameter tercatat {h['diameter']} mm. Pastikan nilai ini sesuai "
            "dengan spesifikasi jaringan dan catatan teknis."
        )
        faktor.append(
            f"Tekanan air tercatat {h['tekanan']:.1f} bar. Bandingkan dengan "
            "tekanan desain dan kondisi operasional jaringan."
        )

        for item in faktor:
            st.markdown(f"- {item}")

        # PERINGATAN RENTANG INPUT
        ranges = {
            "Usia pipa": ("usia_pipa", h["usia"]),
            "Diameter pipa": ("diameter_mm", h["diameter"]),
            "Tekanan air": ("tekanan_bar", h["tekanan"]),
            "Riwayat kebocoran": ("riwayat_kebocoran", h["riwayat"])
        }

        outside = []
        for label, (column, value) in ranges.items():
            minimum = pd.to_numeric(data[column], errors="coerce").min()
            maximum = pd.to_numeric(data[column], errors="coerce").max()

            if pd.notna(minimum) and pd.notna(maximum):
                if value < minimum or value > maximum:
                    outside.append(
                        f"{label}: nilai {value} berada di luar rentang "
                        f"data pelatihan {minimum:g}–{maximum:g}. "
                        "Pastikan satuan dan nilai input benar."
                    )

        if outside:
            st.warning(
                "Ada nilai masukan di luar rentang data yang digunakan "
                "untuk melatih model. Hasil perlu ditafsirkan dengan hati-hati."
            )
            for item in outside:
                st.markdown(f"- {item}")

        st.subheader("Potensi Dampak Jika Terjadi Kebocoran")
        for item in dampak:
            st.markdown(f"- {item}")

        st.subheader("Rekomendasi Pemeriksaan")
        for nomor, item in enumerate(rekomendasi, start=1):
            st.markdown(f"{nomor}. {item}")

        st.subheader("Ringkasan Data yang Dianalisis")
        ringkasan = pd.DataFrame({
            "Karakteristik": [
                "Usia Pipa",
                "Jenis Material",
                "Diameter Pipa",
                "Tekanan Air",
                "Riwayat Kebocoran",
                "Kondisi Fisik"
            ],
            "Nilai": [
                f"{h['usia']} tahun",
                h["jenis"],
                f"{h['diameter']} mm",
                f"{h['tekanan']:.1f} bar",
                f"{h['riwayat']} kali",
                h["kondisi"]
            ]
        })
        st.dataframe(ringkasan, hide_index=True, use_container_width=True)

        st.caption(
            "Hasil merupakan klasifikasi awal berdasarkan data yang dimasukkan. "
            "Kategori risiko bukan bukti bahwa kebocoran telah terjadi. "
            "Potensi dampak merupakan kemungkinan apabila kebocoran benar-benar terjadi. "
            "Keputusan teknis tetap memerlukan pemeriksaan lapangan."
        )

# 9. LAPORAN
elif menu == "Laporan":
    st.markdown('<div class="page-title">Laporan Data Jaringan Pipa</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Halaman ini menyajikan ringkasan data jaringan berdasarkan kategori risiko serta menyediakan fasilitas untuk mengunduh data dalam format CSV.</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Data Pipa", total)
    c2.metric("Risiko Tinggi", tinggi)
    c3.metric("Risiko Rendah", rendah)
    st.subheader("Pratinjau Data")
    st.dataframe(data.head(10), hide_index=True, use_container_width=True)
    csv_data = data.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Unduh Laporan Data Pipa (CSV)",
        data=csv_data,
        file_name="laporan_data_pipa.csv",
        mime="text/csv",
        use_container_width=True
    )
