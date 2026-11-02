import io
import pickle
from pathlib import Path
from datetime import date, datetime
from xml.sax.saxutils import escape

import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

from docx import Document
from docx.shared import Pt, Mm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)


# ============================================================
# 1. KONFIGURASI APLIKASI
# ============================================================

st.set_page_config(
    page_title="PERUMDA AIR MINUM X",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE = Path(__file__).parent
DATA_DIR = BASE / "data"

DATA_FILE = DATA_DIR / "data_pipa.csv"
MODEL_FILE = BASE / "model" / "random_forest.pkl"

PREDICTION_FILE = DATA_DIR / "riwayat_prediksi.csv"
HANDLING_FILE = DATA_DIR / "riwayat_penanganan.csv"

NAVY = "#12365A"
BLUE = "#0878C9"
RED = "#E34B55"
ORANGE = "#E99A27"
GREEN = "#15966B"

RISK_CATEGORIES = [
    "Tinggi",
    "Sedang",
    "Rendah"
]

FEATURES = [
    "usia_pipa",
    "jenis_pipa",
    "diameter_mm",
    "tekanan_bar",
    "riwayat_kebocoran",
    "kondisi_pipa"
]

STATUSES = [
    "Belum ditangani",
    "Menunggu pemeriksaan",
    "Sedang diperiksa",
    "Dalam perbaikan",
    "Selesai ditangani",
    "Tidak ditemukan kebocoran"
]

BASE_COLUMNS = [
    "id_pipa",
    "wilayah",
    "usia_pipa",
    "jenis_pipa",
    "diameter_mm",
    "tekanan_bar",
    "riwayat_kebocoran",
    "kondisi_pipa",
    "risiko_kebocoran",
    "hasil_prediksi_terakhir",
    "tanggal_prediksi",
    "status_penanganan",
    "petugas_penanganan",
    "tanggal_penanganan",
    "catatan_penanganan"
]


# ============================================================
# 2. DESAIN VISUAL
# ============================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: Inter, sans-serif;
}

.stApp {
    background: #F3F6FA;
    color: #183B5C;
}

.block-container {
    max-width: 1450px;
    padding-top: 1.35rem;
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

section[data-testid="stSidebar"] > div {
    background: transparent;
}

section[data-testid="stSidebar"] * {
    color: white;
}

section[data-testid="stSidebar"] [data-testid="stRadio"] label {
    background: rgba(255,255,255,0.09);
    padding: 10px 12px;
    border-radius: 9px;
    margin: 4px 0;
}

section[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    background: rgba(255,255,255,0.18);
}

/* HEADER DASHBOARD */

.hero {
    background: linear-gradient(
        115deg,
        #12365A 0%,
        #075B9C 55%,
        #0878C9 100%
    );
    padding: 30px;
    border-radius: 17px;
    color: white;
    margin-bottom: 25px;
    box-shadow: 0 9px 25px rgba(18,54,90,0.15);
}

.hero-brand {
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 18px;
}

.hero-drop {
    font-size: 44px;
    line-height: 1;
}

.hero-name {
    font-size: 14px;
    color: white;
    font-weight: 800;
    letter-spacing: 1.4px;
}

.hero-caption {
    font-size: 10px;
    color: #D5E9FA;
    letter-spacing: 1px;
    margin-top: 5px;
}

.hero h1 {
    color: white;
    font-size: 27px;
    font-weight: 800;
    line-height: 1.35;
    margin: 0 0 11px;
}

.hero p {
    color: #E5F2FC;
    font-size: 13px;
    line-height: 1.8;
    margin: 0;
    max-width: 1100px;
}

/* JUDUL HALAMAN */

.page-title {
    font-size: 25px;
    color: #183B5C;
    font-weight: 800;
    margin-bottom: 4px;
}

.page-subtitle {
    font-size: 13px;
    color: #71849A;
    line-height: 1.7;
    margin-bottom: 19px;
}

.section-title {
    font-size: 23px;
    color: #183B5C;
    font-weight: 800;
    margin-bottom: 4px;
}

.section-subtitle {
    font-size: 13px;
    color: #71849A;
    line-height: 1.7;
    margin-bottom: 18px;
}

/* KARTU STATISTIK */

.metric-card {
    background: white;
    border: 1px solid #E3EAF1;
    border-radius: 13px;
    padding: 17px;
    min-height: 116px;
    box-shadow: 0 3px 12px rgba(20,50,80,.04);
}

.metric-label {
    color: #71849A;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: .5px;
}

.metric-value {
    font-size: 29px;
    font-weight: 800;
    line-height: 1.2;
    margin-top: 11px;
}

.metric-note {
    font-size: 11px;
    color: #8A9BAD;
    margin-top: 6px;
}

/* TABEL */

div[data-testid="stDataFrame"] {
    border: 1px solid #E3EAF1;
    border-radius: 10px;
    overflow: hidden;
}

/* FORM */

div[data-testid="stMain"] [data-testid="stWidgetLabel"] {
    color: #183B5C !important;
}

div[data-testid="stMain"] input {
    background: white !important;
    color: #183B5C !important;
    border-color: #CBD5E1 !important;
}

div[data-testid="stMain"] textarea {
    background: white !important;
    color: #183B5C !important;
    border-color: #CBD5E1 !important;
}

div[data-testid="stMain"] [data-baseweb="select"] > div {
    background: white !important;
    color: #183B5C !important;
    border-color: #CBD5E1 !important;
}

div[data-testid="stMain"] [data-baseweb="select"] span {
    color: #183B5C !important;
}

div[data-testid="stForm"] {
    background: white;
    border-radius: 12px;
}

/* TOMBOL */

.stButton button,
.stDownloadButton button,
div[data-testid="stFormSubmitButton"] button {
    background: #0878C9 !important;
    color: white !important;
    border: 0 !important;
    border-radius: 8px !important;
    font-weight: 600;
    min-height: 40px;
}

.stButton button:hover,
.stDownloadButton button:hover {
    background: #12365A !important;
    color: white !important;
}

/* RESPONSIVE HP */

@media(max-width:700px) {

    .block-container {
        padding: 1rem .8rem 1.5rem;
    }

    .hero {
        padding: 21px 17px;
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

    .page-title,
    .section-title {
        font-size: 21px;
    }

    .metric-card {
        padding: 13px;
        min-height: 102px;
    }

    .metric-value {
        font-size: 25px;
    }

}

</style>
""", unsafe_allow_html=True)


# ============================================================
# 3. FUNGSI DATA
# ============================================================

@st.cache_data(show_spinner=False)
def read_pipe_data():

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"File dataset tidak ditemukan: {DATA_FILE}"
        )

    return pd.read_csv(
        DATA_FILE,
        keep_default_na=False
    )


@st.cache_resource(show_spinner=False)
def read_model():

    if not MODEL_FILE.exists():
        raise FileNotFoundError(
            f"File model tidak ditemukan: {MODEL_FILE}"
        )

    with open(MODEL_FILE, "rb") as file:
        return pickle.load(file)


def normalize_data(frame):

    frame = frame.copy()

    defaults = {
        "wilayah": "",
        "usia_pipa": 0,
        "jenis_pipa": "PVC",
        "diameter_mm": 100,
        "tekanan_bar": 3.0,
        "riwayat_kebocoran": 0,
        "kondisi_pipa": "Baik",
        "risiko_kebocoran": "Belum diklasifikasikan",
        "hasil_prediksi_terakhir": "",
        "tanggal_prediksi": "",
        "status_penanganan": "Belum ditangani",
        "petugas_penanganan": "",
        "tanggal_penanganan": "",
        "catatan_penanganan": ""
    }

    for column, default in defaults.items():

        if column not in frame.columns:
            frame[column] = default

        frame[column] = frame[column].fillna(default)

    for column in [
        "id_pipa",
        "wilayah",
        "jenis_pipa",
        "kondisi_pipa",
        "risiko_kebocoran",
        "hasil_prediksi_terakhir",
        "tanggal_prediksi",
        "status_penanganan",
        "petugas_penanganan",
        "tanggal_penanganan",
        "catatan_penanganan"
    ]:

        frame[column] = (
            frame[column]
            .astype(str)
            .replace({
                "nan": "",
                "None": "",
                "NaN": ""
            })
        )

    frame["id_pipa"] = frame["id_pipa"].astype(str)

    for column in [
        "usia_pipa",
        "diameter_mm",
        "riwayat_kebocoran"
    ]:

        frame[column] = pd.to_numeric(
            frame[column],
            errors="coerce"
        ).fillna(0).astype(int)

    frame["tekanan_bar"] = pd.to_numeric(
        frame["tekanan_bar"],
        errors="coerce"
    ).fillna(0.0).astype(float)

    frame.loc[
        frame["status_penanganan"] == "",
        "status_penanganan"
    ] = "Belum ditangani"

    return frame


def current_view(frame):

    """
    Menentukan kategori risiko yang digunakan saat ini.

    Hasil prediksi terbaru digunakan terlebih dahulu.
    Jika belum ada prediksi, gunakan label dataset.
    """

    result = normalize_data(frame)

    dataset_label = result["risiko_kebocoran"].astype(str)

    latest_prediction = (
        result["hasil_prediksi_terakhir"].astype(str)
    )

    valid_prediction = latest_prediction.isin(
        RISK_CATEGORIES
    )

    valid_dataset_label = dataset_label.isin(
        RISK_CATEGORIES
    )

    result["label_risiko_dataset"] = dataset_label

    result["kategori_risiko_terkini"] = "Belum diklasifikasikan"

    result.loc[
        valid_dataset_label,
        "kategori_risiko_terkini"
    ] = dataset_label[valid_dataset_label]

    result.loc[
        valid_prediction,
        "kategori_risiko_terkini"
    ] = latest_prediction[valid_prediction]

    result["sumber_kategori_risiko"] = "Label Dataset"

    result.loc[
        valid_prediction,
        "sumber_kategori_risiko"
    ] = "Prediksi Terbaru"

    return result


def save_pipe_data(frame):

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    frame = normalize_data(frame)

    view_columns = [
        "label_risiko_dataset",
        "kategori_risiko_terkini",
        "sumber_kategori_risiko"
    ]

    frame = frame.drop(
        columns=view_columns,
        errors="ignore"
    )

    frame.to_csv(
        DATA_FILE,
        index=False
    )

    read_pipe_data.clear()


def append_record(path, record):

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    new_record = pd.DataFrame([record])

    if path.exists():

        old_record = pd.read_csv(
            path,
            keep_default_na=False
        )

        new_record = pd.concat(
            [old_record, new_record],
            ignore_index=True
        )

    new_record.to_csv(
        path,
        index=False
    )


def notify(kind, message):

    st.session_state["flash"] = (
        kind,
        message
    )


def next_id(frame):

    if frame.empty:
        return "P001"

    numbers = pd.to_numeric(
        frame["id_pipa"]
        .astype(str)
        .str.extract(r"(\d+)$")[0],
        errors="coerce"
    ).dropna()

    number = (
        int(numbers.max()) + 1
        if not numbers.empty
        else 1
    )

    return f"P{number:03d}"


def make_record(row):

    return {
        "id_pipa": str(row["id_pipa"]),
        "wilayah": str(row["wilayah"]),
        "usia_pipa": int(row["usia_pipa"]),
        "jenis_pipa": str(row["jenis_pipa"]),
        "diameter_mm": int(row["diameter_mm"]),
        "tekanan_bar": float(row["tekanan_bar"]),
        "riwayat_kebocoran": int(row["riwayat_kebocoran"]),
        "kondisi_pipa": str(row["kondisi_pipa"])
    }


def predict_pipe(record, model):

    features = pd.DataFrame(
        [
            {
                column: record[column]
                for column in FEATURES
            }
        ],
        columns=FEATURES
    )

    return str(model.predict(features)[0])


# ============================================================
# 4. PENJELASAN HASIL PREDIKSI
# ============================================================

def build_guidance(category, record):

    if category == "Tinggi":

        explanation = (
            "Model mengelompokkan karakteristik pipa ke kategori "
            "risiko tinggi. Pipa perlu diprioritaskan untuk pemeriksaan "
            "lapangan guna memastikan kondisi fisik dan mengetahui "
            "ada atau tidaknya indikasi kebocoran."
        )

        priority = (
            "Prioritas tinggi: jadwalkan pemeriksaan sesuai prosedur "
            "operasional dan urgensi temuan lapangan."
        )

    elif category == "Sedang":

        explanation = (
            "Model mengelompokkan karakteristik pipa ke kategori "
            "risiko sedang. Pipa memerlukan pemantauan dan pemeriksaan "
            "terencana untuk mengetahui perubahan kondisi."
        )

        priority = (
            "Prioritas menengah: lakukan pemeriksaan berkala dan "
            "tingkatkan pemantauan jika ditemukan indikasi kerusakan."
        )

    else:

        explanation = (
            "Model mengelompokkan karakteristik pipa ke kategori "
            "risiko rendah. Pipa dapat mengikuti jadwal pemeriksaan "
            "rutin dengan tetap memperhatikan perubahan kondisi "
            "jaringan di lapangan."
        )

        priority = (
            "Prioritas rutin: lakukan pemantauan sesuai jadwal "
            "pemeliharaan yang berlaku."
        )

    impacts = [
        (
            "Kehilangan air bersih: air keluar dari jaringan sehingga "
            "volume air yang dapat didistribusikan berkurang."
        ),
        (
            "Penurunan tekanan air: tekanan jaringan dapat menurun "
            "dan mengganggu kelancaran aliran kepada pelanggan."
        ),
        (
            "Gangguan pelayanan: pelanggan di sekitar lokasi dapat "
            "mengalami gangguan selama proses perbaikan."
        ),
        (
            "Gangguan lingkungan: kebocoran besar atau berkepanjangan "
            "dapat menyebabkan genangan, pengikisan tanah, atau "
            "kerusakan permukaan jalan."
        ),
        (
            "Biaya operasional: perusahaan dapat memerlukan biaya "
            "untuk menemukan lokasi kebocoran dan memperbaiki pipa."
        )
    ]

    actions = [
        priority,
        (
            "Pemeriksaan jalur: telusuri jalur distribusi dan amati "
            "genangan, tanah basah, rembesan, atau penurunan "
            "permukaan tanah di sekitar lokasi."
        ),
        (
            "Pemeriksaan badan pipa: amati retakan, korosi, perubahan "
            "bentuk, kerusakan permukaan, dan tanda keausan."
        )
    ]

    material = record["jenis_pipa"]

    if material == "Besi":

        actions.append(
            "Material besi: periksa karat, korosi, kondisi lapisan "
            "pelindung, sambungan, dan bagian yang berpotensi "
            "mengalami penipisan material."
        )

    elif material == "PVC":

        actions.append(
            "Material PVC: periksa retakan, pecahan, perubahan "
            "bentuk, kerusakan akibat benturan, dan kondisi sambungan."
        )

    else:

        actions.append(
            "Material HDPE: periksa sambungan las, fitting, "
            "perubahan bentuk, goresan, dan kerusakan permukaan pipa."
        )

    count = int(record["riwayat_kebocoran"])

    if count > 0:

        actions.append(
            f"Riwayat kebocoran: terdapat catatan {count} kali. "
            "Telusuri lokasi perbaikan sebelumnya dan periksa "
            "sambungan di sekitarnya."
        )

    else:

        actions.append(
            "Riwayat kebocoran: tinjau catatan perbaikan dan kejadian "
            "sebelumnya. Tidak adanya catatan bukan jaminan pipa "
            "belum pernah bocor."
        )

    actions.append(
        f"Usia pipa: tercatat {record['usia_pipa']} tahun. "
        "Bandingkan dengan umur rencana material dan jadwal "
        "pemeliharaan perusahaan."
    )

    actions.append(
        f"Tekanan air: nilai masukan {record['tekanan_bar']:.1f} bar. "
        "Ukur tekanan aktual dan bandingkan dengan spesifikasi "
        "teknis serta standar operasional jaringan."
    )

    actions.append(
        "Konfirmasi dan dokumentasi: jika ditemukan indikasi, "
        "lakukan pemeriksaan lanjutan dengan metode yang sesuai. "
        "Catat ID pipa, lokasi, tanggal, hasil pengukuran, foto "
        "temuan, dan tindak lanjut."
    )

    return explanation, impacts, actions


def show_prediction(result, reference_data):

    category = result["hasil"]

    st.divider()
    st.subheader("Hasil Analisis Prediksi")

    if category == "Tinggi":
        st.error("RISIKO TINGGI")

    elif category == "Sedang":
        st.warning("RISIKO SEDANG")

    else:
        st.success("RISIKO RENDAH")

    explanation, impacts, actions = build_guidance(
        category,
        result
    )

    st.markdown("#### Penjelasan Hasil")
    st.write(explanation)

    st.markdown("#### Faktor yang Perlu Diperhatikan")

    condition = result["kondisi_pipa"]

    if condition == "Buruk":

        st.markdown(
            "- Kondisi fisik tercatat buruk. Periksa retakan, "
            "korosi, deformasi, kerusakan permukaan, dan sambungan pipa."
        )

    elif condition == "Sedang":

        st.markdown(
            "- Kondisi fisik tercatat sedang. Perhatikan perubahan "
            "permukaan, sambungan, dan tanda penurunan kondisi."
        )

    else:

        st.markdown(
            "- Kondisi fisik tercatat baik. Pemeriksaan rutin tetap "
            "diperlukan untuk memastikan kondisi sebenarnya."
        )

    count = int(result["riwayat_kebocoran"])

    if count > 0:

        st.markdown(
            f"- Terdapat riwayat kebocoran {count} kali. "
            "Periksa kembali lokasi dan sambungan yang pernah diperbaiki."
        )

    else:

        st.markdown(
            "- Tidak ada riwayat kebocoran yang dimasukkan. "
            "Pastikan catatan pemeriksaan sebelumnya telah ditinjau."
        )

    material_notes = {
        "Besi": (
            "Material besi: periksa kemungkinan korosi, karat, "
            "dan kerusakan sambungan."
        ),
        "PVC": (
            "Material PVC: periksa kemungkinan retakan, "
            "kerusakan fisik, dan kondisi sambungan."
        ),
        "HDPE": (
            "Material HDPE: periksa kondisi sambungan, fitting, "
            "deformasi, dan permukaan pipa."
        )
    }

    st.markdown(
        f"- Usia pipa tercatat {result['usia_pipa']} tahun. "
        "Bandingkan dengan umur rencana dan spesifikasi material."
    )

    st.markdown(
        f"- {material_notes.get(result['jenis_pipa'], '')}"
    )

    st.markdown(
        f"- Diameter tercatat {result['diameter_mm']} mm. "
        "Pastikan sesuai spesifikasi jaringan."
    )

    st.markdown(
        f"- Tekanan tercatat {result['tekanan_bar']:.1f} bar. "
        "Bandingkan dengan tekanan desain dan kondisi operasional."
    )

    ranges = {
        "Usia pipa": (
            "usia_pipa",
            float(result["usia_pipa"])
        ),
        "Diameter pipa": (
            "diameter_mm",
            float(result["diameter_mm"])
        ),
        "Tekanan air": (
            "tekanan_bar",
            float(result["tekanan_bar"])
        ),
        "Riwayat kebocoran": (
            "riwayat_kebocoran",
            float(result["riwayat_kebocoran"])
        )
    }

    outside = []

    for label, (column, value) in ranges.items():

        minimum = pd.to_numeric(
            reference_data[column],
            errors="coerce"
        ).min()

        maximum = pd.to_numeric(
            reference_data[column],
            errors="coerce"
        ).max()

        if (
            pd.notna(minimum)
            and pd.notna(maximum)
            and (value < minimum or value > maximum)
        ):

            outside.append(
                f"{label}: nilai {value:g} berada di luar "
                f"rentang data pelatihan {minimum:g}–{maximum:g}."
            )

    if outside:

        st.warning(
            "Ada nilai masukan di luar rentang data pelatihan. "
            "Tafsirkan hasil dengan hati-hati."
        )

        for item in outside:
            st.markdown(f"- {item}")

    st.markdown("#### Potensi Dampak Jika Terjadi Kebocoran")

    for item in impacts:
        st.markdown(f"- {item}")

    st.markdown("#### Rekomendasi Pemeriksaan")

    for number, item in enumerate(actions, 1):
        st.markdown(f"{number}. {item}")

    summary = pd.DataFrame({
        "Karakteristik": [
            "ID Pipa",
            "Wilayah",
            "Usia",
            "Material",
            "Diameter",
            "Tekanan",
            "Riwayat Kebocoran",
            "Kondisi"
        ],
        "Nilai": [
            result.get("id_pipa", "Pipa baru/manual"),
            result.get("wilayah", "Belum ditentukan"),
            f"{result['usia_pipa']} tahun",
            result["jenis_pipa"],
            f"{result['diameter_mm']} mm",
            f"{result['tekanan_bar']:.1f} bar",
            f"{result['riwayat_kebocoran']} kali",
            result["kondisi_pipa"]
        ]
    })

    st.markdown("#### Ringkasan Data yang Dianalisis")

    st.dataframe(
        summary,
        hide_index=True,
        use_container_width=True
    )

    st.caption(
        "Kategori risiko merupakan hasil klasifikasi model, bukan bukti "
        "kebocoran telah terjadi. Faktor di atas adalah hal yang perlu "
        "diperiksa, bukan penyebab yang dipastikan oleh model. "
        "Keputusan teknis tetap memerlukan pemeriksaan lapangan."
    )


# ============================================================
# 5. FUNGSI PEMBUATAN LAPORAN WORD
# ============================================================

def create_word_report(frame):

    report = current_view(frame)

    doc = Document()

    section = doc.sections[0]

    section.top_margin = Mm(20)
    section.bottom_margin = Mm(20)
    section.left_margin = Mm(25)
    section.right_margin = Mm(25)

    normal = doc.styles["Normal"]

    normal.font.name = "Times New Roman"
    normal.font.size = Pt(11)
    normal.font.color.rgb = RGBColor(0, 0, 0)

    for style_name in [
        "Heading 1",
        "Heading 2"
    ]:

        style = doc.styles[style_name]
        style.font.name = "Times New Roman"
        style.font.color.rgb = RGBColor(0, 0, 0)

    def write_cell(cell, value, bold=False):

        cell.text = ""

        cell.vertical_alignment = (
            WD_CELL_VERTICAL_ALIGNMENT.CENTER
        )

        paragraph = cell.paragraphs[0]

        run = paragraph.add_run(str(value))
        run.bold = bold
        run.font.name = "Times New Roman"
        run.font.size = Pt(10)
        run.font.color.rgb = RGBColor(0, 0, 0)

    def make_table(headers, rows):

        table = doc.add_table(
            rows=1,
            cols=len(headers)
        )

        table.style = "Table Grid"
        table.alignment = WD_TABLE_ALIGNMENT.CENTER

        for i, header in enumerate(headers):
            write_cell(
                table.rows[0].cells[i],
                header,
                True
            )

        for row in rows:

            cells = table.add_row().cells

            for i, value in enumerate(row):
                write_cell(cells[i], value)

        return table

    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    run = title.add_run(
        "LAPORAN MONITORING JARINGAN PIPA"
    )

    run.bold = True
    run.font.name = "Times New Roman"
    run.font.size = Pt(16)
    run.font.color.rgb = RGBColor(0, 0, 0)

    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER

    run = subtitle.add_run("PERUMDA AIR MINUM X")
    run.bold = True
    run.font.name = "Times New Roman"
    run.font.size = Pt(13)
    run.font.color.rgb = RGBColor(0, 0, 0)

    doc.add_paragraph(
        "Tanggal pembuatan: "
        + datetime.now().strftime("%d-%m-%Y %H:%M")
    )

    total = len(report)

    high = int(
        (report["kategori_risiko_terkini"] == "Tinggi").sum()
    )

    medium = int(
        (report["kategori_risiko_terkini"] == "Sedang").sum()
    )

    low = int(
        (report["kategori_risiko_terkini"] == "Rendah").sum()
    )

    unclassified = int(
        (
            report["kategori_risiko_terkini"]
            == "Belum diklasifikasikan"
        ).sum()
    )

    in_progress = int(
        report["status_penanganan"].isin([
            "Menunggu pemeriksaan",
            "Sedang diperiksa",
            "Dalam perbaikan"
        ]).sum()
    )

    completed = int(
        (
            report["status_penanganan"]
            == "Selesai ditangani"
        ).sum()
    )

    unhandled = int(
        (
            report["status_penanganan"]
            == "Belum ditangani"
        ).sum()
    )

    # RINGKASAN

    doc.add_heading(
        "1. Ringkasan Eksekutif",
        level=1
    )

    doc.add_paragraph(
        f"Laporan ini merangkum {total} data pipa yang tercatat "
        f"dalam sistem. Berdasarkan kategori risiko terkini, "
        f"terdapat {high} pipa risiko tinggi, {medium} pipa risiko "
        f"sedang, {low} pipa risiko rendah, dan {unclassified} "
        "pipa yang belum diklasifikasikan."
    )

    # DISTRIBUSI RISIKO

    doc.add_heading(
        "2. Distribusi Kategori Risiko",
        level=1
    )

    risk_rows = [
        [
            "Tinggi",
            high,
            f"{high / total * 100:.1f}%" if total else "0%"
        ],
        [
            "Sedang",
            medium,
            f"{medium / total * 100:.1f}%" if total else "0%"
        ],
        [
            "Rendah",
            low,
            f"{low / total * 100:.1f}%" if total else "0%"
        ],
        [
            "Belum diklasifikasikan",
            unclassified,
            (
                f"{unclassified / total * 100:.1f}%"
                if total else "0%"
            )
        ],
        [
            "Total",
            total,
            "100%" if total else "0%"
        ]
    ]

    make_table(
        [
            "Kategori Risiko",
            "Jumlah Pipa",
            "Persentase"
        ],
        risk_rows
    )

    # STATUS PENANGANAN

    doc.add_heading(
        "3. Status Pemeriksaan dan Penanganan",
        level=1
    )

    status_rows = []

    for status in STATUSES:

        count = int(
            (report["status_penanganan"] == status).sum()
        )

        status_rows.append([
            status,
            count
        ])

    make_table(
        [
            "Status Penanganan",
            "Jumlah Pipa"
        ],
        status_rows
    )

    doc.add_paragraph(
        f"Sebanyak {unhandled} pipa belum ditangani, "
        f"{in_progress} pipa masih dalam proses, dan "
        f"{completed} pipa telah selesai ditangani."
    )

    # DAFTAR PIPA PRIORITAS

    doc.add_heading(
        "4. Daftar Pipa yang Memerlukan Perhatian",
        level=1
    )

    priority = report[
        report["kategori_risiko_terkini"] == "Tinggi"
    ].head(30)

    priority_rows = []

    for _, row in priority.iterrows():

        priority_rows.append([
            row["id_pipa"],
            row["wilayah"],
            row["usia_pipa"],
            row["jenis_pipa"],
            row["kondisi_pipa"],
            row["status_penanganan"]
        ])

    if not priority_rows:

        priority_rows.append([
            "-", "-", "-", "-", "-", "-"
        ])

    make_table(
        [
            "ID Pipa",
            "Wilayah",
            "Usia",
            "Material",
            "Kondisi",
            "Status"
        ],
        priority_rows
    )

    doc.add_paragraph(
        "Daftar di atas menampilkan maksimal 30 pipa dengan "
        "kategori risiko tinggi sebagai bahan perhatian dan "
        "pemeriksaan."
    )

    # KESIMPULAN

    doc.add_heading(
        "5. Kesimpulan dan Rekomendasi",
        level=1
    )

    doc.add_paragraph(
        "Hasil pengelompokan risiko dapat digunakan untuk membantu "
        "menentukan prioritas pemantauan jaringan. Pipa dengan "
        "kategori risiko tinggi perlu diprioritaskan untuk "
        "pemeriksaan kondisi fisik, sambungan, tekanan air, "
        "dan riwayat kebocoran."
    )

    doc.add_paragraph(
        "Status penyelesaian penanganan perlu diperbarui berdasarkan "
        "hasil pemeriksaan petugas. Kategori risiko dari model "
        "merupakan hasil klasifikasi dan bukan bukti bahwa "
        "kebocoran telah terjadi."
    )

    # METODOLOGI

    doc.add_heading(
        "6. Catatan Metodologi",
        level=1
    )

    doc.add_paragraph(
        "Prototype awal menggunakan dataset simulasi untuk menguji "
        "fungsi aplikasi dan proses klasifikasi. Dataset tersebut "
        "belum mewakili data operasional asli perusahaan. Sebelum "
        "digunakan sebagai dasar keputusan teknis, model perlu "
        "diuji dan divalidasi menggunakan data jaringan serta hasil "
        "pemeriksaan lapangan yang sebenarnya."
    )

    # FOOTER

    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER

    run = footer.add_run(
        "PERUMDA AIR MINUM X | Laporan Monitoring Jaringan Pipa"
    )

    run.font.name = "Times New Roman"
    run.font.size = Pt(9)
    run.font.color.rgb = RGBColor(0, 0, 0)

    buffer = io.BytesIO()

    doc.save(buffer)

    return buffer.getvalue()


# ============================================================
# 6. FUNGSI PEMBUATAN LAPORAN PDF
# ============================================================

def create_pdf_report(frame):

    report = current_view(frame)

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=16 * mm,
        leftMargin=16 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleCustom",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=20,
        textColor=colors.HexColor(NAVY),
        alignment=TA_CENTER,
        spaceAfter=5
    )

    small_style = ParagraphStyle(
        "SmallCustom",
        parent=styles["BodyText"],
        fontSize=8,
        leading=11
    )

    section_style = ParagraphStyle(
        "SectionCustom",
        parent=styles["Heading2"],
        fontSize=11,
        textColor=colors.HexColor(NAVY),
        spaceBefore=10,
        spaceAfter=5
    )

    story = [
        Paragraph(
            "LAPORAN MONITORING JARINGAN PIPA",
            title_style
        ),
        Paragraph(
            "<b>PERUMDA AIR MINUM X</b>",
            styles["Heading3"]
        ),
        Paragraph(
            "Tanggal pembuatan: "
            + datetime.now().strftime("%d-%m-%Y %H:%M"),
            small_style
        ),
        Spacer(1, 7 * mm)
    ]

    total = len(report)

    high = int(
        (report["kategori_risiko_terkini"] == "Tinggi").sum()
    )

    medium = int(
        (report["kategori_risiko_terkini"] == "Sedang").sum()
    )

    low = int(
        (report["kategori_risiko_terkini"] == "Rendah").sum()
    )

    unclassified = int(
        (
            report["kategori_risiko_terkini"]
            == "Belum diklasifikasikan"
        ).sum()
    )

    unhandled = int(
        (
            report["status_penanganan"]
            == "Belum ditangani"
        ).sum()
    )

    in_progress = int(
        report["status_penanganan"].isin([
            "Menunggu pemeriksaan",
            "Sedang diperiksa",
            "Dalam perbaikan"
        ]).sum()
    )

    completed = int(
        (
            report["status_penanganan"]
            == "Selesai ditangani"
        ).sum()
    )

    # 1. RINGKASAN EKSEKUTIF

    story.append(
        Paragraph(
            "1. Ringkasan Eksekutif",
            section_style
        )
    )

    story.append(
        Paragraph(
            f"Laporan merangkum {total} data pipa. Berdasarkan "
            f"kategori risiko terkini, terdapat {high} pipa risiko "
            f"tinggi, {medium} risiko sedang, {low} risiko rendah, "
            f"dan {unclassified} pipa belum diklasifikasikan. "
            f"Status penanganan: {unhandled} belum ditangani, "
            f"{in_progress} dalam proses, dan {completed} "
            "selesai ditangani.",
            small_style
        )
    )

    # 2. DISTRIBUSI RISIKO

    story.append(
        Paragraph(
            "2. Distribusi Kategori Risiko",
            section_style
        )
    )

    risk_rows = [
        [
            "Kategori",
            "Jumlah Pipa",
            "Persentase"
        ],
        [
            "Tinggi",
            str(high),
            f"{high / total * 100:.1f}%" if total else "0%"
        ],
        [
            "Sedang",
            str(medium),
            f"{medium / total * 100:.1f}%" if total else "0%"
        ],
        [
            "Rendah",
            str(low),
            f"{low / total * 100:.1f}%" if total else "0%"
        ],
        [
            "Belum diklasifikasikan",
            str(unclassified),
            (
                f"{unclassified / total * 100:.1f}%"
                if total else "0%"
            )
        ],
        [
            "Total",
            str(total),
            "100%" if total else "0%"
        ]
    ]

    table = Table(
        risk_rows,
        colWidths=[
            65 * mm,
            40 * mm,
            40 * mm
        ]
    )

    table.setStyle(TableStyle([
        (
            "BACKGROUND",
            (0, 0),
            (-1, 0),
            colors.HexColor(NAVY)
        ),
        (
            "TEXTCOLOR",
            (0, 0),
            (-1, 0),
            colors.white
        ),
        (
            "FONTNAME",
            (0, 0),
            (-1, 0),
            "Helvetica-Bold"
        ),
        (
            "GRID",
            (0, 0),
            (-1, -1),
            .4,
            colors.HexColor("#D4DEE8")
        ),
        (
            "ROWBACKGROUNDS",
            (0, 1),
            (-1, -1),
            [
                colors.white,
                colors.HexColor("#F2F6FA")
            ]
        ),
        (
            "PADDING",
            (0, 0),
            (-1, -1),
            6
        ),
        (
            "ALIGN",
            (1, 1),
            (-1, -1),
            "CENTER"
        )
    ]))

    story.append(table)

    # 3. STATUS PENANGANAN

    story.append(
        Paragraph(
            "3. Status Pemeriksaan dan Penanganan",
            section_style
        )
    )

    status_rows = [
        [
            "Status",
            "Jumlah Pipa"
        ]
    ]

    for status in STATUSES:

        count = int(
            (report["status_penanganan"] == status).sum()
        )

        status_rows.append([
            status,
            str(count)
        ])

    status_table = Table(
        status_rows,
        colWidths=[
            100 * mm,
            45 * mm
        ]
    )

    status_table.setStyle(TableStyle([
        (
            "BACKGROUND",
            (0, 0),
            (-1, 0),
            colors.HexColor(NAVY)
        ),
        (
            "TEXTCOLOR",
            (0, 0),
            (-1, 0),
            colors.white
        ),
        (
            "FONTNAME",
            (0, 0),
            (-1, 0),
            "Helvetica-Bold"
        ),
        (
            "GRID",
            (0, 0),
            (-1, -1),
            .4,
            colors.HexColor("#D4DEE8")
        ),
        (
            "ROWBACKGROUNDS",
            (0, 1),
            (-1, -1),
            [
                colors.white,
                colors.HexColor("#F2F6FA")
            ]
        ),
        (
            "PADDING",
            (0, 0),
            (-1, -1),
            5
        )
    ]))

    story.append(status_table)

    # 4. DAFTAR PIPA RISIKO TINGGI

    story.append(
        Paragraph(
            "4. Daftar Pipa Berlabel Risiko Tinggi",
            section_style
        )
    )

    important = report[
        report["kategori_risiko_terkini"] == "Tinggi"
    ].head(30)

    rows = [[
        "ID Pipa",
        "Wilayah",
        "Usia",
        "Material",
        "Kondisi",
        "Status"
    ]]

    for _, row in important.iterrows():

        rows.append([
            escape(str(row["id_pipa"])),
            escape(str(row["wilayah"])),
            str(row["usia_pipa"]),
            escape(str(row["jenis_pipa"])),
            escape(str(row["kondisi_pipa"])),
            escape(str(row["status_penanganan"]))
        ])

    if len(rows) == 1:

        rows.append([
            "-",
            "Tidak ada data",
            "-",
            "-",
            "-",
            "-"
        ])

    pipe_table = Table(
        rows,
        repeatRows=1,
        colWidths=[
            22 * mm,
            26 * mm,
            13 * mm,
            22 * mm,
            22 * mm,
            48 * mm
        ]
    )

    pipe_table.setStyle(TableStyle([
        (
            "BACKGROUND",
            (0, 0),
            (-1, 0),
            colors.HexColor(NAVY)
        ),
        (
            "TEXTCOLOR",
            (0, 0),
            (-1, 0),
            colors.white
        ),
        (
            "FONTNAME",
            (0, 0),
            (-1, 0),
            "Helvetica-Bold"
        ),
        (
            "FONTSIZE",
            (0, 0),
            (-1, -1),
            7
        ),
        (
            "GRID",
            (0, 0),
            (-1, -1),
            .35,
            colors.HexColor("#D4DEE8")
        ),
        (
            "ROWBACKGROUNDS",
            (0, 1),
            (-1, -1),
            [
                colors.white,
                colors.HexColor("#F2F6FA")
            ]
        ),
        (
            "PADDING",
            (0, 0),
            (-1, -1),
            4
        )
    ]))

    story.append(pipe_table)

    story.append(
        Spacer(1, 5 * mm)
    )

    # CATATAN METODOLOGI

    story.append(
        Paragraph(
            "5. Catatan Metodologi",
            section_style
        )
    )

    story.append(
        Paragraph(
            "Prototype awal menggunakan dataset simulasi untuk "
            "menguji fungsi aplikasi dan proses klasifikasi. Dataset "
            "tersebut belum mewakili kondisi operasional asli "
            "perusahaan. Angka laporan perlu divalidasi menggunakan "
            "catatan operasional serta hasil pemeriksaan petugas. "
            "Kategori risiko bukan bukti bahwa pipa telah bocor.",
            small_style
        )
    )

    # FOOTER

    def footer(canvas, document):

        canvas.saveState()

        canvas.setFont(
            "Helvetica",
            8
        )

        canvas.setFillColor(
            colors.HexColor("#71849A")
        )

        canvas.drawString(
            16 * mm,
            9 * mm,
            "PERUMDA AIR MINUM X | Laporan Monitoring Jaringan Pipa"
        )

        canvas.drawRightString(
            A4[0] - 16 * mm,
            9 * mm,
            f"Halaman {document.page}"
        )

        canvas.restoreState()

    doc.build(
        story,
        onFirstPage=footer,
        onLaterPages=footer
    )

    return buffer.getvalue()


# ============================================================
# 7. MEMUAT DATA DAN MODEL
# ============================================================

try:

    data = normalize_data(
        read_pipe_data()
    )

    model = read_model()

except Exception as exc:

    st.error(
        f"Gagal memuat data atau model: {exc}"
    )

    st.stop()


required_columns = [
    "id_pipa",
    "wilayah",
    *FEATURES,
    "risiko_kebocoran"
]

missing = [
    column
    for column in required_columns
    if column not in data.columns
]

if missing:

    st.error(
        "Kolom dataset tidak ditemukan: "
        + ", ".join(missing)
    )

    st.stop()


data_view = current_view(data)


# ============================================================
# 8. SIDEBAR DAN NAVIGASI
# ============================================================

with st.sidebar:

    st.markdown(
        '<h2 style="color:white;">💧 PERUMDA X</h2>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<p style="font-size:10px;color:#D5E9FA;">'
        'SISTEM MONITORING JARINGAN AIR BERSIH</p>',
        unsafe_allow_html=True
    )

    st.divider()

    st.markdown(
        '<p style="font-size:11px;letter-spacing:1.5px;'
        'font-weight:700;">MENU UTAMA</p>',
        unsafe_allow_html=True
    )

    menu = st.radio(
        "Navigasi",
        [
            "Dashboard",
            "Data Pipa",
            "Prediksi Risiko",
            "Monitoring Penanganan",
            "Riwayat Prediksi",
            "Riwayat Penanganan",
            "Laporan"
        ],
        label_visibility="collapsed"
    )


# NOTIFIKASI

if "flash" in st.session_state:

    kind, message = st.session_state.pop("flash")

    if kind == "success":
        st.success(message)

    elif kind == "error":
        st.error(message)

    else:
        st.info(message)


# ============================================================
# 9. PERHITUNGAN DATA
# ============================================================

total = len(data_view)

high_count = int(
    (
        data_view["kategori_risiko_terkini"]
        == "Tinggi"
    ).sum()
)

medium_count = int(
    (
        data_view["kategori_risiko_terkini"]
        == "Sedang"
    ).sum()
)

low_count = int(
    (
        data_view["kategori_risiko_terkini"]
        == "Rendah"
    ).sum()
)

unclassified_count = int(
    (
        data_view["kategori_risiko_terkini"]
        == "Belum diklasifikasikan"
    ).sum()
)


# ============================================================
# 10. DASHBOARD
# ============================================================

if menu == "Dashboard":

    st.markdown(
        '<div class="hero">'
        '<div class="hero-brand">'
        '<span class="hero-drop">💧</span>'
        '<div>'
        '<div class="hero-name">PERUMDA AIR MINUM X</div>'
        '<div class="hero-caption">'
        'SISTEM MONITORING JARINGAN DISTRIBUSI AIR BERSIH'
        '</div>'
        '</div>'
        '</div>'
        '<h1>Sistem Monitoring dan Prediksi Risiko Kebocoran Pipa</h1>'
        '<p>'
        'Sistem ini menyajikan informasi mengenai kondisi jaringan '
        'distribusi air bersih serta mengidentifikasi tingkat risiko '
        'kebocoran berdasarkan karakteristik pipa. Proses klasifikasi '
        'menggunakan metode Random Forest untuk membantu pemantauan '
        'dan penentuan prioritas pemeriksaan.'
        '</p>'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-title">'
        'Ringkasan Monitoring Jaringan'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-subtitle">'
        'Gambaran jumlah pipa berdasarkan kategori tingkat risiko '
        'kebocoran pada jaringan distribusi air bersih.'
        '</div>',
        unsafe_allow_html=True
    )

    cols = st.columns(4)

    metrics = [
        (
            "TOTAL PIPA",
            total,
            NAVY,
            "Seluruh data jaringan"
        ),
        (
            "RISIKO TINGGI",
            high_count,
            RED,
            "Prioritas pemeriksaan"
        ),
        (
            "RISIKO SEDANG",
            medium_count,
            ORANGE,
            "Perlu pemantauan"
        ),
        (
            "RISIKO RENDAH",
            low_count,
            GREEN,
            "Pemeriksaan rutin"
        )
    ]

    for col, (label, value, color, note) in zip(
        cols,
        metrics
    ):

        with col:

            st.markdown(
                f'<div class="metric-card">'
                f'<div class="metric-label">{label}</div>'
                f'<div class="metric-value" style="color:{color};">'
                f'{value:,}</div>'
                f'<div class="metric-note">{note}</div>'
                f'</div>',
                unsafe_allow_html=True
            )

    if unclassified_count > 0:

        st.info(
            f"Terdapat {unclassified_count} pipa yang belum "
            "memiliki kategori risiko terkini."
        )

    st.write("")

    left, right = st.columns(2)

    with left:

        with st.container(border=True):

            st.subheader("Distribusi Tingkat Risiko")

            st.caption(
                "Jumlah pipa pada setiap kategori risiko."
            )

            fig, ax = plt.subplots(
                figsize=(6, 3.5)
            )

            values = [
                high_count,
                medium_count,
                low_count
            ]

            bars = ax.barh(
                ["Tinggi", "Sedang", "Rendah"],
                values,
                color=[RED, ORANGE, GREEN],
                height=.48
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
                linewidth=.8
            )

            ax.set_axisbelow(True)

            maximum = max(values) if max(values) > 0 else 1

            for bar in bars:

                ax.text(
                    bar.get_width() + maximum * .02,
                    bar.get_y() + bar.get_height() / 2,
                    str(int(bar.get_width())),
                    va="center",
                    fontsize=9,
                    color=NAVY,
                    fontweight="bold"
                )

            ax.set_xlim(
                0,
                maximum * 1.2
            )

            plt.tight_layout()

            st.pyplot(
                fig,
                use_container_width=True
            )

            plt.close(fig)

    with right:

        with st.container(border=True):

            st.subheader("Komposisi Tingkat Risiko")

            st.caption(
                "Persentase setiap kategori risiko terhadap seluruh data pipa."
            )

            fig, ax = plt.subplots(
                figsize=(6, 3.5)
            )

            values = [
                high_count,
                medium_count,
                low_count
            ]

            if sum(values) > 0:

                ax.pie(
                    values,
                    labels=[
                        "Tinggi",
                        "Sedang",
                        "Rendah"
                    ],
                    colors=[
                        RED,
                        ORANGE,
                        GREEN
                    ],
                    startangle=90,
                    counterclock=False,
                    autopct="%1.1f%%",
                    pctdistance=.78,
                    wedgeprops={
                        "width": .36,
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

            st.pyplot(
                fig,
                use_container_width=True
            )

            plt.close(fig)


# ============================================================
# 11. DATA PIPA
# ============================================================

elif menu == "Data Pipa":

    st.markdown(
        '<div class="page-title">'
        'Pengelolaan Data Jaringan Pipa'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="page-subtitle">'
        'Lihat, cari, tambahkan, perbarui, dan hapus data pipa '
        'yang tercatat.'
        '</div>',
        unsafe_allow_html=True
    )

    tab_view, tab_add, tab_edit = st.tabs(
        [
            "Lihat Data",
            "Tambah Data",
            "Edit / Hapus"
        ]
    )

    # --------------------------------------------------------
    # LIHAT DATA
    # --------------------------------------------------------

    with tab_view:

        with st.form("search_form"):

            c1, c2 = st.columns([2, 1])

            with c1:

                search_text = st.text_input(
                    "Cari ID Pipa atau Wilayah",
                    placeholder="Contoh: P001 atau Wilayah A"
                )

            with c2:

                risk_filter = st.selectbox(
                    "Kategori Risiko",
                    [
                        "Semua",
                        "Tinggi",
                        "Sedang",
                        "Rendah",
                        "Belum diklasifikasikan"
                    ]
                )

            search_submit = st.form_submit_button(
                "Cari Data",
                type="primary",
                use_container_width=True
            )

        if "search_saved" not in st.session_state:

            st.session_state["search_saved"] = ""
            st.session_state["filter_saved"] = "Semua"

        if search_submit:

            st.session_state["search_saved"] = (
                search_text.strip()
            )

            st.session_state["filter_saved"] = risk_filter

        shown = data_view.copy()

        query = st.session_state["search_saved"]
        selected_filter = st.session_state["filter_saved"]

        if query:

            mask = (
                shown["id_pipa"]
                .astype(str)
                .str.contains(
                    query,
                    case=False,
                    na=False
                )
                |
                shown["wilayah"]
                .astype(str)
                .str.contains(
                    query,
                    case=False,
                    na=False
                )
            )

            shown = shown[mask]

        if selected_filter != "Semua":

            shown = shown[
                shown["kategori_risiko_terkini"]
                == selected_filter
            ]

        columns = [
            "id_pipa",
            "wilayah",
            *FEATURES,
            "risiko_kebocoran",
            "hasil_prediksi_terakhir",
            "kategori_risiko_terkini",
            "status_penanganan"
        ]

        st.dataframe(
            shown[columns],
            hide_index=True,
            use_container_width=True,
            height=430
        )

        st.caption(
            f"Menampilkan {len(shown)} dari {len(data)} data pipa."
        )

        if st.button("Tampilkan Semua Data"):

            st.session_state["search_saved"] = ""
            st.session_state["filter_saved"] = "Semua"

            st.rerun()

    # --------------------------------------------------------
    # TAMBAH DATA
    # --------------------------------------------------------

    with tab_add:

        st.subheader("Tambah Data Pipa Baru")

        with st.form("add_pipe_form"):

            new_id = st.text_input(
                "ID Pipa",
                value=next_id(data)
            )

            new_area = st.text_input(
                "Wilayah",
                placeholder="Contoh: Wilayah A"
            )

            a, b = st.columns(2)

            with a:

                age = st.number_input(
                    "Usia Pipa (tahun)",
                    0,
                    100,
                    10
                )

                material = st.selectbox(
                    "Jenis Material",
                    ["PVC", "Besi", "HDPE"]
                )

                diameter = st.number_input(
                    "Diameter Pipa (mm)",
                    1,
                    1000,
                    100
                )

            with b:

                pressure = st.number_input(
                    "Tekanan Air (bar)",
                    0.0,
                    20.0,
                    3.0,
                    .1
                )

                history = st.number_input(
                    "Riwayat Kebocoran (kali)",
                    0,
                    100,
                    0
                )

                condition = st.selectbox(
                    "Kondisi Fisik",
                    ["Baik", "Sedang", "Buruk"]
                )

            add_submit = st.form_submit_button(
                "Simpan Data Pipa",
                type="primary",
                use_container_width=True
            )

        if add_submit:

            new_id = new_id.strip().upper()
            new_area = new_area.strip()

            if not new_id or not new_area:

                st.error(
                    "ID Pipa dan Wilayah wajib diisi."
                )

            elif new_id in data["id_pipa"].values:

                st.error(
                    "ID Pipa sudah digunakan. Masukkan ID berbeda."
                )

            else:

                new_row = {
                    "id_pipa": new_id,
                    "wilayah": new_area,
                    "usia_pipa": age,
                    "jenis_pipa": material,
                    "diameter_mm": diameter,
                    "tekanan_bar": pressure,
                    "riwayat_kebocoran": history,
                    "kondisi_pipa": condition,
                    "risiko_kebocoran": "Belum diklasifikasikan",
                    "hasil_prediksi_terakhir": "",
                    "tanggal_prediksi": "",
                    "status_penanganan": "Belum ditangani",
                    "petugas_penanganan": "",
                    "tanggal_penanganan": "",
                    "catatan_penanganan": ""
                }

                try:

                    updated = pd.concat(
                        [
                            data,
                            pd.DataFrame([new_row])
                        ],
                        ignore_index=True
                    )

                    save_pipe_data(
                        normalize_data(updated)
                    )

                    notify(
                        "success",
                        f"Data pipa {new_id} berhasil ditambahkan."
                    )

                    st.rerun()

                except Exception as exc:

                    st.error(
                        f"Data gagal disimpan: {exc}"
                    )

    # --------------------------------------------------------
    # EDIT DAN HAPUS
    # --------------------------------------------------------

    with tab_edit:

        st.subheader("Perbarui atau Hapus Data Pipa")

        if data.empty:

            st.info("Belum ada data pipa.")

        else:

            selected_id = st.selectbox(
                "Pilih ID Pipa",
                data["id_pipa"].tolist(),
                key="edit_pipe_id"
            )

            current = data[
                data["id_pipa"] == selected_id
            ].iloc[0]

            with st.form("edit_pipe_form"):

                edit_area = st.text_input(
                    "Wilayah",
                    value=str(current["wilayah"])
                )

                a, b = st.columns(2)

                with a:

                    edit_age = st.number_input(
                        "Usia Pipa (tahun)",
                        0,
                        100,
                        int(current["usia_pipa"])
                    )

                    type_options = [
                        "PVC",
                        "Besi",
                        "HDPE"
                    ]

                    old_type = str(current["jenis_pipa"])

                    edit_material = st.selectbox(
                        "Jenis Material",
                        type_options,
                        index=(
                            type_options.index(old_type)
                            if old_type in type_options
                            else 0
                        )
                    )

                    edit_diameter = st.number_input(
                        "Diameter Pipa (mm)",
                        1,
                        1000,
                        int(current["diameter_mm"])
                    )

                with b:

                    edit_pressure = st.number_input(
                        "Tekanan Air (bar)",
                        0.0,
                        20.0,
                        float(current["tekanan_bar"]),
                        .1
                    )

                    edit_history = st.number_input(
                        "Riwayat Kebocoran (kali)",
                        0,
                        100,
                        int(current["riwayat_kebocoran"])
                    )

                    condition_options = [
                        "Baik",
                        "Sedang",
                        "Buruk"
                    ]

                    old_condition = str(current["kondisi_pipa"])

                    edit_condition = st.selectbox(
                        "Kondisi Fisik",
                        condition_options,
                        index=(
                            condition_options.index(old_condition)
                            if old_condition in condition_options
                            else 0
                        )
                    )

                edit_submit = st.form_submit_button(
                    "Simpan Perubahan",
                    type="primary",
                    use_container_width=True
                )

            if edit_submit:

                if not edit_area.strip():

                    st.error("Wilayah wajib diisi.")

                else:

                    updated = data.copy()

                    idx = updated.index[
                        updated["id_pipa"] == selected_id
                    ][0]

                    updated.loc[idx, "wilayah"] = edit_area.strip()
                    updated.loc[idx, "usia_pipa"] = edit_age
                    updated.loc[idx, "jenis_pipa"] = edit_material
                    updated.loc[idx, "diameter_mm"] = edit_diameter
                    updated.loc[idx, "tekanan_bar"] = edit_pressure
                    updated.loc[idx, "riwayat_kebocoran"] = edit_history
                    updated.loc[idx, "kondisi_pipa"] = edit_condition

                    updated.loc[
                        idx,
                        "hasil_prediksi_terakhir"
                    ] = ""

                    updated.loc[
                        idx,
                        "tanggal_prediksi"
                    ] = ""

                    try:

                        save_pipe_data(
                            normalize_data(updated)
                        )

                        notify(
                            "success",
                            f"Data pipa {selected_id} berhasil diperbarui. "
                            "Lakukan prediksi ulang karena karakteristik berubah."
                        )

                        st.rerun()

                    except Exception as exc:

                        st.error(
                            f"Perubahan gagal disimpan: {exc}"
                        )

            st.divider()

            confirm = st.checkbox(
                f"Saya yakin ingin menghapus data {selected_id}.",
                key=f"confirm_{selected_id}"
            )

            if st.button(
                "Hapus Data Terpilih",
                disabled=not confirm
            ):

                try:

                    updated = data[
                        data["id_pipa"] != selected_id
                    ].copy()

                    save_pipe_data(updated)

                    notify(
                        "success",
                        f"Data pipa {selected_id} berhasil dihapus."
                    )

                    st.rerun()

                except Exception as exc:

                    st.error(
                        f"Data gagal dihapus: {exc}"
                    )


# ============================================================
# 12. PREDIKSI RISIKO
# ============================================================

elif menu == "Prediksi Risiko":

    st.markdown(
        '<div class="page-title">'
        'Prediksi Risiko Kebocoran Pipa'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="page-subtitle">'
        'Pilih pipa yang sudah terdaftar atau masukkan '
        'karakteristik pipa baru.'
        '</div>',
        unsafe_allow_html=True
    )

    mode = st.radio(
        "Metode Prediksi",
        [
            "Pipa Terdaftar",
            "Pipa Baru (Manual)"
        ],
        horizontal=True
    )

    # --------------------------------------------------------
    # PREDIKSI PIPA TERDAFTAR
    # --------------------------------------------------------

    if mode == "Pipa Terdaftar":

        if data.empty:

            st.info(
                "Belum ada data pipa. Tambahkan data melalui menu Data Pipa."
            )

        else:

            selected_id = st.selectbox(
                "Pilih ID Pipa",
                data["id_pipa"].tolist(),
                key="prediction_id"
            )

            row = data[
                data["id_pipa"] == selected_id
            ].iloc[0]

            record = make_record(row)

            st.subheader(
                "Identitas dan Karakteristik Pipa"
            )

            a, b, c = st.columns(3)

            a.metric(
                "Wilayah",
                record["wilayah"]
            )

            b.metric(
                "Usia Pipa",
                f"{record['usia_pipa']} tahun"
            )

            c.metric(
                "Material",
                record["jenis_pipa"]
            )

            d, e, f = st.columns(3)

            d.metric(
                "Diameter",
                f"{record['diameter_mm']} mm"
            )

            e.metric(
                "Tekanan",
                f"{record['tekanan_bar']:.1f} bar"
            )

            f.metric(
                "Riwayat Kebocoran",
                f"{record['riwayat_kebocoran']} kali"
            )

            st.write(
                f"**Kondisi fisik:** {record['kondisi_pipa']}"
            )

            if st.button(
                "Prediksi Risiko Pipa Ini",
                type="primary",
                use_container_width=True
            ):

                try:

                    category = predict_pipe(
                        record,
                        model
                    )

                    now = datetime.now().strftime(
                        "%Y-%m-%d %H:%M"
                    )

                    result = {
                        **record,
                        "hasil": category
                    }

                    updated = data.copy()

                    idx = updated.index[
                        updated["id_pipa"] == selected_id
                    ][0]

                    updated.loc[
                        idx,
                        "hasil_prediksi_terakhir"
                    ] = category

                    updated.loc[
                        idx,
                        "tanggal_prediksi"
                    ] = now

                    save_pipe_data(
                        normalize_data(updated)
                    )

                    append_record(
                        PREDICTION_FILE,
                        {
                            "tanggal_prediksi": now,
                            **record,
                            "hasil_prediksi": category
                        }
                    )

                    st.session_state["last_prediction"] = result

                    notify(
                        "success",
                        f"Prediksi {selected_id} berhasil disimpan. "
                        f"Hasil: risiko {category.lower()}."
                    )

                    st.rerun()

                except Exception as exc:

                    st.error(
                        f"Prediksi gagal: {exc}"
                    )

    # --------------------------------------------------------
    # PREDIKSI MANUAL
    # --------------------------------------------------------

    else:

        st.caption(
            "Gunakan pilihan ini untuk menguji pipa yang belum terdaftar."
        )

        with st.form("manual_prediction_form"):

            manual_id = st.text_input(
                "ID Pipa (opsional)",
                placeholder="Contoh: UJI-001"
            )

            manual_area = st.text_input(
                "Wilayah (opsional)",
                placeholder="Contoh: Wilayah A"
            )

            a, b = st.columns(2)

            with a:

                age = st.number_input(
                    "Usia Pipa (tahun)",
                    0,
                    100,
                    10
                )

                material = st.selectbox(
                    "Jenis Material",
                    [
                        "PVC",
                        "Besi",
                        "HDPE"
                    ]
                )

                diameter = st.number_input(
                    "Diameter Pipa (mm)",
                    1,
                    1000,
                    100
                )

            with b:

                pressure = st.number_input(
                    "Tekanan Air (bar)",
                    0.0,
                    20.0,
                    3.0,
                    .1
                )

                history = st.number_input(
                    "Riwayat Kebocoran (kali)",
                    0,
                    100,
                    0
                )

                condition = st.selectbox(
                    "Kondisi Fisik",
                    [
                        "Baik",
                        "Sedang",
                        "Buruk"
                    ]
                )

            save_new = st.checkbox(
                "Simpan pipa ini ke Data Pipa setelah prediksi"
            )

            submitted = st.form_submit_button(
                "Prediksi Pipa Baru",
                type="primary",
                use_container_width=True
            )

        if submitted:

            record = {
                "id_pipa": (
                    manual_id.strip().upper()
                    or "Pipa baru/manual"
                ),
                "wilayah": (
                    manual_area.strip()
                    or "Belum ditentukan"
                ),
                "usia_pipa": age,
                "jenis_pipa": material,
                "diameter_mm": diameter,
                "tekanan_bar": pressure,
                "riwayat_kebocoran": history,
                "kondisi_pipa": condition
            }

            if (
                save_new
                and record["id_pipa"] == "Pipa baru/manual"
            ):

                st.error(
                    "Isi ID Pipa sebelum menyimpan ke Data Pipa."
                )

            elif (
                save_new
                and record["id_pipa"] in data["id_pipa"].values
            ):

                st.error(
                    "ID Pipa sudah terdaftar. Gunakan ID berbeda."
                )

            else:

                try:

                    category = predict_pipe(
                        record,
                        model
                    )

                    now = datetime.now().strftime(
                        "%Y-%m-%d %H:%M"
                    )

                    result = {
                        **record,
                        "hasil": category
                    }

                    append_record(
                        PREDICTION_FILE,
                        {
                            "tanggal_prediksi": now,
                            **record,
                            "hasil_prediksi": category
                        }
                    )

                    if save_new:

                        new_row = {
                            **record,
                            "risiko_kebocoran": "Belum diklasifikasikan",
                            "hasil_prediksi_terakhir": category,
                            "tanggal_prediksi": now,
                            "status_penanganan": "Belum ditangani",
                            "petugas_penanganan": "",
                            "tanggal_penanganan": "",
                            "catatan_penanganan": ""
                        }

                        updated = pd.concat(
                            [
                                data,
                                pd.DataFrame([new_row])
                            ],
                            ignore_index=True
                        )

                        save_pipe_data(
                            normalize_data(updated)
                        )

                    st.session_state["last_prediction"] = result

                    notify(
                        "success",
                        f"Prediksi berhasil. Hasil: risiko {category.lower()}."
                    )

                    st.rerun()

                except Exception as exc:

                    st.error(
                        f"Prediksi gagal: {exc}"
                    )

    if "last_prediction" in st.session_state:

        show_prediction(
            st.session_state["last_prediction"],
            data
        )


# ============================================================
# 13. MONITORING PENANGANAN
# ============================================================

elif menu == "Monitoring Penanganan":

    st.markdown(
        '<div class="page-title">'
        'Monitoring Pemeriksaan dan Penanganan'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="page-subtitle">'
        'Perbarui status pemeriksaan dan perbaikan berdasarkan '
        'hasil pekerjaan petugas lapangan.'
        '</div>',
        unsafe_allow_html=True
    )

    a, b, c = st.columns(3)

    a.metric(
        "Belum Ditangani",
        int(
            (
                data["status_penanganan"]
                == "Belum ditangani"
            ).sum()
        )
    )

    b.metric(
        "Dalam Proses",
        int(
            data["status_penanganan"].isin([
                "Menunggu pemeriksaan",
                "Sedang diperiksa",
                "Dalam perbaikan"
            ]).sum()
        )
    )

    c.metric(
        "Selesai Ditangani",
        int(
            (
                data["status_penanganan"]
                == "Selesai ditangani"
            ).sum()
        )
    )

    st.subheader("Daftar Status Penanganan")

    st.dataframe(
        data[[
            "id_pipa",
            "wilayah",
            "hasil_prediksi_terakhir",
            "status_penanganan",
            "petugas_penanganan",
            "tanggal_penanganan",
            "catatan_penanganan"
        ]],
        hide_index=True,
        use_container_width=True
    )

    if not data.empty:

        selected_id = st.selectbox(
            "Pilih ID Pipa",
            data["id_pipa"].tolist(),
            key="handling_id"
        )

        row = data[
            data["id_pipa"] == selected_id
        ].iloc[0]

        st.write(
            f"**Wilayah:** {row['wilayah']} | "
            f"**Prediksi terakhir:** "
            f"{row['hasil_prediksi_terakhir'] or 'Belum ada'}"
        )

        old_status = str(
            row["status_penanganan"]
        )

        old_index = (
            STATUSES.index(old_status)
            if old_status in STATUSES
            else 0
        )

        with st.form("handling_form"):

            new_status = st.selectbox(
                "Status Penanganan",
                STATUSES,
                index=old_index
            )

            officer = st.text_input(
                "Nama Petugas",
                value=str(row["petugas_penanganan"])
            )

            handling_date = st.date_input(
                "Tanggal Pemeriksaan / Penanganan",
                value=date.today()
            )

            notes = st.text_area(
                "Catatan Pemeriksaan atau Perbaikan",
                value=str(row["catatan_penanganan"]),
                placeholder=(
                    "Tuliskan lokasi, temuan, tindakan, "
                    "dan hasil pekerjaan."
                )
            )

            save_status = st.form_submit_button(
                "Simpan Status Penanganan",
                type="primary",
                use_container_width=True
            )

        if save_status:

            updated = data.copy()

            pos = updated.index[
                updated["id_pipa"] == selected_id
            ][0]

            updated.loc[
                pos,
                "status_penanganan"
            ] = new_status

            updated.loc[
                pos,
                "petugas_penanganan"
            ] = officer.strip()

            updated.loc[
                pos,
                "tanggal_penanganan"
            ] = handling_date.isoformat()

            updated.loc[
                pos,
                "catatan_penanganan"
            ] = notes.strip()

            try:

                save_pipe_data(
                    normalize_data(updated)
                )

                append_record(
                    HANDLING_FILE,
                    {
                        "waktu_pencatatan": (
                            datetime.now().strftime(
                                "%Y-%m-%d %H:%M"
                            )
                        ),
                        "id_pipa": selected_id,
                        "wilayah": str(row["wilayah"]),
                        "status_sebelumnya": old_status,
                        "status_penanganan": new_status,
                        "petugas": officer.strip(),
                        "tanggal_penanganan": handling_date.isoformat(),
                        "catatan": notes.strip()
                    }
                )

                notify(
                    "success",
                    f"Status {selected_id} berhasil diperbarui "
                    f"menjadi {new_status}."
                )

                st.rerun()

            except Exception as exc:

                st.error(
                    f"Status gagal disimpan: {exc}"
                )


# ============================================================
# 14. RIWAYAT PREDIKSI
# ============================================================

elif menu == "Riwayat Prediksi":

    st.markdown(
        '<div class="page-title">Riwayat Prediksi</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="page-subtitle">'
        'Daftar hasil prediksi yang pernah dilakukan pada data pipa.'
        '</div>',
        unsafe_allow_html=True
    )

    if PREDICTION_FILE.exists():

        history = pd.read_csv(
            PREDICTION_FILE,
            keep_default_na=False
        )

        st.dataframe(
            history,
            hide_index=True,
            use_container_width=True
        )

        st.download_button(
            "Unduh Riwayat Prediksi CSV",
            data=history.to_csv(
                index=False
            ).encode("utf-8"),
            file_name="riwayat_prediksi.csv",
            mime="text/csv"
        )

    else:

        st.info(
            "Belum ada riwayat prediksi."
        )


# ============================================================
# 15. RIWAYAT PENANGANAN
# ============================================================

elif menu == "Riwayat Penanganan":

    st.markdown(
        '<div class="page-title">Riwayat Penanganan Pipa</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="page-subtitle">'
        'Riwayat perubahan status pemeriksaan dan penanganan pipa.'
        '</div>',
        unsafe_allow_html=True
    )

    if HANDLING_FILE.exists():

        history = pd.read_csv(
            HANDLING_FILE,
            keep_default_na=False
        )

        st.dataframe(
            history,
            hide_index=True,
            use_container_width=True
        )

        st.download_button(
            "Unduh Riwayat Penanganan CSV",
            data=history.to_csv(
                index=False
            ).encode("utf-8"),
            file_name="riwayat_penanganan.csv",
            mime="text/csv"
        )

    else:

        st.info(
            "Belum ada perubahan status penanganan yang dicatat."
        )


# ============================================================
# 16. LAPORAN
# ============================================================

elif menu == "Laporan":

    report = current_view(data)

    st.markdown(
        '<div class="page-title">'
        'Laporan Monitoring Jaringan Pipa'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="page-subtitle">'
        'Ringkasan kategori risiko dan status penanganan '
        'untuk dokumentasi dan pelaporan.'
        '</div>',
        unsafe_allow_html=True
    )

    total_report = len(report)

    high_report = int(
        (
            report["kategori_risiko_terkini"]
            == "Tinggi"
        ).sum()
    )

    medium_report = int(
        (
            report["kategori_risiko_terkini"]
            == "Sedang"
        ).sum()
    )

    low_report = int(
        (
            report["kategori_risiko_terkini"]
            == "Rendah"
        ).sum()
    )

    in_progress = int(
        report["status_penanganan"].isin([
            "Menunggu pemeriksaan",
            "Sedang diperiksa",
            "Dalam perbaikan"
        ]).sum()
    )

    completed = int(
        (
            report["status_penanganan"]
            == "Selesai ditangani"
        ).sum()
    )

    a, b, c, d = st.columns(4)

    a.metric(
        "Total Data Pipa",
        total_report
    )

    b.metric(
        "Risiko Tinggi",
        high_report
    )

    c.metric(
        "Dalam Proses",
        in_progress
    )

    d.metric(
        "Selesai Ditangani",
        completed
    )

    # DISTRIBUSI RISIKO

    st.subheader("Distribusi Risiko")

    risk_summary = pd.DataFrame({
        "Kategori Risiko": [
            "Tinggi",
            "Sedang",
            "Rendah",
            "Belum diklasifikasikan"
        ],
        "Jumlah Pipa": [
            high_report,
            medium_report,
            low_report,
            unclassified_count
        ]
    })

    st.dataframe(
        risk_summary,
        hide_index=True,
        use_container_width=True
    )

    # STATUS PENANGANAN

    st.subheader(
        "Ringkasan Status Penanganan"
    )

    status_summary = (
        report["status_penanganan"]
        .value_counts()
        .rename_axis("Status")
        .reset_index(name="Jumlah Pipa")
    )

    st.dataframe(
        status_summary,
        hide_index=True,
        use_container_width=True
    )

    # INFORMASI LAPORAN

    st.info(
        "Laporan dibuat ulang dari data terbaru setiap kali halaman "
        "ini dimuat. Setelah ada perubahan, unduh kembali dokumen "
        "agar file yang tersimpan di perangkat berisi data terbaru."
    )

    # UNDUH PDF DAN WORD

    st.subheader("Unduh Laporan untuk Atasan")

    try:

        pdf_bytes = create_pdf_report(report)
        word_bytes = create_word_report(report)

        col_pdf, col_word = st.columns(2)

        with col_pdf:

            st.download_button(
                label="Unduh Laporan Monitoring (PDF)",
                data=pdf_bytes,
                file_name=(
                    "laporan_monitoring_pipa_"
                    f"{date.today().isoformat()}.pdf"
                ),
                mime="application/pdf",
                type="primary",
                use_container_width=True
            )

        with col_word:

            st.download_button(
                label="Unduh Laporan Monitoring (Word)",
                data=word_bytes,
                file_name=(
                    "laporan_monitoring_pipa_"
                    f"{date.today().isoformat()}.docx"
                ),
                mime=(
                    "application/vnd.openxmlformats-officedocument."
                    "wordprocessingml.document"
                ),
                use_container_width=True
            )

    except Exception as exc:

        st.error(
            f"Gagal membuat laporan PDF/Word: {exc}"
        )

    # UNDUH DATA CSV

    st.subheader("Unduh Data Pipa")

    csv_bytes = report.drop(
        columns=[
            "label_risiko_dataset",
            "sumber_kategori_risiko"
        ],
        errors="ignore"
    ).to_csv(
        index=False
    ).encode("utf-8-sig")

    st.download_button(
        "Unduh Data Pipa Terbaru (CSV)",
        data=csv_bytes,
        file_name=(
            f"data_pipa_terbaru_{date.today().isoformat()}.csv"
        ),
        mime="text/csv",
        use_container_width=True
    )

    st.caption(
        "File CSV berisi data pipa beserta kategori risiko terkini."
    )